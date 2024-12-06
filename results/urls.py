
from django.urls import path
from . import views

urlpatterns = [
    path('select/',
         views.select_result_parameters, name='select_results'),
    path('view/<int:session_id>/<int:term_id>/<int:child_id>/<int:assessment_id>/',
         views.view_results, name='view_results'),
]
