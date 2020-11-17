from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, UserPostListView
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='schedule-home'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
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
    path('General_Pref/', views.General_Pref, name='General_Pref')
]
