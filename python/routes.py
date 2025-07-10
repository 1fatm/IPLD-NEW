from flask import Flask, render_template, session
from python import app
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()
# Supabase configuration
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

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
    obtenir_statistiques
)
from python.Fonctions import (
    consulter_fonction,
    voirdetailsfonction,
    changer_statut_fonction,
    transmettre_fonction,
    valide_fonction,
    demandes_transmises_fonction,
    voirdetailsdirectfonction
)
@app.route('/')
def index():
    return render_template('accueil.html')

@app.route('/chefdedepartement')
def pagechefdepartement():
    if 'departement' not in session:
        return render_template('connexionchefdepartement.html', error="Veuillez vous connecter d'abord.")
    departement=session['departement']
    demandes=supabase.table('demandes').select('*').eq('departement', departement).eq('transmis', 'false').execute()
    demandes_data = demandes.data
    demande=supabase.table('demandes').select('*').eq('departement', departement).execute()
    #compter le nombre de demandes en attente
    attente = sum(1 for demande in demande.data if demande['statut'] == 'en_attente')
    approuve = sum(1 for demande in demande.data if demande['statut'] == 'approuve')
    rejete = sum(1 for demande in demande.data if demande['statut'] == 'rejete')
    transmise = sum(1 for demande in demande.data if str(demande['transmis']).lower() == 'true')
    session['attente'] = attente
    session['approuve'] = approuve
    session['rejete'] = rejete
    session['transmis'] = transmise
    print(transmise)
    for demande in demandes_data:
        date_str = demande.get('date_creation')
        if date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")  # format Supabase ISO
            demande['date_creation'] = dt.strftime('%d/%m/%Y %H:%M')
        else:
                    demande['date_creation'] = 'N/A'
    return render_template('chefdedepartement.html', lesdemandes=demandes_data, session=session)

@app.route('/pagedirection')
def pagedirection_route():
    if 'role' not in session or session['role'] != 'directeur':
        return render_template('connexiondirection.html', error="Veuillez vous connecter d'abord.")
    #on va afficher les information(demandes) faites à la direction
    demandes=supabase.table('transmis').select('*').execute().data
    montant = sum(demande['montant_total'] for demande in demandes)
    session['montant'] = montant
    total= len(demandes)
    session['total'] = total
    demandes = demandes[:5]
    return render_template('pagedirection.html', session=session, lesdemandes=demandes)

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
    if 'departement' not in session:
        return render_template('connexionchefdepartement.html', error="Veuillez vous connecter d'abord.")
    return consulter_fonction()

@app.route('/connexiondirection')
def connexiondirection_route():
    return render_template('connexiondirection.html')

@app.route('/inscriptiondirection')
def inscriptiondirection_route():
    return render_template('inscriptiondirection.html')

@app.route('/soumettredemande')
def soumettre_demande():
    if 'departement' not in session:
        return render_template('connexionchefdepartement.html', error="Veuillez vous connecter d'abord.")
    return render_template('soumettredemande.html')

@app.route('/synthese')
def synthese_route():
    if 'departement' not in session:
        return render_template('connexionchefdepartement.html', error="Veuillez vous connecter d'abord.")
    return render_template('synthese.html')



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


@app.route('/obtenir_statistiques', methods=['GET'])
def obtenir_statistiques_route():
    return obtenir_statistiques()

# Routes pour les fonctionnalités du chef de département
@app.route('/consulter_demandes_chef', methods=['GET'])
def consulter_demandes_chef_route():
    return consulter_demandes()
@app.route('/transmetteredemande')
def transmettre_route():
    return valide_fonction()
@app.route('/synthese_chef', methods=['GET'])
def synthese_chef_route():
    return synthese_route()
@app.route('/detailsdemandes', methods=['POST'])
def detailsdemandes_route():
    return voirdetailsfonction()

@app.route('/detailsdemandesdirect', methods=['POST'])
def detailsdemandesdirect_route():
    return voirdetailsdirectfonction()

@app.route('/changerstatut', methods=['POST'])
def changer_statut_route():
    return changer_statut_fonction()
@app.route('/transmettredemande', methods=['POST'])
def transmetteredemande_route():
    return transmettre_fonction()

@app.route('/demandetransmises')
def demandetransmises_route():
    return demandes_transmises_fonction()

@app.route('/pagedemande')
def pagedemande_route():
    if 'role' not in session or session['role'] != 'directeur':
        return render_template('connexiondirection.html', error="Veuillez vous connecter d'abord.")
    #on va afficher les information(demandes) faites à la direction
    demandes=supabase.table('transmis').select('*').execute().data
    montant = sum(demande['montant_total'] for demande in demandes)
    session['montant'] = montant
    total= len(demandes)
    session['total'] = total
    return render_template('demandedirection.html', session=session, lesdemandes=demandes)
