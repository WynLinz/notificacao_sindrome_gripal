from rest_framework import serializers
from .models import CasoNacional, ResumoRegional, HistoricoAtualizacao


class CasoNacionalSerializer(serializers.ModelSerializer):
    regiao_display = serializers.CharField(source='regiao', read_only=True)
    
    class Meta:
        model = CasoNacional
        fields = [
            'id', 'data', 'regiao', 'regiao_display', 'estado', 'municipio',
            'casos_confirmados', 'casos_suspeitos', 'casos_descartados', 'obitos',
            'ultima_atualizacao'
        ]
        read_only_fields = ['id', 'ultima_atualizacao']


class ResumoRegionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumoRegional
        fields = [
            'id', 'data', 'regiao',
            'total_casos_confirmados', 'total_casos_suspeitos',
            'total_casos_descartados', 'total_obitos',
            'ultima_atualizacao'
        ]
        read_only_fields = ['id', 'ultima_atualizacao']


class HistoricoAtualizacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricoAtualizacao
        fields = [
            'id', 'data_atualizacao', 'registros_importados',
            'registros_atualizados', 'status', 'mensagem_erro'
        ]
        read_only_fields = ['id', 'data_atualizacao']
