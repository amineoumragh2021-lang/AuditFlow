# Diagramme pour Présentation PFA - AuditFlow

```mermaid
flowchart LR
    subgraph "Utilisateurs"
        R[Responsable]
        A[Auditeur]
        C[Client]
    end

    subgraph "Application Django"
        Auth[Authentification]
        Dash[Dashboard]
        AuditM[Gestion Audits]
        RapportM[Gestion Rapports]
        Check[Checklist]
        Cal[Calendrier]
    end

    subgraph "Base de Données"
        DB[(SQLite)]
    end

    R --> Auth
    A --> Auth
    C --> Auth

    Auth --> Dash
    Dash --> AuditM
    Dash --> RapportM
    Dash --> Check
    Dash --> Cal

    AuditM --> DB
    RapportM --> DB
    Check --> DB

    style R fill:#FFA07A
    style A fill:#98FB98
    style C fill:#DDA0DD
    style Auth fill:#87CEEB
    style Dash fill:#F0E68C
```

## Architecture Simplifiée

**3 Types d'utilisateurs** :
- Responsable : Planifie les audits
- Auditeur : Réalise les audits et rédige les rapports
- Client : Consulte les rapports

**Fonctionnalités principales** :
- Authentification sécurisée
- Dashboard personnalisé par rôle
- Gestion des audits (création, modification)
- Gestion des rapports avec checklist
- Calendrier des audits

**Technologies** :
- Django (Framework web Python)
- SQLite (Base de données)
- ReportLab (Génération PDF)
