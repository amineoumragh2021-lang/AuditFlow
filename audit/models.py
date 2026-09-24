from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


PRIORITIES = [('CRITICAL', 'Critique'), ('HIGH', 'Élevé'), ('MEDIUM', 'Modéré'), ('LOW', 'Faible')]


class Organisation(models.Model):
    nom = models.CharField('Nom', max_length=150, unique=True)

    def __str__(self):
        return self.nom


class Department(models.Model):
    nom = models.CharField('Nom', max_length=100)
    organisation = models.ForeignKey(Organisation, on_delete=models.PROTECT, verbose_name='Organisation')

    class Meta:
        constraints = [models.UniqueConstraint(fields=['organisation', 'nom'], name='department_name_per_org')]

    def __str__(self):
        return f'{self.organisation} · {self.nom}'


class Profile(models.Model):
    ROLE_CHOICES = [
        ('RESPONSABLE', 'Responsable Audit'),
        ('AUDITEUR', 'Auditeur'),
        ('CLIENT', 'Client'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='AUDITEUR')
    telephone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_role_display()}"


class Audit(models.Model):
    STAGES = [('PLANNING', 'Planification'), ('FIELDWORK', 'Travaux terrain'), ('REVIEW', 'Revue'), ('REPORTING', 'Rapport'), ('CLOSED', 'Clôture')]
    organisation = models.ForeignKey(Organisation, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Organisation')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True, blank=True, verbose_name='Département')
    stage = models.CharField('Étape', max_length=20, choices=STAGES, default='PLANNING')
    progress = models.PositiveSmallIntegerField('Progression (%)', default=0, validators=[MaxValueValidator(100)])
    priority = models.CharField('Risque', max_length=10, choices=PRIORITIES, default='MEDIUM')
    end_date = models.DateField('Échéance', null=True, blank=True)
    TYPE_CHOICES = [
        ('QUALITE', 'Audit qualité'),
        ('SECURITE', 'Audit sécurité'),
        ('ENVIRONNEMENT', 'Audit environnement'),
        ('INTERNE', 'Audit interne'),
    ]

    titre = models.CharField(max_length=150)
    type_audit = models.CharField(max_length=30, choices=TYPE_CHOICES, default='QUALITE')
    date_audit = models.DateField()
    description = models.TextField(blank=True)
    client = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audits_client',
        help_text='Client ou département demandeur concerné par cet audit.'
    )
    auditeur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audits_affectes'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audits_crees'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_audit']

    def __str__(self):
        return self.titre


class ChecklistItem(models.Model):
    """Point de contrôle associé à un type d'audit."""
    type_audit = models.CharField(max_length=30, choices=Audit.TYPE_CHOICES)
    texte = models.CharField(max_length=255)
    ordre = models.PositiveIntegerField(default=1)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['type_audit', 'ordre']
        verbose_name = 'Point de checklist'
        verbose_name_plural = 'Points de checklist'

    def __str__(self):
        return f"{self.get_type_audit_display()} - {self.texte}"


class Rapport(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='rapports')
    auteur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='rapports_rediges')
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"Rapport - {self.audit.titre}"

    @property
    def checklist_score(self):
        conformes = self.checklist_reponses.filter(statut='CONFORME').count()
        non_conformes = self.checklist_reponses.filter(statut='NON_CONFORME').count()

        total = conformes + non_conformes

        if total == 0:
            return 0

        return round((conformes / total) * 100)


class ChecklistResponse(models.Model):
    """Réponse de l'auditeur pour chaque point de checklist dans un rapport."""
    STATUT_CHOICES = [
        ('CONFORME', 'Conforme'),
        ('NON_CONFORME', 'Non conforme'),
        ('ABORDABLE', 'Abordable'),
    ]

    rapport = models.ForeignKey(Rapport, on_delete=models.CASCADE, related_name='checklist_reponses')
    item = models.ForeignKey(ChecklistItem, on_delete=models.CASCADE)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='CONFORME')
    remarque = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = 'Réponse checklist'
        verbose_name_plural = 'Réponses checklist'

    def __str__(self):
        if self.statut == 'CONFORME':
            etat = 'Conforme'
        elif self.statut == 'NON_CONFORME':
            etat = 'Non conforme'
        else:
            etat = 'Abordable'
        return f"{self.item.texte} : {etat}"


class Finding(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='findings', verbose_name='Mission')
    titre = models.CharField('Constat', max_length=200)
    description = models.TextField('Description', blank=True)
    priority = models.CharField('Gravité', max_length=10, choices=PRIORITIES, default='MEDIUM')
    resolved = models.BooleanField('Résolu', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre


class Risk(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='risks', verbose_name='Mission')
    titre = models.CharField('Risque', max_length=200)
    description = models.TextField('Description', blank=True)
    impact = models.PositiveSmallIntegerField('Impact (1–5)', default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    likelihood = models.PositiveSmallIntegerField('Probabilité (1–5)', default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    findings = models.ManyToManyField(Finding, blank=True, verbose_name='Constats associés')

    @property
    def priority(self):
        score = self.impact * self.likelihood
        return 'CRITICAL' if score >= 20 else 'HIGH' if score >= 12 else 'MEDIUM' if score >= 6 else 'LOW'

    def get_priority_display(self):
        return dict(PRIORITIES)[self.priority]

    def __str__(self):
        return self.titre


class CorrectiveAction(models.Model):
    STATES = [('OPEN', 'Ouverte'), ('IN_PROGRESS', 'En cours'), ('EVIDENCE', 'Preuve attendue'), ('COMPLETED', 'Terminée')]
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='actions', verbose_name='Mission')
    finding = models.ForeignKey(Finding, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Constat associé')
    titre = models.CharField('Action', max_length=200)
    description = models.TextField('Description / preuve', blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Responsable')
    priority = models.CharField('Priorité', max_length=10, choices=PRIORITIES, default='MEDIUM')
    due_date = models.DateField('Échéance')
    state = models.CharField('État', max_length=20, choices=STATES, default='OPEN')

    @property
    def overdue_days(self):
        return max(0, (timezone.localdate() - self.due_date).days) if self.state != 'COMPLETED' else 0

    @property
    def owner_name(self):
        return (self.owner.get_full_name() or self.owner.username) if self.owner else 'Non affectée'

    @property
    def owner_initial(self):
        return self.owner_name[0].upper() if self.owner else '—'

    def __str__(self):
        return self.titre


class Document(models.Model):
    audit = models.ForeignKey(Audit, on_delete=models.CASCADE, related_name='documents', verbose_name='Mission')
    titre = models.CharField('Titre', max_length=200)
    file = models.FileField('Fichier', upload_to='audit_documents/%Y/%m/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre
