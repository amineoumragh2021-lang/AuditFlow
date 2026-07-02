# Diagrammes de l'Application AuditFlow

Ce dossier contient les diagrammes représentant l'architecture et le fonctionnement de l'application Django AuditFlow.

## Diagrammes Disponibles

### 1. [diagramme_classes.md](./diagramme_classes.md)
**Diagramme de Classes - Modèles de Données**
- Représente les modèles Django et leurs relations
- Montre la structure de la base de données
- Définit les cardinalités entre les entités

**Entités principales :**
- User (Django Auth)
- Profile (rôles: RESPONSABLE, AUDITEUR, CLIENT)
- Audit (planification d'audit)
- ChecklistItem (points de contrôle)
- Rapport (rapport d'audit)
- ChecklistResponse (réponses de checklist)

### 2. [diagramme_flux.md](./diagramme_flux.md)
**Diagramme de Flux - Workflow de l'Application**
- Montre le flux utilisateur complet
- Illustre les différents parcours selon les rôles
- Définit les contrôles et validations

**Flux principaux :**
- Authentification et attribution de rôle
- Dashboard personnalisé par rôle
- Création et modification d'audit (Responsable)
- Création et modification de rapport (Auditeur)
- Consultation des audits et rapports (Client)
- Export PDF

### 3. [diagramme_architecture.md](./diagramme_architecture.md)
**Diagramme d'Architecture - Structure de l'Application**
- Présente l'architecture MVT de Django
- Montre l'organisation des fichiers et répertoires
- Illustre les interactions entre les composants

**Couches de l'application :**
- Client (Navigateur)
- URL Routing
- Views Layer (logique métier)
- Forms Layer (validation)
- Models Layer (données)
- Database (SQLite)
- Static Files

### 4. [diagramme_sequence.md](./diagramme_sequence.md)
**Diagramme de Séquence - Cas d'Utilisation Principaux**
- Détaille les interactions entre composants
- Montre l'ordre chronologique des opérations
- Présente 5 scénarios clés

**Scénarios couverts :**
1. Connexion utilisateur
2. Création d'audit (Responsable)
3. Création de rapport avec checklist (Auditeur)
4. Modification de rapport (Auditeur)
5. Export PDF

## Comment Visualiser les Diagrammes

### Format Mermaid (.md)
- [Mermaid Live Editor](https://mermaid.live/)
- [VS Code](https://code.visualstudio.com/) avec extension Mermaid
- [GitHub](https://github.com/) (support natif Mermaid)

### Format PlantUML (.puml)
- [PlantUML Online Server](https://plantuml.com/online)
- [VS Code](https://code.visualstudio.com/) avec extension PlantUML
- [IntelliJ IDEA](https://www.jetbrains.com/idea/) avec plugin PlantUML
- [PlantText](https://www.planttext.com/)

Pour visualiser un diagramme PlantUML :
1. Copiez le contenu du fichier .puml
2. Collez-le dans un éditeur PlantUML en ligne
3. Le diagramme sera généré automatiquement
4. Exportez en PNG/SVG si nécessaire

## Technologies de l'Application

- **Framework Backend** : Django 4.x
- **Base de données** : SQLite
- **Authentification** : Django Auth System
- **Génération PDF** : ReportLab
- **Frontend** : HTML5, CSS3, JavaScript (Vanilla)
- **Architecture** : MVT (Model-View-Template)

## Rôles et Permissions

### RESPONSABLE
- Créer/modifier des audits
- Gérer les utilisateurs
- Gérer les checklists
- Voir tous les audits et rapports
- Accéder au calendrier

### AUDITEUR
- Voir ses audits assignés
- Créer des rapports pour ses audits
- Modifier ses propres rapports
- Voir ses rapports
- Accéder au calendrier

### CLIENT
- Voir ses audits
- Voir les rapports de ses audits
- Accéder au calendrier
- S' inscrire (créer compte)

## Flux de Données Principal

1. **Planification** : Responsable crée un audit avec client et auditeur
2. **Exécution** : Auditeur réalise l'audit à la date prévue
3. **Rapport** : Auditeur rédige un rapport avec checklist après la date
4. **Consultation** : Client consulte le rapport et le score de conformité
5. **Export** : Génération PDF du rapport complet
