# Diagramme de Séquence - Version Ultra-Simple

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

## Explication simple

1. **Connexion** : L'utilisateur se connecte avec email et mot de passe
2. **Planifier** : Le responsable crée un nouvel audit
3. **Voir** : L'auditeur consulte les audits qui lui sont assignés
4. **Rédiger** : L'auditeur écrit le rapport après l'audit
5. **Consulter** : Le client voit les rapports de ses audits
6. **Exporter** : N'importe qui peut télécharger le rapport en PDF
