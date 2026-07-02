# Diagramme d'Architecture - Structure de l'Application

```mermaid
graph TB
    subgraph "Client (Navigateur)"
        Browser[Navigateur Web]
        Templates[Templates HTML]
    end
    
    subgraph "Django Application"
        subgraph "URL Routing"
            URLs[urls.py]
            ConfigURLs[config/urls.py]
        end
        
        subgraph "Views Layer"
            Views[views.py]
            AuthViews[login_view, register_view, logout_view]
            DashboardViews[dashboard]
            AuditViews[audits_list, audit_create, audit_update, audit_detail]
            RapportViews[rapports_list, rapport_create, rapport_detail, rapport_modifier, rapport_pdf]
            ChecklistViews[checklist_list, checklist_create]
            UserViews[users_list, user_create]
            CalendarView[calendar_view]
        end
        
        subgraph "Forms Layer"
            Forms[forms.py]
            UserForm[UserForm]
            RegisterForm[RegisterForm]
            AuditForm[AuditForm]
            RapportForm[RapportForm]
            RapportChecklistForm[RapportChecklistForm]
        end
        
        subgraph "Models Layer"
            Models[models.py]
            User[User - Django Auth]
            Profile[Profile]
            Audit[Audit]
            ChecklistItem[ChecklistItem]
            Rapport[Rapport]
            ChecklistResponse[ChecklistResponse]
        end
        
        subgraph "Decorators"
            Decorators[decorators.py]
            RoleRequired[role_required]
        end
        
        subgraph "Signals"
            Signals[signals.py]
        end
        
        subgraph "Management Commands"
            SeedDemo[seed_demo.py]
        end
    end
    
    subgraph "Database"
        SQLite[(SQLite - db.sqlite3)]
    end
    
    subgraph "Static Files"
        Static[static/]
        CSS[CSS]
        JS[JavaScript]
    end
    
    %% Connections
    Browser -->|HTTP Request| ConfigURLs
    ConfigURLs --> URLs
    URLs --> Views
    Views -->|Validation| Forms
    Forms -->|CRUD Operations| Models
    Models -->|Query| SQLite
    Models -->|Return Data| Views
    Views -->|Render| Templates
    Templates -->|HTTP Response| Browser
    
    Views -->|Check Role| Decorators
    Decorators -->|Allow/Deny| Views
    
    Views -->|Use| Models
    Models -->|Auto-create Profile| Signals
    
    SeedDemo -->|Populate DB| Models
    
    Templates -->|Load| Static
```

## Structure des Répertoires

```
audit_pfa2004_corrige_sans_statut/
├── config/                    # Configuration Django
│   ├── __init__.py
│   ├── settings.py           # Paramètres de l'application
│   ├── urls.py               # URLs racine
│   ├── asgi.py               # ASGI config
│   └── wsgi.py               # WSGI config
│
├── audit/                     # Application principale
│   ├── __init__.py
│   ├── admin.py              # Administration Django
│   ├── models.py             # Modèles de données
│   ├── views.py              # Vues et logique métier
│   ├── urls.py               # URLs de l'application
│   ├── forms.py              # Formulaires
│   ├── decorators.py         # Décorateurs de permission
│   ├── signals.py            # Signaux Django
│   ├── management/           # Commandes de gestion
│   │   └── commands/
│   │       └── seed_demo.py  # Script de démo
│   └── migrations/           # Migrations DB
│       ├── 0001_initial.py
│       ├── 0002_remove_checklistresponse_est_conforme_and_more.py
│       ├── 0003_remove_audit_statut_abordable.py
│       └── 0004_audit_types_client_register.py
│
├── templates/                 # Templates HTML
│   └── audit/
│       ├── base.html         # Template de base
│       ├── login.html        # Page de connexion
│       ├── register.html     # Page d'inscription
│       ├── dashboard.html    # Dashboard
│       ├── audits_list.html  # Liste des audits
│       ├── audit_detail.html # Détail audit
│       ├── rapports_list.html # Liste des rapports
│       ├── rapport_detail.html # Détail rapport
│       ├── rapport_modifier.html # Modification rapport
│       ├── checklist_list.html # Liste checklist
│       ├── users_list.html   # Liste utilisateurs
│       ├── form_page.html    # Formulaire générique
│       └── calendar.html     # Calendrier
│
├── static/                    # Fichiers statiques
│   └── audit/
│       ├── css/               # Styles CSS
│       └── js/                # Scripts JavaScript
│
├── db.sqlite3                 # Base de données SQLite
├── manage.py                  # Script de gestion Django
├── create_db.py               # Script de création DB
├── database_setup.sql         # Setup SQL
├── requirements.txt           # Dépendances Python
└── README_*.md               # Documentation
```

## Technologies Utilisées

- **Framework** : Django 4.x
- **Base de données** : SQLite
- **Authentification** : Django Auth System
- **Génération PDF** : ReportLab
- **Frontend** : HTML5, CSS3, JavaScript (Vanilla)
- **Architecture** : MVT (Model-View-Template)
