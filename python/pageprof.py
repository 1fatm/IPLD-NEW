from supabase import create_client, Client
from flask import request, redirect, url_for, session, jsonify, flash, render_template
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import uuid

load_dotenv()
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

# Configuration pour les uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, folder):
    """Sauvegarde un fichier uploadé et retourne le chemin"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Ajouter un UUID pour éviter les conflits de noms
        filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, folder, filename)
        
        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        file.save(filepath)
        return filepath
    return None

def pageprof():
    """Fonction pour afficher la page du professeur"""
    if 'username' not in session or session.get('role') != 'professeur':
        return redirect(url_for('connexionprof_route'))
    
    # Récupérer les informations du professeur pour pré-remplir le formulaire
    try:
        prof_info = supabase.table('Professeurs').select('*').eq('email', session['username']).execute()
        if prof_info.data:
            prof_data = prof_info.data[0]
            # Formatage des données pour le template
            prof_data['nom_complet'] = f"{prof_data['prenom']} {prof_data['nom']}"
            return render_template('pageprof.html', prof_data=prof_data, session=session)
        else:
            flash('Erreur: Informations du professeur non trouvées', 'error')
            return render_template('pageprof.html', session=session)
    except Exception as e:
        print(f"Erreur lors de la récupération des données du professeur: {e}")
        flash('Erreur lors du chargement des données', 'error')
        return render_template('pageprof.html', session=session)

def creer_demande():
    """Fonction pour créer une nouvelle demande budgétaire"""
    print("=== DÉBUT CRÉATION DEMANDE ===")
    
    # Vérification de l'authentification
    if 'username' not in session or session.get('role') != 'professeur':
        print("❌ Accès non autorisé - Session:", session)
        return jsonify({'success': False, 'message': 'Accès non autorisé'}), 403
    
    # Vérifier si c'est une sauvegarde en brouillon
    is_draft = request.form.get('action') == 'brouillon'
    
    try:
        # Récupérer les informations du professeur d'abord
        email_demandeur = session.get('username')
        print(f"🔍 Recherche du professeur: {email_demandeur}")
        
        try:
            prof_info = supabase.table('Professeurs').select('*').eq('email', email_demandeur).execute()
            print(f"📊 Résultat recherche professeur: {prof_info.data}")
        except Exception as e:
            print(f"❌ Erreur lors de la recherche du professeur: {e}")
            return jsonify({'success': False, 'message': 'Erreur lors de la recherche du professeur'}), 500
        
        if not prof_info.data:
            print("❌ Professeur non trouvé")
            return jsonify({'success': False, 'message': 'Professeur non trouvé dans la base de données'}), 404
        
        # Récupérer les informations du professeur
        prof_data = prof_info.data[0]
        nom_demandeur = f"{prof_data['prenom']} {prof_data['nom']}"
        departement = prof_data['departement']
        
        print(f"✅ Professeur trouvé - Nom: {nom_demandeur}, Département: {departement}")
        
        # Récupérer les données du formulaire
        titre_demande = request.form.get('title', '').strip()
        categorie = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        montant_total = request.form.get('amount', '').strip()
        
        print(f"📝 Données reçues:")
        print(f"   - Nom: {nom_demandeur}")
        print(f"   - Email: {email_demandeur}")
        print(f"   - Département: {departement}")
        print(f"   - Titre: {titre_demande}")
        print(f"   - Catégorie: {categorie}")
        print(f"   - Description: {description}")
        print(f"   - Montant: {montant_total}")
        print(f"   - Mode: {'Brouillon' if is_draft else 'Soumission'}")
        
        # Validation des données obligatoires (seulement pour soumission)
        if not is_draft:
            if not titre_demande or not categorie or not description or not montant_total:
                print("❌ Données manquantes")
                return jsonify({'success': False, 'message': 'Tous les champs obligatoires doivent être remplis'}), 400
        
        # Conversion du montant
        try:
            montant_total = float(montant_total) if montant_total else 0
        except ValueError:
            if not is_draft:
                print("❌ Montant invalide")
                return jsonify({'success': False, 'message': 'Le montant doit être un nombre valide'}), 400
            montant_total = 0
        
        # Traiter les articles (si fournis)
        articles = []
        item_names = request.form.getlist('itemName[]')
        item_quantities = request.form.getlist('itemQuantity[]')
        item_prices = request.form.getlist('itemPrice[]')
        
        print(f"📦 Articles reçus: {len(item_names)} articles")
        
        if item_names:
            for i in range(len(item_names)):
                if (i < len(item_names) and item_names[i] and item_names[i].strip()):
                    try:
                        quantite = int(item_quantities[i]) if (i < len(item_quantities) and item_quantities[i] and item_quantities[i].strip()) else 1
                        prix_unitaire = float(item_prices[i]) if (i < len(item_prices) and item_prices[i] and item_prices[i].strip()) else 0
                        
                        article = {
                            'nom': item_names[i].strip(),
                            'quantite': quantite,
                            'prix_unitaire': prix_unitaire,
                            'prix_total': quantite * prix_unitaire
                        }
                        articles.append(article)
                        print(f"   ✅ Article {i+1}: {article}")
                    except (ValueError, IndexError) as e:
                        print(f"   ❌ Erreur article {i+1}: {e}")
                        continue
        
        # Traiter les pièces jointes (optionnel)
        pieces_jointes = []
        if 'attachments' in request.files:
            for file in request.files.getlist('attachments'):
                if file and file.filename and file.filename.strip():
                    try:
                        # Vérifier la taille du fichier
                        file.seek(0, 2)  # Aller à la fin du fichier
                        file_size = file.tell()
                        file.seek(0)  # Revenir au début
                        
                        if file_size > MAX_FILE_SIZE:
                            print(f'❌ Fichier {file.filename} trop volumineux')
                            continue
                            
                        # Sauvegarder le fichier
                        filepath = save_uploaded_file(file, 'pieces_jointes')
                        if filepath:
                            pieces_jointes.append({
                                'nom_fichier': file.filename,
                                'chemin': filepath,
                                'taille': file_size,
                                'type': file.content_type
                            })
                            print(f"📎 Pièce jointe sauvegardée: {file.filename}")
                    except Exception as e:
                        print(f"❌ Erreur pièce jointe: {e}")
                        continue
        
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
            'statut': 'brouillon' if is_draft else 'en_attente',
            'chemin_articles': json.dumps(articles) if articles else None,
            'chemin_pieces_jointes': json.dumps(pieces_jointes) if pieces_jointes else None,
            'date_creation': datetime.now().isoformat(),
            'date_modification': datetime.now().isoformat()
        }
        
        print(f"💾 Données à insérer dans la base:")
        for key, value in demande_data.items():
            if key not in ['chemin_articles', 'chemin_pieces_jointes']:
                print(f"   {key}: {value}")
            else:
                print(f"   {key}: {'Oui' if value else 'Non'}")
        
        # Insérer dans la base de données
        try:
            print("🔄 Insertion dans Supabase...")
            result = supabase.table('demandes').insert(demande_data).execute()
            print(f"📊 Résultat insertion: {result}")
            
            # Vérifier si l'insertion a réussi
            if result.data:
                print("✅ Demande créée avec succès!")
                message = 'Brouillon sauvegardé avec succès !' if is_draft else 'Demande créée avec succès ! Elle sera traitée par le chef de département.'
                return jsonify({'success': True, 'message': message})
            else:
                print(f"❌ Échec de l'insertion - Pas de données retournées")
                return jsonify({'success': False, 'message': 'Erreur lors de la création de la demande'}), 500
                
        except Exception as e:
            print(f"❌ Exception lors de l'insertion: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'message': f'Erreur de base de données: {str(e)}'}), 500
            
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Une erreur s\'est produite: {str(e)}'}), 500
    
    finally:
        print("=== FIN CRÉATION DEMANDE ===")

def sauvegarder_brouillon():
    """Fonction pour sauvegarder une demande en brouillon"""
    # Ajouter un indicateur pour le brouillon dans les données du formulaire
    from werkzeug.datastructures import MultiDict
    
    # Créer une nouvelle forme de données avec l'indicateur brouillon
    form_data = MultiDict(request.form)
    form_data['action'] = 'brouillon'
    
    # Temporairement remplacer request.form
    original_form = request.form
    request.form = form_data
    
    try:
        result = creer_demande()
        return result
    finally:
        # Restaurer le formulaire original
        request.form = original_form

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
                # Formater la date
                date_creation = demande['date_creation']
                if 'T' in date_creation:
                    date_creation = date_creation.split('T')[0]
                
                # Mapper les statuts pour l'affichage
                statut_display = {
                    'brouillon': 'Brouillon',
                    'en_attente': 'En attente',
                    'approuve_chef': 'Approuvé par le chef',
                    'rejete_chef': 'Rejeté par le chef',
                    'approuve_direction': 'Approuvé par la direction',
                    'rejete_direction': 'Rejeté par la direction',
                    'finalise': 'Finalisé'
                }.get(demande['statut'], demande['statut'])
                
                demandes.append({
                    'id': demande['id'],
                    'titre_demande': demande['titre_demande'],
                    'categorie': demande['categorie'],
                    'montant_total': demande['montant_total'],
                    'statut': demande['statut'],
                    'statut_display': statut_display,
                    'date_creation': date_creation,
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