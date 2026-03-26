# 🚀 QUICK START — Configuração de Segurança

**Tempo estimado:** 5-10 minutos

---

## 1️⃣ Copiar Variáveis de Ambiente

```bash
# Na raiz do projeto
cp .env.example .env
```

---

## 2️⃣ Gerar SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

**Copie o resultado gerado e cole no `.env`:**
```env
SECRET_KEY=seu-valor-super-seguro-aqui
```

---

## 3️⃣ Instalar Dependências

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Aplicar Migrações (se houver)

```bash
python manage.py migrate
```

---

## 5️⃣ Testar Login com Rate Limiting

### Teste 1: Login Bem-Sucedido
```bash
# Abrir http://127.0.0.1:8000/login
# Usuário: admin
# Senha: admin123
# Resultado esperado: ✅ Login bem-sucedido
```

### Teste 2: Rate Limiting Ativo
```bash
# Fazer 6 tentativas de login com senha errada em 10 minutos
# Tentativa 1-5: ❌ "Usuário ou senha inválidos"
# Tentativa 6: 🚫 HTTP 403 Forbidden (Rate limit excedido)
```

---

## 6️⃣ Validação de CPF

### Teste: Adicionar Responsável
```bash
# Ir para: http://127.0.0.1:8000/alunos/responsavel/novo/
# Tentar CPF inválido: 111.111.111-11
# Resultado esperado: ❌ "CPF inválido (dígito verificador incorreto)"

# Tentar CPF válido: (gerar em https://www.4devs.com.br/gerador_cpf)
# Resultado esperado: ✅ Responsável criado
```

---

## 7️⃣ Proteção de API REST

### Teste 1: Sem Autenticação
```bash
curl http://127.0.0.1:8000/api/v1/alunos/
# Resultado esperado: 🔴 HTTP 403 Forbidden
```

### Teste 2: Com Login
```bash
# Fazer login no navegador
# Ir para: http://127.0.0.1:8000/api/v1/alunos/
# Resultado esperado: ✅ Lista de alunos em JSON
```

### Teste 3: Tentar POST (Criar)
```bash
curl -X POST http://127.0.0.1:8000/api/v1/alunos/ \
  -H "Content-Type: application/json" \
  -d '{"nome":"Teste"}'
# Resultado esperado: 🔴 HTTP 403 (não-staff não pode criar)
```

---

## 8️⃣ Parâmetros Validados

### Teste: Mês Inválido
```bash
# Ir para: http://127.0.0.1:8000/api/v1/alunos/aniversariantes/?mes=13
# Resultado esperado: ✅ Mostra aniversariantes do mês padrão (hoje)
```

---

## ✅ Próximos Passos

1. **Ativar Audit Log** (já instalado)
   - Descomente em `settings.py` quando pronto
   - Requer nova migração

2. **Configurar `.env` para Produção**
   - Mude `DEBUG=False`
   - Configure `ALLOWED_HOSTS` real
   - Configure `SECRET_KEY` mais segura

3. **Adicionar Email**
   - Configure `EMAIL_*` em `.env`
   - Ative notificações de segurança

---

## 🐛 Debugging

### Logs de Segurança
```bash
# Ver logs de tentativas de login
tail -f logs/django.log

# Ver logs de segurança
tail -f logs/security.log
```

### Modo Debug
```bash
# Em desenvolvimento, deixar DEBUG=True em .env
DEBUG=True

# Em produção, SEMPRE FALSE
DEBUG=False
```

---

## 🆘 Problemas Comuns

### "ModuleNotFoundError: No module named 'django_ratelimit'"
```bash
# Solução: Instalar dependências
pip install -r requirements.txt
```

### "RecursionError" ou "ImportError"
```bash
# Solução: Limpar cache Python
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

### "403 Forbidden" em todas as requisições
```bash
# Verificar se está autenticado
# Ir para http://127.0.0.1:8000/login
# Fazer login com admin/admin123
```

---

## 📚 Documentação Completa

Para entender cada aspecto de segurança:

1. **ANALISE_SEGURANCA.md** — Por quê cada correção foi feita
2. **RECOMENDACOES_SEGURANCA.md** — Código pronto para copiar/colar
3. **README.md** — Modo de usar o sistema

---

**Tudo pronto! 🎉**

Qualquer dúvida, consulte os arquivos de documentação.
