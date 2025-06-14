"""
    Shayane KATCHERA
    test de Flask pour créer un espace personnel protégé par mot de passe.
"""

from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)

# Mot de passe que tu définis toi-même
PASSWORD = "monmotdepasse"

# Page de connexion (formulaire)
with open('login.html', 'r') as file:
    login_page = file.read()

# Page personnelle (ton espace)
dashboard_page = '''
<!DOCTYPE html>
<html>
<head><title>Espace Personnel</title></head>
<body>
    <h2>Bienvenue dans ton espace personnel !</h2>
    <ul>
        <li><a href="/app1">Application 1</a></li>
        <li><a href="/app2">Application 2</a></li>
    </ul>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form['password']
        if password == PASSWORD:
            return redirect(url_for('dashboard'))
        else:
            error = "Mot de passe incorrect."
    return render_template_string(login_page, error=error)

@app.route('/dashboard')
def dashboard():
    return render_template_string(dashboard_page)

@app.route('/app1')
def app1():
    return "<h3>Ceci est ton application 1 (à coder plus tard)</h3>"

@app.route('/app2')
def app2():
    return "<h3>Ceci est ton application 2 (à coder plus tard)</h3>"

if __name__ == '__main__':
    app.run(debug=True)
