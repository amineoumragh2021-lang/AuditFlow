# Tous les Diagrammes - AuditFlow

Ce document contient tous les diagrammes de l'application AuditFlow en format Mermaid.

---

## 1. Diagramme de Classes

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

---

## 2. Diagramme de Flux

```mermaid
flowchart TD
    Start([Début]) --> Login{Connexion?}
    Login -->|Non| LoginPage[Page de connexion]
    LoginPage --> Login
    Login -->|Oui| CheckRole{Vérifier rôle}
    
    CheckRole -->|RESPONSABLE| RespDashboard[Dashboard Responsable]
    CheckRole -->|AUDITEUR| AudDashboard[Dashboard Auditeur]
    CheckRole -->|CLIENT| CliDashboard[Dashboard Client]
    
    RespDashboard --> RespActions{Actions Responsable}
    AudDashboard --> AudActions{Actions Auditeur}
    CliDashboard --> CliActions{Actions Client}
    
    RespActions -->|Gérer utilisateurs| UsersList[Liste utilisateurs]
    RespActions -->|Créer audit| AuditCreate[Créer audit]
    RespActions -->|Modifier audit| AuditUpdate[Modifier audit]
    RespActions -->|Gérer checklist| ChecklistList[Gérer checklist]
    RespActions -->|Voir audits| AuditsList[Liste audits]
    RespActions -->|Voir rapports| RapportsList[Liste rapports]
    RespActions -->|Calendrier| Calendar[Calendrier]
    
    AudActions -->|Voir mes audits| AuditsListAud[Mes audits]
    AudActions -->|Créer rapport| RapportCreate[Créer rapport]
    AudActions -->|Modifier rapport| RapportUpdate[Modifier rapport]
    AudActions -->|Voir rapports| RapportsListAud[Mes rapports]
    AudActions -->|Calendrier| CalendarAud[Calendrier]
    
    CliActions -->|Voir mes audits| AuditsListCli[Mes audits]
    CliActions -->|Voir rapports| RapportsListCli[Rapports]
    CliActions -->|Calendrier| CalendarCli[Calendrier]
    
    AuditCreate --> AuditForm[Remplir formulaire]
    AuditForm --> AuditSave[Enregistrer audit]
    AuditSave --> AuditsList
    
    RapportCreate --> SelectAudit[Sélectionner audit]
    SelectAudit --> CheckDate{Date passée?}
    CheckDate -->|Non| ErrorDate[Erreur: date future]
    CheckDate -->|Oui| CheckRapport{Rapport existe?}
    CheckRapport -->|Oui| RapportDetail[Voir rapport existant]
    CheckRapport -->|Non| FillChecklist[Remplir checklist]
    FillChecklist --> SaveRapport[Enregistrer rapport]
    SaveRapport --> RapportsListAud
    
    RapportUpdate --> RapportDetailPage[Détail rapport]
    RapportDetailPage --> EditContent[Modifier contenu]
    EditContent --> EditChecklist[Modifier checklist]
    EditChecklist --> SaveUpdate[Enregistrer modifications]
    SaveUpdate --> RapportDetail
    
    RapportDetail --> ExportPDF{Exporter PDF?}
    ExportPDF -->|Oui| GeneratePDF[Générer PDF]
    ExportPDF -->|Non| End([Fin])
    GeneratePDF --> Download[Télécharger PDF]
    Download --> End
    
    UsersList --> RespDashboard
    AuditsList --> RespDashboard
    RapportsList --> RespDashboard
    ChecklistList --> RespDashboard
    Calendar --> RespDashboard
    
    AuditsListAud --> AudDashboard
    RapportsListAud --> AudDashboard
    CalendarAud --> AudDashboard
    
    AuditsListCli --> CliDashboard
    RapportsListCli --> CliDashboard
    CalendarCli --> CliDashboard
    
    RespDashboard --> Logout{Déconnexion?}
    AudDashboard --> Logout
    CliDashboard --> Logout
    Logout -->|Oui| LoginPage
    Logout -->|Non| End
```

---

## 3. Diagramme d'Architecture

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
    
    Browser --> ConfigURLs : HTTP Request
    ConfigURLs --> URLs
    URLs --> Views
    Views --> Forms : Validation
    Forms --> Models : CRUD Operations
    Models --> SQLite : Query
    SQLite --> Models : Return Data
    Models --> Views : Return Data
    Views --> Templates : Render
    Templates --> Browser : HTTP Response
    
    Views --> Decorators : Check Role
    Decorators --> Views : Allow/Deny
    
    Views --> Models : Use
    Models --> Signals : Auto-create Profile
    
    SeedDemo --> Models : Populate DB
    
    Templates --> Static : Load
```

---

## 4. Diagramme de Séquence (Version Simplifiée)

```mermaid
sequenceDiagram
    participant User as Utilisateur
    participant App as Application Django
    participant DB as Base de Données

    Note over User,DB: Flux principal de l'application

    %% 1. Connexion
    User->>App: Se connecte (email/password)
    App->>DB: Vérifie identifiants
    DB-->>App: Utilisateur trouvé
    App-->>User: Dashboard affiché

    %% 2. Création d'audit (Responsable)
    User->>App: Crée un audit
    App->>DB: Enregistre l'audit
    DB-->>App: Audit créé
    App-->>User: Confirmation

    %% 3. Rédaction de rapport (Auditeur)
    User->>App: Rédige rapport pour audit
    App->>DB: Vérifie date et existence
    DB-->>App: OK
    App->>DB: Enregistre rapport + checklist
    DB-->>App: Rapport créé
    App-->>User: Rapport affiché

    %% 4. Modification de rapport (Auditeur)
    User->>App: Modifie son rapport
    App->>DB: Met à jour rapport et checklist
    DB-->>App: Modifications enregistrées
    App-->>User: Rapport mis à jour

    %% 5. Consultation (Client)
    User->>App: Consulte ses audits/rapports
    App->>DB: Récupère données
    DB-->>App: Données
    App-->>User: Liste affichée

    %% 6. Export PDF
    User->>App: Demande PDF
    App->>DB: Récupère rapport complet
    DB-->>App: Données
    App->>App: Génère PDF
    App-->>User: Fichier PDF téléchargé
```

---

## 5. Diagramme de Séquence (Version par Rôle)

```mermaid
sequenceDiagram
    participant Resp as Responsable
    participant Aud as Auditeur
    participant Cli as Client
    participant App as Application Django
    participant DB as Base de Données

    Note over Resp,DB: Cycle de vie d'un audit

    %% Phase 1: Planification (Responsable)
    rect rgb(200, 220, 255)
        Note over Resp,App: Phase 1 - Planification
        Resp->>App: Crée un audit
        App->>DB: Enregistre audit (titre, type, date)
        DB-->>App: Audit créé
        App->>DB: Affecte client et auditeur
        DB-->>App: Affectation OK
        App-->>Resp: Audit planifié
    end

    %% Phase 2: Consultation (Auditeur et Client)
    rect rgb(220, 255, 220)
        Note over Aud,App: Phase 2 - Consultation
        Aud->>App: Consulte ses audits assignés
        App->>DB: Récupère audits de l'auditeur
        DB-->>App: Liste des audits
        App-->>Aud: Affiche ses audits
        
        Cli->>App: Consulte ses audits
        App->>DB: Récupère audits du client
        DB-->>App: Liste des audits
        App-->>Cli: Affiche ses audits
    end

    %% Phase 3: Exécution et Rapport (Auditeur)
    rect rgb(255, 220, 220)
        Note over Aud,App: Phase 3 - Rédaction du rapport
        Aud->>App: Demande à rédiger rapport
        App->>DB: Vérifie date de l'audit
        DB-->>App: Date passée ✓
        App->>DB: Vérifie si rapport existe
        DB-->>App: Aucun rapport ✓
        App->>DB: Charge checklist du type d'audit
        DB-->>App: Items de checklist
        App-->>Aud: Formulaire avec checklist
        Aud->>App: Soumet rapport + réponses
        App->>DB: Enregistre rapport
        App->>DB: Enregistre réponses checklist
        DB-->>App: Rapport créé
        App-->>Aud: Rapport enregistré
    end

    %% Phase 4: Modification (Auditeur)
    rect rgb(255, 255, 220)
        Note over Aud,App: Phase 4 - Modification
        Aud->>App: Modifie son rapport
        App->>DB: Vérifie autorisation (auteur)
        DB-->>App: Autorisé ✓
        App->>DB: Met à jour contenu
        App->>DB: Met à jour réponses checklist
        DB-->>App: Modifications OK
        App-->>Aud: Rapport mis à jour
    end

    %% Phase 5: Consultation (Client)
    rect rgb(220, 255, 255)
        Note over Cli,App: Phase 5 - Consultation du rapport
        Cli->>App: Consulte les rapports
        App->>DB: Récupère rapports de ses audits
        DB-->>App: Liste des rapports
        App-->>Cli: Affiche rapports
        Cli->>App: Ouvre un rapport
        App->>DB: Récupère rapport + checklist
        DB-->>App: Détails complets
        App-->>Cli: Affiche rapport avec score
    end

    %% Phase 6: Export (Tous les rôles)
    rect rgb(255, 200, 255)
        Note over Cli,App: Phase 6 - Export PDF
        Cli->>App: Demande PDF du rapport
        App->>DB: Récupère toutes les données
        DB-->>App: Données complètes
        App->>App: Génère PDF (ReportLab)
        App-->>Cli: Fichier PDF téléchargé
    end
```

---

## 6. Diagramme de Séquence (Version Ultra-Simple)

```mermaid
sequenceDiagram
    participant User as Utilisateur
    participant System as Système
    participant DB as Base de données

    Note over User,DB: Processus simple d'AuditFlow

    %% 1. Connexion
    User->>System: Se connecte
    System->>DB: Vérifie utilisateur
    DB-->>System: OK
    System-->>User: Bienvenue

    %% 2. Responsable crée un audit
    User->>System: Planifie un audit
    System->>DB: Sauvegarde l'audit
    DB-->>System: Audit enregistré
    System-->>User: Audit créé ✓

    %% 3. Auditeur voit ses audits
    User->>System: Voir mes audits
    System->>DB: Cherche audits
    DB-->>System: Liste trouvée
    System-->>User: Voici vos audits

    %% 4. Auditeur rédige le rapport
    User->>System: Écrire rapport
    System->>DB: Vérifie date
    DB-->>System: Date OK
    System->>DB: Sauvegarde rapport
    DB-->>System: Rapport enregistré
    System-->>User: Rapport envoyé ✓

    %% 5. Client voit le rapport
    User->>System: Voir les rapports
    System->>DB: Cherche rapports
    DB-->>System: Liste trouvée
    System-->>User: Voici les rapports

    %% 6. Export PDF
    User->>System: Télécharger PDF
    System->>DB: Prend les données
    DB-->>System: Données prêtes
    System->>System: Crée le PDF
    System-->>User: PDF téléchargé ✓
```

---

## 7. Diagramme d'Activité (Version Ultra-Simple)

```mermaid
flowchart TD
    Start([Début]) --> Connect[Se connecter]
    Connect --> Role{Rôle?}

    Role -->|Responsable| Resp[Créer audits]
    Role -->|Auditeur| Aud[Écrire rapports]
    Role -->|Client| Cli[Voir rapports]

    Resp --> Done([Fin])
    Aud --> Done
    Cli --> Done

    style Start fill:#90EE90
    style Done fill:#FFB6C1
    style Resp fill:#FFA07A
    style Aud fill:#98FB98
    style Cli fill:#DDA0DD
```

---

## 8. Diagramme des Cas d'Utilisation

```mermaid
flowchart TD
    Resp[Responsable Audit]
    Aud[Auditeur]
    Cli[Client]
    
    UC1[Se connecter]
    UC2[S'inscrire]
    UC3[Voir Dashboard]
    UC4[Créer un audit]
    UC5[Modifier un audit]
    UC6[Voir les audits]
    UC7[Voir le détail d'un audit]
    UC8[Créer un rapport]
    UC9[Modifier un rapport]
    UC10[Voir les rapports]
    UC11[Voir le détail d'un rapport]
    UC12[Exporter un rapport en PDF]
    UC13[Gérer les utilisateurs]
    UC14[Gérer les checklists]
    UC15[Voir le calendrier]
    
    Resp --> UC1
    Resp --> UC3
    Resp --> UC4
    Resp --> UC5
    Resp --> UC6
    Resp --> UC7
    Resp --> UC10
    Resp --> UC11
    Resp --> UC12
    Resp --> UC13
    Resp --> UC14
    Resp --> UC15
    
    Aud --> UC1
    Aud --> UC3
    Aud --> UC6
    Aud --> UC7
    Aud --> UC8
    Aud --> UC9
    Aud --> UC10
    Aud --> UC11
    Aud --> UC12
    Aud --> UC15
    
    Cli --> UC1
    Cli --> UC2
    Cli --> UC3
    Cli --> UC6
    Cli --> UC7
    Cli --> UC10
    Cli --> UC11
    Cli --> UC12
    Cli --> UC15
```

---

## Résumé

Ce document contient **8 diagrammes** couvrant tous les aspects de l'application AuditFlow :

1. **Diagramme de Classes** - Structure des modèles de données
2. **Diagramme de Flux** - Workflow complet de l'application
3. **Diagramme d'Architecture** - Structure technique MVT Django
4. **Diagramme de Séquence (Simplifié)** - Interactions principales
5. **Diagramme de Séquence (par Rôle)** - Cycle de vie d'un audit
6. **Diagramme de Séquence (Ultra-Simple)** - Version très simple
7. **Diagramme d'Activité (Ultra-Simple)** - Workflow minimal
8. **Diagramme des Cas d'Utilisation** - Fonctionnalités par rôle

Tous ces diagrammes sont disponibles en format Mermaid (.md) et PlantUML (.puml) dans le dossier `diagrammes/`.
