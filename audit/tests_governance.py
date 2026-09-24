from datetime import timedelta
from tempfile import TemporaryDirectory

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .forms import AuditForm
from .models import Audit, Profile, Organisation, Department, Finding, Risk, CorrectiveAction, Document


class GovernanceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager = User.objects.create_user('manager')
        cls.auditor = User.objects.create_user('auditor')
        cls.client_user = User.objects.create_user('customer')
        cls.other = User.objects.create_user('other')
        for user, role in [(cls.manager, 'RESPONSABLE'), (cls.auditor, 'AUDITEUR'), (cls.client_user, 'CLIENT'), (cls.other, 'CLIENT')]:
            Profile.objects.update_or_create(user=user, defaults={'role': role})
        cls.org = Organisation.objects.create(nom='Organisation A')
        cls.department = Department.objects.create(nom='IT', organisation=cls.org)
        cls.audit = Audit.objects.create(titre='Mission visible', date_audit=timezone.localdate(), client=cls.client_user, auditeur=cls.auditor, organisation=cls.org, department=cls.department, stage='FIELDWORK', progress=40)
        cls.private = Audit.objects.create(titre='Mission confidentielle', date_audit=timezone.localdate(), client=cls.other)
        cls.finding = Finding.objects.create(audit=cls.audit, titre='Acces non revus', priority='CRITICAL')
        cls.private_finding = Finding.objects.create(audit=cls.private, titre='Constat confidentiel')
        cls.risk = Risk.objects.create(audit=cls.audit, titre='Acces excessifs', impact=5, likelihood=4)
        cls.risk.findings.add(cls.finding)
        cls.action = CorrectiveAction.objects.create(audit=cls.audit, titre='Revoir les acces', finding=cls.finding, priority='CRITICAL', due_date=timezone.localdate() - timedelta(days=3))
        CorrectiveAction.objects.create(audit=cls.audit, titre='Action terminee', state='COMPLETED', due_date=timezone.localdate() - timedelta(days=5))

    def test_dashboard_metrics_and_nullable_owner(self):
        self.client.force_login(self.client_user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['critical_findings'], 1)
        self.assertEqual(response.context['overdue_actions'], 1)
        self.assertEqual(len(response.context['lifecycle']), 5)
        self.assertEqual(response.context['risk_bubbles'][0]['risk'].priority, 'CRITICAL')
        self.assertEqual(response.context['risk_bubbles'][0]['risk'].finding_count, 1)
        self.assertNotContains(response, 'Mission confidentielle')
        self.assertContains(response, 'Revoir les acces')

    def test_all_workspace_lists_and_settings_render(self):
        self.client.force_login(self.manager)
        for kind in ['findings', 'risks', 'actions', 'documents', 'organisations', 'departments']:
            self.assertEqual(self.client.get(reverse('governance_list', args=[kind])).status_code, 200)
            self.assertEqual(self.client.get(reverse('governance_create', args=[kind])).status_code, 200)
        self.assertEqual(self.client.get(reverse('workspace_settings')).status_code, 200)

    def test_client_cannot_modify_and_auditor_cannot_access_other_mission(self):
        self.client.force_login(self.client_user)
        self.assertEqual(self.client.post(reverse('governance_create', args=['findings']), {'audit': self.audit.pk, 'titre': 'Forbidden', 'priority': 'LOW'}).status_code, 403)
        self.client.force_login(self.auditor)
        self.assertEqual(self.client.get(reverse('governance_edit', args=['findings', self.private_finding.pk])).status_code, 404)
        response = self.client.post(reverse('governance_create', args=['findings']), {'audit': self.private.pk, 'titre': 'Forbidden', 'priority': 'LOW'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('audit', response.context['form'].errors)
        self.assertFalse(Finding.objects.filter(titre='Forbidden').exists())

    def test_actions_creation_edit_and_link_validation(self):
        self.client.force_login(self.manager)
        payload = {'audit': self.audit.pk, 'finding': self.private_finding.pk, 'titre': 'Action nouvelle', 'priority': 'HIGH', 'due_date': timezone.localdate().isoformat(), 'state': 'OPEN'}
        response = self.client.post(reverse('governance_create', args=['actions']), payload)
        self.assertIn('finding', response.context['form'].errors)
        payload['finding'] = self.finding.pk
        self.assertEqual(self.client.post(reverse('governance_create', args=['actions']), payload).status_code, 302)
        action = CorrectiveAction.objects.get(titre='Action nouvelle')
        payload['state'] = 'COMPLETED'
        self.assertEqual(self.client.post(reverse('governance_edit', args=['actions', action.pk]), payload).status_code, 302)
        action.refresh_from_db()
        self.assertEqual(action.state, 'COMPLETED')

    def test_risk_bounds_and_related_finding_validation(self):
        self.client.force_login(self.manager)
        payload = {'audit': self.audit.pk, 'titre': 'Risque invalide', 'impact': 6, 'likelihood': 0}
        response = self.client.post(reverse('governance_create', args=['risks']), payload)
        self.assertIn('impact', response.context['form'].errors)
        self.assertIn('likelihood', response.context['form'].errors)
        payload.update(impact=4, likelihood=3, findings=[self.private_finding.pk])
        response = self.client.post(reverse('governance_create', args=['risks']), payload)
        self.assertIn('findings', response.context['form'].errors)

    def test_organisation_and_search_filters_export_scope(self):
        self.client.force_login(self.manager)
        response = self.client.get(reverse('dashboard'), {'org': self.org.pk, 'q': 'visible'})
        self.assertEqual(response.context['stats']['total_audits'], 1)
        self.assertNotContains(response, 'Mission confidentielle')
        self.assertEqual(self.client.get(reverse('dashboard'), {'quarter': 'bad'}).status_code, 200)
        self.client.force_login(self.client_user)
        self.audit.titre = '=SUM(A1)'
        self.audit.save()
        export = self.client.get(reverse('export_missions'))
        self.assertContains(export, "'=SUM(A1)")
        self.assertNotContains(export, 'Mission confidentielle')

    def test_document_upload_download_and_scope(self):
        with TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            self.client.force_login(self.auditor)
            response = self.client.post(reverse('governance_create', args=['documents']), {'audit': self.audit.pk, 'titre': 'Preuve', 'file': SimpleUploadedFile('preuve.txt', b'preuve audit')})
            self.assertEqual(response.status_code, 302)
            document = Document.objects.get(titre='Preuve')
            url = reverse('download_document', args=[document.pk])
            response = self.client.get(url)
            self.assertEqual(b''.join(response.streaming_content), b'preuve audit')
            self.assertIn('attachment', response['Content-Disposition'])
            self.client.force_login(self.other)
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_audit_department_and_date_validation(self):
        other_org = Organisation.objects.create(nom='Autre organisation')
        data = {'titre': 'Test', 'type_audit': 'QUALITE', 'date_audit': '2026-09-24', 'end_date': '2026-09-23', 'organisation': other_org.pk, 'department': self.department.pk, 'stage': 'PLANNING', 'progress': 120, 'priority': 'MEDIUM'}
        form = AuditForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue({'department', 'end_date', 'progress'}.issubset(form.errors))
