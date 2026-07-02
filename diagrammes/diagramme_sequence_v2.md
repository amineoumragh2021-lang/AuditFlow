# Diagramme de Séquence - Version par Rôle

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

## Description par Phase

### Phase 1 - Planification (Responsable)
- Création de l'audit avec titre, type et date
- Affectation d'un client et d'un auditeur
- Confirmation de la planification

### Phase 2 - Consultation (Auditeur et Client)
- L'auditeur voit ses audits assignés
- Le client voit ses audits demandés
- Accès au calendrier partagé

### Phase 3 - Rédaction du rapport (Auditeur)
- Vérification que la date de l'audit est passée
- Vérification qu'aucun rapport n'existe déjà
- Chargement de la checklist selon le type d'audit
- Soumission du rapport avec les réponses de checklist

### Phase 4 - Modification (Auditeur)
- Vérification que l'auditeur est l'auteur
- Modification du contenu textuel
- Mise à jour des réponses de checklist

### Phase 5 - Consultation du rapport (Client)
- Liste des rapports de ses audits
- Détail du rapport avec score de conformité
- Visualisation des réponses de checklist

### Phase 6 - Export PDF (Tous les rôles)
- Récupération de toutes les données du rapport
- Génération du PDF avec ReportLab
- Téléchargement du fichier
