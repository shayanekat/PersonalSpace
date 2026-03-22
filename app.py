"""
    Shayane KATCHERA
    test de Flask pour créer un espace personnel protégé par mot de passe.
"""

import os
from functools import wraps

import werkzeug.security
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flask import (Flask, redirect, render_template, render_template_string,
                   request, session, url_for)

load_dotenv()  # Charge les variables du fichier .env

# Création de l'application Flask
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
EDITOR_FOLDER = os.path.join(app.root_path, 'apps', 'editor')

# Mot de passe que tu définis toi-même
PASSWORD_HASH = os.getenv("PASSWORD_HASH")


def get_text_files():
    os.makedirs(EDITOR_FOLDER, exist_ok=True)
    return sorted(
        file_name
        for file_name in os.listdir(EDITOR_FOLDER)
        if file_name.endswith('.txt')
    )


def get_selected_file(files, requested_name=None):
    if not files:
        return None
    if requested_name in files:
        return requested_name
    return files[0]

# decorateur pour vérifier si l'utilisateur est connecté
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# Page de connexion (formulaire)
with open('login.html', 'r') as file:
    login_page = file.read()

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form['password']
        if PASSWORD_HASH and werkzeug.security.check_password_hash(PASSWORD_HASH, password):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            error = "Mot de passe incorrect."
    return render_template_string(login_page, error=error)


@app.route('/dashboard')
@login_required
def dashboard():
    with open('dashboard.html', 'r') as file:
        dashboard_page = file.read()
    return render_template_string(dashboard_page)


@app.route('/texteditor', methods=['GET', 'POST'])
@login_required
def texteditor():
    files = get_text_files()
    selected = get_selected_file(files, request.args.get('file'))

    message = None

    # Sauvegarde
    if request.method == 'POST':
        selected = get_selected_file(files, request.form.get('file'))
        content = request.form.get('content', '')

        if selected:
            with open(os.path.join(EDITOR_FOLDER, selected), 'w', encoding='utf-8') as f:
                f.write(content)

            message = "Sauvegardé"
        else:
            message = "Crée d'abord un onglet"

    # Lecture du fichier sélectionné
    content = ""
    if selected:
        with open(os.path.join(EDITOR_FOLDER, selected), 'r', encoding='utf-8') as f:
            content = f.read()

    return render_template(
        'texteditor.html',
        files=files,
        selected=selected,
        content=content,
        message=message
    )


@app.route('/create_file', methods=['POST'])
@login_required
def create_file():
    raw_name = request.form.get('name', '').strip()
    name = secure_filename(raw_name)

    if not name:
        files = get_text_files()
        selected = get_selected_file(files)
        content = ""
        if selected:
            with open(os.path.join(EDITOR_FOLDER, selected), 'r', encoding='utf-8') as f:
                content = f.read()

        return render_template(
            'texteditor.html',
            files=files,
            selected=selected,
            content=content,
            message="Nom d'onglet invalide"
        )

    if not name.endswith('.txt'):
        name += '.txt'

    path = os.path.join(EDITOR_FOLDER, name)

    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8'):
            pass

    return redirect(url_for('texteditor', file=name))


@app.route('/delete_file', methods=['POST'])
@login_required
def delete_file():
    files = get_text_files()
    name = get_selected_file(files, request.form.get('file'))

    if not name:
        return redirect(url_for('texteditor'))

    path = os.path.join(EDITOR_FOLDER, name)

    if os.path.exists(path):
        os.remove(path)

    remaining_files = get_text_files()
    next_file = get_selected_file(remaining_files)
    if next_file:
        return redirect(url_for('texteditor', file=next_file))
    return redirect(url_for('texteditor'))


@app.route('/app2')
@login_required
def app2():
    return "<h3>Ceci est ton application 2 (à coder plus tard)</h3>"

if __name__ == '__main__':
    app.run(debug=True)
