from flask import Flask

app = Flask(__name__)
app.secret_key = 'yourlove'

from python import routes, authentification,pageprof,Fonctions  # En bas pour éviter les imports circulaires
