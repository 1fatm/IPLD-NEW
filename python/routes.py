from flask import Flask, render_template,session
from python import app
from python.authentification import inscriptioncheffonction,inscriptionproffonction, inscriptiondirectionfonction,connexionproffonction, connexioncheffonction, connexiondirectionfonction, deconnexionfonction
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

if __name__ == '__main__':
    app.run(debug=True)
