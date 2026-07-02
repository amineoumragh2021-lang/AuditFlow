# Modifications finales AuditFlow

## Fonctionnel

- L'inscription publique crée uniquement un compte **Client**.
- Les rôles **Responsable Audit** et **Auditeur** sont créés par le responsable/admin depuis la gestion des utilisateurs ou via `seed_demo`.
- Le champ **statut** de l'audit est supprimé.
- Les réponses de checklist ne sont plus des cases cochées : chaque point accepte **Conforme**, **Non conforme** ou **Abordable**.
- Les types d'audit sont : **Qualité**, **Sécurité**, **Environnement**, **Interne**.
- Chaque type possède 40 questions professionnelles dans la commande `seed_demo`.
- Le calendrier est personnel : client, auditeur et responsable voient les audits selon leur rôle.

## Commandes utiles

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Comptes de test créés par seed_demo

- responsable@audit.com / 123456
- auditeur@audit.com / 123456
- client@audit.com / 123456
