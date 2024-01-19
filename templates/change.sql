-- SQLite
CREATE TABLE commentaire (
    id INT PRIMARY KEY,
    Commentaire VARCHAR(500),
    Code_cours VARCHAR(500),
    FOREIGN KEY (Code_cours) REFERENCES Cours(Code_cours)
);