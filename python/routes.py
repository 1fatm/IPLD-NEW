from flask import Flask, render_template, session
from python import app
from python.authentification import (
    inscriptioncheffonction, 
    inscriptionproffonction, 
    inscriptiondirectionfonction,
    connexionproffonction, 
    connexioncheffonction, 
    connexiondirectionfonction, 
    deconnexionfonction
)

from python.pageprof import (
    creer_demande,
    sauvegarder_brouillon,
    consulter_demandes,
    consulter_brouillons,
    charger_brouillon,
    supprimer_brouillon,
    obtenir_statistiques
)
from python.Fonctions import(
    voirdetailsfonction
)
@app.route('/')
def index():
    return render_template('accueil.html')

@app.route('/chefdedepartement')
def pagechefdepartement():
    return render_template('chefdedepartement.html')

@app.route('/connexionprof')
def connexionprof_route():
    return render_template('connexionprof.html')

@app.route('/connexionchef')
def connexionchef_route():
    return render_template('connexionchefdepartement.html')

@app.route('/inscriptionchef')
def inscriptionchef_route():
    return render_template('inscriptionchefdepartement.html')

@app.route('/inscriptionprof')
def inscriptionprof_route():
    return render_template('inscriptionprof.html')

@app.route('/consulterlesdemandes')
def consulterpage_route():
    return render_template('consulter.html')

@app.route('/connexiondirection')
def connexiondirection_route():
    return render_template('connexiondirection.html')

@app.route('/inscriptiondirection')
def inscriptiondirection_route():
    return render_template('inscriptiondirection.html')

@app.route('/soumettredemande')
def soumettre_demande():
    return render_template('soumettredemande.html')

@app.route('/synthese')
def synthese_route():
    return render_template('synthese.html')

@app.route('/transmettredemande')
def transmettre_route():
    return render_template('transmettre.html')

@app.route('/inscriptionchefcode', methods=['POST'])
def inscriptionchefcode_route():
    return inscriptioncheffonction()

@app.route('/inscriptionprofcode', methods=['POST'])
def inscriptionprofcode_route():
    return inscriptionproffonction()

@app.route('/inscriptiondirectioncode', methods=['POST'])
def inscriptiondirectioncode_route():
    return inscriptiondirectionfonction()

@app.route('/pageprof')
def pageprof_route():
    return render_template('pageprof.html')

@app.route('/connexionprofcode', methods=['POST'])
def connexionprofcode_route():
    return connexionproffonction()

@app.route('/connexionchefcode', methods=['POST'])
def connexionchefcode_route():
    return connexioncheffonction()

@app.route('/connexiondirectioncode', methods=['POST'])
def connexiondirectioncode_route():
    return connexiondirectionfonction()

@app.route('/deconnexion')
def deconnexion_route():
    return deconnexionfonction()



@app.route('/creer_demande', methods=['POST'])
def creer_demande_route():
    return creer_demande()

@app.route('/sauvegarder_brouillon', methods=['POST'])
def sauvegarder_brouillon_route():
    return sauvegarder_brouillon()

@app.route('/consulter_demandes', methods=['GET'])
def consulter_demandes_route():
    return consulter_demandes()

@app.route('/consulter_brouillons', methods=['GET'])
def consulter_brouillons_route():
    return consulter_brouillons()

@app.route('/charger_brouillon', methods=['GET'])
def charger_brouillon_route():
    return charger_brouillon()

@app.route('/supprimer_brouillon', methods=['POST'])
def supprimer_brouillon_route():
    return supprimer_brouillon()

@app.route('/obtenir_statistiques', methods=['GET'])
def obtenir_statistiques_route():
    return obtenir_statistiques()

@app.route('/detailsdemandes',methods=['POST'])
def details_route():
    return voirdetailsfonction()


@app.route('/changerstatut',methods=['POST'])
def changer_statut_route():
    return changer_statut_fonction()


if __name__ == '__main__':
    app.run(debug=True)