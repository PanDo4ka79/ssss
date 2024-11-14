from django.urls import path
from . import views
from .views import PostUpdateView, PostCreateView, PostDeleteView, become_author, PostEditView
urlpatterns = [
    path('news/', views.news_list, name='news_list'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('news/search/', views.news_search, name='news_search'),
    path('news/create/', PostCreateView.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', PostUpdateView.as_view(), name='news_edit'),
    path('news/<int:pk>/delete/', PostDeleteView.as_view(), name='news_delete'),
    path('articles/create/', PostCreateView.as_view(), name='article_create'),
    path('articles/<int:pk>/edit/', PostUpdateView.as_view(), name='article_edit'),
    path('articles/<int:pk>/delete/', PostDeleteView.as_view(), name='article_delete'),
    path('become_author/', become_author, name='become_author'),
    path('post/create/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', PostEditView.as_view(), name='post_edit'),
    path('category/<int:category_id>/subscribe/', views.subscribe_to_category, name='subscribe_to_category'),


]
