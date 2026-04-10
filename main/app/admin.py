from django.contrib import admin
from django.utils.html import format_html
from .models import CasoNacional, ResumoRegional, HistoricoAtualizacao

@admin.register(CasoNacional)
class CasoNacionalAdmin(admin.ModelAdmin):
    list_display = ['data', 'estado', 'regiao', 'casos_confirmados', 'obitos', 'ultima_atualizacao']
    list_filter = ['estado', 'regiao', 'data']
    search_fields = ['estado', 'municipio', 'regiao']
    readonly_fields = ['ultima_atualizacao', 'data_importacao', 'origem_id']
    
    fieldsets = (
        ('Informações Geográficas', {
            'fields': ('data', 'estado', 'regiao', 'municipio')
        }),
        ('Dados de Casos', {
            'fields': ('casos_confirmados', 'casos_suspeitos', 'casos_descartados', 'obitos')
        }),
        ('Rastreamento', {
            'fields': ('origem_id', 'ultima_atualizacao', 'data_importacao'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-data']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ResumoRegional)
class ResumoRegionalAdmin(admin.ModelAdmin):
    list_display = ['data', 'regiao', 'total_casos_confirmados', 'total_obitos', 'ultima_atualizacao']
    list_filter = ['regiao', 'data']
    search_fields = ['regiao']
    readonly_fields = ['ultima_atualizacao']
    
    fieldsets = (
        ('Informações Regionais', {
            'fields': ('data', 'regiao')
        }),
        ('Totalizações', {
            'fields': ('total_casos_confirmados', 'total_casos_suspeitos', 'total_casos_descartados', 'total_obitos')
        }),
        ('Rastreamento', {
            'fields': ('ultima_atualizacao',),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ['-data']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HistoricoAtualizacao)
class HistoricoAtualizacaoAdmin(admin.ModelAdmin):
    list_display = ['data_atualizacao', 'status_badge', 'registros_importados', 'registros_atualizados']
    list_filter = ['status', 'data_atualizacao']
    readonly_fields = ['data_atualizacao', 'mensagem_erro']
    
    fieldsets = (
        ('Status da Sincronização', {
            'fields': ('data_atualizacao', 'status', 'mensagem_erro')
        }),
        ('Dados Processados', {
            'fields': ('registros_importados', 'registros_atualizados')
        }),
    )
    
    ordering = ['-data_atualizacao']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def status_badge(self, obj):
        colors = {
            'sucesso': '#28a745',
            'erro': '#dc3545',
            'em_progresso': '#ffc107',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

