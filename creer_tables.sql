-- Table GroupeTD : groupes d'étudiants
CREATE TABLE GroupeTD (
  ID_TD INTEGER PRIMARY KEY AUTOINCREMENT,
  Code_TD TEXT NOT NULL,
  Nom_TD TEXT NOT NULL,
  Niveau_etude TEXT NOT NULL
);

-- Table Utilisateur : étudiants et enseignants avec rôle
CREATE TABLE Utilisateur (
  Numero_utilisateur INTEGER PRIMARY KEY,
  Mot_de_passe TEXT NOT NULL,
  Role TEXT NOT NULL CHECK(Role IN ('etudiant', 'enseignant')),
  Nom TEXT NOT NULL,
  Prenom TEXT NOT NULL,

  -- Uniquement pour les étudiants :
  Niveau_etude TEXT,
  ID_TD TEXT,
  FOREIGN KEY (ID_TD) REFERENCES GroupeTD(ID_TD)
);

-- Table Jour : dates et jours de la semaine
CREATE TABLE Jour (
  date_jour DATE PRIMARY KEY,
  jour_semaine TEXT NOT NULL
);


-- Table Cours : description des cours
CREATE TABLE Cours (
  Code_cours TEXT PRIMARY KEY,
  date_jour DATE NOT NULL,
  Duree TEXT NOT NULL,
  Debut TEXT NOT NULL,
  Fin TEXT NOT NULL,
  Activite TEXT NOT NULL,
  Type_cours TEXT NOT NULL,
  Niveau_etude TEXT NOT NULL,
  FOREIGN KEY (date_jour) REFERENCES Jour(date_jour)
);

-- Table de liaison entre Cours et Salles (car un cours peut avoir lieu dans plusieurs salles)
CREATE TABLE Salles (
    Nom_salle TEXT,
    Code_cours TEXT,
    Batiment TEXT NOT NULL,
    Capacite INTEGER NOT NULL,
    PRIMARY KEY (Code_cours, Nom_salle),
    FOREIGN KEY (Code_cours) REFERENCES Cours(Code_cours)
);

-- Table de liaison entre Enseignant et Cours
CREATE TABLE Enseignant_Cours (
  Enseignant_nom TEXT,
  Code_cours TEXT,
  PRIMARY KEY (Enseignant_nom, Code_cours),
  FOREIGN KEY (Enseignant_nom) REFERENCES Utilisateur(Nom),
  FOREIGN KEY (Code_cours) REFERENCES Cours(Code_cours)
);

-- Table de liaison entre Cours et Groupes TD (relation n-n)
CREATE TABLE Cours_GroupeTD (
  Code_cours TEXT,
  ID_TD INTEGER,
  PRIMARY KEY (Code_cours, ID_TD),
  FOREIGN KEY (Code_cours) REFERENCES Cours(Code_cours),
  FOREIGN KEY (ID_TD) REFERENCES GroupeTD(ID_TD)
);