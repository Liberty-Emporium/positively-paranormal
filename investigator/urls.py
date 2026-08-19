from django.urls import path
from . import views

app_name = 'investigator'

urlpatterns = [
    # Home & Dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Cases
    path('cases/', views.case_list, name='case_list'),
    path('cases/new/', views.case_create, name='case_create'),
    path('cases/<int:pk>/', views.case_detail, name='case_detail'),

    # Sessions
    path('cases/<int:case_pk>/sessions/new/', views.session_create, name='session_create'),
    path('cases/<int:case_pk>/sessions/<int:session_pk>/', views.session_detail, name='session_detail'),
    path('cases/<int:case_pk>/sessions/<int:session_pk>/end/', views.session_end, name='session_end'),

    # EVP
    path('cases/<int:case_pk>/sessions/<int:session_pk>/evp/', views.evp_recorder, name='evp_recorder'),
    path('cases/<int:case_pk>/sessions/<int:session_pk>/evp/save/', views.evp_save, name='evp_save'),

    # EMF
    path('cases/<int:case_pk>/sessions/<int:session_pk>/emf/', views.emf_meter, name='emf_meter'),
    path('cases/<int:case_pk>/sessions/<int:session_pk>/emf/save/', views.emf_save_reading, name='emf_save_reading'),
    path('cases/<int:case_pk>/sessions/<int:session_pk>/emf/readings.json', views.emf_readings_json, name='emf_readings_json'),

    # Evidence
    path('cases/<int:case_pk>/sessions/<int:session_pk>/evidence/new/', views.evidence_upload, name='evidence_upload'),
]