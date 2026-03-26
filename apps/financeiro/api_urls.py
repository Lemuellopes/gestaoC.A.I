from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .serializers import MensalidadeViewSet

router = DefaultRouter()
router.register(r'financeiro/mensalidades', MensalidadeViewSet, basename='mensalidade')

urlpatterns = [path('', include(router.urls))]
