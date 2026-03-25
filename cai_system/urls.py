from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('apps.dashboard.urls')),
    path('alunos/', include('apps.alunos.urls')),
    path('professores/', include('apps.professores.urls')),
    path('turmas/', include('apps.turmas.urls')),
    path('financeiro/', include('apps.financeiro.urls')),
    # API endpoints
    path('api/v1/', include('apps.alunos.api_urls')),
    path('api/v1/', include('apps.professores.api_urls')),
    path('api/v1/', include('apps.turmas.api_urls')),
    path('api/v1/', include('apps.financeiro.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
