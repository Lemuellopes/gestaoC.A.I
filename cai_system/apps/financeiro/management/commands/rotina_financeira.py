from datetime import date

from django.core.management.base import BaseCommand, CommandError

from apps.financeiro.services import processar_rotina_financeira


class Command(BaseCommand):
    help = (
        'Executa a rotina financeira mensal: gera/atualiza mensalidades do mes e '
        'atualiza status vencidos. Ideal para agendamento automatico.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--mes', type=int, help='Mes de referencia (1-12).')
        parser.add_argument('--ano', type=int, help='Ano de referencia (ex: 2026).')
        parser.add_argument(
            '--proximo-mes',
            action='store_true',
            help='Executa a rotina para o proximo mes automaticamente.',
        )

    def handle(self, *args, **options):
        hoje = date.today()

        mes = options.get('mes')
        ano = options.get('ano')

        if options.get('proximo_mes'):
            if hoje.month == 12:
                mes, ano = 1, hoje.year + 1
            else:
                mes, ano = hoje.month + 1, hoje.year
        else:
            mes = mes or hoje.month
            ano = ano or hoje.year

        if mes < 1 or mes > 12:
            raise CommandError('Mes invalido. Use um valor entre 1 e 12.')

        criadas, atualizadas = processar_rotina_financeira(mes, ano, referencia=hoje)

        self.stdout.write(
            self.style.SUCCESS(
                f'Rotina financeira concluida para {mes:02d}/{ano}. '
                f'Mensalidades criadas: {criadas}. Status atualizados: {atualizadas}.'
            )
        )
