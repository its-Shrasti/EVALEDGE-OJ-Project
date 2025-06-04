from django.urls import path
from . import views

urlpatterns = [
    path('', views.problem_list, name='problem_list'),  # /problems/
    path('add/', views.add_problem, name='add_problem'),  # /problems/add/
    path('<int:problem_id>/', views.problem_detail, name='problem_detail'),  # /problems/2/
    path('<int:problem_id>/submit/', views.submit_code, name='submit_code'),  # /problems/2/submit/
    #path('ai-review/', views.ai_review_code, name='ai_review_code'),
]



