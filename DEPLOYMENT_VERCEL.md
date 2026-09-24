# Déployer AuditFlow sur Vercel depuis GitHub

## Analyse effectuée avant modification

- Racine Git : ce dossier, celui contenant `manage.py`, `requirements.txt`, `audit/` et `config/`. Le dépôt configuré est `https://github.com/amineoumragh2021-lang/AuditFlow.git`, branche `main`.
- Projet Django : `config`. `manage.py` utilise `config.settings`, `ROOT_URLCONF` vaut `config.urls`, et `WSGI_APPLICATION` vaut `config.wsgi.application`. Les fichiers WSGI et ASGI existants sont standards. Ils sont conservés, comme les routes.
- Application métier : `audit`. Les formulaires écrivent les utilisateurs, profils, missions, rapports, réponses, constats, risques et actions. L’authentification écrit des sessions. Ce n’est donc pas une démonstration en lecture seule.
- SQLite existant contient notamment 5 utilisateurs, 2 audits, 1 rapport, 160 points de checklist et 40 réponses. Aucun transfert, remplacement ou nettoyage de ces données n’a été effectué.
- Les cinq migrations `audit/0001` à `audit/0005` existent et sont appliquées localement. Elles utilisent les opérations Django, sans SQL spécifique à SQLite. Aucune nouvelle migration métier n’est nécessaire.
- Les documents utilisent `FileField` et `private_uploads/`. Ce dossier ne peut pas être un stockage persistant sur Vercel : un backend privé compatible S3 est configuré pour la production.
- Statiques : 3 CSS, 2 JavaScript propres au projet ; les icônes et graphiques sont des SVG intégrés aux templates. Aucun fichier image local manquant n’a été trouvé. Tailwind CDN et Google Fonts utilisent HTTPS ; ces dépendances externes existantes sont conservées.
- Aucun `.gitignore`, `vercel.json`, `render.yaml`, `Procfile` ou script de build Render n’existait. Seuls un commentaire et les anciens domaines autorisés faisaient référence à Render.
- `create_db.py` et `database_setup.sql` sont d’anciens outils MySQL, non utilisés par Django. Le générateur PowerPoint est également indépendant de l’application web.
- Une faute `xfrom` au début de `audit/views.py` empêchait tout démarrage. Seul ce caractère superflu est corrigé dans ce fichier.

## Méthode Vercel retenue

Vercel détecte Django à partir des dépendances, de `manage.py` et de `WSGI_APPLICATION`. Le point d’entrée existant `config/wsgi.py:application` suffit. Aucun `api/index.py`, aucune réécriture de routes et aucun `vercel.json` ne sont nécessaires ici.

`.python-version` sélectionne Python 3.12. `requirements.txt` utilise Django 5.2 LTS et contient les dépendances réellement utilisées par le web. Les outils PowerPoint, MySQL et Gunicorn sont disponibles séparément dans `requirements-tools.txt`.

La plateforme exécute automatiquement `collectstatic` lorsque `STATIC_ROOT` est configuré, puis sert les fichiers sous `/static/` depuis son CDN. `STORAGES['staticfiles']` utilise WhiteNoise avec manifeste et compression ; l’ancien `STATICFILES_STORAGE` a été remplacé. WhiteNoise reste utilisable hors Vercel.

Sources officielles vérifiées : [Django sur Vercel](https://vercel.com/docs/frameworks/full-stack/django), [runtime Python](https://vercel.com/docs/functions/runtimes/python), [WhiteNoise](https://whitenoise.readthedocs.io/en/stable/django.html), [django-storages S3](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html).

## Variables Vercel : liste exacte

Ajouter ces variables dans **Settings → Environment Variables** pour **Production**. Pour les previews, utiliser une base et un bucket distincts ou une branche Neon isolée.

| Variable | Valeur à fournir |
| --- | --- |
| `SECRET_KEY` | Nouvelle chaîne aléatoire d’au moins 50 caractères ; ne jamais réutiliser l’ancienne clé du dépôt. |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | Domaine exact, sans protocole, ex. `auditflow-votre-nom.vercel.app`. Plusieurs domaines séparés par des virgules. |
| `CSRF_TRUSTED_ORIGINS` | Origine HTTPS exacte, ex. `https://auditflow-votre-nom.vercel.app`. Plusieurs origines séparées par des virgules. |
| `DATABASE_URL` | URL PostgreSQL Neon avec `sslmode=require`, de préférence l’URL poolée pour l’application. |
| `AWS_STORAGE_BUCKET_NAME` | Nom d’un bucket **privé**, ex. `auditflow-documents`. |
| `AWS_S3_ENDPOINT_URL` | Endpoint S3 HTTPS affiché par le fournisseur. Pour Supabase : `https://REFERENCE.storage.supabase.co/storage/v1/s3`. |
| `AWS_S3_REGION_NAME` | Région affichée par la configuration S3 du fournisseur. |
| `AWS_ACCESS_KEY_ID` | Identifiant d’accès S3, uniquement côté serveur. |
| `AWS_SECRET_ACCESS_KEY` | Secret S3, uniquement côté serveur. |

Les exemples de `.env.example` sont fictifs. Ne pas les utiliser tels quels en production. Générer la clé avec :

```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Vercel fournit automatiquement `VERCEL`, `VERCEL_URL`, `VERCEL_BRANCH_URL` et `VERCEL_PROJECT_PRODUCTION_URL`. Garder activée l’exposition des variables système dans les paramètres du projet. Le code ajoute ces domaines précis aux listes autorisées, sans autoriser tous les sites `*.vercel.app`.

En production, une variable essentielle absente provoque une erreur explicite. Aucun repli vers une base SQLite ou des documents éphémères n’est effectué sur Vercel. Les cookies sécurisés, la redirection HTTPS et les en-têtes HSTS sont actifs ; les en-têtes du proxy Vercel sont pris en compte.

## Base de données et documents persistants

1. Créer un projet Neon gratuit, directement chez Neon ou via le Marketplace Vercel. Choisir une région proche de l’application.
2. Copier l’URL PostgreSQL poolée dans `DATABASE_URL` sur Vercel. Le code utilise des connexions courtes, désactive les curseurs serveur et les prepared statements pour être compatible avec le pooler.
3. Créer un projet Supabase gratuit pour les fichiers, puis un bucket Storage **privé** nommé par exemple `auditflow-documents`. Ne pas rendre le bucket public.
4. Dans la configuration S3 de Supabase, générer les clés S3 et copier l’endpoint et la région. Renseigner les cinq variables `AWS_*` dans Vercel. Ce sont des clés S3, pas la clé publique `anon`.
5. Les téléchargements restent protégés par les contrôles Django existants. Le backend S3 ne change ni les écrans ni les règles métier.

Sources : [Neon et Django](https://neon.com/docs/guides/django), [authentification S3 Supabase](https://supabase.com/docs/guides/storage/s3/authentication), [quota gratuit Storage](https://supabase.com/docs/guides/storage/pricing).

Les requêtes d’upload passant par Django restent soumises aux limites de corps HTTP de Vercel. Pour ce déploiement, utiliser de petites pièces jointes (moins de 4 Mo, en laissant de la place au formulaire). Les gros uploads nécessiteraient ultérieurement un flux direct vers le stockage ; ce changement fonctionnel n’a pas été introduit. Voir les [limites Vercel Functions](https://vercel.com/docs/functions/limitations).

## Initialiser Neon depuis l’ordinateur

Ne pas lancer les migrations au démarrage de chaque requête ni automatiquement contre la production depuis les builds de preview.

Dans PowerShell, depuis ce dossier, utiliser un Python 3.12 avec les dépendances installées. Pour cette copie du projet, le runtime isolé créé pendant la vérification est disponible :

```powershell
$auditPython = (Resolve-Path '.deployment-check/python/python.exe').Path
$env:DEBUG = 'True'
```

Sur une autre machine avec Python 3.12 installé :

```powershell
py -3.12 -m venv .venv
$auditPython = (Resolve-Path '.venv/Scripts/python.exe').Path
& $auditPython -m pip install -r requirements.txt
$env:DEBUG = 'True'
```

Créer manuellement `.env.neon` (ignoré par Git) contenant uniquement `DATABASE_URL=...` avec l’URL **directe**, non poolée, de la base Neon cible, en conservant `sslmode=require`. Ne jamais coller cette URL dans une commande Git.

```powershell
& $auditPython -m dotenv -f .env.neon run -- $auditPython manage.py migrate --plan
& $auditPython -m dotenv -f .env.neon run -- $auditPython manage.py migrate --noinput
& $auditPython -m dotenv -f .env.neon run -- $auditPython manage.py migrate --check
```

Ces commandes utilisent explicitement Neon ; elles ne touchent pas `db.sqlite3`. Elles doivent être exécutées une fois avant la mise en service, puis après chaque ajout de migration.

Pour une base vide, créer un compte responsable :

```powershell
& $auditPython -m dotenv -f .env.neon run -- $auditPython manage.py createsuperuser --username admin
& $auditPython -m dotenv -f .env.neon run -- $auditPython manage.py shell -c "from django.contrib.auth.models import User; from audit.models import Profile; Profile.objects.update_or_create(user=User.objects.get(username='admin'), defaults={'role':'RESPONSABLE'})"
```

Le mot de passe est demandé interactivement. La connexion AuditFlow utilise l’adresse email saisie lors de la création. Aucun `seed_demo` automatique et aucun compte à mot de passe public ne sont créés.

### Transférer les données existantes, si souhaité

Le déploiement ne copie pas automatiquement SQLite vers PostgreSQL. La base locale est conservée. Pour transférer son contenu, utiliser une **base Neon vide** après migration, avant de créer des comptes portant les mêmes noms.

Vérifier que `.env` contient `DATABASE_URL=` vide :

```powershell
New-Item -ItemType Directory -Force data-exports | Out-Null
& $auditPython -m dotenv -f .env run -- $auditPython manage.py dumpdata auth.user auth.group audit --natural-foreign --natural-primary --output data-exports/auditflow.json
& $auditPython -m dotenv -f .env.neon run -- $auditPython manage.py loaddata data-exports/auditflow.json
```

Ne pas importer ce fichier dans une base contenant déjà des données métier : des identifiants pourraient entrer en conflit. Les sessions ne sont pas transférées. Le fichier d’export contient des données privées et reste ignoré par Git. Si des comptes de démonstration sont importés, changer leurs mots de passe avant publication.

Lors de l’analyse, aucun document n’était enregistré. Si des documents sont ajoutés avant le transfert, copier également les fichiers de `private_uploads/` vers le bucket privé **en conservant leurs chemins relatifs** (`audit_documents/...`) : `dumpdata` ne transfère que les noms des fichiers.

## Envoyer sur GitHub : commandes à exécuter vous-même

Le dépôt est déjà sur `main` et `origin` est configuré. Aucun commit ni push n’a été fait par l’assistant. Le retrait de `db.sqlite3` et des caches du suivi est déjà préparé dans l’index Git, avec les fichiers conservés sur disque.

Les commandes ci-dessous incluent les fichiers métier et statiques de la version actuelle, dont certains n’étaient pas encore suivis par Git. Les examiner avant de valider le commit.

```powershell
Set-Location 'C:\Users\amine\Desktop\AuditFlow_CORRIGE_Date_Rapport_Modifier\audit_pfa2004_corrige_sans_statut'
git status --short
git branch --show-current
git add -- .gitignore .vercelignore .python-version .env.example requirements.txt requirements-tools.txt DEPLOYMENT_VERCEL.md README_GOUVERNANCE.md audit config static templates
git diff --cached --stat
git diff --cached --check
git diff --cached --name-only
git commit -m "Prepare AuditFlow for Vercel with PostgreSQL and private storage"
git push origin main
```

Exécuter `git commit` seulement après validation du contenu préparé. Ne pas utiliser de push forcé. Les chemins `.env`, `.env.neon`, `.venv*`, `.deployment-check`, `private_uploads`, `data-exports`, SQLite et ses sauvegardes ne doivent pas figurer comme ajouts.

Le retrait du suivi ne purge pas les anciennes versions de SQLite ou de la clé Django déjà présentes dans l’historique distant. La nouvelle clé de production doit être différente ; aucune réécriture de l’historique n’a été effectuée.

## Réglages précis dans Vercel

1. Choisir un compte **Hobby** si le projet est personnel/non commercial et respecte les quotas gratuits.
2. **Add New → Project → Import Git Repository**, puis sélectionner `amineoumragh2021-lang/AuditFlow`.
3. **Root Directory** : `./` pour ce dépôt, car `manage.py` est à sa racine Git. Ne pas saisir le nom du dossier Windows. Si vous créez un autre dépôt englobant le dossier parent, choisir alors le sous-dossier qui contient `manage.py`.
4. **Framework Preset** : **Django**. Si un ancien projet Vercel existe, retirer ses anciens overrides et vérifier ce preset.
5. Laisser **Install Command**, **Build Command** et **Output Directory** aux valeurs par défaut. Ne pas utiliser Gunicorn, `runserver`, un dossier `api`, ou la sortie d’un site statique.
6. Ajouter les dix variables listées plus haut. Ne pas copier `.env` vers GitHub. Vérifier le domaine Vercel retenu pour `ALLOWED_HOSTS` et `CSRF_TRUSTED_ORIGINS`.
7. Initialiser Neon avec les commandes précédentes. Ne pas connecter les previews à la base de production par défaut.
8. Cliquer **Deploy**. Les logs doivent montrer l’installation Python/Django et `collectstatic`. En cas de configuration manquante, corriger la variable indiquée puis relancer le déploiement.
9. Dans **Settings → Git**, vérifier **Production Branch = main**. Les prochains pushs autorisés vers `main` déclencheront les déploiements.
10. Vérifier en HTTPS : connexion, tableau de bord, création/modification d’une mission, export PDF, dépôt/téléchargement d’un petit document, CSS et JavaScript sans 404, puis relecture des données après un redéploiement.

Vercel Hobby est destiné aux usages personnels et non commerciaux. Neon et Supabase offrent des quotas gratuits, qui ne garantissent pas un service illimité. Sources : [Vercel Hobby](https://vercel.com/docs/plans/hobby), [Neon Free](https://neon.com/pricing), [Supabase Storage](https://supabase.com/docs/guides/storage/pricing).

## Fonctionnement local

La configuration charge `.env.local`, puis `.env`, sans écraser les variables du processus. Un `.env` local privé a été créé avec une nouvelle clé, `DEBUG=True` et `DATABASE_URL=` vide. La rotation de cette clé peut demander une nouvelle connexion aux sessions locales existantes.

Dans l’environnement de vérification, une variable système `DEBUG=release` était déjà présente. Elle n’est pas une valeur Django valide ; la définir à `True` dans le terminal local, sans changer les variables globales de Windows.

```powershell
$auditPython = (Resolve-Path '.deployment-check/python/python.exe').Path
$env:DEBUG = 'True'
& $auditPython manage.py check
& $auditPython manage.py runserver 127.0.0.1:8000 --noreload
```

Pour une nouvelle copie, créer un `.env` privé contenant une clé générée, `DEBUG=True` et `DATABASE_URL=` vide. Aucun réglage S3 n’est nécessaire en local. Ne pas recopier les valeurs fictives de production de `.env.example` sans les adapter.

## Vérifications exécutées

- Python 3.12.10 isolé, Django 5.2.17 ; installation complète et `pip check` sans conflit.
- Paquets binaires et dépendances résolus pour Python 3.12 / Linux x86_64, notamment Pillow et psycopg.
- `manage.py check` : aucun problème.
- `showmigrations audit` : les cinq migrations appliquées.
- `makemigrations --check --dry-run` : aucune modification de schéma requise.
- `migrate --check` : aucune migration en attente sur SQLite.
- Les tests créent une base SQLite temporaire et y exécutent les migrations depuis zéro.
- `collectstatic --noinput` : 132 fichiers collectés, 396 traitements de manifeste/compression.
- Les cinq assets du projet ont une URL avec empreinte dans le manifeste de production.
- `manage.py test` : 19 tests réussis, dont 6 nouveaux tests de configuration de déploiement.
- `check --deploy --fail-level WARNING` avec configuration Vercel fictive complète : aucun avertissement. Le pilote PostgreSQL et le backend S3 se chargent correctement.
- Imports WSGI et ASGI réussis ; génération réelle d’un PDF existant réussie sans modifier les données.
- Démarrage local sous Python 3.12 : `/login/` et `/static/audit/css/theme.css` répondent HTTP 200 sur `http://127.0.0.1:8000`.
- Empreinte SHA-256 de `db.sqlite3` identique avant et après les vérifications. Les empreintes des templates, statiques, modèles métier et migrations sont également inchangées.

Les services Neon/Supabase et un build distant Vercel ne sont pas testés sans vos comptes et identifiants. Cette préparation n’est pas un déploiement déjà effectué. Les tests de configuration utilisent des valeurs fictives et n’ouvrent aucune connexion vers ces services.

## Fichiers concernés par cette adaptation

Modifiés : `requirements.txt`, `config/settings.py`, `audit/views.py` (uniquement la faute de syntaxe).

Créés et destinés à Git : `.gitignore`, `.vercelignore`, `.python-version`, `.env.example`, `requirements-tools.txt`, `config/test_deployment.py`, `DEPLOYMENT_VERCEL.md`.

Créés localement, exclus de Git : `.env`, `.deployment-check/` (runtime et paquets de vérification), `staticfiles/` (sortie générée).

Retirés **uniquement du suivi Git**, conservés sur disque :

```text
db.sqlite3
audit/__pycache__/__init__.cpython-313.pyc
audit/__pycache__/decorators.cpython-313.pyc
audit/__pycache__/forms.cpython-313.pyc
audit/__pycache__/models.cpython-313.pyc
audit/__pycache__/urls.cpython-313.pyc
audit/__pycache__/views.cpython-313.pyc
audit/management/__pycache__/__init__.cpython-313.pyc
audit/management/commands/__pycache__/__init__.cpython-313.pyc
audit/management/commands/__pycache__/seed_demo.cpython-313.pyc
audit/migrations/__pycache__/0001_initial.cpython-313.pyc
audit/migrations/__pycache__/0002_remove_checklistresponse_est_conforme_and_more.cpython-313.pyc
audit/migrations/__pycache__/0003_remove_audit_statut_abordable.cpython-313.pyc
audit/migrations/__pycache__/0004_audit_types_client_register.cpython-313.pyc
audit/migrations/__pycache__/__init__.cpython-313.pyc
config/__pycache__/__init__.cpython-313.pyc
config/__pycache__/settings.cpython-313.pyc
config/__pycache__/urls.cpython-313.pyc
config/__pycache__/wsgi.cpython-313.pyc
```

Les autres modifications affichées par `git status` existaient avant cette demande. Les templates, le design, les modèles métier, les migrations, les routes et les données métier n’ont pas été modifiés par cette adaptation.
