from django.shortcuts import render
from django.db.models import Q, Sum, Count
from django.db import models
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import CasoNacional, ResumoRegional, HistoricoAtualizacao
from .serializers import (
    CasoNacionalSerializer,
    ResumoRegionalSerializer,
    HistoricoAtualizacaoSerializer
)
from .services import sincronizar_dados_open_data


class CasoNacionalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para consultar casos nacionais de síndrome gripal
    
    Filtros disponíveis:
    - estado: UF (ex: SP, RJ)
    - regiao: Região (ex: Sudeste)
    - data: Data específica (YYYY-MM-DD)
    - data_inicio: Data inicial
    - data_fim: Data final
    """
    queryset = CasoNacional.objects.all()
    serializer_class = CasoNacionalSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado', 'regiao', 'data']
    search_fields = ['estado', 'municipio']
    ordering_fields = ['data', 'casos_confirmados', 'obitos']
    ordering = ['-data']
    
    @action(detail=False, methods=['get'])
    def por_estado(self, request):
        """Retorna casos agrupados por estado"""
        estado = request.query_params.get('estado')
        
        if not estado:
            return Response(
                {'erro': 'Parâmetro "estado" é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        casos = self.queryset.filter(estado=estado.upper()).order_by('-data')
        serializer = self.get_serializer(casos, many=True)
        
        # Totais
        totais = casos.aggregate(
            total_confirmados=Sum('casos_confirmados'),
            total_suspeitos=Sum('casos_suspeitos'),
            total_descartados=Sum('casos_descartados'),
            total_obitos=Sum('obitos'),
        )
        
        return Response({
            'estado': estado.upper(),
            'totais': totais,
            'detalhes': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def por_regiao(self, request):
        """Retorna casos agrupados por região"""
        regiao = request.query_params.get('regiao')
        
        if not regiao:
            return Response(
                {'erro': 'Parâmetro "regiao" é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        casos = self.queryset.filter(regiao__icontains=regiao).order_by('-data')
        serializer = self.get_serializer(casos, many=True)
        
        # Totais
        totais = casos.aggregate(
            total_confirmados=Sum('casos_confirmados'),
            total_suspeitos=Sum('casos_suspeitos'),
            total_descartados=Sum('casos_descartados'),
            total_obitos=Sum('obitos'),
        )
        
        return Response({
            'regiao': regiao,
            'totais': totais,
            'detalhes': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def ultimos_registros(self, request):
        """Retorna os últimos N registros"""
        limite = int(request.query_params.get('limite', 100))
        casos = self.queryset[:limite]
        serializer = self.get_serializer(casos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estatisticas(self, request):
        """Retorna estatísticas gerais"""
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        
        queryset = self.queryset
        
        if data_inicio:
            queryset = queryset.filter(data__gte=data_inicio)
        if data_fim:
            queryset = queryset.filter(data__lte=data_fim)
        
        stats = queryset.aggregate(
            total_confirmados=Sum('casos_confirmados'),
            total_suspeitos=Sum('casos_suspeitos'),
            total_descartados=Sum('casos_descartados'),
            total_obitos=Sum('obitos'),
            numero_estados=Count('estado', distinct=True),
            numero_registros=Count('id')
        )
        
        return Response(stats)


class ResumoRegionalViewSet(viewsets.ReadOnlyModelViewSet):
    """API para consultar resumos regionais"""
    queryset = ResumoRegional.objects.all()
    serializer_class = ResumoRegionalSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['regiao', 'data']
    ordering = ['-data']
    
    @action(detail=False, methods=['get'])
    def por_regiao(self, request):
        """Retorna resumo de uma região específica"""
        regiao = request.query_params.get('regiao')
        
        if not regiao:
            return Response(
                {'erro': 'Parâmetro "regiao" é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resumos = self.queryset.filter(regiao__icontains=regiao).order_by('-data')
        serializer = self.get_serializer(resumos, many=True)
        return Response(serializer.data)


class HistoricoAtualizacaoViewSet(viewsets.ReadOnlyModelViewSet):
    """API para consultar histórico de sincronizações"""
    queryset = HistoricoAtualizacao.objects.all()
    serializer_class = HistoricoAtualizacaoSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering = ['-data_atualizacao']
    
    @action(detail=False, methods=['post'])
    def sincronizar_agora(self, request):
        """Dispara uma sincronização manual com Open Data SUS"""
        try:
            historico = sincronizar_dados_open_data()
            serializer = self.get_serializer(historico)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'erro': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def ultima_sincronizacao(self, request):
        """Retorna informações da última sincronização"""
        ultima = self.queryset.first()
        
        if not ultima:
            return Response({'mensagem': 'Nenhuma sincronização realizada'})
        
        serializer = self.get_serializer(ultima)
        return Response(serializer.data)


def home_dashboard(request):
    """View para dashboard HTML com gráficos e dados em tempo real"""
    from django.db.models import Count
    import json
    
    # Estatísticas gerais
    total_confirmados = CasoNacional.objects.aggregate(Sum('casos_confirmados'))['casos_confirmados__sum'] or 0
    total_obitos = CasoNacional.objects.aggregate(Sum('obitos'))['obitos__sum'] or 0
    total_suspeitos = CasoNacional.objects.aggregate(Sum('casos_suspeitos'))['casos_suspeitos__sum'] or 0
    total_descartados = CasoNacional.objects.aggregate(Sum('casos_descartados'))['casos_descartados__sum'] or 0
    numero_estados = CasoNacional.objects.values('estado').distinct().count()
    numero_registros = CasoNacional.objects.count()
    
    # Taxa de mortalidade
    taxa_mortalidade = (total_obitos / total_confirmados * 100) if total_confirmados > 0 else 0
    
    # Dados por região
    por_regiao = list(ResumoRegional.objects.values('regiao').annotate(
        total=Sum('total_casos_confirmados'),
        obitos=Sum('total_obitos')
    ).order_by('-total'))
    
    # Dados por estado (Top 10)
    por_estado = list(CasoNacional.objects.values('estado').annotate(
        total=Sum('casos_confirmados'),
        obitos=Sum('obitos')
    ).order_by('-total')[:10])
    
    # Evolução temporal (últimos 30 dias)
    from datetime import timedelta
    data_limite = CasoNacional.objects.aggregate(max_data=models.Max('data'))['max_data']
    if data_limite:
        data_inicio = data_limite - timedelta(days=30)
        evolucao = list(CasoNacional.objects.filter(
            data__gte=data_inicio
        ).values('data').annotate(
            confirmados=Sum('casos_confirmados'),
            suspeitos=Sum('casos_suspeitos'),
            descartados=Sum('casos_descartados')
        ).order_by('data'))
        
        # Converter datas para string ISO format
        for item in evolucao:
            item['data'] = item['data'].isoformat()
    else:
        evolucao = []
    
    # Últimos registros
    ultimos_registros = CasoNacional.objects.all()[:5]
    
    # Última sincronização
    ultima_sincronizacao = HistoricoAtualizacao.objects.first()
    
    context = {
        'total_confirmados': total_confirmados,
        'total_obitos': total_obitos,
        'total_suspeitos': total_suspeitos,
        'total_descartados': total_descartados,
        'numero_estados': numero_estados,
        'numero_registros': numero_registros,
        'taxa_mortalidade': f"{taxa_mortalidade:.2f}",
        'por_regiao': json.dumps(por_regiao),
        'por_estado': json.dumps(por_estado),
        'evolucao': json.dumps(evolucao),
        'ultimos_registros': ultimos_registros,
        'ultima_sincronizacao': ultima_sincronizacao,
    }
    
    return render(request, 'home_dashboard.html', context)

