# Modification de la base de données

Changements appliqués :

1. Le champ `statut` a été supprimé du modèle `Audit`.
2. Les réponses checklist utilisent maintenant uniquement :
   - `CONFORME` = Conforme
   - `NON_CONFORME` = Non conforme
   - `ABORDABLE` = Abordable
3. L’inscription permet de créer les rôles : Client, Responsable Audit et Auditeur.
4. Le calendrier affiche les audits selon le rôle connecté :
   - Client : ses audits
   - Auditeur : ses audits affectés
   - Responsable : tous les audits

## Commandes à lancer après extraction

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Si tu veux repartir avec une base propre dans XAMPP/MySQL :

```sql
DROP DATABASE IF EXISTS audit_pfa_db;
CREATE DATABASE audit_pfa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Puis lance :

```bash
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```
