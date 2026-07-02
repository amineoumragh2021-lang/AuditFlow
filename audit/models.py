from django.db import models
from django.contrib.auth.models import User


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
