"""Governance workspace: scoped records, dashboard metrics and editing."""
import csv
from datetime import date, timedelta
from pathlib import Path

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseForbidden, FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Audit, Organisation, Department, Finding, Risk, CorrectiveAction, Document, ChecklistResponse, PRIORITIES


def role(user):
    return getattr(getattr(user, 'profile', None), 'role', 'CLIENT')


def visible_audits(user):
    qs = Audit.objects.all()
    if role(user) == 'AUDITEUR':
        return qs.filter(auditeur=user)
    if role(user) == 'CLIENT':
        return qs.filter(client=user)
    return qs


def filter_audits(request):
    qs = visible_audits(request.user)
    org = request.GET.get('org', '')
    if org.isdigit():
        qs = qs.filter(organisation_id=int(org))
    quarter = request.GET.get('quarter', '')
    if quarter:
        try:
            year, number = map(int, quarter.split('-Q'))
            if number not in range(1, 5) or year not in range(1900, 9999):
                raise ValueError
            start = date(year, (number - 1) * 3 + 1, 1)
            end = date(year + 1, 1, 1) if number == 4 else date(year, number * 3 + 1, 1)
            qs = qs.filter(date_audit__gte=start, date_audit__lt=end)
        except ValueError:
            pass
    query = request.GET.get('q', '').strip()
    if query:
        qs = qs.filter(Q(titre__icontains=query) | Q(description__icontains=query) | Q(auditeur__first_name__icontains=query) | Q(auditeur__last_name__icontains=query) | Q(findings__titre__icontains=query)).distinct()
    return qs


def plan_start(request):
    try:
        year, quarter = map(int, request.GET.get('quarter', '').split('-Q'))
        if quarter not in range(1, 5) or year not in range(1900, 9999):
            raise ValueError
        return date(year, (quarter - 1) * 3 + 1, 1)
    except ValueError:
        return timezone.localdate().replace(day=1)


def board_context(request, audits):
    today = timezone.localdate()
    all_visible = visible_audits(request.user)
    findings = Finding.objects.filter(audit__in=audits).select_related('audit')
    actions = CorrectiveAction.objects.filter(audit__in=audits).select_related('audit', 'owner')
    risks = Risk.objects.filter(audit__in=audits).select_related('audit').annotate(finding_count=Count('findings'))
    domain = request.GET.get('domain', '')
    if domain in dict(Audit.TYPE_CHOICES):
        risks = risks.filter(audit__type_audit=domain)
    bubbles = []
    risk_counts = dict.fromkeys(dict(PRIORITIES), 0)
    for risk in risks:
        risk_counts[risk.priority] += 1
        bubbles.append({'risk': risk, 'x': 38 + (risk.impact - 1) * 54, 'y': 226 - (risk.likelihood - 1) * 48, 'radius': min(23, 7 + risk.finding_count * 3)})
    lifecycle = []
    total = audits.count()
    for code, label in Audit.STAGES:
        count = audits.filter(stage=code).count()
        lifecycle.append({'label': label, 'count': count, 'percent': round(count * 100 / total) if total else 0})
    departments = Department.objects.filter(pk__in=audits.values('department_id')).order_by('nom')
    metrics = []
    for department in departments:
        responses = ChecklistResponse.objects.filter(rapport__audit__in=audits, rapport__audit__department=department, rapport__audit__date_audit__lte=today)
        if role(request.user) == 'AUDITEUR':
            responses = responses.filter(rapport__auteur=request.user)
        counts = responses.aggregate(ok=Count('pk', filter=Q(statut='CONFORME')), ko=Count('pk', filter=Q(statut='NON_CONFORME')))
        denominator = counts['ok'] + counts['ko']
        metrics.append({'label': department.nom, 'score': round(counts['ok'] * 100 / denominator) if denominator else None})
    quarter_choices = []
    years = set(all_visible.dates('date_audit', 'year').values_list('date_audit__year', flat=True)) | {today.year}
    for year in sorted(years, reverse=True):
        for quarter in range(1, 5):
            quarter_choices.append(f'{year}-Q{quarter}')
    selected_actions = actions
    if request.GET.get('actions', 'open') == 'open':
        selected_actions = actions.exclude(state='COMPLETED')
    elif request.GET.get('actions') == 'completed':
        selected_actions = actions.filter(state='COMPLETED')
    overdue = actions.filter(due_date__lt=today).exclude(state='COMPLETED')
    period_start = today - timedelta(days=90)
    previous_start = period_start - timedelta(days=90)
    current_count = all_visible.filter(date_audit__gte=period_start, date_audit__lte=today).count()
    previous_count = all_visible.filter(date_audit__gte=previous_start, date_audit__lt=period_start).count()
    return {
        'lifecycle': lifecycle, 'risk_bubbles': bubbles,
        'risk_legend': [{'code': code, 'label': label, 'count': risk_counts[code]} for code, label in PRIORITIES],
        'board_findings': findings.order_by('-created_at')[:12],
        'critical_findings': findings.filter(priority='CRITICAL', resolved=False).count(),
        'finding_total': findings.count(), 'active_audits': audits.exclude(stage='CLOSED').count(),
        'overdue_actions': overdue.count(), 'open_actions': actions.exclude(state='COMPLETED').count(),
        'corrective_actions': selected_actions.order_by('due_date')[:4],
        'all_actions': actions.order_by('due_date')[:12],
        'notifications': overdue.order_by('due_date')[:6], 'notification_count': overdue.count(),
        'department_metrics': metrics, 'domains': Audit.TYPE_CHOICES,
        'organisations': Organisation.objects.filter(pk__in=all_visible.values('organisation_id')),
        'quarter_choices': quarter_choices, 'filter_query': request.GET.urlencode(),
        'audit_trend': round((current_count - previous_count) * 100 / previous_count) if previous_count else None,
    }


MODULES = {
    'findings': (Finding, 'Constats', ['audit', 'titre', 'description', 'priority', 'resolved']),
    'risks': (Risk, 'Risques', ['audit', 'titre', 'description', 'impact', 'likelihood', 'findings']),
    'actions': (CorrectiveAction, 'Actions correctives', ['audit', 'finding', 'titre', 'description', 'owner', 'priority', 'due_date', 'state']),
    'documents': (Document, 'Documents', ['audit', 'titre', 'file']),
    'organisations': (Organisation, 'Organisations', ['nom']),
    'departments': (Department, 'Départements', ['organisation', 'nom']),
}


def module_config(kind):
    if kind not in MODULES:
        raise Http404
    return MODULES[kind]


def records(user, kind):
    model, _, _ = module_config(kind)
    if kind in ['organisations', 'departments']:
        return model.objects.all() if role(user) == 'RESPONSABLE' else model.objects.none()
    return model.objects.filter(audit__in=visible_audits(user)).select_related('audit')


@login_required
def module_list(request, kind):
    model, title, _ = module_config(kind)
    qs = records(request.user, kind)
    query = request.GET.get('q', '').strip()
    if query:
        qs = qs.filter(**{('nom' if kind in ['organisations', 'departments'] else 'titre') + '__icontains': query})
    if 'audit' in request.GET and kind not in ['organisations', 'departments']:
        qs = qs.filter(audit_id=request.GET['audit']) if request.GET['audit'].isdigit() else qs.none()
    if kind == 'actions':
        if request.GET.get('state') in dict(CorrectiveAction.STATES):
            qs = qs.filter(state=request.GET['state'])
        if request.GET.get('overdue') == '1':
            qs = qs.filter(due_date__lt=timezone.localdate()).exclude(state='COMPLETED')
    return render(request, 'audit/governance_list.html', {
        'title': title, 'kind': kind, 'records': qs.order_by('-pk'),
        'can_edit': role(request.user) != 'CLIENT' and (kind not in ['organisations', 'departments'] or role(request.user) == 'RESPONSABLE'),
        'action_states': CorrectiveAction.STATES,
    })


@login_required
def module_edit(request, kind, pk=None):
    model, title, fields = module_config(kind)
    if role(request.user) == 'CLIENT' or (kind in ['organisations', 'departments'] and role(request.user) != 'RESPONSABLE'):
        return HttpResponseForbidden('Accès réservé aux responsables et auditeurs autorisés.')
    instance = get_object_or_404(records(request.user, kind), pk=pk) if pk else None
    form_class = forms.modelform_factory(model, fields=fields, widgets={'due_date': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')})
    form = form_class(request.POST or None, request.FILES or None, instance=instance)
    scoped = visible_audits(request.user)
    if kind == 'departments' and instance:
        form.fields['organisation'].disabled = True
    if 'audit' in form.fields:
        form.fields['audit'].queryset = scoped
        if instance:
            # Moving a record could expose its linked documents or findings to a different client.
            form.fields['audit'].disabled = True
        elif request.GET.get('audit', '').isdigit():
            form.fields['audit'].initial = scoped.filter(pk=request.GET['audit']).first()
    for name in ['finding', 'findings']:
        if name in form.fields:
            form.fields[name].queryset = Finding.objects.filter(audit__in=scoped)
    if 'owner' in form.fields:
        form.fields['owner'].queryset = User.objects.filter(Q(profile__role='RESPONSABLE') | Q(audits_affectes__in=scoped) | Q(audits_client__in=scoped)).distinct()
    if request.method == 'POST' and form.is_valid():
        audit = form.cleaned_data.get('audit')
        linked = form.cleaned_data.get('findings')
        finding = form.cleaned_data.get('finding')
        if finding and finding.audit_id != audit.pk:
            form.add_error('finding', 'Le constat doit appartenir à la mission choisie.')
        if linked is not None and linked.exclude(audit=audit).exists():
            form.add_error('findings', 'Les constats doivent appartenir à la mission choisie.')
        if not form.errors:
            form.save()
            messages.success(request, 'Enregistrement effectué.')
            return redirect('governance_list', kind=kind)
    return render(request, 'audit/form_page.html', {'form': form, 'title': f'{title} · ' + ('Modifier' if pk else 'Ajouter'), 'button': 'Enregistrer'})


@login_required
def download_document(request, pk):
    document = get_object_or_404(records(request.user, 'documents'), pk=pk)
    try:
        return FileResponse(document.file.open('rb'), as_attachment=True, filename=Path(document.file.name).name)
    except FileNotFoundError:
        raise Http404('Fichier indisponible')


@login_required
def settings_view(request):
    form_class = forms.modelform_factory(User, fields=['first_name', 'last_name'])
    form = form_class(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profil mis à jour.')
        return redirect('workspace_settings')
    return render(request, 'audit/workspace_settings.html', {'form': form})


def safe_cell(value):
    text = str(value or '')
    return "'" + text if text.lstrip().startswith(('=', '+', '-', '@')) else text


@login_required
def export_missions(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="auditflow-missions.csv"'
    response.write('\ufeff')
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Mission', 'Périmètre', 'Organisation', 'Département', 'Auditeur', 'Début', 'Échéance', 'Progression (%)', 'Risque', 'Étape'])
    for audit in filter_audits(request).select_related('organisation', 'department', 'auditeur'):
        writer.writerow([safe_cell(value) for value in [audit.titre, audit.description, audit.organisation, audit.department, audit.auditeur, audit.date_audit, audit.end_date, audit.progress, audit.get_priority_display(), audit.get_stage_display()]])
    return response
