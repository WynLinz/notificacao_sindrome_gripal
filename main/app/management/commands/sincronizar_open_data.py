from django.core.management.base import BaseCommand, CommandError
from app.services import sincronizar_dados_open_data


class Command(BaseCommand):
    help = 'Sincroniza dados da API Open Data SUS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Exibe mais detalhes durante a sincronização',
        )

    def handle(self, *args, **options):
        try:
            self.stdout.write(self.style.SUCCESS('Iniciando sincronização com Open Data SUS...'))
            
            historico = sincronizar_dados_open_data()
            
            if historico.status == 'sucesso':
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Sincronização concluída com sucesso!\n'
                    f'  - Registros importados: {historico.registros_importados}\n'
                    f'  - Registros atualizados: {historico.registros_atualizados}'
                ))
            else:
                self.stdout.write(self.style.ERROR(
                    f'✗ Erro na sincronização:\n'
                    f'  {historico.mensagem_erro}'
                ))
                raise CommandError(historico.mensagem_erro)
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Erro: {str(e)}'))
            raise CommandError(str(e))
