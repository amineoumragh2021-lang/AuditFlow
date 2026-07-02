from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from audit.models import Audit, ChecklistItem, Profile
from datetime import date, timedelta

CHECKLISTS = {
    'QUALITE': [
        "Les procédures sont-elles documentées ?", "Les procédures sont-elles appliquées ?", "Les enregistrements qualité sont-ils conservés ?", "Les documents qualité sont-ils à jour ?", "Les responsabilités qualité sont-elles définies ?", "Les objectifs qualité sont-ils communiqués ?", "Les indicateurs qualité sont-ils suivis ?", "Les non-conformités sont-elles enregistrées ?", "Les actions correctives sont-elles suivies ?", "Les actions préventives sont-elles mises en œuvre ?", "Les audits internes qualité sont-ils réalisés ?", "Les rapports d'audit sont-ils documentés ?", "Les fournisseurs sont-ils évalués ?", "Les fournisseurs sont-ils réévalués périodiquement ?", "Les réclamations clients sont-elles traitées ?", "Les délais de traitement sont-ils respectés ?", "La traçabilité des produits est-elle assurée ?", "Les compétences du personnel sont-elles évaluées ?", "Les formations qualité sont-elles enregistrées ?", "Les équipements de mesure sont-ils entretenus ?", "Les équipements de mesure sont-ils étalonnés ?", "Les risques qualité sont-ils évalués ?", "Les opportunités d'amélioration sont-elles identifiées ?", "Les revues de direction sont-elles réalisées ?", "Les ressources nécessaires sont-elles suffisantes ?", "Les processus sont-ils maîtrisés ?", "Les modifications de processus sont-elles contrôlées ?", "Les données qualité sont-elles sauvegardées ?", "Les accès aux documents sont-ils sécurisés ?", "Les résultats qualité sont-ils analysés ?", "Les objectifs qualité sont-ils atteints ?", "La satisfaction client est-elle mesurée ?", "Les exigences clients sont-elles définies ?", "Les exigences légales sont-elles respectées ?", "Les procédures d'urgence existent-elles ?", "Les rapports qualité sont-ils archivés ?", "Les audits précédents sont-ils suivis ?", "Les écarts qualité sont-ils clôturés ?", "Les réunions qualité sont-elles tenues ?", "Le système qualité est-il efficace ?"
    ],
    'SECURITE': [
        "Les EPI sont-ils disponibles ?", "Les EPI sont-ils portés correctement ?", "Les extincteurs sont-ils vérifiés ?", "Les sorties de secours sont-elles dégagées ?", "Les plans d'évacuation sont-ils affichés ?", "Les exercices d'évacuation sont-ils réalisés ?", "Les risques professionnels sont-ils identifiés ?", "Les risques sont-ils évalués régulièrement ?", "Les accidents sont-ils enregistrés ?", "Les incidents sont-ils analysés ?", "Les actions correctives sécurité sont-elles appliquées ?", "Le personnel reçoit-il une formation sécurité ?", "Les nouveaux employés sont-ils sensibilisés ?", "Les machines disposent-elles de protections ?", "Les équipements sont-ils contrôlés périodiquement ?", "Les produits dangereux sont-ils identifiés ?", "Les fiches de sécurité sont-elles disponibles ?", "Les zones dangereuses sont-elles signalées ?", "L'éclairage est-il suffisant ?", "Les voies de circulation sont-elles sécurisées ?", "Les installations électriques sont-elles conformes ?", "Les câbles sont-ils protégés ?", "Les équipements de levage sont-ils inspectés ?", "Les permis de travail sont-ils utilisés ?", "Les procédures d'urgence sont-elles connues ?", "Les trousses de secours sont-elles disponibles ?", "Les secouristes sont-ils désignés ?", "Le bruit est-il maîtrisé ?", "Les vibrations sont-elles surveillées ?", "La qualité de l'air est-elle contrôlée ?", "Les équipements sous pression sont-ils vérifiés ?", "Les sous-traitants respectent-ils les règles sécurité ?", "Les visiteurs reçoivent-ils des consignes ?", "Les audits sécurité sont-ils réalisés ?", "Les inspections terrain sont-elles effectuées ?", "Les objectifs sécurité sont-ils suivis ?", "Les indicateurs sécurité sont-ils analysés ?", "La direction participe-t-elle à la sécurité ?", "Les situations dangereuses sont-elles signalées ?", "L'amélioration continue sécurité est-elle démontrée ?"
    ],
    'ENVIRONNEMENT': [
        "Les aspects environnementaux sont-ils identifiés ?", "Les impacts environnementaux sont-ils évalués ?", "Les exigences légales environnementales sont-elles respectées ?", "Les déchets sont-ils triés ?", "Les déchets dangereux sont-ils identifiés ?", "Les déchets sont-ils stockés correctement ?", "Les déchets sont-ils éliminés par un organisme agréé ?", "La consommation d'eau est-elle suivie ?", "La consommation d'énergie est-elle suivie ?", "La consommation de carburant est-elle contrôlée ?", "Les émissions atmosphériques sont-elles surveillées ?", "Les rejets liquides sont-ils contrôlés ?", "Les nuisances sonores sont-elles maîtrisées ?", "Les produits chimiques sont-ils inventoriés ?", "Les produits chimiques sont-ils stockés correctement ?", "Les fuites sont-elles signalées immédiatement ?", "Les équipements anti-pollution sont-ils entretenus ?", "Les objectifs environnementaux sont-ils définis ?", "Les objectifs environnementaux sont-ils suivis ?", "Le personnel est-il sensibilisé à l'environnement ?", "Les formations environnementales sont-elles réalisées ?", "Les situations d'urgence environnementales sont-elles identifiées ?", "Les procédures d'urgence environnementales sont-elles testées ?", "Les audits environnementaux sont-ils réalisés ?", "Les non-conformités environnementales sont-elles traitées ?", "Les actions correctives environnementales sont-elles suivies ?", "Les ressources naturelles sont-elles préservées ?", "Le recyclage est-il encouragé ?", "La consommation de papier est-elle réduite ?", "Les zones de stockage sont-elles conformes ?", "Les sols sont-ils protégés contre les pollutions ?", "Les eaux pluviales sont-elles maîtrisées ?", "Les fournisseurs respectent-ils les exigences environnementales ?", "Les indicateurs environnementaux sont-ils analysés ?", "Les inspections environnementales sont-elles réalisées ?", "La biodiversité est-elle prise en compte ?", "Les risques environnementaux sont-ils évalués ?", "La direction participe-t-elle aux actions environnementales ?", "L'amélioration continue environnementale est-elle démontrée ?", "Le système environnemental est-il efficace ?"
    ],
    'INTERNE': [
        "Les objectifs de l'entreprise sont-ils définis ?", "Les responsabilités sont-elles clairement attribuées ?", "Les processus sont-ils documentés ?", "Les procédures sont-elles appliquées ?", "Les indicateurs de performance sont-ils suivis ?", "Les risques internes sont-ils identifiés ?", "Les risques sont-ils évalués régulièrement ?", "Les plans d'action sont-ils suivis ?", "Les audits précédents sont-ils clôturés ?", "Les non-conformités sont-elles enregistrées ?", "Les actions correctives sont-elles efficaces ?", "Les réunions de pilotage sont-elles réalisées ?", "Les décisions sont-elles documentées ?", "Les ressources sont-elles suffisantes ?", "Les compétences sont-elles évaluées ?", "Les formations sont-elles planifiées ?", "Les formations sont-elles enregistrées ?", "Les exigences réglementaires sont-elles respectées ?", "Les documents sont-ils maîtrisés ?", "Les enregistrements sont-ils conservés ?", "La communication interne est-elle efficace ?", "Les objectifs sont-ils communiqués aux équipes ?", "Les données sont-elles sécurisées ?", "Les sauvegardes sont-elles réalisées ?", "Les accès sont-ils contrôlés ?", "Les fournisseurs sont-ils évalués ?", "Les contrats sont-ils suivis ?", "Les réclamations sont-elles traitées ?", "Les délais sont-ils respectés ?", "Les audits internes sont-ils planifiés ?", "Les résultats des audits sont-ils analysés ?", "Les opportunités d'amélioration sont-elles identifiées ?", "Les projets sont-ils suivis ?", "Les ressources financières sont-elles contrôlées ?", "Les tableaux de bord sont-ils à jour ?", "Les écarts sont-ils analysés ?", "Les plans stratégiques sont-ils suivis ?", "La direction participe-t-elle au système de management ?", "L'amélioration continue est-elle démontrée ?", "Le système de management est-il efficace ?"
    ],
}


class Command(BaseCommand):
    help = 'Créer les comptes de test et les checklists professionnelles.'

    def handle(self, *args, **options):
        data = [
            ('responsable', 'responsable@audit.com', 'Responsable', 'Audit', 'RESPONSABLE'),
            ('auditeur', 'auditeur@audit.com', 'Auditeur', 'Qualité', 'AUDITEUR'),
            ('client', 'client@audit.com', 'Client', 'Industriel', 'CLIENT'),
        ]
        users = {}
        for username, email, first_name, last_name, role in data:
            user, _ = User.objects.get_or_create(username=username, defaults={'email': email})
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.set_password('123456')
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()
            users[role] = user

        ChecklistItem.objects.all().delete()
        total = 0
        for type_audit, questions in CHECKLISTS.items():
            for ordre, texte in enumerate(questions, start=1):
                ChecklistItem.objects.create(type_audit=type_audit, texte=texte, ordre=ordre, actif=True)
                total += 1

        Audit.objects.get_or_create(
            titre='Audit qualité démo',
            defaults={
                'type_audit': 'QUALITE',
                'date_audit': date.today() + timedelta(days=3),
                'client': users['CLIENT'],
                'auditeur': users['AUDITEUR'],
                'created_by': users['RESPONSABLE'],
                'description': 'Audit de démonstration planifié automatiquement.',
            }
        )
        self.stdout.write(self.style.SUCCESS(f'Données créées : 3 comptes et {total} points de checklist.'))
