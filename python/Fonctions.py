from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector,os,re
import io
import base64
from mysql.connector import Error


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
    cursor = db.cursor()
except Error as e:
    print(f"Error connecting to MySQL: {e}")

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
            return countcopiesnonnotees()
        else:
            erreur_message = "Identifiants incorrects"
            return render_template('connexion_prof.html', erreur_message=erreur_message)

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
            return statistiques_etudiant()
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
    sess_id = session.get('id')
    cursor = db.cursor()
    print(sess_id)  
    requete = """
    SELECT e.nom_complet, e.classe, ex.nom AS examen_nom, c.fichier_pdf, c.date_soumission, c.id,ex.datedesoumission
    FROM copies c
    JOIN etudiants e ON c.id_etudiant = e.id
    JOIN examens ex ON c.id_examen = ex.id
    WHERE ex.idprof = %s
    """
    cursor.execute(requete, (sess_id,))
    devoirsoumis = cursor.fetchall()
    print(devoirsoumis)  

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

def infodev():
    sess_username=session.get('username')
    id=request.form['id']
    sess_id = session.get('id')
    curseur=db.cursor()
    curseur.execute("Select * from examens where id=%s",(id,))
    infodevoirs=curseur.fetchall()
    db.commit()
    print(infodevoirs)
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
    sess_id = session.get('id')
    idcopie=request.form['id']
    note=request.form['note']
    commentaire=request.form['commentaire']
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
    SELECT e.nom_complet, e.classe, ex.nom AS examen_nom, c.note,c.commentaire
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

def afficher_examens():
    sess_id = session.get('id')  # ID du professeur connecté
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

def statistiques_etudiant():
    sess_id = session.get('id')  # ID de l'étudiant connecté
    curseur = db.cursor()
    # Récupérer les statistiques des examens donnés par ce professeur
    requete = """
    select count(*) from  copies where id_etudiant=%s

    """
    curseur.execute(requete, (sess_id,))
    soumis = curseur.fetchone()[0]
    requete = """SELECT COUNT(*) 
        FROM examens 
        JOIN etudiants ON examens.classe = etudiants.classe 
        WHERE etudiants.id = %s 
        AND etudiants.id NOT IN (SELECT id_etudiant FROM copies)
    """
    curseur.execute(requete, (sess_id,))
    non_soumis = curseur.fetchone()[0]
    requete = """SELECT COUNT(*) 
        FROM examens 
        JOIN etudiants ON examens.classe = etudiants.classe 
        WHERE etudiants.id = %s 
        AND etudiants.id NOT IN (SELECT id_etudiant FROM copies)
        AND examens.datedesoumission < NOW()
    """
    curseur.execute(requete, (sess_id,))
    enretard = curseur.fetchone()[0]
    curseur.close()

    return render_template('pageaccueil_etudiant.html',soumis=soumis,non_soumis=non_soumis,enretard=enretard,sess_username=session['username'])

def afficher_devoirs():
    if 'id' not in session:
        flash("Veuillez vous connecter.", "warning")
        return redirect('/')

    cursor = db.cursor()
    try:
        user_id = session['id']
        cursor.execute("SELECT classe FROM etudiants WHERE id = %s", (user_id,))
        classe = cursor.fetchone()[0]
        requete = """ Select examens.nom, examens.description, examens.type, examens.classe, examens.chemin, examens.datedesoumission, enseignants.nom_complet, examens.id
        FROM examens 
        JOIN enseignants on examens.idprof=enseignants.id
        WHERE examens.classe = %s
        """
        cursor.execute(requete, (classe,))
        devoirs = cursor.fetchall()
        print(devoirs[0][7])
        if devoirs:
            verifdevoir=True
            return render_template('devoir.html', devoirs=devoirs,verifdevoir=verifdevoir)
        else:
            verifdevoir=False
            return render_template('devoir.html',verifdevoir=verifdevoir)
    except mysql.connector.Error as err:
        flash(f"Erreur lors de la récupération des devoirs : {err}", "danger")
        return redirect('/accueiletudiant')

def afficher_notifications():
    if 'id' not in session:
        return redirect('/connexion_etudiant')

    id_etudiant = session['id']
    
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT classe FROM etudiants WHERE id = %s", (id_etudiant,))
    etudiant = cursor.fetchone()
    
    if not etudiant:
        return "Étudiant non trouvé", 404
    
    classe_etudiant = etudiant['classe']

    cursor.execute("""
        SELECT e.id, e.nom, e.datedesoumission, e.date_creation, ens.nom_complet AS prof,
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
