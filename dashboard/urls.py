from django.urls import path 
from . import views 

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('correspondences/', views.correspondences, name='correspondences'),
    path('e-learning/', views.e_learning, name='e_learning'),
    path('student-results/', views.student_results, name='student_results'),
    path('bills/', views.bills, name='bills'),
    path('payment-histories/', views.payment_histories, name='payment_histories'),
    path('change-password/', views.change_password, name='change_password'),
]