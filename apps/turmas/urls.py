from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_turmas, name='lista_turmas'),
    path('nova/', views.nova_turma, name='nova_turma'),
    path('<int:pk>/', views.detalhe_turma, name='detalhe_turma'),
    path('<int:pk>/editar/', views.editar_turma, name='editar_turma'),
    path('<int:pk>/matricular/', views.matricular_aluno, name='matricular_aluno'),
]
