from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.parent_login_view, name='parent_login'),
    path('logout/', views.parent_logout_view, name='parent_logout'),
]
