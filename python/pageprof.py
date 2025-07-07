from supabase import create_client, Client
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import uuid

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def creer_demande():
    """Fonction pour créer une nouvelle demande budgétaire"""
    print("=== DÉBUT CRÉATION DEMANDE ===")
    
    # Vérification de l'authentification
    if 'username' not in session or session.get('role') != 'professeur':
        print("❌ Accès non autorisé - Session:", session)
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    try:
        # Récupérer les données du formulaire
        nom_demandeur = request.form.get('teacherName')
        email_demandeur = session.get('username')
        titre_demande = request.form.get('title')
        categorie = request.form.get('category')
        description = request.form.get('description')
        montant_total = request.form.get('amount')
        
        print(f"📝 Données reçues:")
        print(f"   - Nom: {nom_demandeur}")
        print(f"   - Email: {email_demandeur}")
        print(f"   - Titre: {titre_demande}")
        print(f"   - Catégorie: {categorie}")
        print(f"   - Description: {description}")
        print(f"   - Montant: {montant_total}")
        
        # Validation des données obligatoires
        if not nom_demandeur or not titre_demande or not categorie or not description or not montant_total:
            print("❌ Données manquantes")
            return jsonify({'success': False, 'message': 'Tous les champs obligatoires doivent être remplis'}), 400
        
        # Conversion du montant
        try:
            montant_total = float(montant_total)
        except ValueError:
            print("❌ Montant invalide")
            return jsonify({'success': False, 'message': 'Montant invalide'}), 400
        
        # Récupérer les informations du professeur
        print(f"🔍 Recherche du professeur: {email_demandeur}")
        try:
            prof_info = supabase.table('Professeurs').select('*').eq('email', email_demandeur).execute()
            print(f"📊 Résultat recherche professeur: {prof_info}")
        except Exception as e:
            print(f"❌ Erreur lors de la recherche du professeur: {e}")
            return jsonify({'success': False, 'message': 'Erreur lors de la recherche du professeur'}), 500
        
        if not prof_info.data:
            print("❌ Professeur non trouvé")
            return jsonify({'success': False, 'message': 'Professeur non trouvé'}), 404
        
        departement = prof_info.data[0]['departement']
        print(f"✅ Professeur trouvé - Département: {departement}")
        
        # Traiter les articles (si fournis)
        articles = []
        item_names = request.form.getlist('itemName[]')
        item_quantities = request.form.getlist('itemQuantity[]')
        item_prices = request.form.getlist('itemPrice[]')
        
        print(f"📦 Articles reçus: {len(item_names)} articles")
        print(f"   - Noms: {item_names}")
        print(f"   - Quantités: {item_quantities}")
        print(f"   - Prix: {item_prices}")
        
        for i in range(len(item_names)):
            if item_names[i] and item_quantities[i] and item_prices[i]:
                try:
                    article = {
                        'nom': item_names[i],
                        'quantite': int(item_quantities[i]),
                        'prix_unitaire': float(item_prices[i]),
                        'prix_total': int(item_quantities[i]) * float(item_prices[i])
                    }
                    articles.append(article)
                    print(f"   ✅ Article {i+1}: {article}")
                except ValueError as e:
                    print(f"   ❌ Erreur article {i+1}: {e}")
        
        # Traiter les pièces jointes
        pieces_jointes = []
        if 'attachments' in request.files:
            for file in request.files.getlist('attachments'):
                if file.filename:
                    try:
                        pieces_jointes.append({
                            'nom_fichier': file.filename,
                            'taille': len(file.read()),
                            'type': file.content_type
                        })
                        print(f"📎 Pièce jointe: {file.filename}")
                    except Exception as e:
                        print(f"❌ Erreur pièce jointe: {e}")
        
        # Préparer les données pour la base
        demande_data = {
            'nom_demandeur': nom_demandeur,
            'email_demandeur': email_demandeur,
            'role_demandeur': 'professeur',
            'departement': departement,
            'titre_demande': titre_demande,
            'categorie': categorie,
            'description': description,
            'montant_total': montant_total,
            'statut': 'en_attente',
            'chemin_articles': json.dumps(articles) if articles else None,
            'chemin_pieces_jointes': json.dumps(pieces_jointes) if pieces_jointes else None
        }
        
        print(f"💾 Données à insérer dans la base:")
        print(f"   {demande_data}")
        
        # Insérer dans la base de données
        try:
            print("🔄 Insertion dans Supabase...")
            result = supabase.table('demandes').insert(demande_data).execute()
            print(f"📊 Résultat insertion: {result}")
            
            # Vérifier si l'insertion a réussi
            if hasattr(result, 'data') and result.data:
                print("✅ Demande créée avec succès!")
                return jsonify({
                    'success': True, 
                    'message': 'Demande créée avec succès', 
                    'demande_id': result.data[0]['id']
                })
            else:
                print(f"❌ Échec de l'insertion - result: {result}")
                # Essayer de récupérer l'erreur
                error_message = "Erreur lors de la création de la demande"
                if hasattr(result, 'error') and result.error:
                    error_message = f"Erreur Supabase: {result.error}"
                return jsonify({'success': False, 'message': error_message}), 500
                
        except Exception as e:
            print(f"❌ Exception lors de l'insertion: {e}")
            print(f"   Type: {type(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Erreur base de données: {str(e)}'}), 500
            
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Une erreur s\'est produite: {str(e)}'}), 500
    
    finally:
        print("=== FIN CRÉATION DEMANDE ===")

# Fonction de test pour vérifier la connexion Supabase
def test_supabase_connection():
    """Fonction pour tester la connexion à Supabase"""
    try:
        # Test simple de connexion
        result = supabase.table('demandes').select('count').execute()
        print(f"✅ Connexion Supabase OK: {result}")
        return True
    except Exception as e:
        print(f"❌ Erreur connexion Supabase: {e}")
        return False

# Reste du code (autres fonctions)...
def sauvegarder_brouillon():
    """Fonction pour sauvegarder une demande en brouillon"""
    if 'username' not in session or session.get('role') != 'professeur':
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    try:
        # Récupérer les données JSON
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Aucune donnée reçue'}), 400
        
        email_demandeur = session.get('username')
        
        # Récupérer les informations du professeur
        prof_info = supabase.table('Professeurs').select('*').eq('email', email_demandeur).execute()
        if not prof_info.data:
            return jsonify({'success': False, 'message': 'Professeur non trouvé'}), 404
        
        departement = prof_info.data[0]['departement']
        
        # Préparer les données du brouillon
        brouillon_data = {
            'nom_demandeur': data.get('teacherName', ''),
            'email_demandeur': email_demandeur,
            'role_demandeur': 'professeur',
            'departement': departement,
            'titre_demande': data.get('title', ''),
            'categorie': data.get('category', ''),
            'description': data.get('description', ''),
            'montant_total': float(data.get('amount', 0)) if data.get('amount') else 0,
            'statut': 'brouillon',
            'chemin_articles': json.dumps(data.get('articles', [])) if data.get('articles') else None,
            'chemin_pieces_jointes': json.dumps(data.get('pieces_jointes', [])) if data.get('pieces_jointes') else None
        }
        
        # Vérifier si c'est une mise à jour d'un brouillon existant
        brouillon_id = data.get('brouillon_id')
        if brouillon_id:
            result = supabase.table('demandes').update(brouillon_data).eq('id', brouillon_id).eq('email_demandeur', email_demandeur).execute()
        else:
            result = supabase.table('demandes').insert(brouillon_data).execute()
        
        if result.data:
            return jsonify({
                'success': True, 
                'message': 'Brouillon sauvegardé avec succès', 
                'brouillon_id': result.data[0]['id']
            })
        else:
            return jsonify({'success': False, 'message': 'Erreur lors de la sauvegarde du brouillon'}), 500
            
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du brouillon: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Une erreur s\'est produite: {str(e)}'}), 500

def consulter_demandes():
    """Fonction pour consulter toutes les demandes d'un professeur"""
    if 'username' not in session or session.get('role') != 'professeur':
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    try:
        email_demandeur = session.get('username')
        
        # Récupérer toutes les demandes du professeur
        result = supabase.table('demandes').select('*').eq('email_demandeur', email_demandeur).order('date_creation', desc=True).execute()
        
        if result.data:
            # Traiter les données pour le frontend
            demandes = []
            for demande in result.data:
                demandes.append({
                    'id': demande['id'],
                    'titre_demande': demande['titre_demande'],
                    'categorie': demande['categorie'],
                    'montant_total': demande['montant_total'],
                    'statut': demande['statut'],
                    'date_creation': demande['date_creation'],
                    'date_modification': demande['date_modification'],
                    'description': demande['description'],
                    'commentaire_chef': demande.get('commentaire_chef', ''),
                    'commentaire_direction': demande.get('commentaire_direction', ''),
                    'articles': json.loads(demande['chemin_articles']) if demande.get('chemin_articles') else [],
                    'pieces_jointes': json.loads(demande['chemin_pieces_jointes']) if demande.get('chemin_pieces_jointes') else []
                })
            
            return jsonify({'success': True, 'demandes': demandes})
        else:
            return jsonify({'success': True, 'demandes': []})
            
    except Exception as e:
        print(f"Erreur lors de la consultation des demandes: {str(e)}")
        return jsonify({'success': False, 'message': f'Une erreur s\'est produite: {str(e)}'}), 500

def consulter_brouillons():
    """Fonction pour consulter les brouillons d'un professeur"""
    if 'username' not in session or session.get('role') != 'professeur':
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    try:
        email_demandeur = session.get('username')
        
        # Récupérer tous les brouillons du professeur
        result = supabase.table('demandes').select('*').eq('email_demandeur', email_demandeur).eq('statut', 'brouillon').order('date_creation', desc=True).execute()
        
        if result.data:
            brouillons = []
            for brouillon in result.data:
                brouillons.append({
                    'id': brouillon['id'],
                    'titre_demande': brouillon['titre_demande'],
                    'categorie': brouillon['categorie'],
                    'montant_total': brouillon['montant_total'],
                    'date_creation': brouillon['date_creation'],
                    'date_modification': brouillon['date_modification'],
                    'nom_demandeur': brouillon['nom_demandeur'],
                    'description': brouillon['description'],
                    'articles': json.loads(brouillon['chemin_articles']) if brouillon.get('chemin_articles') else [],
                    'pieces_jointes': json.loads(brouillon['chemin_pieces_jointes']) if brouillon.get('chemin_pieces_jointes') else []
                })
            
            return jsonify({'success': True, 'brouillons': brouillons})
        else:
            return jsonify({'success': True, 'brouillons': []})
            
    except Exception as e:
        print(f"Erreur lors de la consultation des brouillons: {str(e)}")
        return jsonify({'success': False, 'message': f'Une erreur s\'est produite: {str(e)}'}), 500

def charger_brouillon():
    """Fonction pour charger un brouillon spécifique"""
    if 'username' not in session or session.get('role') != 'professeur':
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    try:
        brouillon_id = request.args.get('id')
        email_demandeur = session.get('username')
        
        if not brouillon_id:
            return jsonify({'success': False, 'message': 'ID du brouillon manquant'}), 400
        
        # Récupérer le brouillon
        result = supabase.table('demandes').select('*').eq('id', brouillon_id).eq('email_demandeur', email_demandeur).eq('statut', 'brouillon').execute()
        
        if result.data:
            brouillon = result.data[0]
            brouillon_data = {
                'id': brouillon['id'],
                'nom_demandeur': brouillon['nom_demandeur'],
                'titre_demande': brouillon['titre_demande'],
                'categorie': brouillon['categorie'],
                'description': brouillon['description'],
                'montant_total': brouillon['montant_total'],
                'articles': json.loads(brouillon['chemin_articles']) if brouillon.get('chemin_articles') else [],
                'pieces_jointes': json.loads(brouillon['chemin_pieces_jointes']) if brouillon.get('chemin_pieces_jointes') else []
            }
            
            return jsonify({'success': True, 'brouillon': brouillon_data})
        else:
            return jsonify({'success': False, 'message': 'Brouillon non trouvé'}), 404
            
    except Exception as e:
        print(f"Erreur lors du chargement du brouillon: {str(e)}")
        return jsonify({'success': False, 'message': f'Une erreur s\'est produite: {str(e)}'}), 500

def supprimer_brouillon():
    """Fonction pour supprimer un brouillon"""
    if 'username' not in session or session.get('role') != 'professeur':
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Aucune donnée reçue'}), 400
            
        brouillon_id = data.get('id')
        email_demandeur = session.get('username')
        
        if not brouillon_id:
            return jsonify({'success': False, 'message': 'ID du brouillon manquant'}), 400
        
        # Supprimer le brouillon
        result = supabase.table('demandes').delete().eq('id', brouillon_id).eq('email_demandeur', email_demandeur).eq('statut', 'brouillon').execute()
        
        if result.data:
            return jsonify({'success': True, 'message': 'Brouillon supprimé avec succès'})
        else:
            return jsonify({'success': False, 'message': 'Brouillon non trouvé ou impossible à supprimer'}), 404
            
    except Exception as e:
        print(f"Erreur lors de la suppression du brouillon: {str(e)}")
        return jsonify({'success': False, 'message': f'Une erreur s\'est produite: {str(e)}'}), 500

def obtenir_statistiques():
    """Fonction pour obtenir les statistiques des demandes d'un professeur"""
    if 'username' not in session or session.get('role') != 'professeur':
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    try:
        email_demandeur = session.get('username')
        
        # Récupérer toutes les demandes (sauf brouillons)
        result = supabase.table('demandes').select('*').eq('email_demandeur', email_demandeur).neq('statut', 'brouillon').execute()
        
        if result.data:
            demandes = result.data
            
            # Calculer les statistiques
            total_demandes = len(demandes)
            total_montant = sum(float(d['montant_total']) for d in demandes)
            
            # Statistiques par statut
            stats_statut = {}
            for demande in demandes:
                statut = demande['statut']
                if statut not in stats_statut:
                    stats_statut[statut] = {'count': 0, 'montant': 0}
                stats_statut[statut]['count'] += 1
                stats_statut[statut]['montant'] += float(demande['montant_total'])
            
            # Statistiques par catégorie
            stats_categorie = {}
            for demande in demandes:
                categorie = demande['categorie']
                if categorie not in stats_categorie:
                    stats_categorie[categorie] = {'count': 0, 'montant': 0}
                stats_categorie[categorie]['count'] += 1
                stats_categorie[categorie]['montant'] += float(demande['montant_total'])
            
            statistiques = {
                'total_demandes': total_demandes,
                'total_montant': total_montant,
                'stats_statut': stats_statut,
                'stats_categorie': stats_categorie
            }
            
            return jsonify({'success': True, 'statistiques': statistiques})
        else:
            return jsonify({'success': True, 'statistiques': {
                'total_demandes': 0,
                'total_montant': 0,
                'stats_statut': {},
                'stats_categorie': {}
            }})
            
    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques: {str(e)}")
        return jsonify({'success': False, 'message': f'Une erreur s\'est produite: {str(e)}'}), 500