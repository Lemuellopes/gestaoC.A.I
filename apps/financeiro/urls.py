from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_financeiro, name='financeiro'),
    path('mensalidades/', views.lista_mensalidades, name='lista_mensalidades'),
    path('mensalidades/nova/', views.nova_mensalidade, name='nova_mensalidade'),
    path('mensalidades/<int:mensalidade_pk>/pagar/', views.registrar_pagamento, name='registrar_pagamento'),
]
