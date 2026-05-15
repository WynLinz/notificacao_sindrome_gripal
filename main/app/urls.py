from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from . import views

#alterar "adm django"
admin.site.site_header = "ADM SITE"
admin.site.site_title = "Sindrome Gripal"
#admin.site.site_url = "notificacao-sindrome-gripal.herokuapp.com"

# Configuração do router para API REST
router = DefaultRouter()
router.register(r'casos-nacionais', views.CasoNacionalViewSet, basename='caso-nacional')
router.register(r'resumos-regionais', views.ResumoRegionalViewSet, basename='resumo-regional')
router.register(r'historico-atualizacoes', views.HistoricoAtualizacaoViewSet, basename='historico-atualizacao')

urlpatterns = [
    # API REST
    path('api/v1/', include(router.urls)),
    
    # Dashboard
    path('', views.home_dashboard, name='home'),
]
