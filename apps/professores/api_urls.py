from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .serializers import ProfessorViewSet

router = DefaultRouter()
router.register(r'professores', ProfessorViewSet, basename='professor')

urlpatterns = [path('', include(router.urls))]
