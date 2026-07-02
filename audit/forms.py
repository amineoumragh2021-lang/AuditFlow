from django import forms
from django.contrib.auth.models import User
from .models import Audit, Rapport, Profile


class UserForm(forms.ModelForm):
    """Formulaire réservé au Responsable Audit pour créer les comptes internes."""
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}),
        min_length=6,
    )
    role = forms.ChoiceField(label='Rôle', choices=Profile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
            'username': "Nom d'utilisateur",
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'username': forms.TextInput(attrs={'placeholder': "Nom d'utilisateur"}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Cet email est déjà utilisé.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username

    def save(self, commit=True):
        role = self.cleaned_data.pop('role')
        password = self.cleaned_data.pop('password')
        user = super().save(commit=False)
        user.email = user.email.lower()
        user.set_password(password)
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = role
            profile.save()
        return user


class RegisterForm(forms.ModelForm):
    """Inscription publique : seul le rôle CLIENT est autorisé."""
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'placeholder': 'Mot de passe'}),
        min_length=6,
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'email': 'Email',
            'username': "Nom d'utilisateur",
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Prénom'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Nom'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'username': forms.TextInput(attrs={'placeholder': "Nom d'utilisateur"}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Cet email est déjà utilisé.')
        return email

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username

    def save(self, commit=True):
        password = self.cleaned_data.pop('password')
        user = super().save(commit=False)
        user.email = user.email.lower()
        user.set_password(password)
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = 'CLIENT'
            profile.save()
        return user


class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['titre', 'type_audit', 'date_audit', 'client', 'auditeur', 'description']
        labels = {
            'titre': 'Titre de l’audit',
            'type_audit': 'Type d’audit',
            'date_audit': 'Date de l’audit',
            'client': 'Client concerné',
            'auditeur': 'Auditeur affecté',
            'description': 'Description',
        }
        widgets = {
            'date_audit': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Objectif ou description de l’audit...'}),
            'titre': forms.TextInput(attrs={'placeholder': 'Exemple : Audit qualité ligne production'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['auditeur'].queryset = User.objects.filter(profile__role='AUDITEUR')
        self.fields['auditeur'].empty_label = 'Choisir un auditeur'
        self.fields['client'].queryset = User.objects.filter(profile__role='CLIENT')
        self.fields['client'].empty_label = 'Choisir un client'


class RapportForm(forms.ModelForm):
    class Meta:
        model = Rapport
        fields = ['audit', 'contenu']
        labels = {
            'audit': 'Audit concerné',
            'contenu': 'Contenu du rapport',
        }
        widgets = {
            'contenu': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Observations, résultats, recommandations...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'profile') and user.profile.role == 'AUDITEUR':
            self.fields['audit'].queryset = Audit.objects.filter(auditeur=user)


class RapportChecklistForm(forms.ModelForm):
    class Meta:
        model = Rapport
        fields = ['contenu']
        labels = {
            'contenu': 'Résumé du rapport',
        }
        widgets = {
            'contenu': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Observations générales, problèmes trouvés, recommandations...'
            }),
        }
