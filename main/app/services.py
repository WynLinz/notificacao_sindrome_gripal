import requests
import logging
from datetime import datetime
from typing import Dict, List, Any
from django.db import transaction
from .models import CasoNacional, ResumoRegional, HistoricoAtualizacao

logger = logging.getLogger(__name__)

class OpenDataSUSAPI:
    """
    Serviço para consumir dados da API Open Data SUS
    Documentação: https://dadosabertos.saude.gov.br/
    """
    
    BASE_URL = "https://dadosabertos.saude.gov.br/api/3/action"
    DATASET_NAME = "casos-nacionais"
    TIMEOUT = 30
    
    # Mapeamento de regiões brasileiras por UF
    ESTADO_REGIAO = {
        'AC': 'Norte', 'AM': 'Norte', 'AP': 'Norte', 'PA': 'Norte', 
        'RO': 'Norte', 'RR': 'Norte', 'TO': 'Norte',
        'AL': 'Nordeste', 'BA': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste',
        'PB': 'Nordeste', 'PE': 'Nordeste', 'PI': 'Nordeste', 'RN': 'Nordeste', 'SE': 'Nordeste',
        'DF': 'Centro-Oeste', 'GO': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'MT': 'Centro-Oeste',
        'ES': 'Sudeste', 'MG': 'Sudeste', 'RJ': 'Sudeste', 'SP': 'Sudeste',
        'PR': 'Sul', 'RS': 'Sul', 'SC': 'Sul',
    }
    
    @staticmethod
    def get_dataset_info() -> Dict[str, Any]:
        """Obtém informações sobre o dataset"""
        try:
            url = f"{OpenDataSUSAPI.BASE_URL}/package_show"
            params = {'id': OpenDataSUSAPI.DATASET_NAME}
            response = requests.get(url, params=params, timeout=OpenDataSUSAPI.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Erro ao obter informações do dataset: {e}")
            raise
    
    @staticmethod
    def get_resources() -> List[Dict[str, Any]]:
        """Lista todos os recursos (arquivos) do dataset"""
        try:
            dataset_info = OpenDataSUSAPI.get_dataset_info()
            return dataset_info.get('result', {}).get('resources', [])
        except Exception as e:
            logger.error(f"Erro ao obter recursos: {e}")
            raise
    
    @staticmethod
    def fetch_csv_data(resource_url: str) -> List[Dict[str, Any]]:
        """Baixa dados de um arquivo CSV e retorna como lista de dicionários"""
        try:
            response = requests.get(resource_url, timeout=OpenDataSUSAPI.TIMEOUT)
            response.raise_for_status()
            
            # Parse CSV
            import csv
            from io import StringIO
            
            csv_file = StringIO(response.text)
            reader = csv.DictReader(csv_file)
            data = list(reader)
            
            logger.info(f"Dados baixados: {len(data)} registros")
            return data
        except requests.RequestException as e:
            logger.error(f"Erro ao baixar dados CSV: {e}")
            raise
    
    @staticmethod
    def parse_data(raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Normaliza e valida os dados da API
        """
        parsed_data = []
        
        for record in raw_data:
            try:
                # Adapte os nomes das colunas conforme necessário
                estado = record.get('UF', record.get('estado', ''))
                data_str = record.get('data', record.get('Data', ''))
                
                if not estado or not data_str:
                    logger.warning(f"Registro incompleto: {record}")
                    continue
                
                # Parse da data
                try:
                    data_obj = datetime.strptime(data_str, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        data_obj = datetime.strptime(data_str, '%d/%m/%Y').date()
                    except ValueError:
                        logger.warning(f"Data inválida: {data_str}")
                        continue
                
                parsed_record = {
                    'estado': estado.upper()[:2],
                    'regiao': OpenDataSUSAPI.ESTADO_REGIAO.get(estado.upper()[:2], 'Brasil'),
                    'data': data_obj,
                    'municipio': record.get('municipio', record.get('Municipio', '')),
                    'casos_confirmados': int(record.get('casos_confirmados', record.get('Confirmados', 0)) or 0),
                    'casos_suspeitos': int(record.get('casos_suspeitos', record.get('Suspeitos', 0)) or 0),
                    'casos_descartados': int(record.get('casos_descartados', record.get('Descartados', 0)) or 0),
                    'obitos': int(record.get('obitos', record.get('Obitos', 0)) or 0),
                    'origem_id': f"{estado}-{data_str}",
                }
                
                parsed_data.append(parsed_record)
            
            except Exception as e:
                logger.warning(f"Erro ao processar registro: {record} - {e}")
                continue
        
        return parsed_data
    
    @staticmethod
    @transaction.atomic
    def save_casos_nacionais(parsed_data: List[Dict[str, Any]]) -> tuple:
        """
        Salva ou atualiza os dados no banco de dados
        Retorna (registros_importados, registros_atualizados)
        """
        importados = 0
        atualizados = 0
        
        for record in parsed_data:
            try:
                obj, created = CasoNacional.objects.update_or_create(
                    origem_id=record['origem_id'],
                    defaults=record
                )
                
                if created:
                    importados += 1
                else:
                    atualizados += 1
            
            except Exception as e:
                logger.error(f"Erro ao salvar registro: {record} - {e}")
                continue
        
        return importados, atualizados
    
    @staticmethod
    @transaction.atomic
    def update_resumos_regionais():
        """Atualiza os resumos regionais agregando dados por região"""
        from django.db.models import Sum
        
        # Obtém todas as datas únicas
        datas = CasoNacional.objects.values_list('data', flat=True).distinct()
        
        for data in datas:
            registros = CasoNacional.objects.filter(data=data)
            regioes = registros.values_list('regiao', flat=True).distinct()
            
            for regiao in regioes:
                registros_regiao = registros.filter(regiao=regiao)
                
                totais = registros_regiao.aggregate(
                    total_confirmados=Sum('casos_confirmados'),
                    total_suspeitos=Sum('casos_suspeitos'),
                    total_descartados=Sum('casos_descartados'),
                    total_obitos=Sum('obitos'),
                )
                
                ResumoRegional.objects.update_or_create(
                    data=data,
                    regiao=regiao,
                    defaults={
                        'total_casos_confirmados': totais['total_confirmados'] or 0,
                        'total_casos_suspeitos': totais['total_suspeitos'] or 0,
                        'total_casos_descartados': totais['total_descartados'] or 0,
                        'total_obitos': totais['total_obitos'] or 0,
                    }
                )


def sincronizar_dados_open_data():
    """
    Função principal para sincronizar dados com Open Data SUS
    Pode ser executada manualmente ou via Celery
    """
    historico = HistoricoAtualizacao.objects.create(
        status='em_progresso'
    )
    
    try:
        logger.info("Iniciando sincronização com Open Data SUS...")
        
        # Obtém recursos disponíveis
        recursos = OpenDataSUSAPI.get_resources()
        
        if not recursos:
            raise Exception("Nenhum recurso encontrado no dataset")
        
        logger.info(f"Recursos encontrados: {len(recursos)}")
        
        # Processa o primeiro recurso CSV disponível
        for recurso in recursos:
            if recurso.get('format', '').upper() == 'CSV':
                url_recurso = recurso.get('url')
                
                if url_recurso:
                    logger.info(f"Processando recurso: {recurso.get('name')}")
                    
                    # Baixa e processa dados
                    raw_data = OpenDataSUSAPI.fetch_csv_data(url_recurso)
                    parsed_data = OpenDataSUSAPI.parse_data(raw_data)
                    
                    # Salva no banco de dados
                    importados, atualizados = OpenDataSUSAPI.save_casos_nacionais(parsed_data)
                    
                    # Atualiza resumos
                    OpenDataSUSAPI.update_resumos_regionais()
                    
                    historico.registros_importados = importados
                    historico.registros_atualizados = atualizados
                    historico.status = 'sucesso'
                    
                    logger.info(
                        f"Sincronização concluída: {importados} importados, {atualizados} atualizados"
                    )
                    break
        
    except Exception as e:
        logger.error(f"Erro durante sincronização: {e}")
        historico.status = 'erro'
        historico.mensagem_erro = str(e)
    
    finally:
        historico.save()
        return historico
