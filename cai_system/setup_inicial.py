#!/usr/bin/env python
"""
Script de configuração inicial do C.A.I — Centro Aquetico Infatil
Execute: python setup_inicial.py
"""
import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cai_system.settings')

# Garante que estamos no diretório correto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

django.setup()

from django.contrib.auth import get_user_model

Usuario = get_user_model()


def criar_usuarios():
    print("👤 Criando usuários...")

    if not Usuario.objects.filter(username='admin').exists():
        Usuario.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@cai.com.br',
            first_name='Administrador',
            last_name='CAI',
            perfil='admin'
        )
        print("   ✅ admin / admin123 (Administrador)")

    if not Usuario.objects.filter(username='coordenacao').exists():
        Usuario.objects.create_user(
            username='coordenacao',
            password='coord123',
            email='coord@cai.com.br',
            first_name='Coordenação',
            last_name='CAI',
            perfil='coordenacao'
        )
        print("   ✅ coordenacao / coord123")

    if not Usuario.objects.filter(username='financeiro').exists():
        Usuario.objects.create_user(
            username='financeiro',
            password='fin123',
            email='financeiro@cai.com.br',
            first_name='Financeiro',
            last_name='CAI',
            perfil='financeiro'
        )
        print("   ✅ financeiro / fin123")


def criar_professores():
    from apps.professores.models import Professor, HorarioDisponibilidade
    print("\n🏊 Criando instrutores...")

    professores_data = [
        {
            'nome': 'Ana Paula Oliveira',
            'cpf': '111.111.111-11',
            'telefone': '(87) 99111-0001',
            'email': 'ana@cai.com.br',
            'especialidade': 'bebe_conforto',
            'formacao': 'Educação Física - UNIFASB',
            'registro_cref': 'CREF 012345-G/PE',
            'anos_experiencia': 5,
            'tipo_contrato': 'clt',
            'salario': Decimal('2800.00'),
            'status': 'ativo',
            'data_admissao': date(2021, 3, 1),
            'cidade': 'Araripina',
            'estado': 'PE',
        },
        {
            'nome': 'Carlos Eduardo Santos',
            'cpf': '222.222.222-22',
            'telefone': '(87) 99222-0002',
            'email': 'carlos@cai.com.br',
            'especialidade': 'natacao_infantil',
            'formacao': 'Educação Física - UFPE',
            'registro_cref': 'CREF 023456-G/PE',
            'anos_experiencia': 8,
            'tipo_contrato': 'clt',
            'salario': Decimal('3200.00'),
            'status': 'ativo',
            'data_admissao': date(2020, 1, 15),
            'cidade': 'Araripina',
            'estado': 'PE',
        },
        {
            'nome': 'Fernanda Lima Costa',
            'cpf': '333.333.333-33',
            'telefone': '(87) 99333-0003',
            'email': 'fernanda@cai.com.br',
            'especialidade': 'auto_salvamento',
            'formacao': 'Educação Física - UPE',
            'registro_cref': 'CREF 034567-G/PE',
            'anos_experiencia': 3,
            'tipo_contrato': 'pj',
            'salario': Decimal('2200.00'),
            'status': 'ativo',
            'data_admissao': date(2023, 2, 1),
            'cidade': 'Ouricuri',
            'estado': 'PE',
        },
    ]

    criados = []
    for data in professores_data:
        prof, created = Professor.objects.get_or_create(cpf=data['cpf'], defaults=data)
        if created:
            print(f"   ✅ {prof.nome}")
        criados.append(prof)

    # Horários
    dias_semana = [
        (0, '08:00', '12:00'),
        (1, '08:00', '12:00'),
        (2, '08:00', '12:00'),
        (3, '08:00', '12:00'),
        (4, '08:00', '12:00'),
        (5, '07:00', '11:00'),
    ]
    from datetime import time
    for prof in criados:
        if not prof.horarios.exists():
            for dia, ini, fim in dias_semana:
                h, m = map(int, ini.split(':'))
                hf, mf = map(int, fim.split(':'))
                HorarioDisponibilidade.objects.create(
                    professor=prof,
                    dia_semana=dia,
                    hora_inicio=time(h, m),
                    hora_fim=time(hf, mf)
                )

    return criados


def criar_responsaveis():
    from apps.alunos.models import Responsavel
    print("\n👨‍👩‍👦 Criando responsáveis...")

    responsaveis_data = [
        {'nome': 'Maria Silva', 'cpf': '444.444.444-44', 'telefone': '(87) 99400-0001', 'parentesco': 'mae', 'cidade': 'Araripina', 'estado': 'PE'},
        {'nome': 'João Santos', 'cpf': '555.555.555-55', 'telefone': '(87) 99500-0002', 'parentesco': 'pai', 'cidade': 'Araripina', 'estado': 'PE'},
        {'nome': 'Luiza Ferreira', 'cpf': '666.666.666-66', 'telefone': '(87) 99600-0003', 'parentesco': 'mae', 'cidade': 'Araripina', 'estado': 'PE'},
        {'nome': 'Pedro Alves', 'cpf': '777.777.777-77', 'telefone': '(87) 99700-0004', 'parentesco': 'pai', 'cidade': 'Exu', 'estado': 'PE'},
        {'nome': 'Ana Rodrigues', 'cpf': '888.888.888-88', 'telefone': '(87) 99800-0005', 'parentesco': 'mae', 'cidade': 'Araripina', 'estado': 'PE'},
        {'nome': 'Carlos Melo', 'cpf': '999.999.999-99', 'telefone': '(87) 99900-0006', 'parentesco': 'pai', 'cidade': 'Ipubi', 'estado': 'PE'},
    ]

    criados = []
    for data in responsaveis_data:
        resp, created = Responsavel.objects.get_or_create(cpf=data['cpf'], defaults=data)
        if created:
            print(f"   ✅ {resp.nome}")
        criados.append(resp)
    return criados


def criar_alunos(responsaveis):
    from apps.alunos.models import Aluno
    print("\n👶 Criando alunos...")

    hoje = date.today()

    alunos_data = [
        {'nome': 'Sofia Silva', 'data_nascimento': date(hoje.year - 1, 6, 15), 'responsavel_principal': responsaveis[0], 'autorizacao_foto': True},
        {'nome': 'Miguel Santos', 'data_nascimento': date(hoje.year - 2, 3, 22), 'responsavel_principal': responsaveis[1], 'autorizacao_foto': True},
        {'nome': 'Laura Ferreira', 'data_nascimento': date(hoje.year - 3, hoje.month, 10), 'responsavel_principal': responsaveis[2], 'autorizacao_foto': True},
        {'nome': 'Gabriel Alves', 'data_nascimento': date(hoje.year - 4, 9, 5), 'responsavel_principal': responsaveis[3], 'autorizacao_foto': False},
        {'nome': 'Valentina Rodrigues', 'data_nascimento': date(hoje.year - 5, 1, 28), 'responsavel_principal': responsaveis[4], 'autorizacao_foto': True},
        {'nome': 'Arthur Melo', 'data_nascimento': date(hoje.year - 2, 7, 14), 'responsavel_principal': responsaveis[5], 'autorizacao_foto': True},
        {'nome': 'Isabella Costa', 'data_nascimento': date(hoje.year - 1, hoje.month, 3), 'responsavel_principal': responsaveis[0], 'autorizacao_foto': True},
        {'nome': 'Benjamin Lima', 'data_nascimento': date(hoje.year - 4, 11, 19), 'responsavel_principal': responsaveis[1], 'autorizacao_foto': False},
    ]

    criados = []
    for data in alunos_data:
        if not Aluno.objects.filter(nome=data['nome']).exists():
            idade = (hoje - data['data_nascimento']).days // 365
            if idade <= 2:
                faixa = 'bebe'
            elif idade <= 4:
                faixa = 'toddler'
            else:
                faixa = 'kids'
            aluno = Aluno.objects.create(
                nome=data['nome'],
                data_nascimento=data['data_nascimento'],
                faixa_etaria=faixa,
                status='ativo',
                responsavel_principal=data['responsavel_principal'],
                autorizacao_foto=data['autorizacao_foto'],
                data_matricula=hoje - timedelta(days=90),
            )
            print(f"   ✅ {aluno.nome} — {aluno.matricula}")
            criados.append(aluno)
        else:
            criados.append(Aluno.objects.get(nome=data['nome']))
    return criados


def criar_turmas(professores):
    from apps.turmas.models import Turma
    print("\n🏫 Criando turmas...")
    from datetime import time

    turmas_data = [
        {
            'nome': 'Bebê Conforto — Manhã',
            'faixa_etaria': 'bebe',
            'dia_semana': 1,
            'horario_inicio': time(8, 0),
            'horario_fim': time(9, 0),
            'capacidade': 8,
            'professor_responsavel': professores[0],
            'status': 'ativa',
        },
        {
            'nome': 'Pequenos — Segunda/Quarta',
            'faixa_etaria': 'toddler',
            'dia_semana': 0,
            'horario_inicio': time(9, 0),
            'horario_fim': time(10, 0),
            'capacidade': 10,
            'professor_responsavel': professores[1],
            'status': 'ativa',
        },
        {
            'nome': 'Infantil — Tarde',
            'faixa_etaria': 'kids',
            'dia_semana': 2,
            'horario_inicio': time(15, 0),
            'horario_fim': time(16, 0),
            'capacidade': 10,
            'professor_responsavel': professores[1],
            'status': 'ativa',
        },
        {
            'nome': 'Auto Salvamento — Sábado',
            'faixa_etaria': 'mista',
            'dia_semana': 5,
            'horario_inicio': time(8, 0),
            'horario_fim': time(9, 30),
            'capacidade': 12,
            'professor_responsavel': professores[2],
            'status': 'ativa',
        },
    ]

    criados = []
    for data in turmas_data:
        turma, created = Turma.objects.get_or_create(nome=data['nome'], defaults=data)
        if created:
            print(f"   ✅ {turma.nome}")
        criados.append(turma)
    return criados


def criar_matriculas(alunos, turmas):
    from apps.turmas.models import Matricula
    print("\n📋 Criando matrículas...")

    vinculos = [
        (alunos[0], turmas[0], Decimal('150.00')),
        (alunos[6], turmas[0], Decimal('150.00')),
        (alunos[1], turmas[1], Decimal('180.00')),
        (alunos[5], turmas[1], Decimal('180.00')),
        (alunos[2], turmas[1], Decimal('180.00')),
        (alunos[3], turmas[2], Decimal('180.00')),
        (alunos[4], turmas[2], Decimal('180.00')),
        (alunos[7], turmas[3], Decimal('200.00')),
    ]

    for aluno, turma, valor in vinculos:
        if not Matricula.objects.filter(aluno=aluno, turma=turma).exists():
            Matricula.objects.create(
                aluno=aluno,
                turma=turma,
                status='ativa',
                data_inicio=date.today() - timedelta(days=60),
                valor_mensalidade=valor
            )
            print(f"   ✅ {aluno.nome} → {turma.nome}")


def criar_mensalidades(alunos):
    from apps.turmas.models import Matricula
    from apps.financeiro.models import Mensalidade, Pagamento
    print("\n💰 Criando mensalidades e pagamentos...")

    hoje = date.today()
    admin_user = Usuario.objects.filter(username='admin').first()

    for aluno in alunos:
        matricula = Matricula.objects.filter(aluno=aluno, status='ativa').first()
        if not matricula:
            continue
        valor = matricula.valor_mensalidade

        # Mês anterior — paga
        mes_ant = hoje.month - 1 if hoje.month > 1 else 12
        ano_ant = hoje.year if hoje.month > 1 else hoje.year - 1
        mens_ant, created = Mensalidade.objects.get_or_create(
            aluno=aluno, mes=mes_ant, ano=ano_ant,
            defaults={
                'valor_total': valor,
                'data_vencimento': date(ano_ant, mes_ant, 10),
                'status': 'paga',
                'valor_pago': valor,
            }
        )
        if created:
            Pagamento.objects.create(
                mensalidade=mens_ant,
                valor=valor,
                forma_pagamento='pix',
                data_pagamento=date(ano_ant, mes_ant, 8),
                registrado_por=admin_user,
            )

        # Mês atual — situação variada
        import random
        random.seed(aluno.id)
        status_choices = ['pendente', 'pendente', 'vencida', 'paga', 'parcial']
        status = random.choice(status_choices)

        mens_atual, created = Mensalidade.objects.get_or_create(
            aluno=aluno, mes=hoje.month, ano=hoje.year,
            defaults={
                'valor_total': valor,
                'data_vencimento': date(hoje.year, hoje.month, 10),
                'status': status,
                'valor_pago': valor if status == 'paga' else (valor / 2 if status == 'parcial' else Decimal('0')),
            }
        )
        if created and status in ('paga', 'parcial'):
            Pagamento.objects.create(
                mensalidade=mens_atual,
                valor=valor if status == 'paga' else valor / 2,
                forma_pagamento='pix',
                data_pagamento=date(hoje.year, hoje.month, 5),
                registrado_por=admin_user,
            )
        if created:
            print(f"   ✅ {aluno.nome} — {status}")


def main():
    print("=" * 55)
    print("  🏊 C.A.I — Setup Inicial do Sistema")
    print("  C.A.I")
    print("=" * 55)

    try:
        from django.db import connection
        connection.ensure_connection()
    except Exception as e:
        print(f"\n❌ Erro de conexão com banco: {e}")
        print("Execute primeiro: python manage.py migrate")
        return

    criar_usuarios()
    professores = criar_professores()
    responsaveis = criar_responsaveis()
    alunos = criar_alunos(responsaveis)
    turmas = criar_turmas(professores)
    criar_matriculas(alunos, turmas)
    criar_mensalidades(alunos)

    print("\n" + "=" * 55)
    print("  ✅ Setup concluído com sucesso!")
    print("=" * 55)
    print("\n📌 Acesse: http://127.0.0.1:8000/")
    print("👤 Login: admin | Senha: admin123")
    print("🔧 Admin Django: http://127.0.0.1:8000/admin/")
    print("🔌 API REST: http://127.0.0.1:8000/api/v1/")
    print("=" * 55)


if __name__ == '__main__':
    main()
