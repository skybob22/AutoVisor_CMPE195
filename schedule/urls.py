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
]

