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
    obtenir_statistiques,
    sauvegarder_brouillon,
    consulter_brouillons,
    obtenir_brouillon,
    modifier_brouillon,
    supprimer_brouillon,
    soumettre_brouillon,
    detail_demande,
    obtenir_demande_details
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

# Routes pour les fonctionnalités des professeurs
@app.route('/creer_demande', methods=['POST'])
def creer_demande_route():
    return creer_demande()

@app.route('/consulter_demandes', methods=['GET'])
def consulter_demandes_route():
    return consulter_demandes()

@app.route('/obtenir_statistiques', methods=['GET'])
def obtenir_statistiques_route():
    return obtenir_statistiques()

@app.route('/sauvegarder_brouillon', methods=['POST'])
def sauvegarder_brouillon_route():
    return sauvegarder_brouillon()

@app.route('/consulter_brouillons', methods=['GET'])
def consulter_brouillons_route():
    return consulter_brouillons()

@app.route('/obtenir_brouillon/<int:brouillon_id>', methods=['GET'])
def obtenir_brouillon_route(brouillon_id):
    return obtenir_brouillon(brouillon_id)

@app.route('/modifier_brouillon/<int:brouillon_id>', methods=['POST'])
def modifier_brouillon_route(brouillon_id):
    return modifier_brouillon(brouillon_id)

@app.route('/supprimer_brouillon/<int:brouillon_id>', methods=['DELETE'])
def supprimer_brouillon_route(brouillon_id):
    return supprimer_brouillon(brouillon_id)

@app.route('/soumettre_brouillon/<int:brouillon_id>', methods=['POST'])
def soumettre_brouillon_route(brouillon_id):
    return soumettre_brouillon(brouillon_id)

@app.route('/detail_demande')
def detail_demande_route():
    return render_template('detail.html')

@app.route('/detail_demande')
def detail_demande():
    return detail_demande()

@app.route('/obtenir_demande_details/<int:demande_id>')
def obtenir_demande_details_route(demande_id):
    return obtenir_demande_details(demande_id)



if __name__ == '__main__':
    app.run(debug=True)