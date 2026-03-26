from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_professores, name='lista_professores'),
    path('novo/', views.novo_professor, name='novo_professor'),
    path('<int:pk>/', views.perfil_professor, name='perfil_professor'),
    path('<int:pk>/editar/', views.editar_professor, name='editar_professor'),
]
