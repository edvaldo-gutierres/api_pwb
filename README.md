# API Power BI 

Este projeto demonstra como acessar a API do Power BI utilizando Python.

O objetivo é listar workspaces, datasets, atualizar modelos semânticos, etc., via **Service Principal**.

---

## Estrutura de Pastas

```text
API_PWB (raiz do projeto)
│
├── .venv/                       # Ambiente virtual (gerado automaticamente pelo Poetry ou Python)
├── docs/
│   ├── Configuração.md          # Documentação detalhada de configuração
│
├── .env                         # Variáveis de ambiente (APP_ID, CLIENT_SECRET, TENANT_ID)
├── .gitignore                   # Arquivos/pastas ignorados pelo Git
├── .pre-commit-config.yaml      # Configuração de hooks pré-commit 
├── main.py                      # Script principal (autenticação, chamadas à API, exibição de dados)
├── poetry.lock                  # Arquivo de bloqueio de dependências do Poetry
├── pyproject.toml               # Arquivo principal de configuração do Poetry (dependências, etc.)
└── README.md                    # Este arquivo
```

---

## Pré-Requisitos

1. **Windows Subsystem for Linux (WSL)**  
   - Ter o WSL instalado e configurado no Windows 10 ou superior.  
   - [Documentação Oficial do WSL](https://docs.microsoft.com/pt-br/windows/wsl/)

2. **Python 3.11 ou versão compatível**  
   - Verifique com `python --version` (dentro do WSL).

3. **Poetry**  
   - Para gerenciar as dependências do projeto:  
     ```bash
     curl -sSL https://install.python-poetry.org | python3 -
     ```
   - Adicione o Poetry ao PATH conforme instruções exibidas após a instalação.

4. **Conta e Configurações no Azure AD / Power BI**  
   - Registro de Aplicativo no Azure AD (App Registration)  
   - Permissões de **Application** 
   - Habilitar **Allow service principals to use Power BI APIs** no **Portal de Administração** do Power BI  
   - Adicionar o service principal no workspace necessário (como Membro, Contribuidor ou Admin)

---

## Configuração

1. **Clonar o Repositório**  
   ```bash
   git clone <URL-do-seu-repositorio>
   cd <nome-da-pasta>
   ```

2. **Instalar Dependências com Poetry**  
   ```bash
   poetry install
   ```

3. **Variáveis de Ambiente**  
   Crie o arquivo `.env` na raiz do projeto, definindo:
   ```env
   APP_ID=seu_app_id
   CLIENT_SECRET=seu_client_secret
   TENANT_ID=seu_tenant_id
   ```
   > **Atenção**: Não commitar esse arquivo sem o .gitignore em repositórios públicos, pois contém credenciais sensíveis.

---

## Como Executar

1. **Ativar o Ambiente Poetry**  
   ```bash
   poetry shell
   ```
   Isso garante que os pacotes sejam executados no ambiente virtual criado pelo Poetry.

2. **Rodar o Script Principal**  
   ```bash
   python main.py
   ```
   O script:
   - Lê as variáveis de ambiente (`.env`)  
   - Obtém o token de acesso via MSAL (Service Principal)  
   - Lista workspaces, reports e datasets do Power BI  
   - Pode disparar o refresh (atualizar o modelo semântico) de um dataset

3. **Exibir Datasets em Formato de Tabela**  
   - No script, utilizamos a biblioteca `tabulate` (caso esteja declarada no `pyproject.toml`) para formatação amigável no console.  
   - Ajuste ou remova prints indesejados conforme necessário.

---

## Documentos de Apoio

Na pasta [`docs/`](docs/), você encontra arquivos que detalham configurações e permissões:
- **Configuração.md**: Passo a passo de como configurar o aplicativo no Azure AD e no Power BI.  

---

## Observações

- **Propagação de Permissões**: Após conceder permissões no Azure AD e no Portal de Administração do Power BI, aguarde alguns minutos até que elas sejam efetivadas.
- **Manutenção**: Sempre que atualizar dependências, rode `poetry update` e commit o novo `poetry.lock`.
- **Segurança**: Proteja o arquivo `.env` para não expor suas credenciais.

---

## Referências

- [Documentação Oficial do Power BI REST API](https://learn.microsoft.com/pt-br/rest/api/power-bi/)
- [Azure Active Directory - App Registration](https://learn.microsoft.com/pt-br/azure/active-directory/develop/quickstart-register-app)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [WSL Documentation](https://docs.microsoft.com/pt-br/windows/wsl/)

---

**Autor**: Edvaldo Gutierres Ferreira  
**Contato**: edvaldo_gutierres@yahoo.com.br

---