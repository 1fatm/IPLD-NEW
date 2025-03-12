from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector,os,re

app = Flask(__name__)
app.secret_key = 'your_love'
import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="gestion_examens"
    )
    print("Connexion réussie à la base de données.")
except mysql.connector.Error as err:
    print(f"Erreur de connexion : {err}")

if db.is_connected():
    cursor = db.cursor()
    curseur = db.cursor()
def inscriptionetu():
    if request.method == 'POST':
        nom_complet = request.form['name']
        email = request.form['email']
        mot_de_passe = request.form['password']
        confirm_password = request.form['confirm-password']
        classe = request.form['classe']
        if mot_de_passe != confirm_password:
            erreur_password="Les mots de passe ne correspondent pas."
            return render_template('inscription_etudiant.html', erreur_password=erreur_password)

        mot_de_passe_hash = generate_password_hash(mot_de_passe)

        cursor = db.cursor()
        cursor.execute("SELECT * FROM etudiants WHERE email = %s", (email,))
        utilisateur_exist = cursor.fetchone()

        if utilisateur_exist:
            erreur_message="Utilisateur deja existant"
            return render_template('inscription_etudiant.html', erreur_message=erreur_message)

        sql = "INSERT INTO etudiants (nom_complet, email, mot_de_passe, classe) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (nom_complet, email, mot_de_passe_hash, classe))
        db.commit()
        cursor.close()

        succes_message="Inscription réussie !"
        return render_template ('inscription_etudiant.html',succes_message=succes_message)

def inscriptionprof():
    if request.method == 'POST':
        nom_complet = request.form['name']
        email = request.form['email']
        mot_de_passe = request.form['password']
        confirm_password = request.form['confirm-password']

        if mot_de_passe != confirm_password:
            erreur_password="Les mots de passe ne correspondent pas."
            return render_template('inscription_prof.html', erreur_password=erreur_password)

        mot_de_passe_hash = generate_password_hash(mot_de_passe)

        cursor = db.cursor()
        cursor.execute("SELECT * FROM enseignants WHERE email = %s", (email,))
        utilisateur_exist = cursor.fetchone()

        if utilisateur_exist:
            erreur_message="Utilisateur deja existant"
            return render_template ('inscription_prof.html',erreur_message=erreur_message)

        sql = "INSERT INTO enseignants (nom_complet, email, mot_de_passe) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nom_complet, email, mot_de_passe_hash))
        db.commit()
        cursor.close()

        succes_message="Inscription réussie !"
        return render_template ('inscription_prof.html',succes_message=succes_message)

def connexionprof():
    if request.method == 'POST':
        email = request.form['username']
        mot_de_passe = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT * FROM enseignants WHERE email = %s", (email,))
        enseignant = cursor.fetchone()

        if enseignant and check_password_hash(enseignant[3], mot_de_passe):
            session['username'] = enseignant[1]
            session['id'] = enseignant[0]
            return render_template('accueilp.html', sess_username=session['username'])
        else:
            erreur_message="Identifiants incorrects"
            return render_template('connexion_prof.html',erreur_message=erreur_message,sess_username=session['username'])

def connexionetudiant():
    if request.method == 'POST':
        email = request.form['username']
        mot_de_passe = request.form['password']
        cursor = db.cursor()
        cursor.execute("SELECT * FROM etudiants WHERE email = %s", (email,))
        etudiants = cursor.fetchone()

        if etudiants and check_password_hash(etudiants[3], mot_de_passe):
            session['username']=etudiants[1]
            session['id']=etudiants[0]
            return timeline_eleve()
        else:
            erreur_message="Identifiants incorrects"
            return render_template('connexion_etudiant.html',erreur_message=erreur_message)


def timeline_eleve():

    try:
        sess_id=session['id']
        sess_username=session['username']
        cursor = db.cursor()
        cursor.execute("SELECT * FROM examens WHERE classe = (SELECT classe FROM etudiants WHERE id = %s)", (sess_id,))
        devoirs = cursor.fetchall()
        if devoirs:
            id_prof = devoirs[0][6]  # Vérifiez bien que la colonne 6 est correcte
        cursor.close()
        cursor = db.cursor()
        cursor.execute("SELECT nom_complet FROM enseignants WHERE id=%s", (id_prof,))
        prof = cursor.fetchone()
        prof_nom=prof[0]
        cursor.close()
        return render_template('pageaccueil_etudiant.html', sess_username=sess_username, devoirs=devoirs,prof_nom=prof_nom)
    except Exception as e:
        # En cas d'erreur, fermer le curseur et la connexion, puis afficher un message d'erreur
        cursor.close()
        db.close()
        return f"Une erreur est survenue : {e}"
    
    finally:
        # S'assurer que la connexion à la base de données est fermée après utilisation
        db.close()



def timeline_prof():
    sess_username = session.get('username')
    sess_id = session.get('id')
    cursor = db.cursor()
    print(sess_id)  # This line prints sess_id to the terminal
    requete = """
    SELECT e.nom_complet, e.classe, ex.nom AS examen_nom, c.fichier_pdf, c.date_soumission, c.id
    FROM copies c
    JOIN etudiants e ON c.id_etudiant = e.id
    JOIN examens ex ON c.id_examen = ex.id
    WHERE ex.idprof = %s
    """
    cursor.execute(requete, (sess_id,))
    devoirsoumis = cursor.fetchall()
    print(devoirsoumis)  # This line prints devoirsoumis to the terminal

    db.commit()
    db.close()

    return render_template('copie.html', devoirsoumis=devoirsoumis)

def connexionetu():
    if request.method == 'POST':
        email = request.form['username']
        mot_de_passe = request.form['password']

        cursor = db.cursor()
        cursor.execute("SELECT * FROM etudiants WHERE email = %s", (email,))
        utilisateur = cursor.fetchone()

        if utilisateur and check_password_hash(utilisateur[3], mot_de_passe):
            session['id'] = utilisateur[0]
            session['role'] = utilisateur[4]
            flash("Connexion réussie !", "success")
            return redirect('/pageEtudiant')
        else:
            flash("Email ou mot de passe incorrect.", "danger")
            return redirect('/connexion')

    return render_template('connexion.html')



def nettoyer_nom_fichier(filename):
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    return filename

from flask import request, render_template
import os
import mysql.connector
from werkzeug.utils import secure_filename

import os
from flask import request, render_template
from werkzeug.utils import secure_filename

def ajouter_devoir():
    # Define the directory for saving files
    repertoire = os.path.join('python', 'static', 'images')  # Use os.path.join for cross-platform compatibility
    if not os.path.exists(repertoire):
        print(f"Creating directory: {repertoire}")
        os.makedirs(repertoire)

    # Collect all form data
    nom = request.form.get('nom')
    description = request.form.get('description')
    type_devoir = request.form.get('typedevoir')
    classe = request.form.get('classe')
    fichier = request.files.get('fichier')  # Use request.files for file uploads
    prof = request.form.get('id')
    date = request.form.get('date')

    # Validate file upload
    if not fichier or fichier.filename == '':
        errorfichier = "Fichier non téléchargé"
        return render_template("Ajoutdevoir.html", errorfichier=errorfichier)

    # Validate file extension
    allowed_extensions = {'pdf', 'docx', 'doc'}
    file_extension = fichier.filename.rsplit('.', 1)[1].lower() if '.' in fichier.filename else ''
    if file_extension not in allowed_extensions:
        errorfichier = "Format de fichier non autorisé"
        return render_template("Ajoutdevoir.html", errorfichier=errorfichier)

    # Clean the filename and ensure safe filename
    fichier_filename = secure_filename(fichier.filename)
    print(f"Cleaned filename: {fichier_filename}")

    # Save the file to the directory
    file_path = os.path.join(repertoire, fichier_filename)
    print(f"Saving file to: {file_path}")
    fichier.save(file_path)

    # Verify if the file was saved
    if not os.path.exists(file_path):
        errorfichier = "Échec de l'enregistrement du fichier."
        return render_template("Ajoutdevoir.html", errorfichier=errorfichier)

    # Get the relative path for the database
    chemin1 = os.path.join('static', 'images', fichier_filename)
    print(f"Relative path for database: {chemin1}")

    curseur = db.cursor()
    try:
        

        # Insert data into the database
        requete = '''
        INSERT INTO examens (nom, description, type, classe, chemin, idprof, datedesoumission)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        '''
        values = (nom, description, type_devoir, classe, chemin1, prof, date)

        curseur.execute(requete, values)
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        return render_template("Ajoutdevoir.html", errorfichier=f"Erreur MySQL : {err}")
    finally:
        # Close the resources
        curseur.close()
    return render_template("Ajoutdevoir.html", success_message="Devoir ajouté avec succès.",sess_id=session['id'])

def infodev():
    sess_username=session.get('username')
    id=request.form['id']
    curseur=db.cursor()
    curseur.execute("Select * from examens where id=%s",(id,))
    infodevoirs=curseur.fetchall()
    db.commit()
    curseur.close()
    db.close()
    return render_template('info_dev.html',sess_username=sess_username,infodevoirs=infodevoirs)

def infocopiecode():
    sess_username=session.get('username')
    idcopie=request.form['id']
    sess_id = session.get('id')
    curseur=db.cursor()
    requete = """
    SELECT e.nom_complet, e.classe, ex.nom AS examen_nom, c.fichier_pdf, c.date_soumission, c.id
    FROM copies c
    JOIN etudiants e ON c.id_etudiant = e.id
    JOIN examens ex ON c.id_examen = ex.id
    WHERE ex.idprof = %s and c.id=%s
    """
    curseur.execute(requete, (sess_id,idcopie))
    infocopie=curseur.fetchall()
    db.commit()
    requete="""select note from corrections where id_copie=%s"""
    curseur.execute(requete,(idcopie,))
    note=curseur.fetchall()
    if note:
        note=note[0][0]
    db.commit()
    curseur.close()
    db.close()
    return render_template('info_copie.html',sess_username=sess_username,infocopie=infocopie,note=note)

def soumettrefichier():
        # Define the directory for saving files
    repertoire = os.path.join('python', 'static', 'images','copies')  # Use os.path.join for cross-platform compatibility
    if not os.path.exists(repertoire):
        print(f"Creating directory: {repertoire}")
        os.makedirs(repertoire)

    # Collect all form data
    ideleve= request.form.get('ideleve')
    idev= request.form.get('idev')
    fichier = request.files.get('copie')  # Use request.files for file uploads)

    # Validate file upload
    if not fichier or fichier.filename == '':
        errorfichier = "Fichier non téléchargé"
        return render_template("info_dev.html", errorfichier=errorfichier)

    # Validate file extension
    allowed_extensions = {'pdf', 'docx', 'doc'}
    file_extension = fichier.filename.rsplit('.', 1)[1].lower() if '.' in fichier.filename else ''
    if file_extension not in allowed_extensions:
        errorfichier = "Format de fichier non autorisé"
        return render_template("info_dev.html", errorfichier=errorfichier)

    # Clean the filename and ensure safe filename
    fichier_filename = secure_filename(fichier.filename)
    print(f"Cleaned filename: {fichier_filename}")
    print(f"Cleaned filename: {ideleve}")
    print(f"Cleaned filename: {idev}")


    # Save the file to the directory
    file_path = os.path.join(repertoire, fichier_filename)
    print(f"Saving file to: {file_path}")
    fichier.save(file_path)

    # Verify if the file was saved
    if not os.path.exists(file_path):
        errorfichier = "Échec de l'enregistrement du fichier."
        return render_template("info_dev.html", errorfichier=errorfichier)

    # Get the relative path for the database
    chemin1 = os.path.join('static', 'images','copies',fichier_filename)
    print(f"Relative path for database: {chemin1}")
    curseur = db.cursor()

    # Database connection (using the already defined `db`)
    try:
        requete = '''
        INSERT INTO copies (id_examen,id_etudiant,fichier_pdf)
        VALUES (%s, %s, %s)
        '''
        values = (idev, ideleve, chemin1)
        curseur.execute(requete, values)
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        return render_template("info_dev.html", errorfichier=f"Erreur MySQL : {err}")
    finally:
        curseur.close()
    return render_template("info_dev.html", success_message="Devoir soumis avec succès.",sess_id=session['id'])

def notercopie():
    idcopie=request.form['id']
    note=request.form['note']
    commentaire=request.form['commentaire']
    curseur=db.cursor()
    requete = '''
    insert into corrections (id_copie,note,commentaire) values (%s,%s,%s)
    '''
    values = (idcopie,note, commentaire)
    curseur.execute(requete, values)
    db.commit()
    curseur.close()
    db.close()
    return render_template("info_copie.html", success_message="Note ajoutée avec succès.",note=note)

def updatenote():
    idcopie=request.form['id']
    newnote=request.form['newnote']
    sess_id = session.get('id')
    sess_username = session.get('username')
    curseur=db.cursor()
    requete = '''
    update corrections set note=%s where id_copie=%s
    '''
    values = (newnote,idcopie)
    curseur.execute(requete, values)
    db.commit()
    curseur.close()
    db.close()
    return render_template("info_copie.html")

def afficher_note():
    sess_id = session.get('id')  # Récupération de l'ID du professeur
    if not sess_id:
        return "Erreur : utilisateur non authentifié"

    curseur = db.cursor()

    requete = """
    SELECT e.nom_complet, e.classe, ex.nom AS examen_nom, c.note
    FROM copies cop
    JOIN etudiants e ON cop.id_etudiant = e.id
    JOIN corrections c ON cop.id = c.id_copie
    JOIN examens ex ON cop.id_examen = ex.id
    WHERE ex.idprof = %s
    """
    
    curseur.execute(requete, (sess_id,))
    notes = curseur.fetchall()
    
    curseur.close()
    return render_template('notep.html', notes=notes)
