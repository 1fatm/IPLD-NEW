from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

def ask_ollama(question):
    # Prompt pour guider le modèle
    prompt = f"""
    Tu es un assistant pédagogique spécialisé dans les examens. 
    Tu ne réponds qu'aux questions en rapport avec les examens, les corrections, les notes, ou les sujets d'étude. 
    Si la question n'est pas liée à ces sujets, réponds : 'Je ne peux répondre qu'à des questions en rapport avec les examens.'

    Question : {question}
    """

    # Appel à Ollama via la ligne de commande
    result = subprocess.run(
        ["ollama", "run", "gemma3:1b", prompt],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    question = data.get('question', '')

    if not question:
        return jsonify({"error": "Aucune question fournie"}), 400

    response = ask_ollama(question)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)