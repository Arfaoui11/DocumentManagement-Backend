from django.urls import path, include

from documents import views

urlpatterns = [
    path('', views.DocumentView.as_view({'get': 'list'})),
    path('<int:pk>/', views.DocumentView.as_view({'get': 'retrieve'})),
    path('delete/<int:pk>/', views.DocumentView.as_view({'delete': 'destroy'})),
    path('add/', views.DocumentView.as_view({'post': 'create'})),
]