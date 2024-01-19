from datetime import datetime, timedelta
from contextlib import contextmanager
from flask import Flask, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask import abort
from flask import render_template, request, redirect, url_for
from sqlalchemy import and_
from isoweek import Week

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emploidutemps.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Utilisateur(db.Model):
    Numero_etudiant = db.Column(db.Integer, primary_key=True)
    Mot_de_passe = db.Column(db.String(50), nullable=False)
    Niveau_etude = db.Column(db.String(10), nullable=False)
    Code_TD = db.Column(db.String(500), db.ForeignKey('etudiants.Code_TD'), nullable=False)
    etudiants_relation = db.relationship('Etudiants', back_populates='utilisateur_relation', lazy=True)
    
class Etudiants(db.Model): 
    Code_TD = db.Column(db.String(500), primary_key=True)
    Nom_TD = db.Column(db.String(500))
    Code_cours = db.Column(db.String(500), db.ForeignKey('cours.Code_cours'), nullable=False)
    Niveau_etude = db.Column(db.String(10))
    utilisateur_relation = db.relationship('Utilisateur', back_populates='etudiants_relation', lazy=True)

class Cours(db.Model):
    Code_cours = db.Column(db.String(500), primary_key=True)
    Jour = db.Column(db.Date, db.ForeignKey('jours.Datej'), nullable=False)
    Duree = db.Column(db.String(50))
    Debut = db.Column(db.String(10))
    Fin = db.Column(db.String(10))
    Activite = db.Column(db.String(100))
    Salle = db.Column(db.String(200))
    Enseignant = db.Column(db.String(100))
    Type_cours = db.Column(db.String(100))
    Groupe_TD = db.Column(db.String(300))
    Niveau_etude = db.Column(db.String(10))
    jour_relation = db.relationship('Jours', back_populates='cours_relation', lazy=True)

class Jours(db.Model):
    Datej = db.Column(db.Date, primary_key=True)
    Jour_semaine = db.Column(db.String(50), nullable=False)
    cours_relation = db.relationship('Cours', back_populates='jour_relation', lazy=True)

class Salle(db.Model):
    Nom_salle = db.Column(db.String(500), primary_key=True)
    Code_cours = db.Column(db.String(500), db.ForeignKey('cours.Code_cours'), nullable=False)
    Batiment = db.Column(db.Text(100))
    Capacite = db.Column(db.Integer)

class Enseignants(db.Model):
    Enseignant_nom = db.Column(db.String(200), primary_key=True)
    Code_cours = db.Column(db.String(500), db.ForeignKey('cours.Code_cours'), nullable=False)
    cours_relation = db.relationship('Cours', backref='enseignant', lazy=True)


with app.app_context():
    db.create_all()

@contextmanager
def get_db_session():
    """Gestionnaire de contexte pour la session de base de données."""
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
    finally:
        db.session.close()

@app.route('/jours', methods=['GET'])
def get_jours():
    jours = Jours.query.all()
    if not jours:
        abort(404, description="Aucun jour trouvé")
    jours_list = [{'Datej': j.Datej, 'Jour_semaine': j.Jour_semaine} for j in jours]
    return jsonify({'jours': jours_list})

@app.route('/cours', methods=['GET'])
def get_cours():
    cours = Cours.query.all()
    cours_list = [{'Code_cours': c.Code_cours, 'Jour': c.Jour, 'Duree': c.Duree, 'Debut': c.Debut, 'Fin': c.Fin,
                   'Activite': c.Activite, 'Salle': c.Salle, 'Enseignant': c.Enseignant, 'Type_cours': c.Type_cours,
                   'Groupe_TD': c.Groupe_TD, 'Niveau_etude': c.Niveau_etude} for c in cours]
    return jsonify({'cours': cours_list})

@app.route('/salle', methods=['GET'])
def get_salle():
    salles = Salle.query.all()
    salle_list = [{'Nom_salle': s.Nom_salle, 'Code_cours': s.Code_cours, 'Batiment': s.Batiment, 'Capacite': s.Capacite} for s in salles]
    return jsonify({'salles': salle_list})

@app.route('/enseignants', methods=['GET'])
def get_enseignants():
    enseignants = Enseignants.query.all()
    enseignants_list = [{'Enseignant_nom': e.Enseignant_nom, 'Code_cours': e.Code_cours} for e in enseignants]
    return jsonify({'enseignants': enseignants_list})

@app.route('/etudiants', methods=['GET'])
def get_etudiants():
    etudiants = Etudiants.query.all()
    etudiants_list = [{'Code_TD': e.Code_TD, 'Nom_TD': e.Nom_TD, 'Code_cours': e.Code_cours, 'Niveau_etude': e.Niveau_etude} for e in etudiants]
    return jsonify({'etudiants': etudiants_list})

@app.route('/', methods=['GET', 'POST'])
def home():
    code_td = None  # Définir une valeur par défaut

    if request.method == 'POST':
        if 'connexion' in request.form:
            numero_etudiant = request.form.get('Numero_etudiant')
            mot_de_passe = request.form.get('Mot_de_passe')

            utilisateur = Utilisateur.query.filter_by(Numero_etudiant=numero_etudiant, Mot_de_passe=mot_de_passe).first()

            if utilisateur:
                code_td = utilisateur.Code_TD  # Mettre à jour code_td si l'utilisateur est trouvé
                return redirect(url_for('emplois_du_temps', Code_TD=code_td))
            else:
                return 'Échec de l\'authentification'

        elif 'inscription' in request.form:
            numero_etudiant = request.form.get('numero_etudiant')
            mot_de_passe = request.form.get('mot_de_passe')
            niveau_etude = request.form.get('niveau_etude')
            code_td = request.form.get('code_td')

            nouvel_utilisateur = Utilisateur(Numero_etudiant=numero_etudiant, Mot_de_passe=mot_de_passe, Niveau_etude=niveau_etude, Code_TD=code_td)
            db.session.add(nouvel_utilisateur)
            db.session.commit()
            return redirect(url_for('emplois_du_temps', Code_TD=code_td))

    return render_template('accueil.html')

@app.route('/emplois_du_temps/<Code_TD>', methods=['GET', 'POST'])
def emplois_du_temps(Code_TD):
    niveaux_etude = ['L1', 'L2', 'L3']

    groupes_td = {
        'L1': ['TD06 - MIASHS + Bessières Maths', 'TD07 - MIASHS', 'TD08 - MIASHS (et Oui, si)', 'TD09 - DL Economie-Maths', 'TD10 - DL Gestion-Info', 'TD11 - Economie-Gestion CMI'],
        'L2': ['TD06 - MIASHS (Maths Appliquées) + Bessières', 'TD07 - DL Économie-Maths', 'TD08 - MIASHS parcours MIAGE', 'TD09 - MIASHS parcours MIAGE', 'TD10 - DL Gestion-Informatique', 'TD11 - Économie-Gestion CMI'],
        'L3': ['TD1 - L3 MIAGE CLA', 'TD2 - L3 MIAGE CLA', 'TD3 - DL Info-Gestion', 'TD03 - CMI']
    }

    if request.method == 'POST':
        niveau_etude_selectionne = request.form.get('niveau_etude')
        groupe_td_selectionne = request.form.get('groupe_td')

        # Nouveau champ pour la date spécifiée par l'utilisateur
        date_selectionnee = request.form.get('date_selectionnee')

        # Récupérer les cours correspondant au niveau d'étude, au groupe TD et à la date sélectionnée
        cours_data = get_cours_from_database(niveau_etude_selectionne, groupe_td_selectionne, date_selectionnee)

        return render_template('emplois_du_temps.html', niveaux_etude=niveaux_etude,
                               groupes_td=groupes_td,
                               niveau_etude_selectionne=niveau_etude_selectionne,
                               date_selectionnee=date_selectionnee,
                               groupe_td_selectionne=groupe_td_selectionne,
                               cours_data=cours_data)

    return render_template('emplois_du_temps.html', niveaux_etude=niveaux_etude, groupes_td=groupes_td)


def get_cours_from_database(niveau_etude, groupe_td, date_selectionnee):
    print(f"Niveau d'étude: {niveau_etude}")
    print(f"Groupe TD: {groupe_td}")
    print(f"Date sélectionnée: {date_selectionnee}")
    
    # Récupérer tous les cours correspondant au niveau d'étude, groupe TD, jour et date sélectionnée
    cours_data = Cours.query.filter(
        Cours.Niveau_etude == niveau_etude,
        Cours.Groupe_TD.ilike(f"%{groupe_td}%"),
        Cours.Jour == date_selectionnee  
    ).all()

    cours_list = []
    print(f"Cours data: {cours_data}")

    for cours in cours_data:
        cours_list.append({
            'Code_cours': cours.Code_cours,
            'Jour': cours.Jour,
            'Duree': cours.Duree,
            'Debut': cours.Debut,
            'Fin': cours.Fin,
            'Activite': cours.Activite,
            'Salle': cours.Salle,
            'Enseignant': cours.Enseignant,
            'Type_cours': cours.Type_cours,
            'Groupe_TD': cours.Groupe_TD,
            'Niveau_etude': cours.Niveau_etude
        })

    return cours_list

def verifier_nom_enseignant(nom_enseignant):
    # Vérifiez si le nom de l'enseignant existe dans la base de données
    enseignant = Enseignants.query.filter_by(Enseignant_nom=nom_enseignant).first()
    
    # Si l'enseignant existe, retournez True, sinon, retournez False
    return enseignant is not None

@app.route('/espace_enseignant', methods=['GET', 'POST'])
def espace_enseignant():
    if request.method == 'POST':
        nom_enseignant = request.form.get('nom_enseignant')

        # Vérifiez si le nom de l'enseignant existe dans la base de données
        if verifier_nom_enseignant(nom_enseignant):
            # Nom de l'enseignant vérifié, affichez la page pour le code secret
            return render_template('code_secret.html', nom_enseignant=nom_enseignant)
        else:
            flash("Nom d'enseignant incorrect. Veuillez réessayer.", 'danger')

    return render_template('espace_enseignant.html')

def convertir_format_semaine(date_semaine):
    year, week = map(int, date_semaine.split('-W'))
    debut_semaine = Week(year, week).monday()
    fin_semaine = Week(year, week).saturday()
    return debut_semaine.strftime('%Y-%m-%d'), fin_semaine.strftime('%Y-%m-%d')

CODE_SECRET_ENSEIGNANT = '20232024'
@app.route('/verifier_code_secret', methods=['POST'])
def verifier_code_secret():
    nom_enseignant = request.form.get('nom_enseignant')
    code_secret_saisi = request.form.get('code_secret')
    date_semaine = request.form.get('date_semaine')

    if code_secret_saisi == CODE_SECRET_ENSEIGNANT:
        debut_semaine, fin_semaine = convertir_format_semaine(date_semaine)
        cours_enseignant = obtenir_cours_enseignant_par_semaine(nom_enseignant, debut_semaine, fin_semaine)
        return render_template('emploidutemps_enseignant.html', nom_enseignant=nom_enseignant, cours_enseignant_par_semaine=cours_enseignant)
    else:
        flash('Code secret incorrect. Veuillez réessayer.')
        return redirect(url_for('espace_enseignant'))


@app.route('/obtenir_cours_semaine/<nom_enseignant>/<semaine>', methods=['GET'])
def cours_enseignant_par_semaine(nom_enseignant, date_semaine):
    debut_semaine, fin_semaine = convertir_format_semaine(date_semaine)
    cours_semaine = obtenir_cours_enseignant_par_semaine(nom_enseignant, debut_semaine, fin_semaine)
    return jsonify(cours_semaine)

def obtenir_cours_enseignant_par_semaine(nom_enseignant, debut_semaine, fin_semaine):
    cours_enseignant = Cours.query.filter(
        and_(
            Cours.enseignant.any(Enseignants.Enseignant_nom == nom_enseignant),
            Cours.Jour.between(debut_semaine, fin_semaine)
        )
    ).all()

    cours_par_semaine = {}

    for cours in cours_enseignant:
        semaine = cours.Jour.strftime('%Y-%m-%d')
        if semaine not in cours_par_semaine:
            cours_par_semaine[semaine] = []
        cours_par_semaine[semaine].append({
            'Code_cours': cours.Code_cours,
            'Jour': cours.Jour,
            'Duree': cours.Duree,
            'Debut': cours.Debut,
            'Fin': cours.Fin,
            'Activite': cours.Activite,
            'Salle': cours.Salle,
            'Type_cours': cours.Type_cours,
            'Groupe_TD': cours.Groupe_TD,
            'Niveau_etude': cours.Niveau_etude
        })

    return cours_par_semaine


if __name__ == '__main__':
    app.run(debug=True)

