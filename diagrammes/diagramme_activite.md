# Diagramme d'Activité - Workflow Global

```mermaid
flowchart TD
    Start([Début]) --> Login{Connexion?}
    Login -->|Non| PageLogin[Page de connexion]
    PageLogin --> Login
    Login -->|Oui| VerifRole[Vérifier rôle utilisateur]

    VerifRole --> Role{Quel rôle?}

    Role -->|Responsable| DashResp[Dashboard Responsable]
    Role -->|Auditeur| DashAud[Dashboard Auditeur]
    Role -->|Client| DashCli[Dashboard Client]

    %% Responsable
    DashResp --> ActionResp{Action?}
    ActionResp -->|Créer audit| FormAudit[Formulaire audit]
    FormAudit --> SaveAudit[Enregistrer audit]
    SaveAudit --> DashResp
    ActionResp -->|Voir audits| ListAudits[Liste audits]
    ListAudits --> DashResp
    ActionResp -->|Gérer users| ListUsers[Liste utilisateurs]
    ListUsers --> DashResp
    ActionResp -->|Gérer checklist| ListCheck[Liste checklist]
    ListCheck --> DashResp
    ActionResp -->|Calendrier| CalResp[Calendrier]
    CalResp --> DashResp
    ActionResp -->|Déconnexion| Logout

    %% Auditeur
    DashAud --> ActionAud{Action?}
    ActionAud -->|Voir mes audits| ListAudAud[Mes audits]
    ListAudAud --> DashAud
    ActionAud -->|Créer rapport| SelectAudit[Choisir audit]
    SelectAudit --> CheckDate{Date passée?}
    CheckDate -->|Non| ErreurDate[Erreur: attendre la date]
    ErreurDate --> DashAud
    CheckDate -->|Oui| CheckRapport{Rapport existe?}
    CheckRapport -->|Oui| ViewRapport[Voir rapport]
    ViewRapport --> DashAud
    CheckRapport -->|Non| FormChecklist[Formulaire checklist]
    FormChecklist --> SaveRapport[Enregistrer rapport]
    SaveRapport --> DashAud
    ActionAud -->|Modifier rapport| ModRapport[Modifier rapport]
    ModRapport --> DashAud
    ActionAud -->|Calendrier| CalAud[Calendrier]
    CalAud --> DashAud
    ActionAud -->|Déconnexion| Logout

    %% Client
    DashCli --> ActionCli{Action?}
    ActionCli -->|Voir mes audits| ListAudCli[Mes audits]
    ListAudCli --> DashCli
    ActionCli -->|Voir rapports| ListRapCli[Rapports]
    ListRapCli --> DashCli
    ActionCli -->|Calendrier| CalCli[Calendrier]
    CalCli --> DashCli
    ActionCli -->|Déconnexion| Logout

    %% Export PDF
    ListRapCli --> ExportPDF{Exporter PDF?}
    ExportPDF -->|Oui| GenPDF[Générer PDF]
    ExportPDF -->|Non| DashCli
    GenPDF --> Download[Télécharger]
    Download --> DashCli

    Logout --> PageLogin
    PageLogin --> End([Fin])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style Login fill:#87CEEB
    style Role fill:#FFD700
    style DashResp fill:#FFA07A
    style DashAud fill:#98FB98
    style DashCli fill:#DDA0DD
```

## Description du workflow

### 1. Connexion
- L'utilisateur se connecte
- Le système vérifie son rôle
- Redirection vers le dashboard approprié

### 2. Dashboard Responsable
- Créer des audits
- Voir tous les audits
- Gérer les utilisateurs
- Gérer les checklists
- Voir le calendrier

### 3. Dashboard Auditeur
- Voir ses audits assignés
- Créer des rapports (après date de l'audit)
- Modifier ses rapports
- Voir le calendrier

### 4. Dashboard Client
- Voir ses audits
- Voir les rapports de ses audits
- Exporter les rapports en PDF
- Voir le calendrier
