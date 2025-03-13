CREATE DATABASE IF NOT EXISTS gestion_examens;
USE gestion_examens;


DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS statistiques;
DROP TABLE IF EXISTS plagiat;
DROP TABLE IF EXISTS corrections;
DROP TABLE IF EXISTS copies;
DROP TABLE IF EXISTS examens;
DROP TABLE IF EXISTS enseignants;
DROP TABLE IF EXISTS etudiants;


CREATE TABLE etudiants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom_complet VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    classe Varchar(50) NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE enseignants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom_complet VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE examens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    description TEXT,
    type ENUM('examen', 'quiz', 'devoir') NOT NULL,
    classe Varchar(50) NOT NULL,
    chemin VARCHAR(255) NOT NULL,
    chemin_correction VARCHAR(255) NOT NULL,
    idprof INT NOT NULL,
    datedesoumission DATETIME NOT NULL,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (idprof) REFERENCES enseignants(id) ON DELETE CASCADE
);


CREATE TABLE copies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_examen INT NOT NULL,
    id_etudiant INT NOT NULL,
    fichier_pdf VARCHAR(255) NOT NULL,
    date_soumission TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_examen) REFERENCES examens(id) ON DELETE CASCADE,
    FOREIGN KEY (id_etudiant) REFERENCES etudiants(id) ON DELETE CASCADE
);


CREATE TABLE corrections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_copie INT NOT NULL,
    note DECIMAL(5,2),
    commentaire TEXT,
    correction_automatique BOOLEAN DEFAULT TRUE,
    date_correction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_copie) REFERENCES copies(id) ON DELETE CASCADE
);


CREATE TABLE plagiat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_copie INT NOT NULL,
    score_similarite DECIMAL(5,2),
    rapport TEXT,
    date_analyse TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_copie) REFERENCES copies(id) ON DELETE CASCADE
);


CREATE TABLE statistiques (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_examen INT NOT NULL,
    moyenne DECIMAL(5,2),
    ecart_type DECIMAL(5,2),
    taux_reussite DECIMAL(5,2),
    date_calcul TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_examen) REFERENCES examens(id) ON DELETE CASCADE
);


CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_etudiant INT NULL,
    id_enseignant INT NULL,
    message TEXT NOT NULL,
    reponse TEXT,
    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_etudiant) REFERENCES etudiants(id) ON DELETE CASCADE,
    FOREIGN KEY (id_enseignant) REFERENCES enseignants(id) ON DELETE CASCADE
);
