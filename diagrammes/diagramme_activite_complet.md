# Diagramme d'Activité - Workflow Complet

```mermaid
flowchart TD
    Start([Début]) --> Login[Page de connexion]
    Login --> Auth{Authentification?}
    Auth -->|Échec| Login
    Auth -->|Succès| GetRole[Récupérer rôle]
    
    GetRole --> Role{Quel rôle?}
    
    %% Responsable
    Role -->|Responsable| DashResp[Dashboard Responsable]
    DashResp --> MenuResp{Menu Responsable}
    
    MenuResp -->|Créer audit| NewAudit[Formulaire création audit]
    NewAudit --> ValidateAudit{Formulaire valide?}
    ValidateAudit -->|Non| NewAudit
    ValidateAudit -->|Oui| SaveAudit[Enregistrer audit]
    SaveAudit --> DashResp
    
    MenuResp -->|Modifier audit| SelectAuditMod[Sélectionner audit]
    SelectAuditMod --> EditAudit[Formulaire modification]
    EditAudit --> UpdateAudit[Mettre à jour audit]
    UpdateAudit --> DashResp
    
    MenuResp -->|Voir audits| ListAudits[Liste des audits]
    ListAudits --> ViewAudit{Voir détail?}
    ViewAudit -->|Oui| AuditDetail[Détail audit]
    AuditDetail --> DashResp
    ViewAudit -->|Non| DashResp
    
    MenuResp -->|Gérer utilisateurs| ListUsers[Liste utilisateurs]
    ListUsers --> UserAction{Action?}
    UserAction -->|Ajouter| NewUser[Créer utilisateur]
    NewUser --> DashResp
    UserAction -->|Retour| DashResp
    
    MenuResp -->|Gérer checklist| ListCheck[Liste checklist]
    ListCheck --> CheckAction{Action?}
    CheckAction -->|Ajouter items| NewCheck[Ajouter points]
    NewCheck --> DashResp
    CheckAction -->|Retour| DashResp
    
    MenuResp -->|Voir rapports| ListRapResp[Liste rapports]
    ListRapResp --> DashResp
    
    MenuResp -->|Calendrier| CalResp[Calendrier]
    CalResp --> DashResp
    
    MenuResp -->|Déconnexion| Logout
    
    %% Auditeur
    Role -->|Auditeur| DashAud[Dashboard Auditeur]
    DashAud --> MenuAud{Menu Auditeur}
    
    MenuAud -->|Mes audits| ListAudAud[Mes audits assignés]
    ListAudAud --> SelectAuditAud{Sélectionner?}
    SelectAuditAud -->|Oui| AuditDetailAud[Détail audit]
    AuditDetailAud --> CreateRap{Créer rapport?}
    CreateRap -->|Oui| CheckDate{Date passée?}
    CheckDate -->|Non| ErrorDate[Erreur: attendre date]
    ErrorDate --> DashAud
    CheckDate -->|Oui| CheckRapExist{Rapport existe?}
    CheckRapExist -->|Oui| ViewRapExist[Voir rapport existant]
    ViewRapExist --> DashAud
    CheckRapExist -->|Non| FormChecklist[Formulaire checklist]
    FormChecklist --> SubmitRap[Soumettre rapport]
    SubmitRap --> DashAud
    CreateRap -->|Non| DashAud
    SelectAuditAud -->|Non| DashAud
    
    MenuAud -->|Mes rapports| ListRapAud[Mes rapports]
    ListRapAud --> SelectRap{Sélectionner?}
    SelectRap -->|Oui| RapDetailAud[Détail rapport]
    RapDetailAud --> ModRap{Modifier?}
    ModRap -->|Oui| EditRap[Modifier rapport]
    EditRap --> DashAud
    ModRap -->|Non| DashAud
    SelectRap -->|Non| DashAud
    
    MenuAud -->|Calendrier| CalAud[Calendrier]
    CalAud --> DashAud
    
    MenuAud -->|Déconnexion| Logout
    
    %% Client
    Role -->|Client| DashCli[Dashboard Client]
    DashCli --> MenuCli{Menu Client}
    
    MenuCli -->|Mes audits| ListAudCli[Mes audits]
    ListAudCli --> DashCli
    
    MenuCli -->|Rapports| ListRapCli[Rapports de mes audits]
    ListRapCli --> SelectRapCli{Sélectionner?}
    SelectRapCli -->|Oui| RapDetailCli[Détail rapport]
    RapDetailCli --> ExportPDF{Exporter PDF?}
    ExportPDF -->|Oui| GenPDF[Générer PDF]
    GenPDF --> Download[Télécharger]
    Download --> DashCli
    ExportPDF -->|Non| DashCli
    SelectRapCli -->|Non| DashCli
    
    MenuCli -->|Calendrier| CalCli[Calendrier]
    CalCli --> DashCli
    
    MenuCli -->|Déconnexion| Logout
    
    %% Déconnexion
    Logout --> ConfirmLogout{Confirmer?}
    ConfirmLogout -->|Non| DashResp
    ConfirmLogout -->|Oui| Login
    
    Logout --> ConfirmLogoutAud{Confirmer?}
    ConfirmLogoutAud -->|Non| DashAud
    ConfirmLogoutAud -->|Oui| Login
    
    Logout --> ConfirmLogoutCli{Confirmer?}
    ConfirmLogoutCli -->|Non| DashCli
    ConfirmLogoutCli -->|Oui| Login
    
    Login --> End([Fin])

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style DashResp fill:#FFA07A
    style DashAud fill:#98FB98
    style DashCli fill:#DDA0DD
    style Login fill:#87CEEB
```

## Description détaillée du workflow

### Phase d'authentification
1. L'utilisateur accède à la page de connexion
2. Saisit email et mot de passe
3. Le système vérifie les identifiants
4. Si succès, récupère le rôle de l'utilisateur

### Workflow Responsable
- **Créer audit** : Formulaire de création → Validation → Enregistrement
- **Modifier audit** : Sélection → Formulaire → Mise à jour
- **Voir audits** : Liste → Détail optionnel
- **Gérer utilisateurs** : Liste → Ajout/Création
- **Gérer checklist** : Liste → Ajout de points
- **Voir rapports** : Consultation globale
- **Calendrier** : Vue calendrier

### Workflow Auditeur
- **Mes audits** : Liste des audits assignés → Détail → Option créer rapport
- **Création rapport** : Vérification date → Vérification existence → Formulaire checklist → Soumission
- **Mes rapports** : Liste → Détail → Option modification
- **Calendrier** : Vue calendrier

### Workflow Client
- **Mes audits** : Liste des audits demandés
- **Rapports** : Liste des rapports → Détail → Option export PDF
- **Calendrier** : Vue calendrier

### Déconnexion
- Confirmation avant déconnexion
- Retour à la page de connexion
