from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('audits/', views.audits_list, name='audits_list'),
    path('audits/ajouter/', views.audit_create, name='audit_create'),
    path('audits/<int:pk>/modifier/', views.audit_update, name='audit_update'),
    path('audits/<int:pk>/', views.audit_detail, name='audit_detail'),
    path('audits/<int:audit_id>/rapport/', views.rapport_create_for_audit, name='rapport_create_for_audit'),

    path('rapports/', views.rapports_list, name='rapports_list'),
    path('rapports/<int:pk>/', views.rapport_detail, name='rapport_detail'),
    path('rapports/<int:pk>/modifier/', views.rapport_modifier, name='rapport_modifier'),
    path('rapports/<int:pk>/pdf/', views.rapport_pdf, name='rapport_pdf'),

    path('calendrier/', views.calendar_view, name='calendrier'),
    path('calendar/', views.calendar_view, name='calendar'),

    path('checklists/', views.checklist_list, name='checklist_list'),
    path('checklists/ajouter/', views.checklist_create, name='checklist_create'),

    path('utilisateurs/', views.users_list, name='users_list'),
    path('utilisateurs/ajouter/', views.user_create, name='user_create'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('inscription/', views.register_view, name='inscription_client'),
    path('register/', views.register_view, name='register'),

    path('rapports/<int:pk>/modifier/', views.rapport_modifier, name='rapport_update'),

    
]
