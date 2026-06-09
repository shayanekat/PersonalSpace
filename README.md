# Personal Space

ceci est un espace personnel pour y ranger des applications développées par moi-même en python et pouvoir les lancer depuis n'importe où moyennant une connexion internet.

## Pipeline pour ajouter une app au projet

### En local

1. créer le nouveau dossier correspondant dans `./app` avec tout le necessaire
2. *(opttionnel)* ajouter un fichier python test dans le dossier créé pour s'assurer que ça fonctionne
3. dans `./app.py`, ajouter une fonction qui contient tout le code necessaire avec les decorateurs `@app.route('/<nom_app>')` et `@login_required` (prendre les autres apps existantes en exemple)
4. dans le dossier `./templates`, créer un template `<nom_app>.html` en suivant les autres templates existants comme exemple
5. dans le dossier `./static`, créer un fichier `<nom_app>.css` en respectant la palette de couleur des autres app (voir les autres css)
6. dans `./dashboard.html`, ajouter un lien vers la nouvelle app
7. faire un/des test(s) en local et corrgier les erreurs eventuelle
8. mettre à jour le fichier `./.gitignore` si besoin
9. mettre à jour `./requirements.txt` si besoin
10. pousser les modifications sur github

### Sur le serveur

1. importer les dernières modifications avec un `git pull`
2. installer les nouvelles libs python si necessaire avec `pip install -r requirements.txt`
3. relancer le site web avec `sudo systemctl restart shaykat`
4. verifier le statut du site avec `sudo systemctl status shaykat`
5. verifier que cela à bien fonctionner, et corriger les erreurs eventuelles
6. en cas d'erreur, consulter les logs avec `sudo journalctl -u shaykat -f`
