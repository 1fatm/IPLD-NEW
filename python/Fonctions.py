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

def voirdetailsfonction():
    iddemande=request.form.get('id')
    voirdetails=supabase.table('demandes').select('*').eq('id', iddemande).execute()
    demande=voirdetails.data[0]
    print(demande)
    return render_template("details.html", demande=demande)

def changer_statut_fonction():
    iddemande=request.form.get('id')
    statut=request.form.get('statut')
    changerstatut=supabase.table('demandes').update({'statut': statut}).eq('id', iddemande).execute()
    voirdetails=supabase.table('demandes').select('*').eq('id', iddemande).execute()
    demande=voirdetails.data[0]
    return render_template("details.html", demande=demande)