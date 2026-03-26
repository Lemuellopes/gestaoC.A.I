# 🏊 C.A.I — Sistema Administrativo
## Centro Aquático Infantil — Instituto Tia Duda

---

## 📋 Visão Geral

Sistema administrativo completo desenvolvido em **Django 4.2** para gerenciamento do Centro Aquático Infantil. Inclui:

- ✅ Autenticação com perfis de acesso (Admin, Coordenação, Financeiro, Professor)
- ✅ Gestão de alunos e responsáveis com dados médicos e autorizações
- ✅ Gestão de professores/instrutores com horários de disponibilidade
- ✅ Controle de turmas, matrículas com validação de vagas e duplicidade
- ✅ Módulo financeiro com mensalidades, pagamentos e dashboard
- ✅ Dashboard com KPIs operacionais e financeiros
- ✅ API REST completa (Django REST Framework)
- ✅ Admin Django customizado com Jazzmin
- ✅ Interface responsiva com paleta visual do C.A.I

---

## 🚀 Instalação

### 1. Pré-requisitos

- Python 3.10+
- pip

### 2. Criar ambiente virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Aplicar migrações do banco de dados

```bash
python manage.py migrate
```

### 5. Executar setup com dados iniciais (recomendado)

```bash
python setup_inicial.py
```

> Cria usuários, instrutores, responsáveis, alunos, turmas, matrículas e mensalidades de demonstração.

### 6. Iniciar o servidor

```bash
python manage.py runserver
```

Acesse: **http://127.0.0.1:8000/**

---

## 👤 Usuários de Acesso

| Usuário       | Senha      | Perfil        |
|---------------|------------|---------------|
| `admin`       | `admin123` | Administrador |
| `coordenacao` | `coord123` | Coordenação   |
| `financeiro`  | `fin123`   | Financeiro    |

---

## 🔗 URLs do Sistema

| URL                          | Descrição                     |
|------------------------------|-------------------------------|
| `/`                          | Dashboard principal           |
| `/login/`                    | Login                         |
| `/alunos/`                   | Lista de alunos               |
| `/alunos/<id>/`              | Perfil do aluno               |
| `/alunos/novo/`              | Cadastrar aluno               |
| `/alunos/responsavel/novo/`  | Cadastrar responsável         |
| `/professores/`              | Lista de instrutores          |
| `/professores/<id>/`         | Perfil do instrutor           |
| `/turmas/`                   | Lista de turmas               |
| `/turmas/<id>/`              | Detalhe da turma              |
| `/financeiro/`               | Dashboard financeiro          |
| `/financeiro/mensalidades/`  | Lista de mensalidades         |
| `/admin/`                    | Admin Django (Jazzmin)        |
| `/api/v1/`                   | API REST (DRF Browsable API)  |

---

## 🔌 API REST — Endpoints

### Alunos
```
GET    /api/v1/alunos/                    Lista com filtros
POST   /api/v1/alunos/                    Criar aluno
GET    /api/v1/alunos/<id>/               Detalhe
PUT    /api/v1/alunos/<id>/               Atualizar
DELETE /api/v1/alunos/<id>/               Remover
GET    /api/v1/alunos/ativos/             Apenas ativos
GET    /api/v1/alunos/por_faixa_etaria/   Distribuição por faixa
GET    /api/v1/alunos/aniversariantes/    Aniversariantes do mês
```

Filtros disponíveis: `?status=ativo&faixa_etaria=bebe&search=sofia`

### Professores
```
GET    /api/v1/professores/               Lista com filtros
GET    /api/v1/professores/ativos/        Apenas ativos
GET    /api/v1/professores/por_especialidade/
```

Filtros: `?especialidade=natacao_infantil&status=ativo&cidade=Araripina`

### Turmas
```
GET    /api/v1/turmas/                    Lista com filtros
GET    /api/v1/turmas/ativas/             Apenas ativas
GET    /api/v1/turmas/<id>/matriculas/    Alunos da turma
```

Filtros: `?status=ativa&faixa_etaria=bebe&dia_semana=0`

### Financeiro
```
GET    /api/v1/financeiro/mensalidades/             Lista com filtros
GET    /api/v1/financeiro/mensalidades/vencidas/    Apenas vencidas
GET    /api/v1/financeiro/mensalidades/resumo_mes/  Resumo do mês
GET    /api/v1/financeiro/mensalidades/resumo_ultimos_meses/
```

Filtros: `?status=vencida&mes=3&ano=2026&aluno=1`

---

## 🗂️ Estrutura do Projeto

```
cai_system/
├── manage.py
├── setup_inicial.py       ← Script de dados iniciais
├── requirements.txt
├── README.md
├── cai_system/            ← Configurações Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/          ← Usuários e perfis
│   ├── alunos/            ← Alunos e responsáveis
│   ├── professores/       ← Instrutores e horários
│   ├── turmas/            ← Turmas e matrículas
│   ├── financeiro/        ← Mensalidades e pagamentos
│   └── dashboard/         ← Dashboard e KPIs
├── templates/
│   ├── base.html
│   ├── registration/login.html
│   ├── dashboard/
│   ├── alunos/
│   ├── professores/
│   ├── turmas/
│   └── financeiro/
└── static/
```

---

## 🎨 Paleta Visual

| Cor              | Código    | Uso                    |
|------------------|-----------|------------------------|
| Azul principal   | `#1a6fb5` | Sidebar, botões, links |
| Azul escuro      | `#0a3560` | Sidebar fundo          |
| Teal             | `#00a8b5` | Instrutores, destaques |
| Amarelo          | `#f5c400` | Logo, aniversariantes  |
| Verde            | `#2ecc71` | Pagamentos, ativos     |
| Vermelho         | `#e74c3c` | Atrasos, vencidos      |

---

## ⚙️ Configurações para Produção

```python
# settings.py — altere antes de ir para produção:
DEBUG = False
SECRET_KEY = 'sua-chave-super-secreta-aqui'
ALLOWED_HOSTS = ['seu-dominio.com.br']

# Banco de dados PostgreSQL (recomendado):
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cai_db',
        'USER': 'cai_user',
        'PASSWORD': 'senha_segura',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 📝 Notas Técnicas

- **Matrícula automática**: Gerada sequencialmente no formato `CAI0001`
- **Cálculo de idade**: Calculado automaticamente a partir da data de nascimento
- **Faixa etária automática**: Atribuída conforme a idade (0-2=Bebê, 2-4=Toddler, 4-6=Kids)
- **Unicidade de matrícula ativa**: Constraint no banco impede duplicidade por turma
- **Atualização de status financeiro**: Ao salvar pagamento, a mensalidade é recalculada automaticamente
- **Tempo de casa do professor**: Calculado dinamicamente a partir da data de admissão

---

*C.A.I — Centro Aquático Infantil | Instituto Tia Duda | Araripina — PE*
