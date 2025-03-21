# Utiliser une image de base Python
FROM python:3.11-slim


# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers nécessaires
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port utilisé par l'application
EXPOSE 5000

# Commande pour lancer l'application
CMD ["python", "app.py"]