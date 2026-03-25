from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .serializers import TurmaViewSet

router = DefaultRouter()
router.register(r'turmas', TurmaViewSet, basename='turma')

urlpatterns = [path('', include(router.urls))]
