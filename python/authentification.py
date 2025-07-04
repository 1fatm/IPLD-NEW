from supabase import create_client, Client
from app import app
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
# Supabase configuration
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
    if deja_inscrit.data:
        print("L'email existe déjà :", email)
        return render_template("inscriptionchefdepartement.html", error="Cet email est déjà utilisé. Veuillez en choisir un autre.")
    try:
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
    if deja_inscrit.data:
        print("L'email existe déjà :", email)
        return render_template("inscriptionprof.html", error="Cet email est déjà utilisé. Veuillez en choisir un autre.")
    try:
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
    if deja_inscrit.data:
        print("L'email existe déjà :", email)
        return render_template("inscriptiondirection.html", error="Cet email est déjà utilisé. Veuillez en choisir un autre.")
    try:
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
        return render_template("inscriptiondirection.html", error="Une erreur s'est produite lors de l'inscription. Veuillez réessayer.")
