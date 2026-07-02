# Workflow Simplifié pour PFA

```mermaid
flowchart TD
    Start([Début]) --> Login[Connexion]
    Login --> Role{Rôle?}

    Role -->|Responsable| R[Planifier audit]
    Role -->|Auditeur| A[Réaliser audit + Rapport]
    Role -->|Client| C[Consulter rapport]

    R --> Create[Créer audit]
    Create --> Assign[Assigner auditeur et client]
    Assign --> Save[Enregistrer]

    A --> View[Voir audits assignés]
    View --> CheckDate{Date passée?}
    CheckDate -->|Oui| Write[Écrire rapport]
    Write --> Checklist[Remplir checklist]
    Checklist --> SaveRap[Enregistrer]

    C --> ViewRap[Voir rapports]
    ViewRap --> PDF{Exporter PDF?}
    PDF -->|Oui| Download[Télécharger]

    Save --> End([Fin])
    SaveRap --> End
    ViewRap --> End
    Download --> End

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style R fill:#FFA07A
    style A fill:#98FB98
    style C fill:#DDA0DD
```

## Workflow de l'Application

### Étape 1 : Planification (Responsable)
- Créer un nouvel audit
- Définir le type, la date et la description
- Assigner un auditeur et un client

### Étape 2 : Exécution (Auditeur)
- Consulter les audits assignés
- Attendre la date de l'audit
- Rédiger le rapport avec checklist
- Évaluer chaque point (Conforme/Non conforme/Abordable)

### Étape 3 : Consultation (Client)
- Voir les rapports de ses audits
- Consulter le score de conformité
- Exporter en PDF si nécessaire
