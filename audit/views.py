from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from datetime import datetime, timedelta, date
from .models import Audit, Rapport, ChecklistItem, ChecklistResponse, Profile
from .forms import UserForm, RegisterForm, AuditForm, RapportForm, RapportChecklistForm
from .decorators import role_required
from django.http import HttpResponse
from django.db.models import Count, Q
from django.utils import timezone
from .governance import filter_audits, board_context, plan_start


def get_user_role(user):
    """Retourne le rôle de l’utilisateur et crée un profil Client si le profil manque."""
    profile, _ = Profile.objects.get_or_create(user=user, defaults={'role': 'CLIENT'})
    return profile.role



def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        user_obj = User.objects.filter(email=email).first()
        if user_obj:
            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )

            if user is not None:
                login(request, user)
                request.session.set_expiry(30 * 24 * 60 * 60 if request.POST.get('remember_me') == '1' else 0)
                return redirect('dashboard')

        messages.error(request, 'Email ou mot de passe incorrect.')

    return render(request, 'audit/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Votre compte client a été créé avec succès.')
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'audit/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    user = request.user
    role = get_user_role(user)

    if role == 'AUDITEUR':
        audits = Audit.objects.filter(auditeur=user)
        rapports = Rapport.objects.filter(auteur=user)
    elif role == 'CLIENT':
        audits = Audit.objects.filter(client=user)
        rapports = Rapport.objects.filter(audit__client=user)
    else:
        audits = Audit.objects.all()
        rapports = Rapport.objects.all()

    today = timezone.localdate()
    audits = filter_audits(request)
    rapports = rapports.filter(audit__in=audits)
    rapports = rapports.filter(audit__date_audit__lte=today)
    responses = ChecklistResponse.objects.filter(rapport__in=rapports)
    counts = responses.aggregate(
        conformes=Count('pk', filter=Q(statut='CONFORME')),
        non_conformes=Count('pk', filter=Q(statut='NON_CONFORME')),
        abordables=Count('pk', filter=Q(statut='ABORDABLE')),
    )
    evaluated = counts['conformes'] + counts['non_conformes']
    completed_ids = set(rapports.values_list('audit_id', flat=True))
    stats = {
        'total_audits': audits.count(),
        'audits_a_venir': audits.filter(date_audit__gte=datetime.now().date()).count(),
        'audits_realises': rapports.values('audit').distinct().count(),
        'total_rapports': rapports.count(),
        'total_users': User.objects.count(),
        'total_checklist': ChecklistItem.objects.filter(actif=True).count(),
        **counts,
        'conformite': round(counts['conformes'] * 100 / evaluated) if evaluated else None,
        'controles': evaluated,
        'sans_rapport': audits.filter(date_audit__lt=today).exclude(pk__in=completed_ids).count(),
    }

    missions = list(audits.select_related('auditeur', 'client').order_by('-date_audit'))
    for mission in missions:
        mission.dashboard_state = 'Rapport disponible' if mission.pk in completed_ids else ('Planifié' if mission.date_audit >= today else 'Sans rapport')
        mission.dashboard_tone = 'green' if mission.pk in completed_ids else ('blue' if mission.date_audit >= today else 'amber')
    type_metrics = []
    for code, label in Audit.TYPE_CHOICES:
        group = responses.filter(rapport__audit__type_audit=code).aggregate(
            ok=Count('pk', filter=Q(statut='CONFORME')),
            ko=Count('pk', filter=Q(statut='NON_CONFORME')),
        )
        total = group['ok'] + group['ko']
        type_metrics.append({'label': label.replace('Audit ', ''), 'score': round(group['ok'] * 100 / total) if total else None})
    month_start = plan_start(request)
    months = []
    for offset in range(6):
        index = month_start.month - 1 + offset
        months.append(date(month_start.year + index // 12, index % 12 + 1, 1))
    end_index = month_start.month - 1 + 6
    plan_end = date(month_start.year + end_index // 12, end_index % 12 + 1, 1)
    plan = audits.filter(Q(date_audit__gte=month_start) | Q(end_date__gte=month_start), date_audit__lt=plan_end).order_by('date_audit')[:6]
    for mission in plan:
        start = max(month_start, mission.date_audit)
        mission.month_column = (start.year - month_start.year) * 12 + start.month - month_start.month + 1
        end = mission.end_date or mission.date_audit
        mission.month_span = max(1, min(7 - mission.month_column, (end.year - start.year) * 12 + end.month - start.month + 1))
    derniers_audits = audits.order_by('-created_at')[:5]
    derniers_rapports = rapports.order_by('-date_creation')[:5]

    return render(request, 'audit/dashboard.html', {
        'stats': stats,
        'derniers_audits': derniers_audits,
        'derniers_rapports': derniers_rapports,
        'missions': missions,
        'type_metrics': type_metrics,
        'months': months,
        'plan': plan,
        **board_context(request, audits),
        'findings': responses.filter(statut='NON_CONFORME').select_related('item', 'rapport__audit', 'rapport__auteur')[:4],
        'today': today,
    })


@login_required
@role_required('RESPONSABLE')
def users_list(request):
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'audit/users_list.html', {'users': users})


@login_required
@role_required('RESPONSABLE')
def user_create(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur ajouté avec succès.')
            return redirect('users_list')
    else:
        form = UserForm()
    return render(request, 'audit/form_page.html', {
        'form': form,
        'title': 'Ajouter un utilisateur',
        'button': 'Enregistrer',
    })


@login_required
def audits_list(request):
    role = get_user_role(request.user)
    if role == 'AUDITEUR':
        audits = Audit.objects.filter(auditeur=request.user)
    elif role == 'CLIENT':
        audits = Audit.objects.filter(client=request.user)
    else:
        audits = Audit.objects.all()
    return render(request, 'audit/audits_list.html', {'audits': audits})


@login_required
@role_required('RESPONSABLE')
def audit_create(request):
    if request.method == 'POST':
        form = AuditForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.created_by = request.user
            audit.save()
            messages.success(request, 'Audit planifié avec succès.')
            return redirect('audits_list')
    else:
        form = AuditForm()
    return render(request, 'audit/form_page.html', {
        'form': form,
        'title': 'Planifier un audit',
        'button': 'Créer l’audit',
    })


@login_required
@role_required('RESPONSABLE')
def audit_update(request, pk):
    audit = get_object_or_404(Audit, pk=pk)

    if request.method == 'POST':
        form = AuditForm(request.POST, instance=audit)

        if form.is_valid():
            form.save()
            messages.success(request, "Audit modifié avec succès.")
            return redirect('audits_list')
    else:
        form = AuditForm(instance=audit)

    return render(request, 'audit/form_page.html', {
        'form': form,
        'title': 'Modifier un audit',
        'button': 'Enregistrer les modifications',
    })


@login_required
@role_required('RESPONSABLE')
def checklist_list(request):
    items = ChecklistItem.objects.all().order_by('type_audit', 'ordre')
    grouped = {}
    for item in items:
        grouped.setdefault(item.get_type_audit_display(), []).append(item)
    return render(request, 'audit/checklist_list.html', {'grouped': grouped})


@login_required
@role_required('RESPONSABLE')
def checklist_create(request):
    if request.method == 'POST':
        type_audit = request.POST.get('type_audit')
        textes = request.POST.getlist('texte[]')
        created = 0
        for index, texte in enumerate(textes, start=1):
            texte = texte.strip()
            if texte:
                ChecklistItem.objects.create(type_audit=type_audit, texte=texte, ordre=index)
                created += 1
        if created:
            messages.success(request, f'{created} point(s) de checklist ajouté(s).')
            return redirect('checklist_list')
        messages.error(request, 'Ajoutez au moins un point de checklist.')

    return render(request, 'audit/checklist_form.html', {
        'types_audit': Audit.TYPE_CHOICES,
    })


@login_required
def rapports_list(request):
    role = get_user_role(request.user)
    today = date.today()

    if role == 'AUDITEUR':
        rapports = Rapport.objects.filter(
            auteur=request.user,
            audit__date_audit__lte=today
        )
    elif role == 'CLIENT':
        rapports = Rapport.objects.filter(
            audit__client=request.user,
            audit__date_audit__lte=today
        )
    else:
        rapports = Rapport.objects.filter(
            audit__date_audit__lte=today
        )

    rapports = rapports.select_related('audit', 'auteur', 'audit__client').order_by('-date_creation')
    return render(request, 'audit/rapports_list.html', {'rapports': rapports})


@login_required
@role_required('AUDITEUR')
def rapport_create(request):
    """Page simple : choix manuel de l'audit, sans checklist dynamique."""
    if request.method == 'POST':
        form = RapportForm(request.POST, user=request.user)
        if form.is_valid():
            rapport = form.save(commit=False)
            rapport.auteur = request.user
            rapport.save()
            messages.success(request, 'Rapport ajouté avec succès.')
            return redirect('rapports_list')
    else:
        form = RapportForm(user=request.user)
    return render(request, 'audit/form_page.html', {
        'form': form,
        'title': 'Ajouter un rapport simple',
        'button': 'Publier le rapport',
    })


@login_required
@role_required('AUDITEUR')
def rapport_create_for_audit(request, audit_id):
    audit = get_object_or_404(Audit, pk=audit_id, auditeur=request.user)

    # Interdire la rédaction avant la date exacte de l'audit
    if audit.date_audit > date.today():
        messages.error(
            request,
            "Vous ne pouvez pas rédiger le rapport avant la date prévue de l'audit."
        )
        return redirect('audits_list')

    # Un seul rapport par audit : si le rapport existe, l'auditeur peut le modifier dans le détail
    rapport_existant = Rapport.objects.filter(audit=audit).first()
    if rapport_existant:
        messages.warning(
            request,
            "Un rapport existe déjà pour cet audit. Vous pouvez le modifier depuis le détail du rapport."
        )
        return redirect('rapport_detail', pk=rapport_existant.pk)

    checklist_items = ChecklistItem.objects.filter(
        type_audit=audit.type_audit,
        actif=True
    ).order_by('ordre')

    if request.method == 'POST':
        form = RapportChecklistForm(request.POST)

        if form.is_valid():
            rapport = form.save(commit=False)
            rapport.audit = audit
            rapport.auteur = request.user
            rapport.save()

            if hasattr(audit, 'statut'):
                audit.statut = 'TERMINE'
                audit.save()

            for item in checklist_items:
                value = request.POST.get(f'item_{item.id}', 'CONFORME')

                if value not in ('CONFORME', 'NON_CONFORME', 'ABORDABLE'):
                    value = 'CONFORME'

                ChecklistResponse.objects.create(
                    rapport=rapport,
                    item=item,
                    statut=value,
                    remarque=request.POST.get(f'remarque_{item.id}', '').strip()
                )

            messages.success(request, 'Rapport avec checklist ajouté avec succès.')
            return redirect('rapport_detail', pk=rapport.pk)

    else:
        form = RapportChecklistForm()

    return render(request, 'audit/rapport_checklist_form.html', {
        'form': form,
        'audit': audit,
        'checklist_items': checklist_items,
    })


@login_required
def rapport_detail(request, pk):
    rapport = get_object_or_404(
        Rapport.objects.select_related(
            'audit',
            'auteur',
            'audit__client'
        ).prefetch_related(
            'checklist_reponses__item'
        ),
        pk=pk
    )

    role = get_user_role(request.user)

    if role == 'AUDITEUR' and rapport.auteur != request.user:
        messages.error(request, "Vous n'avez pas l'autorisation de consulter ce rapport.")
        return redirect('rapports_list')

    if role == 'CLIENT' and rapport.audit.client != request.user:
        messages.error(request, "Vous n'avez pas l'autorisation de consulter ce rapport.")
        return redirect('rapports_list')

    checklist = rapport.checklist_reponses.all()

    conformes = checklist.filter(statut='CONFORME').count()
    non_conformes = checklist.filter(statut='NON_CONFORME').count()
    abordables = checklist.filter(statut='ABORDABLE').count()

    total = conformes + non_conformes
    score = round((conformes / total) * 100, 2) if total > 0 else 0

    return render(request, 'audit/rapport_detail.html', {
        'rapport': rapport,
        'checklist': checklist,
        'conformes': conformes,
        'non_conformes': non_conformes,
        'abordables': abordables,
        'score': score,
    })
@login_required
def calendar_view(request):
    """Calendrier des audits - accessible à tous les rôles."""
    import calendar as cal
    
    user = request.user
    role = get_user_role(user)

    if role == 'AUDITEUR':
        audits = Audit.objects.filter(auditeur=user)
    elif role == 'CLIENT':
        audits = Audit.objects.filter(client=user)
    else:
        audits = Audit.objects.all()

    # Récupérer la date actuelle
    today = datetime.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Générer le calendrier
    days_matrix = cal.monthcalendar(year, month)
    
    # Créer un dictionnaire des audits par date
    audits_by_date = {}
    month_start = datetime(year, month, 1).date()
    if month == 12:
        month_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        month_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    month_audits = audits.filter(date_audit__gte=month_start, date_audit__lte=month_end)
    
    for audit in month_audits:
        if audit.date_audit not in audits_by_date:
            audits_by_date[audit.date_audit] = []
        audits_by_date[audit.date_audit].append(audit)
    
    # Construire les jours du calendrier
    calendar_days = []
    weekday_start = cal.monthrange(year, month)[0]  # 0=Monday, 6=Sunday
    
    # Ajouter les jours du mois précédent
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    prev_month_days = cal.monthrange(prev_year, prev_month)[1]
    
    for day in range(prev_month_days - weekday_start + 1, prev_month_days + 1):
        prev_date = datetime(prev_year, prev_month, day).date()
        calendar_days.append({
            'day': day,
            'date': prev_date,
            'is_other_month': True,
            'is_today': False,
            'audits': audits_by_date.get(prev_date, [])
        })
    
    # Ajouter les jours du mois courant
    for day in range(1, cal.monthrange(year, month)[1] + 1):
        current_date = datetime(year, month, day).date()
        calendar_days.append({
            'day': day,
            'date': current_date,
            'is_other_month': False,
            'is_today': current_date == today,
            'audits': audits_by_date.get(current_date, [])
        })
    
    # Ajouter les jours du mois suivant pour compléter la grille
    next_days = 42 - len(calendar_days)  # 6 lignes × 7 jours
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    for day in range(1, next_days + 1):
        next_date = datetime(next_year, next_month, day).date()
        calendar_days.append({
            'day': day,
            'date': next_date,
            'is_other_month': True,
            'is_today': False,
            'audits': audits_by_date.get(next_date, [])
        })
    
    # Navigation
    if month == 1:
        prev_month_url = f"?year={year-1}&month=12"
    else:
        prev_month_url = f"?year={year}&month={month-1}"
    
    if month == 12:
        next_month_url = f"?year={year+1}&month=1"
    else:
        next_month_url = f"?year={year}&month={month+1}"
    
    context = {
        'calendar_days': calendar_days,
        'today': today,
        'current_month': f"{cal.month_name[month]} {year}",
        'year': year,
        'month': month,
        'prev_month_url': prev_month_url,
        'next_month_url': next_month_url,
    }
    return render(request, 'audit/calendar.html', context)

@login_required
def rapport_pdf(request, pk):
    rapport = get_object_or_404(
        Rapport.objects.select_related('audit', 'auteur', 'audit__client').prefetch_related('checklist_reponses__item'),
        pk=pk
    )

    role = get_user_role(request.user)
    if role == 'AUDITEUR' and rapport.auteur != request.user:
        messages.error(request, "Vous n'avez pas l'autorisation de télécharger ce rapport.")
        return redirect('rapports_list')
    if role == 'CLIENT' and rapport.audit.client != request.user:
        messages.error(request, "Vous n'avez pas l'autorisation de télécharger ce rapport.")
        return redirect('rapports_list')

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import cm
    except ImportError:
        return HttpResponse(
            "Le module reportlab n'est pas installé. Exécutez : pip install reportlab",
            status=500
        )

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_{rapport.id}.pdf"'

    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 2 * cm

    p.setFont("Helvetica-Bold", 18)
    p.drawString(2 * cm, y, "Rapport d'audit")
    y -= 1 * cm

    p.setFont("Helvetica-Bold", 14)
    p.drawString(2 * cm, y, rapport.audit.titre)
    y -= 0.8 * cm

    p.setFont("Helvetica", 10)
    p.drawString(2 * cm, y, f"Type : {rapport.audit.get_type_audit_display()}")
    y -= 0.5 * cm
    p.drawString(2 * cm, y, f"Date audit : {rapport.audit.date_audit}")
    y -= 0.5 * cm
    p.drawString(2 * cm, y, f"Client : {(rapport.audit.client.get_full_name() or rapport.audit.client.username) if rapport.audit.client else 'Non affecté'}")
    y -= 0.5 * cm
    p.drawString(2 * cm, y, f"Auditeur : {(rapport.auteur.get_full_name() or rapport.auteur.username) if rapport.auteur else 'Non affecté'}")
    y -= 0.5 * cm
    p.drawString(2 * cm, y, f"Score : {rapport.checklist_score}%")
    y -= 1 * cm

    p.setFont("Helvetica-Bold", 12)
    p.drawString(2 * cm, y, "Observations et recommandations")
    y -= 0.6 * cm

    p.setFont("Helvetica", 10)
    for line in rapport.contenu.splitlines():
        p.drawString(2 * cm, y, line[:100])
        y -= 0.45 * cm
        if y < 2 * cm:
            p.showPage()
            y = height - 2 * cm

    y -= 0.5 * cm
    p.setFont("Helvetica-Bold", 12)
    p.drawString(2 * cm, y, "Checklist")
    y -= 0.6 * cm

    p.setFont("Helvetica", 9)
    for rep in rapport.checklist_reponses.all():
        texte = f"{rep.item.ordre}. {rep.item.texte} - {rep.get_statut_display()}"
        p.drawString(2 * cm, y, texte[:120])
        y -= 0.45 * cm

        if rep.remarque:
            p.drawString(2.5 * cm, y, f"Remarque : {rep.remarque[:100]}")
            y -= 0.45 * cm

        if y < 2 * cm:
            p.showPage()
            y = height - 2 * cm
            p.setFont("Helvetica", 9)

    p.save()
    return response


# Alias pour l'inscription client
def inscription_client(request):
    return register_view(request)


@login_required
def audit_detail(request, pk):
    audit = get_object_or_404(Audit, pk=pk)
    role = get_user_role(request.user)

    if role == 'AUDITEUR' and audit.auditeur != request.user:
        messages.error(request, "Vous n'avez pas l'autorisation de consulter cet audit.")
        return redirect('audits_list')

    if role == 'CLIENT' and audit.client != request.user:
        messages.error(request, "Vous n'avez pas l'autorisation de consulter cet audit.")
        return redirect('audits_list')

    return render(request, 'audit/audit_detail.html', {'audit': audit})





# Version finale : modifier rapport par l'auditeur
@login_required
@role_required('AUDITEUR')
def rapport_modifier(request, pk):
    rapport = get_object_or_404(
        Rapport.objects.select_related('audit', 'auteur')
        .prefetch_related('checklist_reponses__item'),
        pk=pk,
        auteur=request.user
    )

    checklist_items = ChecklistItem.objects.filter(
        type_audit=rapport.audit.type_audit,
        actif=True
    ).order_by('ordre')

    if request.method == 'POST':
        rapport.contenu = request.POST.get('contenu', '').strip()
        rapport.save()

        for item in checklist_items:
            valeur = request.POST.get(f'item_{item.id}', 'CONFORME')

            ChecklistResponse.objects.update_or_create(
                rapport=rapport,
                item=item,
                defaults={
                    'statut': valeur,
                    'remarque': request.POST.get(
                        f'remarque_{item.id}', ''
                    ).strip()
                }
            )

        messages.success(request, "Rapport modifié avec succès.")
        return redirect('rapport_detail', pk=rapport.pk)

    return render(request, 'audit/rapport_modifier.html', {
        'rapport': rapport,
        'checklist_items': checklist_items,
    })
