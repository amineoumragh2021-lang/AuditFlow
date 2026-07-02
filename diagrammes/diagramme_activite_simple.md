# Diagramme d'Activité - Version Ultra-Simple

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

## Workflow ultra-simple

1. **Se connecter**
2. **Selon le rôle** :
   - Responsable → Crée des audits
   - Auditeur → Écrit des rapports
   - Client → Voit les rapports
3. **Fin**
