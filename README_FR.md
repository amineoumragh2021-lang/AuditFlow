# AuditPro PFA — Version TailwindCSS avancée

Application web Django pour la gestion des audits industriels avec :

- Rôles : Responsable Audit, Auditeur, Client
- Inscription et connexion
- Planification des audits
- Affectation client + auditeur
- Checklists par type d'audit
- 180 points de checklist de démonstration
- Rapports avec score de conformité
- Interface TailwindCSS avancée avec animations, cartes glassmorphism, compteurs animés et responsive mobile
- Base de données MySQL via XAMPP

## Installation

1. Démarrer MySQL dans XAMPP.
2. Créer la base dans phpMyAdmin :

```sql
CREATE DATABASE audit_pfa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. Ouvrir le dossier qui contient `manage.py` dans VS Code.
4. Installer les dépendances :

```powershell
pip install -r requirements.txt
```

5. Créer les tables et les données de test :

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
```

6. Lancer le serveur :

```powershell
python manage.py runserver
```

Ouvrir :

```text
http://127.0.0.1:8000
```

## Lancer sur iPhone dans le même Wi-Fi

Lance le serveur comme ceci :

```powershell
python manage.py runserver 0.0.0.0:8000
```

Puis ouvre Safari avec l'adresse IP du PC, par exemple :

```text
http://192.168.1.101:8000
```

Si ton IP change, ajoute-la dans `config/settings.py`, dans `CSRF_TRUSTED_ORIGINS`.

## Comptes de test

```text
Responsable Audit : responsable@audit.com / 123456
Auditeur : auditeur@audit.com / 123456
Client : client@audit.com / 123456
```

