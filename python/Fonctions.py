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