
from supabase import create_client, Client
from app import app
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
import hashlib
from datetime import datetime

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def inscriptioncheffonction():
    nom=request.form.get('nom')
    prenom=request.form.get('prenom')
    email=request.form.get('email')
    motdepasse=request.form.get('password')
    confirm_motdepasse=request.form.get('confirm_password')
    departement=request.form.get('departement')
    if (motdepasse !=confirm_motdepasse):
        return render_template("inscriptionchefdepartement.html", error="Les mots de passe ne correspondent pas.")
    #on va d'abord verifier si il est pas deja inscrit
    deja_inscrit=supabase.table('Chef').select('email').eq('email', email).execute()
    try:
        if deja_inscrit.data:
            print("L'email existe déjà :", email)
            return render_template("inscriptionchefdepartement.html", error="Cet email est déjà utilisé. Veuillez en choisir un autre.")
        motdepasse = hashlib.sha256(motdepasse.encode()).hexdigest()  # Hasher le mot de passe avant de le stocker
        supabase.table('Chef').insert({
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'mot_de_passe': motdepasse,
            'departement': departement
        }).execute()
        #On va l'ajouter aussi dans les utilisateurs
        supabase.auth.sign_up(
            {
                "email": email,
                "password": motdepasse,
                "options": {
                    "data": {
                        "role": "chef_departement",
                    "nom": nom,
                    "prenom": prenom,
                    "departement": departement
                }
            }
        })
        print("Inscription réussie pour le chef de département :", nom, prenom)
        return render_template("inscriptionchefdepartement.html", success="Inscription réussie. Veuillez vous connecter.")
    except Exception as e:
        print("Erreur lors de l'inscription :",e)
        return render_template("inscriptionchefdepartement.html", error="Une erreur s'est produite lors de l'inscription. Veuillez réessayer.")


def inscriptionproffonction():
    nom=request.form.get('nom')
    prenom=request.form.get('prenom')
    email=request.form.get('email')
    motdepasse=request.form.get('password')
    confirm_motdepasse=request.form.get('confirm_password')
    departement=request.form.get('departement')
    if (motdepasse !=confirm_motdepasse):
        return render_template("inscriptionprof.html", error="Les mots de passe ne correspondent pas.")
    #on va d'abord verifier si il est pas deja inscrit
    deja_inscrit=supabase.table('Professeurs').select('email').eq('email', email).execute()
    try:
        if deja_inscrit.data:
            print("L'email existe déjà :", email)
            return render_template("inscriptionprof.html", error="Cet email est déjà utilisé. Veuillez en choisir un autre.")
        motdepasse = hashlib.sha256(motdepasse.encode()).hexdigest() 
        supabase.table('Professeurs').insert({
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'mot_de_passe': motdepasse,
            'departement': departement
        }).execute()
        #On va l'ajouter aussi dans les utilisateurs
        supabase.auth.sign_up(
            {
                "email": email,
                "password": motdepasse,
                "options": {
                    "data": {
                        "role": "professeur",
                    "nom": nom,
                    "prenom": prenom,
                    "departement": departement
                }
            }
        })
        print("Inscription réussie pour le professeur:", nom, prenom)
        return render_template("inscriptionprof.html", success="Inscription réussie. Veuillez vous connecter.")
    except Exception as e:
        print("Erreur lors de l'inscription :",e)
        return render_template("inscriptionprof.html", error="Une erreur s'est produite lors de l'inscription. Veuillez réessayer.")

def inscriptiondirectionfonction():
    nom=request.form.get('nom')
    prenom=request.form.get('prenom')
    email=request.form.get('email')
    motdepasse=request.form.get('password')
    confirm_motdepasse=request.form.get('confirm_password')
    departement=request.form.get('departement')
    if (motdepasse !=confirm_motdepasse):
        return render_template("inscriptiondirection.html", error="Les mots de passe ne correspondent pas.")
    #on va d'abord verifier si il est pas deja inscrit
    deja_inscrit=supabase.table('Direction').select('email').eq('email', email).execute()
    try:
        if deja_inscrit.data:
            print("L'email existe déjà :", email)
            return render_template("inscriptiondirection.html", error="Cet email est déjà utilisé. Veuillez en choisir un autre.")
        motdepasse=hashlib.sha256(motdepasse.encode()).hexdigest()
        supabase.table('Direction').insert({
            'nom': nom,
            'prenom': prenom,
            'email': email,
            'mot_de_passe': motdepasse,
            'departement': departement
        }).execute()
        #On va l'ajouter aussi dans les utilisateurs
        supabase.auth.sign_up(
            {
                "email": email,
                "password": motdepasse,
                "options": {
                    "data": {
                        "role": "directeur",
                    "nom": nom,
                    "prenom": prenom,
                    "departement": departement
                }
            }
        })
        print("Inscription réussie pour le directeur:", nom, prenom)
        return render_template("inscriptiondirection.html", success="Inscription réussie. Veuillez vous connecter.")
    except Exception as e:
        print("Erreur lors de l'inscription :",e)
        return render_template("inscriptiondirection.html", error="Une erreur s'est produite lors de l'inscription du directeur")

def connexionproffonction():
    mail = request.form.get('email')
    motdepasse = request.form.get('password')
    try:
        
        motdepassesup = supabase.table('Professeurs').select('*').eq('email', mail).execute()
        if not motdepassesup.data:
            return render_template("connexionprof.html", error="Cet utilisateur n'existe pas. Veuillez réessayer.")
        mot_de_passe = motdepassesup.data[0]['mot_de_passe']
        #verifier si le mot de passe correspond
        motdepasse = hashlib.sha256(motdepasse.encode()).hexdigest() 
        if not motdepasse==mot_de_passe:
            print("Les mots de passe ne correspondent pas")
            return render_template("connexionprof.html", error="Identifiants invalides. Veuillez réessayer.")
        else:
            session['username']=motdepassesup.data[0]['email']
            session['role']='professeur'
            print("Connexion réussie pour le professeur :", mail)
            return render_template("pageprof.html", session=session)
    except Exception as e:
        print("Erreur lors de la connexion :", e)
        return render_template("connexionprof.html", error="Identifiants invalides. Veuillez réessayer.")


def connexioncheffonction():
    mail = request.form.get('email')
    motdepasse = request.form.get('password')
    try:
        motdepassesup = supabase.table('Chef').select('*').eq('email', mail).execute()
        if not motdepassesup.data:
            return render_template("connexionchefdepartement.html", error="Cet utilisateur n'existe pas. Veuillez réessayer.")
        mot_de_passe = motdepassesup.data[0]['mot_de_passe']
        departement = motdepassesup.data[0]['departement']
        nom=motdepassesup.data[0]['nom']
        prenom=motdepassesup.data[0]['prenom']
        #verifier si le mot de passe correspond
        motdepasse = hashlib.sha256(motdepasse.encode()).hexdigest() 
        if not motdepasse==mot_de_passe:
            return render_template("connexionchefdepartement.html", error="Identifiants invalides. Veuillez réessayer.")
        else:
            #on récupére les informations du chef
            session['username']=motdepassesup.data[0]['email']
            session['role']='Chef du Departement '+departement
            session['nom']=nom
            session['departement']=departement
            session['prenom']=prenom
            print("Connexion réussie pour le chef :", mail)
            #on recupere les demandes faites par les professeurs de son departement
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
            lesdemandes = demandes.data if demandes.data else []
            for demande in lesdemandes:
                date_str = demande.get('date_creation')
                if date_str:
                    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")  # format Supabase ISO
                    demande['date_creation'] = dt.strftime('%d/%m/%Y %H:%M')
                else:
                    demande['date_creation'] = 'N/A'
            return render_template("chefdedepartement.html", session=session, lesdemandes=lesdemandes)
    except Exception as e:
        print("Erreur lors de la connexion :", e)
        return render_template("connexionchefdepartement.html", error="Identifiants invalides. Veuillez réessayer.")

def connexiondirectionfonction():
    mail = request.form.get('email')
    motdepasse = request.form.get('password')
    try:
        #unhash the password before checking
        motdepassesup = supabase.table('Direction').select('*').eq('email', mail).execute()
        if not motdepassesup.data:
            return render_template("connexiondirection.html", error="Cet utilisateur n'existe pas. Veuillez réessayer.")
        mot_de_passe = motdepassesup.data[0]['mot_de_passe']
        # Check the password against the hashed password
        # If the password is not hashed, return an error
        motdepasse = hashlib.sha256(motdepasse.encode()).hexdigest()  # Hash the password before checking
        if not motdepasse==mot_de_passe:
            return render_template("connexiondirection.html", error="Identifiants invalides. Veuillez réessayer.")
        else:
            session['username']=motdepassesup.data[0]['email']
            session['role']='directeur'
            print("Connexion réussie pour le directeur :", mail)
            return render_template("pagedirection.html", session=session)
    except Exception as e:
        print("Erreur lors de la connexion :", e)
        return render_template("connexiondirection.html", error="Identifiants invalides. Veuillez réessayer.")


def deconnexionfonction():
    session.clear()  
    return redirect(url_for('index'))

