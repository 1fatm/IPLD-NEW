from flask import Flask, render_template,session
from python import app
from python.Fonctions import inscriptionetu,inscriptionprof,connexionprof,connexionetudiant,ajouter_devoir,infodev,soumettrefichier,infocopiecode,notercopie,updatenote,timeline_prof,afficher_note,deconnection,afficher_examens,trier_classe,countcopiesnonnotees,trier_date,statistiques_etudiant,afficher_devoirs,generer_statistiques,afficher_notifications,afficher_notes,voirlesnotes,statistiquesp,chatbot,generernote,copieparexam


@app.route('/')
def index():
    return render_template('accueil.html')


@app.route('/chefdedepartement')
def pagechefdepartement():
    return render_template('chefdedepartement.html')

@app.route('/connexionprof')
def connexionprof_route():
    return render_template('connexionprof.html')
@app.route('/inscriptionprof')
def inscriptionprof_route():
    
    return render_template('inscriptionprof.html')

@app.route('/inscriptionchefdepartement')
def inscriptionchefdepartement_route():
    
    return render_template('inscriptionchefdepartement.html')
@app.route('/inscriptiondirection')
def inscriptiondirection_route():
    
    return render_template('inscriptiondirection.html')


@app.route('/consulterlesdemandes')
def consulterpage_route():
    
    return render_template('consulter.html')

@app.route('/soumettredemande')
def soumettre_demande():
    
    return render_template('soumettredemande.html')

@app.route('/synthese')
def synthese_route():
    
 return render_template('synthese.html')
@app.route('/transmettredemande')
def transmettre_route():
    return render_template('transmettre.html')
    
@app.route('/deconnexion')
def deconnexion_route():
    
    return render_template('accueil.html')       
    
@app.route('/pageprof')
def pageprof_route():
    return render_template('pageprof.html')
   
if __name__ == '__main__':
    app.run(debug=True)
