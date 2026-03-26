# C.A.I - Sistema Administrativo v2.0
## Centro Aquetico Infatil - C.A.I
### Versao com Seguranca Reforcada e Design Premium

## Design System - Marine Luxury
Interface desenvolvida com a estetica Marine Luxury:
- Tipografia: Playfair Display (titulos) + DM Sans (corpo) + DM Mono (codigos)
- Paleta: Azul oceano profundo, teal cristalino, dourado premium
- Componentes: Cards com hover animation, badges semanticos, KPI cards
- Responsivo: Sidebar collapsible, layout adaptativo

## Seguranca Implementada
- SESSION_COOKIE_HTTPONLY=True
- CSRF_COOKIE_HTTPONLY=True
- SESSION_COOKIE_AGE=8h
- X_FRAME_OPTIONS=DENY
- Rate Limiting: 5 tentativas -> bloqueio 15 min
- Headers HTTP de seguranca via SecurityHeadersMiddleware
- API Throttling: 500 req/hora usuarios autenticados
- Logs de seguranca em logs/security.log
- Validacao de senhas (min 8 chars, nao numerica, nao comum)

## Instalacao

1. python -m venv venv && source venv/bin/activate
2. pip install -r requirements.txt
3. cp .env.example .env  (edite com sua SECRET_KEY)
4. python manage.py migrate
5. python setup_inicial.py
6. python manage.py runserver

Acesse: http://127.0.0.1:8000/
Login: admin / admin123

## Verificar Seguranca
python check_seguranca.py

## Rotina Automatica de Cobranca (Padrao de Mercado)
O sistema possui uma rotina financeira automatizavel para:
- Gerar/atualizar mensalidades do mes de referencia
- Atualizar mensalidades vencidas automaticamente

Comando manual:
python manage.py rotina_financeira

Para gerar o proximo mes antecipadamente:
python manage.py rotina_financeira --proximo-mes

Exemplo de agendamento no Windows (diario as 00:05):
schtasks /Create /SC DAILY /TN "CAI-RotinaFinanceira" /TR "c:\\Users\\lemue\\Downloads\\cai_sistema_v2_seguro_premium\\.venv\\Scripts\\python.exe c:\\Users\\lemue\\Downloads\\cai_sistema_v2_seguro_premium\\cai_system\\manage.py rotina_financeira" /ST 00:05

## URLs
/ - Dashboard
/login/ - Login com rate limiting
/alunos/ - Gestao de alunos
/professores/ - Gestao de instrutores
/turmas/ - Turmas e matriculas
/financeiro/ - Dashboard financeiro
/admin/ - Admin Django (Jazzmin)
/api/v1/ - API REST com throttling

C.A.I - Araripina, PE
