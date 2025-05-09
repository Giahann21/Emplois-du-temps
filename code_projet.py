from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_de_donnees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret'
db = SQLAlchemy(app)

# Modèles (adaptés à la nouvelle structure de la BDD)
class GroupeTD(db.Model):
    __tablename__ = 'GroupeTD'
    ID_TD = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Code_TD = db.Column(db.String(50), nullable=False)
    Nom_TD = db.Column(db.String(200), nullable=False)
    Niveau_etude = db.Column(db.String(10), nullable=False)

class Utilisateur(db.Model):
    __tablename__ = 'Utilisateur'
    Numero_utilisateur = db.Column(db.Integer, primary_key=True)
    Mot_de_passe = db.Column(db.String(50), nullable=False)
    Role = db.Column(db.String(20), nullable=False)
    Nom = db.Column(db.String(100), nullable=False)
    Prenom = db.Column(db.String(100), nullable=False)
    Niveau_etude = db.Column(db.String(10))
    ID_TD = db.Column(db.Integer, db.ForeignKey('GroupeTD.ID_TD'))

class Jour(db.Model):
    __tablename__ = 'Jour'
    date_jour = db.Column(db.Date, primary_key=True)
    jour_semaine = db.Column(db.String(50), nullable=False)

class Cours(db.Model):
    __tablename__ = 'Cours'
    Code_cours = db.Column(db.String(100), primary_key=True)
    date_jour = db.Column(db.Date, db.ForeignKey('jour.date_jour'), nullable=False)
    Duree = db.Column(db.String(10), nullable=False)
    Debut = db.Column(db.String(10), nullable=False)
    Fin = db.Column(db.String(10), nullable=False)
    Activite = db.Column(db.String(100), nullable=False)
    Type_cours = db.Column(db.String(50), nullable=False)
    Niveau_etude = db.Column(db.String(10), nullable=False)

class CoursGroupeTD(db.Model):
    __tablename__ = 'Cours_GroupeTD'
    Code_cours = db.Column(db.String(100), db.ForeignKey('cours.Code_cours'), primary_key=True)
    ID_TD = db.Column(db.Integer, db.ForeignKey('groupe_t_d.ID_TD'), primary_key=True)

class EnseignantCours(db.Model):
    __tablename__ = 'Enseignant_Cours'
    Enseignant_nom = db.Column(db.String(100), db.ForeignKey('utilisateur.Nom'), primary_key=True)
    Code_cours = db.Column(db.String(100), db.ForeignKey('cours.Code_cours'), primary_key=True)

class Salle(db.Model):
    __tablename__ = 'Salles'
    Nom_salle = db.Column(db.String(100), primary_key=True)
    Code_cours = db.Column(db.String(100), db.ForeignKey('cours.Code_cours'), primary_key=True)
    Batiment = db.Column(db.String(100), nullable=False)
    Capacite = db.Column(db.Integer, nullable=False)

# Routes Flask
@app.route('/')
def home():
    return render_template('accueil.html')

@app.route('/connexion', methods=['POST'])
def connexion():
    numero = request.form.get('Numero_etudiant')
    mdp = request.form.get('Mot_de_passe')
    user = Utilisateur.query.filter_by(Numero_utilisateur=numero, Mot_de_passe=mdp).first()
    if user and user.Role == 'etudiant':
        return redirect(url_for('emplois_du_temps', id_td=user.ID_TD))
    flash("Échec de l'authentification", 'danger')
    return redirect(url_for('home'))

@app.route('/inscription', methods=['POST'])
def inscription():
    try:
        numero = request.form['numero_etudiant']
        existant = Utilisateur.query.filter_by(Numero_utilisateur=numero).first()
        if existant:
            flash("Cet étudiant est déjà inscrit.", 'warning')
            return redirect(url_for('home'))

        data = Utilisateur(
            Numero_utilisateur=numero,
            Mot_de_passe=request.form['mot_de_passe'],
            Role='etudiant',
            Nom=request.form['nom'],
            Prenom=request.form['prenom'],
            Niveau_etude=request.form['niveau_etude'],
            ID_TD=int(request.form['id_td'])
        )
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('emplois_du_temps', id_td=data.ID_TD))
    except Exception as e:
        db.session.rollback()
        return f"Erreur lors de l'inscription : {e}", 500

@app.route('/emplois_du_temps/<int:id_td>', methods=['GET', 'POST'])
def emplois_du_temps(id_td):
    td_connecte = db.session.get(GroupeTD, id_td)
    niveaux_etude = ['L1', 'L2', 'L3']

    # Récupère tous les groupes TD classés par niveau
    groupes_td = {
        niveau: GroupeTD.query.filter_by(Niveau_etude=niveau).all()
        for niveau in niveaux_etude
    }

    # Valeurs par défaut
    td_utilise = td_connecte
    niveau_etude_selectionne = td_connecte.Niveau_etude
    nom_td_selectionne = td_connecte.Nom_TD
    date_selectionnee = None

    if request.method == 'POST':
        niveau_etude_selectionne = request.form.get('niveau_etude')
        nom_td_selectionne = request.form.get('groupe_td')  # Utilise Nom_TD ici
        date_selectionnee = request.form.get('date_selectionnee')

        # Sélectionne le bon groupe TD par Nom_TD
        td_utilise = GroupeTD.query.filter_by(Nom_TD=nom_td_selectionne, Niveau_etude=niveau_etude_selectionne).first()

        if td_utilise:
            id_td = td_utilise.ID_TD
        else:
            flash("Le groupe TD sélectionné n'existe pas.", 'danger')
            td_utilise = td_connecte
            id_td = td_connecte.ID_TD

    # Récupère les cours associés à ce TD
    cours_ids = CoursGroupeTD.query.filter_by(ID_TD=id_td).with_entities(CoursGroupeTD.Code_cours).all()
    cours_query = Cours.query.filter(Cours.Code_cours.in_([cid[0] for cid in cours_ids]))

    if date_selectionnee:
        cours_query = cours_query.filter(Cours.date_jour == date_selectionnee)

    cours = cours_query.all()

    # Construction de la table des cours
    cours_data = []
    for c in cours:
        salles = Salle.query.filter_by(Code_cours=c.Code_cours).with_entities(Salle.Nom_salle).all()
        enseignants = EnseignantCours.query.filter_by(Code_cours=c.Code_cours).with_entities(EnseignantCours.Enseignant_nom).all()
        cours_data.append({
            'Code_cours': c.Code_cours,
            'Jour': c.date_jour,
            'Duree': c.Duree,
            'Debut': c.Debut,
            'Fin': c.Fin,
            'Activite': c.Activite,
            'Type_cours': c.Type_cours,
            'Niveau_etude': c.Niveau_etude,
            'Salle': ", ".join([s[0] for s in salles]),
            'Enseignant': ", ".join([e[0] for e in enseignants]),
            'Nom_TD': td_utilise.Nom_TD
        })

    return render_template('emplois_du_temps.html',
                           cours_data=cours_data,
                           niveaux_etude=niveaux_etude,
                           groupes_td=groupes_td,
                           niveau_etude_selectionne=niveau_etude_selectionne,
                           groupe_td_selectionne=nom_td_selectionne,
                           date_selectionnee=date_selectionnee,
                           nom_td=td_utilise.Nom_TD,
                           groupe=td_utilise)

@app.route('/espace_enseignant', methods=['GET', 'POST'])
def espace_enseignant():
    if request.method == 'POST':
        nom = request.form['nom_enseignant']
        user = Utilisateur.query.filter_by(Nom=nom, Role='enseignant').first()
        if user:
            return render_template('code_secret.html', nom_enseignant=nom)
        flash("Nom incorrect", 'danger')
    return render_template('espace_enseignant.html')

@app.route('/verifier_code_secret', methods=['POST'])
def verifier_code_secret():
    nom = request.form['nom_enseignant']
    code = request.form['code_secret']
    if code == "20232024":
        return redirect(url_for('emplois_du_temps_enseignant', nom_enseignant=nom))
    flash("Code incorrect", 'danger')
    return redirect(url_for('espace_enseignant'))

@app.route('/emplois_du_temps_enseignant/<nom_enseignant>')
def emplois_du_temps_enseignant(nom_enseignant):
    cours_ids = EnseignantCours.query.filter_by(Enseignant_nom=nom_enseignant).with_entities(EnseignantCours.Code_cours).all()
    cours = Cours.query.filter(Cours.Code_cours.in_([cid[0] for cid in cours_ids])).all()
    return render_template('emploidutemps_enseignant.html', nom_enseignant=nom_enseignant, cours_enseignant=cours)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
