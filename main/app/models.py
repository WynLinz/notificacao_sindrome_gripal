from django.db import models
from django.utils import timezone

class CasoNacional(models.Model):
    """Modelo para armazenar dados de casos nacionais de síndrome gripal"""
    
    data = models.DateField(help_text="Data do registro")
    regiao = models.CharField(max_length=50, help_text="Região brasileira")
    estado = models.CharField(max_length=2, help_text="Unidade Federativa (UF)")
    municipio = models.CharField(max_length=100, blank=True, help_text="Município")
    
    casos_confirmados = models.IntegerField(default=0, help_text="Números de casos confirmados")
    casos_suspeitos = models.IntegerField(default=0, help_text="Números de casos suspeitos")
    casos_descartados = models.IntegerField(default=0, help_text="Números de casos descartados")
    obitos = models.IntegerField(default=0, help_text="Números de óbitos")
    
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    data_importacao = models.DateTimeField(auto_now_add=True)
    
    # Campos de rastreamento
    origem_id = models.CharField(max_length=50, unique=True, help_text="ID da API")
    
    class Meta:
        verbose_name = "Caso Nacional"
        verbose_name_plural = "Casos Nacionais"
        ordering = ['-data']
        indexes = [
            models.Index(fields=['estado', '-data']),
            models.Index(fields=['regiao', '-data']),
            models.Index(fields=['-data']),
        ]
    
    def __str__(self):
        return f"{self.estado} - {self.data} ({self.casos_confirmados} confirmados)"


class ResumoRegional(models.Model):
    """Resumo agregado por região"""
    
    data = models.DateField(help_text="Data do registro")
    regiao = models.CharField(max_length=50, help_text="Região brasileira")
    
    total_casos_confirmados = models.IntegerField(default=0)
    total_casos_suspeitos = models.IntegerField(default=0)
    total_casos_descartados = models.IntegerField(default=0)
    total_obitos = models.IntegerField(default=0)
    
    ultima_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Resumo Regional"
        verbose_name_plural = "Resumos Regionais"
        unique_together = ['data', 'regiao']
        ordering = ['-data']
    
    def __str__(self):
        return f"{self.regiao} - {self.data}"


class HistoricoAtualizacao(models.Model):
    """Rastreia quando os dados foram atualizados"""
    
    data_atualizacao = models.DateTimeField(auto_now_add=True)
    registros_importados = models.IntegerField(default=0)
    registros_atualizados = models.IntegerField(default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('sucesso', 'Sucesso'),
            ('erro', 'Erro'),
            ('em_progresso', 'Em Progresso'),
        ],
        default='em_progresso'
    )
    mensagem_erro = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Histórico de Atualização"
        verbose_name_plural = "Históricos de Atualização"
        ordering = ['-data_atualizacao']
    
    def __str__(self):
        return f"{self.data_atualizacao} - {self.status}"
