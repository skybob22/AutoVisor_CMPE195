from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='schedule-home'),
    path('about/', views.about, name='schedule-about'),
    path('transcript/', views.transcript, name='schedule-transcript'),
    path('roadmap/', views.roadmap, name='schedule-roadmap'),
    path('community/', views.community, name='schedule-community'),
    path('roadmap/detail', views.roadmap_detail, name='roadmap-detail'),
    path('transcript/detail', views.transcript_detail, name='transcript-detail'),
    path('Add_course/', views.Add_course, name='Add_course'),
    path('transcript/delete', views.transcriptGrade_delete, name='transcript-delete'),
    path('transcript/', views.index, name='index'),
    path('roadmap/detail', views.roadmap_generated, name='roadmap_generated'),
    path('Preference/', views.Preference,
         name='Preference'),
    path('GE_Pref/', views.GE_Pref, name='GE_Pref'),
    path('Elec_Pref/', views.Elec_Pref, name='Elec_Pref'),
    path('General_Pref/', views.General_Pref, name='General_Pref'),
    path('Preference/delete', views.preferredCourse_delete, name='pref-delete'),
    path('community/', views.community_portal, name='community_portal'),
    path('community/send_friendreq', views.send_friendreq, name='send_friendreq')    
]
