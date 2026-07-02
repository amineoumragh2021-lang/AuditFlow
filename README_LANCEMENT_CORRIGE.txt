Projet corrigé : dashboard sans champ Audit.statut

Commandes à lancer dans ce dossier (celui qui contient manage.py) :

python -m venv venv
venv\Scripts\activate
pip install "django==4.2.16" pymysql
python manage.py migrate
python manage.py seed_demo
python manage.py runserver

Important : l'inscription publique crée uniquement des comptes CLIENT.
Les RESPONSABLES et AUDITEURS sont créés par l'administrateur ou par seed_demo.
