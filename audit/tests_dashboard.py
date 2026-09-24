from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Audit, ChecklistItem, ChecklistResponse, Profile, Rapport


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user('manager')
        cls.auditor = User.objects.create_user('auditor')
        cls.customer = User.objects.create_user('customer')
        cls.other = User.objects.create_user('other')
        for user, role in [(cls.manager, 'RESPONSABLE'), (cls.auditor, 'AUDITEUR'), (cls.customer, 'CLIENT'), (cls.other, 'CLIENT')]:
            Profile.objects.update_or_create(user=user, defaults={'role': role})
        cls.audit = Audit.objects.create(titre='Mission visible', date_audit=timezone.localdate(), auditeur=cls.auditor, client=cls.customer)
        cls.report = Rapport.objects.create(audit=cls.audit, auteur=cls.auditor, contenu='Résultats')
        for index, status in enumerate(['CONFORME', 'NON_CONFORME', 'ABORDABLE']):
            item = ChecklistItem.objects.create(type_audit='QUALITE', texte=f'Point {index}')
            ChecklistResponse.objects.create(rapport=cls.report, item=item, statut=status)
        cls.foreign_audit = Audit.objects.create(titre='Mission confidentielle', date_audit=timezone.localdate(), client=cls.other)
        Rapport.objects.create(audit=cls.foreign_audit, auteur=cls.manager, contenu='Privé')
        cls.future = Audit.objects.create(titre='Mission future', date_audit=timezone.localdate() + timedelta(days=20), client=cls.customer, auditeur=cls.auditor)
        Rapport.objects.create(audit=cls.future, auteur=cls.auditor, contenu='Rapport futur masqué')

    def test_anonymous_redirect(self):
        self.assertRedirects(self.client.get(reverse('dashboard')), '/login/?next=/')

    def test_role_scoping_and_compliance(self):
        for user in [self.customer, self.auditor]:
            self.client.force_login(user)
            response = self.client.get(reverse('dashboard'))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'Mission visible')
            self.assertNotContains(response, 'Mission confidentielle')
            self.assertEqual(response.context['stats']['conformite'], 50)
            self.assertEqual(response.context['stats']['non_conformes'], 1)
            self.assertEqual(response.context['stats']['abordables'], 1)
            self.assertEqual(response.context['stats']['total_rapports'], 1)
            self.assertNotContains(response, 'Nouvelle mission')
            self.assertEqual(len(response.context['missions']), 2)

    def test_manager_has_all_missions_and_create_action(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'Mission confidentielle')
        self.assertContains(response, 'Nouvelle mission')
        self.assertEqual(response.context['stats']['total_audits'], 3)

    def test_empty_dashboard_has_no_fabricated_score(self):
        user = User.objects.create_user('empty')
        Profile.objects.update_or_create(user=user, defaults={'role': 'CLIENT'})
        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['stats']['conformite'])
        self.assertContains(response, 'Aucune mission disponible.')
        self.assertTrue(all(metric['score'] is None for metric in response.context['type_metrics']))

    def test_past_audit_without_report_is_counted(self):
        Audit.objects.create(titre='À restituer', date_audit=timezone.localdate() - timedelta(days=1), client=self.customer)
        self.client.force_login(self.customer)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.context['stats']['sans_rapport'], 1)
        self.assertContains(response, 'Sans rapport')
