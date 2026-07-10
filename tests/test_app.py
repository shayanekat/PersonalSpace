import importlib.util
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

# On charge dynamiquement le fichier app.py comme un module Python.
# Cela permet d'importer l'application Flask sans avoir à modifier PYTHONPATH.
APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
spec = importlib.util.spec_from_file_location("app_module", APP_PATH)
app_module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(app_module)


@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    Fixture pytest qui crée un client de test Flask.

    - tmp_path : dossier temporaire propre à chaque test
    - monkeypatch : permet de modifier des variables du module pendant le test

    On redéfinit EDITOR_FOLDER pour que l'app écrive dans tmp_path
    (évite de polluer le vrai système de fichiers).

    On active TESTING=True pour que Flask ne gère pas les erreurs comme en prod.

    test_client() crée un client HTTP simulé pour appeler les routes Flask.
    """
    monkeypatch.setattr(app_module, "EDITOR_FOLDER", str(tmp_path))
    app_module.app.config.update(TESTING=True, SECRET_KEY="test-secret")
    with app_module.app.test_client() as test_client:
        yield test_client


def authenticate(client):
    """
    Fonction utilitaire pour simuler un utilisateur connecté.
    On modifie la session Flask directement via session_transaction().
    """
    with client.session_transaction() as session:
        session["logged_in"] = True


def test_get_text_files_filters_and_sorts(tmp_path, monkeypatch):
    """
    Test de la fonction get_text_files() :
    - crée des fichiers dans tmp_path
    - monkeypatch redéfinit EDITOR_FOLDER pour pointer vers tmp_path
    - vérifie que la fonction :
        * ignore les fichiers non .txt
        * trie les noms par ordre alphabétique
    """
    monkeypatch.setattr(app_module, "EDITOR_FOLDER", str(tmp_path))
    (tmp_path / "b.txt").write_text("", encoding="utf-8")
    (tmp_path / "a.txt").write_text("", encoding="utf-8")
    (tmp_path / "ignore.md").write_text("", encoding="utf-8")

    files = app_module.get_text_files()

    assert files == ["a.txt", "b.txt"]


def test_get_selected_file_returns_requested_or_first():
    """
    Test de get_selected_file():
    - si le fichier demandé existe → on le retourne
    - sinon → on retourne le premier fichier de la liste
    - si la liste est vide → on retourne None
    """
    files = ["a.txt", "b.txt"]

    assert app_module.get_selected_file(files, "b.txt") == "b.txt"
    assert app_module.get_selected_file(files, "missing.txt") == "a.txt"
    assert app_module.get_selected_file([], "b.txt") is None


def test_protected_route_redirects_when_not_logged_in(client):
    """
    Test d'une route protégée (dashboard) :
    - sans session logged_in → l'utilisateur doit être redirigé
    - Flask renvoie un 302 + Location vers "/"
    """
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_sets_session_on_success(client, monkeypatch):
    """
    Test du login :
    - monkeypatch remplace PASSWORD_HASH par un hash connu
    - on envoie le bon mot de passe
    - on doit être redirigé vers /dashboard
    - la session doit contenir logged_in=True
    """
    monkeypatch.setattr(app_module, "PASSWORD_HASH", generate_password_hash("secret"))

    response = client.post("/", data={"password": "secret"})

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with client.session_transaction() as session:
        assert session["logged_in"] is True


def test_login_returns_error_on_wrong_password(client, monkeypatch):
    """
    Même test que précédemment, mais avec un mauvais mot de passe.
    - la page ne redirige pas
    - elle renvoie un message d'erreur dans le HTML
    """
    monkeypatch.setattr(app_module, "PASSWORD_HASH", generate_password_hash("secret"))

    response = client.post("/", data={"password": "wrong"})

    assert response.status_code == 200
    assert "Mot de passe incorrect." in response.get_data(as_text=True)


def test_create_file_sanitizes_name_and_creates_txt(client, tmp_path):
    """
    Test de création de fichier :
    - simulate login
    - envoie un nom avec espaces → doit être transformé en "Mon_Fichier.txt"
    - vérifie :
        * redirection vers l'éditeur avec le bon nom
        * existence du fichier sur disque
    """
    authenticate(client)

    response = client.post("/create_file", data={"name": "Mon Fichier"})

    created_file = Path(tmp_path) / "Mon_Fichier.txt"
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/texteditor?file=Mon_Fichier.txt")
    assert created_file.exists()


def test_create_file_returns_validation_message_for_invalid_name(client):
    """
    Test validation du nom de fichier :
    - simulate login
    - envoie un nom vide ou invalide
    - la route doit renvoyer la page du formulaire avec un message
    - aucun fichier ne doit être créé
    """
    authenticate(client)

    response = client.post("/create_file", data={"name": "   "})

    assert response.status_code == 200
    assert "editor-form" in response.get_data(as_text=True)
    assert app_module.get_text_files() == []


def test_texteditor_post_saves_file_content(client, tmp_path):
    """
    Test de sauvegarde dans l'éditeur :
    - simulate login
    - crée un fichier notes.txt avec contenu "before"
    - POST vers /texteditor avec nouveau contenu
    - vérifie :
        * le fichier est mis à jour
        * la page contient le message "Sauvegardé"
    """
    authenticate(client)
    file_path = Path(tmp_path) / "notes.txt"
    file_path.write_text("before", encoding="utf-8")

    response = client.post("/texteditor", data={"file": "notes.txt", "content": "after"})

    assert response.status_code == 200
    assert file_path.read_text(encoding="utf-8") == "after"
    assert "Sauvegardé" in response.get_data(as_text=True)


def test_delete_file_removes_file_and_redirects_to_remaining_one(client, tmp_path):
    """
    Test de suppression de fichier :
    - simulate login
    - crée deux fichiers a.txt et b.txt
    - supprime a.txt via POST
    - vérifie :
        * redirection vers l'éditeur du fichier restant
        * a.txt n'existe plus
        * b.txt existe toujours
    """
    authenticate(client)
    file_a = Path(tmp_path) / "a.txt"
    file_b = Path(tmp_path) / "b.txt"
    file_a.write_text("", encoding="utf-8")
    file_b.write_text("", encoding="utf-8")

    response = client.post("/delete_file", data={"file": "a.txt"})

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/texteditor?file=b.txt")
    assert not file_a.exists()
    assert file_b.exists()
