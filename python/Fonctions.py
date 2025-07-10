from supabase import create_client, Client
from app import app
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
import os
from datetime import datetime
# Supabase configuration
load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def voirdetailsfonction():
    iddemande=request.form.get('id')
    voirdetails=supabase.table('demandes').select('*').eq('id', iddemande).execute()
    demande=voirdetails.data[0]
    print(demande)
    # Convertir la date de création en format lisible
    
    date_str = demande.get('date_creation')
    if date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")  # format Supabase ISO
            demande['date_creation'] = dt.strftime('%d/%m/%Y %H:%M')
    else:
         demande['date_creation'] = 'N/A'
    return render_template("details.html", demande=demande)

def voirdetailsdirectfonction():
    iddemande=request.form.get('id')
    voirdetails=supabase.table('demandes').select('*').eq('id', iddemande).execute()
    demande=voirdetails.data[0]
    print(demande)
    return render_template("detailsdirect.html", demande=demande)

def changer_statut_fonction():
    iddemande=request.form.get('id')
    statut=request.form.get('statut')
    changerstatut=supabase.table('demandes').update({'statut': statut}).eq('id', iddemande).execute()
    voirdetails=supabase.table('demandes').select('*').eq('id', iddemande).execute()
    demande=voirdetails.data[0]
    # Convertir la date de création en format lisible
    date_str = demande.get('date_creation')
    if date_str:
                    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")  # format Supabase ISO
                    demande['date_creation'] = dt.strftime('%d/%m/%Y %H:%M')
    else:
                    demande['date_creation'] = 'N/A'
    return render_template("details.html", demande=demande)

def consulter_fonction():
   #selection les demande en attente
    demandes=supabase.table('demandes').select('*').eq('statut', 'en_attente').execute()
    demandes_data = demandes.data   
    for demande in demandes_data:
        # Convertir la date de création en format lisible
        date_str = demande.get('date_creation')
        if date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")  # format Supabase ISO
            demande['date_creation'] = dt.strftime('%d/%m/%Y %H:%M')
        else:
            demande['date_creation'] = 'N/A'
    return render_template("consulter.html", lesdemandes=demandes_data,session=session)

def valide_fonction():
    #selection les demande en attente
    demandes=supabase.table('demandes').select('*').eq('statut', 'approuve').eq('transmis', 'false').execute()
    print(demandes.data)
    demandes_data = demandes.data
    for demande in demandes_data:
        # Convertir la date de création en format lisible
        date_str = demande.get('date_creation')
        if date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")  # format Supabase ISO
            demande['date_creation'] = dt.strftime('%d/%m/%Y %H:%M')
        else:
            demande['date_creation'] = 'N/A'
    return render_template("transmettre.html", lesdemandes=demandes_data,session=session)

def transmettre_fonction():
    iddemande=request.form.get('id')
    #recupere les données de la demande
    demande=supabase.table('demandes').select('*').eq('id', iddemande).execute()
    demande_data = demande.data[0]
    #transmettre la demande
    transmettre=supabase.table('transmis').insert({
        'id': demande_data['id'],
        'titre_demande': demande_data['titre_demande'],
        'categorie': demande_data['categorie'],
        'montant_total': demande_data['montant_total'],
        'role_demandeur': demande_data['role_demandeur'],
        'description': demande_data['description'],
        'departement': demande_data['departement'],
        'date_creation': demande_data['date_creation'],
    }).execute()
    #on le marque comme transmis
    supabase.table('demandes').update({'transmis': 'true'}).eq('id', iddemande).execute()
    return valide_fonction()

def demandes_transmises_fonction():
    departement = session.get('departement')
    #on affiche les demandes transmises
    demandes_transmises = supabase.table('demandes').select('*').eq('departement', departement).eq('transmis', 'true').execute()
    demandes_data = demandes_transmises.data
    for demande in demandes_data:
        # Convertir la date de création en format lisible
        date_str = demande.get('date_creation')
        if date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")  # format Supabase ISO
            demande['date_creation'] = dt.strftime('%d/%m/%Y %H:%M')
        else:
            demande['date_creation'] = 'N/A'
    return render_template("transmis.html", lesdemandes=demandes_data, session=session)

