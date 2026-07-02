# Diagramme de Flux - Workflow de l'Application

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
    
    %% Responsable Actions
    RespActions -->|Gérer utilisateurs| UsersList[Liste utilisateurs]
    RespActions -->|Créer audit| AuditCreate[Créer audit]
    RespActions -->|Modifier audit| AuditUpdate[Modifier audit]
    RespActions -->|Gérer checklist| ChecklistList[Gérer checklist]
    RespActions -->|Voir audits| AuditsList[Liste audits]
    RespActions -->|Voir rapports| RapportsList[Liste rapports]
    RespActions -->|Calendrier| Calendar[Calendrier]
    
    %% Auditeur Actions
    AudActions -->|Voir mes audits| AuditsListAud[Mes audits]
    AudActions -->|Créer rapport| RapportCreate[Créer rapport]
    AudActions -->|Modifier rapport| RapportUpdate[Modifier rapport]
    AudActions -->|Voir rapports| RapportsListAud[Mes rapports]
    AudActions -->|Calendrier| CalendarAud[Calendrier]
    
    %% Client Actions
    CliActions -->|Voir mes audits| AuditsListCli[Mes audits]
    CliActions -->|Voir rapports| RapportsListCli[Rapports]
    CliActions -->|Calendrier| CalendarCli[Calendrier]
    
    %% Flux de création d'audit
    AuditCreate --> AuditForm[Remplir formulaire]
    AuditForm --> AuditSave[Enregistrer audit]
    AuditSave --> AuditsList
    
    %% Flux de création de rapport
    RapportCreate --> SelectAudit[Sélectionner audit]
    SelectAudit --> CheckDate{Date passée?}
    CheckDate -->|Non| ErrorDate[Erreur: date future]
    CheckDate -->|Oui| CheckRapport{Rapport existe?}
    CheckRapport -->|Oui| RapportDetail[Voir rapport existant]
    CheckRapport -->|Non| FillChecklist[Remplir checklist]
    FillChecklist --> SaveRapport[Enregistrer rapport]
    SaveRapport --> RapportsListAud
    
    %% Flux de modification de rapport
    RapportUpdate --> RapportDetailPage[Détail rapport]
    RapportDetailPage --> EditContent[Modifier contenu]
    EditContent --> EditChecklist[Modifier checklist]
    EditChecklist --> SaveUpdate[Enregistrer modifications]
    SaveUpdate --> RapportDetail
    
    %% Export PDF
    RapportDetail --> ExportPDF{Exporter PDF?}
    ExportPDF -->|Oui| GeneratePDF[Générer PDF]
    ExportPDF -->|Non| End([Fin])
    GeneratePDF --> Download[Télécharger PDF]
    Download --> End
    
    %% Navigation
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
    
    %% Déconnexion
    RespDashboard --> Logout{Déconnexion?}
    AudDashboard --> Logout
    CliDashboard --> Logout
    Logout -->|Oui| LoginPage
    Logout -->|Non| End
```

## Description du Workflow

### 1. Authentification
- L'utilisateur se connecte via la page de login
- Le système vérifie les identifiants
- Le rôle de l'utilisateur est déterminé (RESPONSABLE, AUDITEUR, CLIENT)

### 2. Dashboard par Rôle
- **Responsable** : Accès complet à la gestion
- **Auditeur** : Accès limité à ses audits et rapports
- **Client** : Accès en lecture à ses audits et rapports

### 3. Flux Principal
- **Création d'audit** : Responsable planifie un audit avec client et auditeur
- **Création de rapport** : Auditeur rédige rapport après la date de l'audit
- **Checklist** : Points de contrôle évalués (Conforme/Non conforme/Abordable)
- **Modification** : Auditeur peut modifier son propre rapport
- **Export PDF** : Génération de rapport en PDF

### 4. Contrôles d'Accès
- Vérification de la date avant rédaction de rapport
- Un seul rapport par audit
- Accès restreint selon le rôle
