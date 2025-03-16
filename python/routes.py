from flask import Flask, render_template,session
from python import app
from python.Fonctions import inscriptionetu,inscriptionprof,connexionprof,connexionetudiant,ajouter_devoir,infodev,soumettrefichier,infocopiecode,notercopie,updatenote,timeline_prof,afficher_note,deconnection,afficher_examens,trier_classe,countcopiesnonnotees,trier_date,statistiques_etudiant,afficher_devoirs,generer_statistiques,afficher_notifications,afficher_notes,voirlesnotes,statistiquesp,chatbot,generernote,copieparexam


@app.route('/')
def index():
    return render_template('accueil.html')

@app.route('/connectionprofpage')
def Connexionprof():
    return render_template('connexion_prof.html')

@app.route('/connectionetudiantpage')
def Connexionetu():
    return render_template('connexion_etudiant.html')

@app.route('/inscriptionetudiantcode', methods=['POST'])
def Inscription():
    return inscriptionetu()

@app.route('/connexionprofcode', methods=['POST'])
def ConnexionProf():
    return connexionprof()

@app.route('/connexionetudiantcode', methods=['POST'])
def ConnexionEtudiant():
    return connexionetudiant()

@app.route('/inscriptionprofcode', methods=['POST'])
def Inscriptionprof():
    return inscriptionprof()

@app.route('/inscriptionprofpage')
def Inscriptionprofpage():
    return render_template('inscription_prof.html')

@app.route('/inscriptionetudiantpage')
def Inscriptionetupage():
    return render_template('inscription_etudiant.html')

@app.route('/pageEtudiant')
def ConnexionP():
    return render_template('pageEtudiant.html')

@app.route('/info_devcode',methods=['POST'])
def Infodev():
    return infodev()

@app.route('/InscriptionProf')
def InscriptionP():
    return render_template('InscriptionP.html')

@app.route('/Profil')
def Profil():
    return render_template('Profil.html')

@app.route('/ajouterun_devoir', methods=['POST'])
def Ajouterundevoir():
    return ajouter_devoir()

@app.route('/info_copiecode',methods=['POST'])
def copiecode():
    return infocopiecode()

@app.route('/notercopie',methods=['POST'])
def Notercopie():
    return notercopie()

@app.route('/updatenote',methods=['POST'])
def Updatenote():
    return updatenote()

@app.route('/ajouterun_devoir', methods=['POST'])
def Ajoutdevoir_route():
    return ajouter_devoir()

@app.route('/soumettre',methods=['POST'])
def Soumettre():
    return soumettrefichier()

@app.route('/timelineP')
def timelineprof_route():
    return timeline_prof()

@app.route('/examen')
def examen_route():
    return afficher_examens()

@app.route('/accueilp')
def accueilp_route():
    return countcopiesnonnotees()

@app.route('/ajoutdevoirpage')
def AjoutAdmin_route():
    return render_template('Ajoutdevoir.html',sess_username=session['username'],sess_id=session['id'])

@app.route('/copies')
def copiesexamen():
    return copieparexam()

@app.route('/copie' ,methods=['POST'])
def copie_examen():
    return timeline_prof()

@app.route('/notep')
def note_prof():
    return afficher_note()

@app.route('/statistiquesp')
def statistiques():
    return statistiquesp()

@app.route("/accueiletudiant")
def accueiletudiant():
    return statistiques_etudiant()

@app.route("/examen")
def examen():
    return afficher_examens()

@app.route('/devoirs')
def devoirs_page():
    return afficher_devoirs()

@app.route('/notes')
def notes():
    return afficher_notes()

@app.route('/notifications')
def notifications():
    return afficher_notifications()

@app.route('/deconnection')
def deconnecter():
    return deconnection()

@app.route('/trier_classe',methods=['POST'])
def triparclasse():
    return trier_classe()

@app.route('/trier_date',methods=['POST'])
def tripardate():
    return trier_date()

@app.route('/noteexam',methods=['POST'])
def voirnotes():
   return voirlesnotes()
@app.route('/chatbot', methods=['POST'])
def ollama():
    return chatbot()

@app.route('/generernote',methods=['POST'])
def genererfichiernote():
    return generernote()

if __name__ == '__main__':
    app.run(debug=True)
