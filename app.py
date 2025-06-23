"""
    Shayane KATCHERA
    test de Flask pour créer un espace personnel protégé par mot de passe.
"""

import hashlib
import os

import werkzeug.security
from dotenv import load_dotenv
from flask import (Flask, redirect, render_template, render_template_string,
                   request, session, url_for)

load_dotenv()  # Charge les variables du fichier .env

app = Flask(__name__)

# Mot de passe que tu définis toi-même
PASSWORD_HASH = os.getenv("PASSWORD_HASH")

# Page de connexion (formulaire)
with open('login.html', 'r') as file:
    login_page = file.read()

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form['password']
        if werkzeug.security.check_password_hash(PASSWORD_HASH, password):
            return redirect(url_for('dashboard'))
        else:
            error = "Mot de passe incorrect."
    return render_template_string(login_page, error=error)


@app.route('/dashboard')
def dashboard():
    with open('dashboard.html', 'r') as file:
        dashboard_page = file.read()
    return render_template_string(dashboard_page)

@app.route('/texteditor', methods=['GET', 'POST'])
def app1():
    file_path = 'apps/editor/note.txt'
    message = None

    if request.method == 'POST':
        content = request.form['content']
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        message = "✔️ Fichier sauvegardé avec succès."

    # Lire le fichier à chaque affichage
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    return render_template('app1_editor.html', content=content, message=message)


@app.route('/app2')
def app2():
    return "<h3>Ceci est ton application 2 (à coder plus tard)</h3>"

if __name__ == '__main__':
    app.run(debug=True)
