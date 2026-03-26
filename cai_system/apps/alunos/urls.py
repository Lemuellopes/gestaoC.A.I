from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_alunos, name='lista_alunos'),
    path('novo/', views.novo_aluno, name='novo_aluno'),
    path('<int:pk>/', views.perfil_aluno, name='perfil_aluno'),
    path('<int:pk>/editar/', views.editar_aluno, name='editar_aluno'),
    path('<int:pk>/pagamento/', views.registrar_pagamento_aluno, name='pagamento_aluno'),
    path('responsavel/novo/', views.novo_responsavel, name='novo_responsavel'),
]
