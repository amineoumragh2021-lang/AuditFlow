# Diagramme de Classes - Modèles de Données

```mermaid
classDiagram
    class User {
        +int id
        +string username
        +string email
        +string first_name
        +string last_name
        +string password
    }

    class Profile {
        +int id
        +string role
        +string telephone
        +ROLE_CHOICES: RESPONSABLE, AUDITEUR, CLIENT
    }

    class Audit {
        +int id
        +string titre
        +string type_audit
        +date date_audit
        +text description
        +datetime created_at
        +TYPE_CHOICES: QUALITE, SECURITE, ENVIRONNEMENT, INTERNE
    }

    class ChecklistItem {
        +int id
        +string type_audit
        +string texte
        +int ordre
        +bool actif
    }

    class Rapport {
        +int id
        +text contenu
        +datetime date_creation
        +checklist_score() int
    }

    class ChecklistResponse {
        +int id
        +string statut
        +string remarque
        +STATUT_CHOICES: CONFORME, NON_CONFORME, ABORDABLE
    }

    User "1" -- "1" Profile : a
    User "1" -- "0..*" Audit : crée (created_by)
    User "1" -- "0..*" Audit : est client (client)
    User "1" -- "0..*" Audit : est auditeur (auditeur)
    User "1" -- "0..*" Rapport : rédige (auteur)
    
    Audit "1" -- "0..*" Rapport : a
    Rapport "1" -- "0..*" ChecklistResponse : a
    ChecklistItem "1" -- "0..*" ChecklistResponse : a
```

## Description des Relations

- **User ↔ Profile** : Relation One-to-One (1:1)
- **User → Audit (created_by)** : Un utilisateur peut créer plusieurs audits
- **User → Audit (client)** : Un utilisateur peut être client de plusieurs audits
- **User → Audit (auditeur)** : Un utilisateur peut être auditeur de plusieurs audits
- **User → Rapport (auteur)** : Un utilisateur peut rédiger plusieurs rapports
- **Audit → Rapport** : Un audit peut avoir plusieurs rapports
- **Rapport → ChecklistResponse** : Un rapport peut avoir plusieurs réponses de checklist
- **ChecklistItem → ChecklistResponse** : Un item de checklist peut avoir plusieurs réponses
