import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from app.models import CasoNacional, ResumoRegional
from django.db.models import Sum, Min
from datetime import datetime, timedelta
import random

def seed_casos_nacionais():
    """
    Popula o banco com dados de teste para demonstração
    """
    
    # Dados de exemplo
    estados = ['SP', 'RJ', 'MG', 'BA', 'RS', 'PR', 'PE', 'GO', 'SC', 'PB', 'MA', 'CE', 'AL', 'SE',
               'AM', 'AC', 'RO', 'AP', 'TO', 'MT', 'MS', 'DF', 'PA', 'ES', 'RN', 'PI']
    
    regiao_map = {
        'SP': 'Sudeste', 'RJ': 'Sudeste', 'MG': 'Sudeste', 'ES': 'Sudeste',
        'RS': 'Sul', 'SC': 'Sul', 'PR': 'Sul',
        'BA': 'Nordeste', 'PE': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
        'PB': 'Nordeste', 'AL': 'Nordeste', 'SE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste',
        'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'DF': 'Centro-Oeste',
        'PA': 'Norte', 'AM': 'Norte', 'AC': 'Norte', 'RO': 'Norte', 'AP': 'Norte', 'TO': 'Norte'
    }
    
    municipios = [
        'São Paulo', 'Rio de Janeiro', 'Brasília', 'Salvador', 'Fortaleza',
        'Belo Horizonte', 'Curitiba', 'Recife', 'Porto Alegre', 'Manaus'
    ]
    
    # Remover dados antigos
    print("Limpando dados antigos...")
    CasoNacional.objects.all().delete()
    ResumoRegional.objects.all().delete()
    
    print("Gerando dados de teste...")
    
    # Gerar dados para os últimos 30 dias
    data_atual = datetime.now().date()
    casos_criados = 0
    
    for dias_atras in range(30):
        data = data_atual - timedelta(days=dias_atras)
        
        for estado in estados:
            # Simular crescimento de casos com variação aleatória
            base_confirmados = random.randint(100, 1000)
            base_suspeitos = random.randint(50, 500)
            base_descartados = random.randint(30, 300)
            
            # Adicionar variação diária
            variacao = random.randint(-20, 50)
            
            caso = CasoNacional.objects.create(
                data=data,
                estado=estado,
                regiao=regiao_map.get(estado, 'Brasil'),
                municipio=random.choice(municipios),
                casos_confirmados=max(0, base_confirmados + variacao),
                casos_suspeitos=max(0, base_suspeitos + random.randint(-10, 30)),
                casos_descartados=max(0, base_descartados + random.randint(-5, 20)),
                obitos=random.randint(0, 15),
                origem_id=f"{estado}-{data.isoformat()}"
            )
            casos_criados += 1
    
    print(f"✓ Criados {casos_criados} registros de casos nacionais")
    
    # Gerar resumos regionais
    print("Gerando resumos regionais...")
    from django.db.models import Sum
    
    datas = CasoNacional.objects.values_list('data', flat=True).distinct()
    regioes = CasoNacional.objects.values_list('regiao', flat=True).distinct()
    
    resumos_criados = 0
    for data in datas:
        for regiao in regioes:
            registros = CasoNacional.objects.filter(data=data, regiao=regiao)
            
            totais = registros.aggregate(
                total_confirmados=Sum('casos_confirmados'),
                total_suspeitos=Sum('casos_suspeitos'),
                total_descartados=Sum('casos_descartados'),
                total_obitos=Sum('obitos'),
            )
            
            obj, created = ResumoRegional.objects.update_or_create(
                data=data,
                regiao=regiao,
                defaults={
                    'total_casos_confirmados': totais['total_confirmados'] or 0,
                    'total_casos_suspeitos': totais['total_suspeitos'] or 0,
                    'total_casos_descartados': totais['total_descartados'] or 0,
                    'total_obitos': totais['total_obitos'] or 0,
                }
            )
            resumos_criados += 1
    
    print(f"✓ Criados {resumos_criados} resumos regionais")
    
    # Estatísticas
    total_confirmados = CasoNacional.objects.aggregate(Sum('casos_confirmados'))['casos_confirmados__sum']
    total_obitos = CasoNacional.objects.aggregate(Sum('obitos'))['obitos__sum']
    
    print("\n" + "="*50)
    print("RESUMO DOS DADOS GERADOS")
    print("="*50)
    print(f"📊 Total de casos confirmados: {total_confirmados:,}")
    print(f"⚠️  Total de óbitos: {total_obitos:,}")
    print(f"🏢 Estados: {len(estados)}")
    print(f"📅 Período dos dados: {(data_atual - CasoNacional.objects.aggregate(min_data=Min('data'))['min_data']).days} dias")
    print(f"✓ Registros totais: {casos_criados:,}")
    print("="*50)
    print("\n✅ Base de dados populada com sucesso!")
    print("Acesse http://localhost:8000/ para ver o dashboard")

if __name__ == '__main__':
    seed_casos_nacionais()
