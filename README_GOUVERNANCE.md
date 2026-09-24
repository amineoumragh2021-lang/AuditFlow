# Espace de gouvernance AuditFlow

Le tableau de bord reprend les sections de la maquette avec les données de l’application.

## Utilisation

1. Dans **Paramètres**, un responsable peut créer les organisations et départements.
2. Dans **Missions → Modifier**, renseigner l’organisation, le département, l’échéance, l’étape, le risque et la progression.
3. Dans **Constats**, créer les constats et choisir leur gravité. Le champ « Résolu » permet de les clôturer.
4. Dans **Risques**, évaluer impact et probabilité de 1 à 5 et associer les constats de la même mission. La gravité est calculée à partir du produit : critique ≥ 20, élevé ≥ 12, modéré ≥ 6, faible sinon. La taille des bulles dépend du nombre de constats associés.
5. Dans **Actions correctives**, choisir une échéance, un responsable et un état : ouverte, en cours, preuve attendue ou terminée. La description peut contenir la justification et les références aux preuves.
6. Dans **Documents**, déposer les pièces d’une mission. Leur téléchargement nécessite un compte autorisé à consulter la mission.

Les filtres organisation, trimestre et recherche globale s’appliquent au tableau de bord et à son export CSV. Les filtres du tableau des missions sont locaux à ce tableau. Le raccourci Ctrl K (Cmd K sur Mac) cible la recherche globale. La cloche affiche les actions en retard ; les actions terminées en sont exclues.

Les cinq étapes représentent la répartition actuelle des missions. Le pourcentage de chaque étape indique sa part du total, tandis que la progression d’une mission est renseignée séparément. Le planning couvre six mois à partir du trimestre sélectionné, ou du mois courant. La conformité par département repose sur les réponses de checklist conformes et non conformes des rapports visibles. Une absence de données apparaît « — ».

La variation du nombre d’audits compare les 90 derniers jours aux 90 précédents, sur toutes les missions visibles. Elle n’apparaît pas si la période précédente est vide. Les valeurs et portraits de la maquette ne sont pas insérés comme données réelles ; les avatars utilisent les initiales.

## Autorisations

- Responsable : configuration des organisations et départements, gestion des missions et des nouveaux modules.
- Auditeur : gestion des constats, risques, actions et documents des missions qui lui sont affectées.
- Client : consultation et téléchargement dans ses missions, modification de son propre nom.

Les pièces jointes sont stockées dans `private_uploads/`, sans route publique vers ce dossier. Les liens entre risques, constats et actions sont validés pour appartenir à la même mission.

## Vérification et lancement sous Windows

```powershell
.\.venv-local\bin\python.exe manage.py migrate
.\.venv-local\bin\python.exe manage.py test
.\.venv-local\bin\python.exe manage.py runserver 127.0.0.1:8000 --insecure --noreload
```

`--insecure` sert les ressources statiques uniquement pour le développement local avec la configuration actuelle. La migration 0005 ajoute les nouveaux champs et tables ; les missions existantes restent conservées. Une sauvegarde locale préalable est disponible dans `db.sqlite3.before-governance.bak`.
