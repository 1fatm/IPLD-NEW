from flask import Flask, render_template, request, redirect, session, flash, jsonify,send_file
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector,os,re
import io
import base64
from mysql.connector import Error
import subprocess
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import seaborn as sns

app = Flask(__name__)
app.secret_key = 'your_love'
import mysql.connector

def connect():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="gestion_examens"
            
            )
        return connection
    except mysql.connector.Error as err:
        print(f"Erreur de connexion : {err}")
        return None

db=connect()
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
        db=connect()
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
        db=connect()
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
            return countcopiesnonnotees()
        else:
            erreur_message = "Identifiants incorrects"
            return render_template('connexion_prof.html', erreur_message=erreur_message)

def connexionetudiant():
    if request.method == 'POST':
        email = request.form['username']
        mot_de_passe = request.form['password']
        db=connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM etudiants WHERE email = %s", (email,))
        etudiants = cursor.fetchone()

        if etudiants and check_password_hash(etudiants[3], mot_de_passe):
            session['username']=etudiants[1]
            session['id']=etudiants[0]
            return statistiques_etudiant()
        else:
            erreur_message="Identifiants incorrects"
            return render_template('connexion_etudiant.html',erreur_message=erreur_message)

def statistiques_etudiant():
    sess_id = session.get('id') 
    # ID de l'étudiant connecté
    db=connect()

    curseur = db.cursor()

    # Nombre d'examens soumis par l'étudiant
    requete = "SELECT COUNT(*) FROM copies WHERE id_etudiant = %s"
    curseur.execute(requete, (sess_id,))
    soumis = curseur.fetchone()[0]

    # Nombre d'examens non soumis par l'étudiant
    requete = """
        SELECT COUNT(*) 
        FROM examens 
        WHERE classe = (SELECT classe FROM etudiants WHERE id = %s)
        AND id NOT IN (SELECT id_examen FROM copies WHERE id_etudiant = %s)
    """
    curseur.execute(requete, (sess_id, sess_id))
    non_soumis = curseur.fetchone()[0]

    # Nombre d'examens en retard (non soumis et date dépassée)
    requete = """
        SELECT COUNT(*) 
        FROM examens 
        WHERE classe = (SELECT classe FROM etudiants WHERE id = %s)
        AND id NOT IN (SELECT id_examen FROM copies WHERE id_etudiant = %s)
        AND datedesoumission < NOW()
    """
    curseur.execute(requete, (sess_id, sess_id))
    enretard = curseur.fetchone()[0]

    curseur.close()

    return render_template('pageaccueil_etudiant.html',soumis=soumis,non_soumis=non_soumis,enretard=enretard,sess_username=session['username'])



def timeline_eleve():
    try:
        sess_id=session['id']
        sess_username=session['username']
        db=connect()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM examens WHERE classe = (SELECT classe FROM etudiants WHERE id = %s)", (sess_id,))
        devoirs = cursor.fetchall()
        if devoirs:
            id_prof = devoirs[0][6]  
        cursor.close()
        cursor = db.cursor()
        cursor.execute("SELECT nom_complet FROM enseignants WHERE id=%s", (id_prof,))
        prof = cursor.fetchone()
        prof_nom=prof[0]
        cursor.close()
        return render_template('pageaccueil_etudiant.html', sess_username=sess_username, devoirs=devoirs,prof_nom=prof_nom)
    except Exception as e:
        cursor.close()
        db.close()
        return f"Une erreur est survenue : {e}"
    finally:
        db.close()

def timeline_prof():
    sess_username = session.get('username')
    id=request.form['id']
    sess_id = session.get('id')
    db=connect()
    cursor = db.cursor()
    print(sess_id)  
    requete = """
    SELECT e.nom_complet, e.classe, ex.nom AS examen_nom, c.fichier_pdf, c.date_soumission, c.id,ex.datedesoumission
    FROM copies c
    JOIN etudiants e ON c.id_etudiant = e.id
    JOIN examens ex ON c.id_examen = ex.id
    WHERE ex.idprof = %s and ex.id=%s  
    """
    cursor.execute(requete, (sess_id,id))
    devoirsoumis = cursor.fetchall()
    print(devoirsoumis)  

    db.commit()
    db.close()

    return render_template('copie.html', devoirsoumis=devoirsoumis)

def connexionetu():
    if request.method == 'POST':
        email = request.form['username']
        mot_de_passe = request.form['password']
        db=connect()
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
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
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
    repertoire = os.path.join('python', 'static', 'images','examens')  
    if not os.path.exists(repertoire):
        print(f"Creating directory: {repertoire}")
        os.makedirs(repertoire)

    nom = request.form.get('nom')
    description = request.form.get('description')
    type_devoir = request.form.get('typedevoir')
    classe = request.form.get('classe')
    fichier = request.files.get('fichier') 
    fichier_correction = request.files.get('correction')
    prof = request.form.get('id')
    date = request.form.get('date')

    if not fichier or fichier.filename == '':
        errorfichier = "Fichier non téléchargé"
        return render_template("Ajoutdevoir.html", errorfichier=errorfichier)

    allowed_extensions = {'pdf', 'docx', 'doc'}
    file_extension = fichier.filename.rsplit('.', 1)[1].lower() if '.' in fichier.filename else ''
    if file_extension not in allowed_extensions:
        errorfichier = "Format de fichier non autorisé"
        return render_template("Ajoutdevoir.html", errorfichier=errorfichier)

    fichier_filename = secure_filename(fichier.filename)
    print(f"Cleaned filename: {fichier_filename}")

    file_path = os.path.join(repertoire, fichier_filename)
    print(f"Saving file to: {file_path}")
    fichier.save(file_path)

    if not os.path.exists(file_path):
        errorfichier = "Échec de l'enregistrement du fichier."
        return render_template("Ajoutdevoir.html", errorfichier=errorfichier)

    chemin1 = os.path.join('static', 'images', fichier_filename)
    print(f"Relative path for database: {chemin1}")

    repertoire_correction = os.path.join('python', 'static', 'images','corrections')  # Use os.path.join for cross-platform compatibility
    if not os.path.exists(repertoire_correction):
        print(f"Creating directory correction: {repertoire_correction}")
        os.makedirs(repertoire_correction)
    if not fichier_correction or fichier_correction.filename == '':
        errorfichier_correction = "Correction non téléchargé"
        return render_template("Ajoutdevoir.html", errorfichier_correction=errorfichier_correction)

    allowed_extensions = {'pdf', 'docx', 'doc'}
    file_extension = fichier_correction.filename.rsplit('.', 1)[1].lower() if '.' in fichier_correction.filename else ''
    if file_extension not in allowed_extensions:
        errorfichier_correction = "Format de fichier correction non autorisé"
        return render_template("Ajoutdevoir.html", errorfichier_correction=errorfichier_correction)

    fichier_correction_filename = secure_filename(fichier_correction.filename)
    print(f"Cleaned filename: {fichier_correction_filename}")

    file_path = os.path.join(repertoire_correction, fichier_correction_filename)
    print(f"Saving file to: {file_path}")
    fichier_correction.save(file_path)

    if not os.path.exists(file_path):
        errorfichier_correction = "Échec de l'enregistrement du fichier_correction."
        return render_template("Ajoutdevoir.html", errorfichier_correction=errorfichier_correction)

    chemin2 = os.path.join('static', 'images', fichier_correction_filename)
    print(f"Relative path for database: {chemin2}")
    db=connect()
    curseur = db.cursor()
    try:
        

        requete = '''
        INSERT INTO examens (nom, description, type, classe, chemin,chemin_correction, idprof, datedesoumission)
        VALUES (%s, %s, %s, %s, %s, %s, %s,%s)
        '''
        values = (nom, description, type_devoir, classe, chemin1,chemin2, prof, date)

        curseur.execute(requete, values)
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        return render_template("Ajoutdevoir.html", errorfichier=f"Erreur MySQL : {err}",)
    finally:
        curseur.close()
    return render_template("Ajoutdevoir.html", success_message="Devoir ajouté avec succès.",sess_id=session['id'])

def soumettrefichier():
    sess_id = session.get('id')
    repertoire = os.path.join('python','static', 'images', 'copies')
    if not os.path.exists(repertoire):
        os.makedirs(repertoire)
    
    ideleve = request.form.get('ideleve')
    idev = request.form.get('idev')
    fichier = request.files.get('copie')
    
    if not fichier or fichier.filename == '':
        return render_template("info_dev.html", errorfichier="Fichier non téléchargé")
    
    allowed_extensions = {'pdf', 'docx', 'doc'}
    file_extension = fichier.filename.rsplit('.', 1)[1].lower() if '.' in fichier.filename else ''
    if file_extension not in allowed_extensions:
        return render_template("info_dev.html", errorfichier="Format de fichier non autorisé")
    
    fichier_filename = secure_filename(fichier.filename)
    file_path = os.path.join(repertoire, fichier_filename)
    fichier.save(file_path)
    
    if not os.path.exists(file_path):
        return render_template("info_dev.html", errorfichier="Échec de l'enregistrement du fichier.")
    
    chemin1 = os.path.join('python','static', 'images', 'copies', fichier_filename)
    db=connect()
    curseur = db.cursor()
    
    try:
        requete = '''INSERT INTO copies (id_examen, id_etudiant, fichier_pdf) VALUES (%s, %s, %s)'''
        values = (idev, ideleve, chemin1)
        curseur.execute(requete, values)
        db.commit()
        id_copie = curseur.lastrowid
    except mysql.connector.Error as err:
        db.rollback()
        return render_template("info_dev.html", errorfichier=f"Erreur MySQL : {err}")
    finally:
        curseur.close()
    curseur = db.cursor()
    noteria(ideleve, idev, chemin1, id_copie)
    curseur.execute("Select * from examens where id=%s",(idev,))
    infodevoirs=curseur.fetchall()
    db.commit()
    curseur=db.cursor()
    curseur.execute("Select * from copies where id_examen=%s and id_etudiant=%s",(idev,sess_id))
    verificationsoumission=curseur.fetchall()
    if verificationsoumission:
        soumis=True
    else:
        soumis=False
    db.commit()
    return render_template("info_dev.html", success_message="Devoir soumis avec succès.", sess_id=session['id'],infodevoirs=infodevoirs,soumis=soumis)                              

def noteria(ideleve, iddevoir, chemincopie, id_copie):
    db=connect()
    cursor = db.cursor()
    
    cursor.execute("SELECT chemin, chemin_correction FROM examens WHERE id=%s", (iddevoir,))
    result = cursor.fetchone()
    cursor.close()
    
    if not result:
        return "Examen introuvable"
    
    cheminexamen, chemincorrection = result
    
    try:
        with open(cheminexamen, "r", encoding="utf-8", errors="replace") as f:
            contenu_examen = f.read()
        with open(chemincorrection, "r", encoding="utf-8", errors="replace") as f:
            contenu_correction = f.read()
        with open(chemincopie, "r", encoding="utf-8", errors="replace") as f:
            contenu_copie = f.read()
    except FileNotFoundError as e:
        return f"Erreur : fichier introuvable - {e}"
    
    def clean_string(input_string):
        return input_string.replace("\0", "")
    
    contenu_examen = clean_string(contenu_examen)
    contenu_correction = clean_string(contenu_correction)
    contenu_copie = clean_string(contenu_copie)
    
    prompt = f"""
    Tu dois me donner une note en corrigeant la feuille de l'élève à partir du corrigé de l'examen. Tu compares la correction avec ce que l'étudiant a soumis pour chaque réponse trouvé tu lui donne une note. Enfin tu me donnes une note sur 20 pour cette copie.
    Donne-moi juste une note sur 20, rien d'autre.
    
    Correction examen :
    {contenu_correction}
    
    Feuille de l'élève :
    {contenu_copie}
    """
    
    reponse = ask_ollama(prompt)
    print(reponse)
    
    try:
        note = float(reponse.strip())
    except ValueError:
        note = None
    
    if note is not None:
        cursor = db.cursor()
        try:
            requete = '''INSERT INTO corrections (id_copie, note, commentaire, correction_automatique) VALUES (%s, %s, %s, %s)'''
            values = (id_copie, note, "Correction automatique", True)
            cursor.execute(requete, values)
            db.commit()
        except mysql.connector.Error as err:
            db.rollback()
            print(f"Erreur MySQL : {err}")
        finally:
            cursor.close()
    else:
        print("Erreur : L'IA n'a pas retourné une note valide.")
    
    return reponse

def infodev():
    sess_username=session.get('username')
    id=request.form['id']
    sess_id = session.get('id')
    db=connect()
    curseur=db.cursor()
    curseur.execute("Select * from examens where id=%s",(id,))
    infodevoirs=curseur.fetchall()
    db.commit()
    curseur=db.cursor()
    verificationsoumission=curseur.execute("Select * from copies where id_examen=%s and id_etudiant=%s",(id,sess_id))
    verificationsoumission=curseur.fetchall()
    if verificationsoumission:
        soumis=True
    else:
        soumis=False
    db.commit()
    curseur.close()
    db.close()
    return render_template('info_dev.html',sess_username=sess_username,infodevoirs=infodevoirs,soumis=soumis)

def infocopiecode():
    sess_username=session.get('username')
    idcopie=request.form['id']
    sess_id = session.get('id')
    db=connect()
    curseur=db.cursor()
    requete = """
    SELECT e.nom_complet, e.classe, ex.nom AS examen_nom, c.fichier_pdf, c.date_soumission, c.id,ex.datedesoumission
    FROM copies c
    JOIN etudiants e ON c.id_etudiant = e.id
    JOIN examens ex ON c.id_examen = ex.id
    WHERE ex.idprof = %s and c.id=%s
    """
    curseur.execute(requete, (sess_id,idcopie))
    infocopies=curseur.fetchall()
    db.commit()
    requete="""select note from corrections where id_copie=%s"""
    curseur.execute(requete,(idcopie,))
    note=curseur.fetchall()
    if note:
        note=note[0][0]
    db.commit()
    curseur.close()
    db.close()
    return render_template('info_copie.html',sess_username=sess_username,infocopies=infocopies,note=note)

def notercopie():
    sess_id = session.get('id')
    idcopie=request.form['id']
    note=request.form['note']
    commentaire=request.form['commentaire']
    db=connect()
    curseur=db.cursor()
    requete='''select note from corrections where id_copie=%s'''
    curseur.execute(requete,(idcopie,))
    verifnote=curseur.fetchall()

    if verifnote and verifnote[0]:
        verifnote=verifnote[0][0]
        requete= requete = """
        SELECT e.nom_complet, e.classe, ex.nom AS examen_nom, c.fichier_pdf, c.date_soumission, c.id,ex.datedesoumission
        FROM copies c
        JOIN etudiants e ON c.id_etudiant = e.id
        JOIN examens ex ON c.id_examen = ex.id
        WHERE ex.idprof = %s and c.id=%s
        """
        curseur.execute(requete, (sess_id,idcopie))
        infocopies=curseur.fetchall()
        db.commit()
        return render_template("info_copie.html",infocopies=infocopies,note=verifnote)
    else:
        requete = '''
        insert into corrections (id_copie,note,commentaire) values (%s,%s,%s)
        '''
        values = (idcopie,note, commentaire)
        curseur.execute(requete, values)
        db.commit()
        curseur.execute("Select * from examens where id=%s",(idcopie,))
        infocopies=curseur.fetchall()
        db.commit()
        return render_template("info_copie.html",infocopies=infocopies,note=note)

def updatenote():
    idcopie=request.form['id']
    newnote=request.form['newnote']
    sess_id = session.get('id')
    db=connect()
    curseur=db.cursor()
    requete = '''
    update corrections set note=%s where id_copie=%s
    '''
    values = (newnote,idcopie)
    curseur.execute(requete, values)
    requete= requete = """
        SELECT e.nom_complet, e.classe, ex.nom AS examen_nom, c.fichier_pdf, c.date_soumission, c.id,ex.datedesoumission
        FROM copies c
        JOIN etudiants e ON c.id_etudiant = e.id
        JOIN examens ex ON c.id_examen = ex.id
        WHERE ex.idprof = %s and c.id=%s
        """
    curseur.execute(requete, (sess_id,idcopie))
    infocopies=curseur.fetchall()

    db.commit()
    return render_template("info_copie.html",infocopies=infocopies,note=newnote)

def afficher_note():
    sess_id = session.get('id')  # Récupération de l'ID du professeur
    if not sess_id:
        return "Erreur : utilisateur non authentifié"
    db=connect()
    curseur = db.cursor()

    requete="""
    Select examens.nom,examens.classe,examens.description,examens.type,examens.id from examens where idprof=%s
    """
    curseur.execute(requete,(sess_id,))
    examens=curseur.fetchall()
    db.commit()
    curseur.close()
    return render_template('notep.html',examens=examens)

def voirlesnotes(): 
    sess_id = session.get('id')  # ID du professeur connecté
    id=request.form['id']
    db=connect()
    curseur = db.cursor()
    requete = """
    SELECT e.nom_complet, e.classe, ex.nom AS examen_nom, c.note,c.commentaire,ex.id
    FROM copies cop
    JOIN etudiants e ON cop.id_etudiant = e.id
    JOIN corrections c ON cop.id = c.id_copie
    JOIN examens ex ON cop.id_examen = ex.id    
    WHERE ex.idprof = %s and ex.id=%s
    """
    curseur.execute(requete, (sess_id,id))
    notes = curseur.fetchall()
    db.commit()
    curseur.close()
    return render_template('voirnote.html',notes=notes)

def afficher_examens():
    sess_id = session.get('id')  # ID du professeur connecté
    db=connect()
    cursor=db.cursor()
    cursor.execute("SELECT nom,description,type,classe,chemin FROM examens where idprof=%s",(sess_id,))
    examens=cursor.fetchall()
    db.commit()
    verif=True
    if not examens:
        verif=False
    cursor.close()
    return render_template('examen.html',examens=examens,verif=verif)

def generer_statistiques():
    sess_id = session.get('id')  # ID du professeur connecté
    if not sess_id:
        return "Erreur : utilisateur non authentifié"
    db=connect()
    curseur = db.cursor(dictionary=True)

    # Récupérer les statistiques des examens donnés par ce professeur
    requete = """
    SELECT e.classe, c.note
    FROM copies cop
    JOIN corrections c ON cop.id = c.id_copie
    JOIN examens ex ON cop.id_examen = ex.id
    JOIN etudiants e ON cop.id_etudiant = e.id
    WHERE ex.idprof = %s
    """
    curseur.execute(requete, (sess_id,))
    resultats = curseur.fetchall()
    curseur.close()

    if not resultats:
        return "Aucune donnée disponible."

    notes_par_classe = {}
    for row in resultats:
        classe = row["classe"]
        note = row["note"]

        if classe not in notes_par_classe:
            notes_par_classe[classe] = []
        notes_par_classe[classe].append(note)

    statistiques = []
    histogrammes = {}

    for classe, notes in notes_par_classe.items():
        notes_array = np.array(notes)
        moyenne = round(np.mean(notes_array), 2)
        taux_reussite = round((np.sum(notes_array >= 10) / len(notes_array)) * 100, 2)  # % d'élèves ayant >= 10

        plt.figure(figsize=(6, 4))
        plt.hist(notes_array, bins=5, color='skyblue', edgecolor='black', alpha=0.7)
        plt.xlabel('Notes')
        plt.ylabel('Nombre d\'étudiants')
        plt.title(f'Distribution des notes - {classe}')
        
        
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        img_b64 = base64.b64encode(img.getvalue()).decode('utf8')
        histogrammes[classe] = img_b64
        plt.close()

        statistiques.append({
            "classe": classe,
            "moyenne": moyenne,
            "taux_reussite": taux_reussite
        })

    print(histogrammes)  

    return render_template("statistique.html", statistiques=statistiques, histogrammes=histogrammes)

def deconnection():
    session.clear()
    return redirect('/')

def trier_classe():
    sess_id = session.get('id')  # ID du professeur connecté
    db=connect()
    curseur = db.cursor()
    classe = request.form.get('classe')
    verif=True
    print(classe)
    curseur.execute("SELECT nom,description,type,classe,chemin FROM examens where idprof=%s and classe=%s",(sess_id,classe))
    devoirsoumistrié = curseur.fetchall()
    print(devoirsoumistrié)
    if not devoirsoumistrié:
        verif=False
    curseur.close()
    return render_template('examen.html',examens=devoirsoumistrié,verif=verif)


def countcopiesnonnotees():
    sess_id = session.get('id')  # ID du professeur connecté
    sess_username=session.get('username')
    db=connect()
    curseur = db.cursor()
    requete="Select count(*) from copies join examens on copies.id_examen=examens.id where examens.idprof=%s and copies.id not in (select id_copie from corrections)"
    curseur.execute(requete,(sess_id,))
    copiesnonnotees=curseur.fetchone()
    requete2="Select count(*) from examens where idprof=%s and datedesoumission>now()"
    curseur.execute(requete2,(sess_id,))    
    examenencours=curseur.fetchone()
    db.commit()
    curseur.close()
    db.close()
    return render_template('accueilp.html',copiesnonnotees=copiesnonnotees[0],examenencours=examenencours[0],sess_username=sess_username)


def trier_date():
    sess_id = session.get('id')  # ID du professeur connecté
    db=connect()
    curseur = db.cursor()
    date = request.form.get('date')
    verif=True
    print(date)
    if (date=="passe"):
        curseur.execute("SELECT nom,description,type,classe,chemin FROM examens where idprof=%s and datedesoumission<now()",(sess_id,))
        devoirsoumistriédate = curseur.fetchall()
    else:
        curseur.execute("SELECT nom,description,type,classe,chemin FROM examens where idprof=%s and datedesoumission>now()",(sess_id,))
        devoirsoumistriédate = curseur.fetchall()
    print(devoirsoumistriédate)
    if not devoirsoumistriédate:
        verif=False
    curseur.close()
    return render_template('examen.html',examens=devoirsoumistriédate,verif=verif)



def get_statistiques(id_prof):
    db=connect()
    cursor = db.cursor()

    # Récupérer les examens créés par le professeur
    cursor.execute("""
        SELECT e.id, e.nom, e.classe 
        FROM examens e 
        WHERE e.idprof = %s
    """, (id_prof,))
    examens = cursor.fetchall()

    statistiques = []

    for examen in examens:
        examen_id, examen_nom, examen_classe = examen

        # Compter le nombre de notes
        requete = """
            SELECT COUNT(*)
            FROM copies c
            JOIN corrections co ON c.id = co.id_copie
            WHERE c.id_examen = %s
        """
        cursor.execute(requete, (examen_id,))
        nombre_notes = cursor.fetchone()[0]

        # S'il n'y a pas de notes, on passe à l'examen suivant
        if nombre_notes == 0:
            continue

        # Récupérer toutes les notes
        requete = """
            SELECT co.note
            FROM copies c
            JOIN corrections co ON c.id = co.id_copie
            WHERE c.id_examen = %s
        """
        cursor.execute(requete, (examen_id,))
        notes = [note[0] for note in cursor.fetchall()]

        # Calculer la moyenne
        moyenne = sum(notes) / nombre_notes

        # Générer l'histogramme
        plt.figure()
        plt.hist(notes, bins=10, edgecolor='black')
        plt.title(f"Distribution des notes - {examen_nom}")
        plt.xlabel('Notes')
        plt.ylabel('Nombre d\'étudiants')

        # Convertir le graphique en image encodée
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()  # Éviter la fuite de mémoire

        # Ajouter les statistiques de cet examen
        statistiques.append({
            'classe': examen_classe,
            'nom': examen_nom,
            'moyenne': round(moyenne, 2),
            'plot_url': plot_url
        })

    # Fermer la connexion proprement
    cursor.close()
    db.close()

    return statistiques

def statistiquesp():
    if 'id' not in session:
        return redirect('/connexion_prof')

    id_prof = session['id']
    statistiques = get_statistiques(id_prof)

    return render_template('statistique.html', statistiques=statistiques)
def get_statistiques(id_prof):
    db = connect()
    cursor = db.cursor()

    # Récupérer les examens créés par le professeur
    cursor.execute("""
        SELECT e.id, e.nom, e.classe 
        FROM examens e 
        WHERE e.idprof = %s
    """, (id_prof,))
    examens = cursor.fetchall()

    statistiques = []

    for examen in examens:
        examen_id, examen_nom, examen_classe = examen

        # Récupérer toutes les notes
        requete = """
            SELECT co.note
            FROM copies c
            JOIN corrections co ON c.id = co.id_copie
            WHERE c.id_examen = %s
        """
        cursor.execute(requete, (examen_id,))
        notes = [note[0] for note in cursor.fetchall()]

        if len(notes) == 0:
            continue

        moyenne = sum(notes) / len(notes)

        # 📊 1. Histogramme avec Seaborn
        plt.figure(figsize=(14, 10))
        sns.histplot(notes, bins=10, kde=True, color='skyblue')
        plt.title(f"Histogramme des notes - {examen_nom}", fontsize=16)
        plt.xlabel('Notes', fontsize=12)
        plt.ylabel('Nombre d\'étudiants', fontsize=12)
        img_hist = io.BytesIO()
        plt.savefig(img_hist, format='png')
        img_hist.seek(0)
        plot_url_hist = base64.b64encode(img_hist.getvalue()).decode()
        plt.close()

        # 🥧 2. Diagramme circulaire avec Seaborn
        notes_range = ["0-5", "6-10", "11-15", "16-20"]
        counts = [sum(0 <= n <= 5 for n in notes),
                  sum(6 <= n <= 10 for n in notes),
                  sum(11 <= n <= 15 for n in notes),
                  sum(16 <= n <= 20 for n in notes)]

        plt.figure(figsize=(14, 10))
        sns.set_palette("pastel")
        plt.pie(counts, labels=notes_range, autopct='%1.1f%%', startangle=140)
        plt.title(f"Répartition des notes - {examen_nom}", fontsize=16)
        img_pie = io.BytesIO()
        plt.savefig(img_pie, format='png')
        img_pie.seek(0)
        plot_url_pie = base64.b64encode(img_pie.getvalue()).decode()
        plt.close()

        # 📌 3. Diagramme en barres avec Seaborn
        plt.figure(figsize=(14, 10))
        sns.barplot(x=notes_range, y=counts, palette='muted')
        plt.title(f"Notes par tranche - {examen_nom}", fontsize=16)
        plt.xlabel('Tranches de notes', fontsize=12)
        plt.ylabel('Nombre d\'étudiants', fontsize=12)
        img_bar = io.BytesIO()
        plt.savefig(img_bar, format='png')
        img_bar.seek(0)
        plot_url_bar = base64.b64encode(img_bar.getvalue()).decode()
        plt.close()

        # Ajouter toutes les statistiques de cet examen
        statistiques.append({
            'classe': examen_classe,
            'nom': examen_nom,
            'moyenne': round(moyenne, 2),
            'plot_url_hist': plot_url_hist,
            'plot_url_pie': plot_url_pie,
            'plot_url_bar': plot_url_bar
        })

    cursor.close()
    db.close()

    return statistiques
def afficher_devoirs():
    # Vérifier si l'utilisateur est connecté
    if 'id' not in session:
        flash("Veuillez vous connecter.", "warning")
        return redirect('/')

    # Connexion à la base de données
    db = connect()
    cursor = db.cursor()

    try:
        # Récupérer la classe de l'étudiant
        user_id = session['id']
        cursor.execute("SELECT classe FROM etudiants WHERE id = %s", (user_id,))
        classe_result = cursor.fetchone()

        if not classe_result:
            flash("Classe non trouvée pour cet utilisateur.", "danger")
            return redirect('/accueiletudiant')

        classe = classe_result[0]

        # Récupérer les devoirs de la classe
        requete = """
            SELECT examens.nom, examens.description, examens.type, examens.classe, examens.chemin, examens.datedesoumission, enseignants.nom_complet, examens.id
            FROM examens
            JOIN enseignants ON examens.idprof = enseignants.id
            WHERE examens.classe = %s
        """
        cursor.execute(requete, (classe,))
        devoirs = cursor.fetchall()

        # Vérifier si des devoirs ont été trouvés
        if devoirs:
            verifdevoir = True
            return render_template('devoir.html', devoirs=devoirs, verifdevoir=verifdevoir)
        else:
            verifdevoir = False
            return render_template('devoir.html', verifdevoir=verifdevoir)

    except mysql.connector.Error as err:
        flash(f"Erreur lors de la récupération des devoirs : {err}", "danger")
        return redirect('/accueiletudiant')

    finally:
       
        cursor.close()
        db.close()
def afficher_notifications():
    if 'id' not in session:
        return redirect('/connexion_etudiant')

    id_etudiant = session['id']
    db=connect()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT classe FROM etudiants WHERE id = %s", (id_etudiant,))
    etudiant = cursor.fetchone()
    
    if not etudiant:
        return "Étudiant non trouvé", 404
    
    classe_etudiant = etudiant['classe']

    cursor.execute("""
        SELECT e.id, e.nom, e.datedesoumission, c.date_soumission, ens.nom_complet AS prof,
            CASE 
            WHEN c.id IS NOT NULL THEN 'Soumis'
                ELSE 'Non soumis'
            END AS statut
        FROM examens e
        LEFT JOIN copies c ON e.id = c.id_examen AND c.id_etudiant = %s
        JOIN enseignants ens ON e.idprof = ens.id
        WHERE e.classe = %s
    """, (id_etudiant, classe_etudiant))

    examens = cursor.fetchall()
    return render_template('notification.html', examens=examens)

def afficher_notes():
    if 'id' not in session:
        return redirect('/connexion_etudiant')

    id_etudiant = session['id']
    db=connect()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT e.nom AS nom_examen, c.date_soumission, co.note, ex.type
        FROM copies c
        JOIN examens e ON c.id_examen = e.id
        LEFT JOIN corrections co ON c.id = co.id_copie
        JOIN examens ex ON c.id_examen = ex.id
        WHERE c.id_etudiant = %s
    """, (id_etudiant,))
    
    notes = cursor.fetchall()
    
    return render_template('mesnotes.html', notes=notes)

def ask_ollama(question):
    prompt = f"""
Tu es un assistant pédagogique spécialisé dans les examens et les études. Tu es intégré à un site nommé Academix où l'élève peut :
- Soumettre des copies d'examens
- Voir ses notes
- Recevoir des notifications sur les devoirs soumis ou non soumis.

**Règles de réponse :**
- Réponds uniquement aux questions liées aux examens, corrections, notes ou sujets d'étude.
- Si la question concerne un devoir spécifique, dis que tu ne peux pas fournir les réponses des examens.
- Si la question est inappropriée, refuse d’y répondre.
- Si la question n’a rien à voir avec le site, informe l’utilisateur de ton rôle limité.

**Question de l'élève** : {question}
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "gemma3:1b", prompt],
            capture_output=True,
            text=True,
            timeout=10  # Empêche un blocage si Ollama met trop de temps
        )

        if result.returncode != 0:
            return "Je rencontre un problème technique. Veuillez réessayer plus tard."

        return result.stdout.strip()

    except Exception as e:
        print(f"Erreur lors de l'appel à Ollama : {e}")
        return "Une erreur est survenue. Merci de réessayer."

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Aucune question fournie"}), 400

    question = data['question'].strip()
    if not question:
        return jsonify({"error": "La question est vide"}), 400

    response = ask_ollama(question)

    # Retourne la réponse en forçant l'encodage UTF-8
    #return jsonify({"response": response}), 200  
    return jsonify({"response": response}), 200, {'Content-Type': 'application/json; charset=utf-8'}

def generernote():
    sess_id = session.get('id')
    id=request.form['idexam']
    db=connect()
    cursor=db.cursor()
    requete ="""
    SELECT e.nom_complet, e.classe, ex.nom AS examen_nom, c.note,c.commentaire,ex.id
    FROM copies cop
    JOIN etudiants e ON cop.id_etudiant = e.id
    JOIN corrections c ON cop.id = c.id_copie
    JOIN examens ex ON cop.id_examen = ex.id    
    WHERE ex.idprof = %s and ex.id=%s
    """
    cursor.execute(requete, (sess_id,id))
    notes = cursor.fetchall()
    columns=[desc[0] for desc in cursor.description]
    db.commit()
    cursor.close()
    df=pd.DataFrame(notes,columns=columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Notes')

    output.seek(0)
    return send_file(
            output,
            as_attachment=True,
            download_name=f'Notes_{notes[0][2]} {notes[0][1]}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

def copieparexam():
    sess_id = session.get('id')  # ID du professeur connecté
    db=connect()
    curseur = db.cursor()
    requete="""
    Select examens.nom,examens.classe,examens.description,examens.type,examens.id from examens where idprof=%s
    """
    curseur.execute(requete,(sess_id,))
    examens=curseur.fetchall()
    db.commit()
    curseur.close()
    return render_template('Copies.html',examens=examens)
