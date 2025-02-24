from dotenv import load_dotenv
from tabulate import tabulate
import requests
import msal
import os

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do Power BI
TENANT_ID = os.getenv("TENANT_ID")
APP_ID = os.getenv("APP_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
POWER_BI_BASE_URL = "https://api.powerbi.com/v1.0/myorg"


# Função para obter o token de acesso
def request_access_token():
    """
    Obtém um token de acesso do Azure AD para autenticação na API do Power BI.

    Esta função utiliza a biblioteca MSAL para realizar a autenticação OAuth2 com
    as credenciais da aplicação registrada no Azure Active Directory.

    Retorna:
        str: Token de acesso válido para realizar chamadas na API do Power BI.

    Lança:
        Exception: Se houver erro na autenticação, a função levanta uma exceção
        informando o motivo do erro.

    Dependências:
        - A aplicação precisa estar registrada no Azure AD.
        - As variáveis de ambiente TENANT_ID, APP_ID e CLIENT_SECRET devem estar configuradas.
        - O consentimento do administrador deve ser concedido para as permissões da API do Power BI.

    Exemplo de uso:
        access_token = request_access_token()
        headers = {"Authorization": f"Bearer {access_token}"}
    """
    authority_url = f"https://login.microsoftonline.com/{TENANT_ID}"
    scopes = ["https://analysis.windows.net/powerbi/api/.default"]

    client = msal.ConfidentialClientApplication(
        APP_ID, authority=authority_url, client_credential=CLIENT_SECRET
    )
    token_response = client.acquire_token_for_client(scopes=scopes)

    if "access_token" not in token_response:
        raise Exception(
            f"Erro na autenticação: {token_response.get('error_description', 'Desconhecido')}"
        )

    return token_response["access_token"]


# Função para listar workspaces
def list_workspaces(access_token):
    """
    Lista todos os workspaces disponíveis no Power BI para o usuário autenticado.

    Esta função realiza uma requisição à API do Power BI para obter uma lista de
    todos os workspaces acessíveis pelo token de autenticação fornecido.

    Parâmetros:
        access_token (str): Token de acesso obtido via Azure AD para autenticação na API do Power BI.

    Retorna:
        list: Uma lista de dicionários contendo informações dos workspaces disponíveis.
        Cada workspace possui chaves como:
            - 'id': Identificador único do workspace.
            - 'name': Nome do workspace.

    Exceções tratadas:
        - Se a API retornar um erro, a função exibe a mensagem de erro e retorna uma lista vazia.

    Dependências:
        - O usuário ou aplicação precisa ter permissão para acessar os workspaces.
        - O token de acesso deve ser válido e conter a permissão `Workspace.Read.All`.

    Exemplo de uso:
        access_token = request_access_token()
        workspaces = list_workspaces(access_token)
        for ws in workspaces:
            print(f"ID: {ws['id']} - Nome: {ws['name']}")
    """
    endpoint = f"{POWER_BI_BASE_URL}/groups"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        print(f"Erro ao listar workspaces: {response.status_code} - {response.text}")
        return []


# Função para listar relatórios de um workspace
def list_reports(access_token, group_id):
    """
    Lista todos os relatórios disponíveis em um workspace específico no Power BI.

    Esta função faz uma requisição à API do Power BI para obter uma lista de relatórios
    pertencentes a um workspace identificado pelo `group_id`.

    Parâmetros:
        access_token (str): Token de acesso obtido via Azure AD para autenticação na API do Power BI.
        group_id (str): Identificador único do workspace no qual os relatórios serão listados.

    Retorna:
        list: Uma lista de dicionários contendo informações dos relatórios disponíveis.
        Cada relatório possui chaves como:
            - 'id': Identificador único do relatório.
            - 'name': Nome do relatório.
            - 'webUrl': URL do relatório no Power BI Service.

    Exceções tratadas:
        - Se a API retornar um erro, a função exibe a mensagem de erro e retorna uma lista vazia.

    Dependências:
        - O usuário ou aplicação precisa ter permissão para acessar os relatórios no workspace.
        - O token de acesso deve ser válido e conter a permissão `Report.Read.All`.

    Exemplo de uso:
        access_token = request_access_token()
        group_id = "d975d1c2-9dcf-401a-b794-8f158c51a4e1"
        reports = list_reports(access_token, group_id)
        for report in reports:
            print(f"ID: {report['id']} - Nome: {report['name']} - URL: {report['webUrl']}")
    """
    endpoint = f"{POWER_BI_BASE_URL}/groups/{group_id}/reports"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        return response.json().get("value", [])
    else:
        print(f"Erro ao listar relatórios: {response.status_code} - {response.text}")
        return []


# Função para listar datasets de um workspace
def list_datasets(access_token, group_id):
    """
    Lista todos os datasets (modelos semânticos) disponíveis em um workspace do Power BI.

    Esta função faz uma requisição à API do Power BI para obter uma lista de datasets
    associados a um workspace específico, identificado pelo `group_id`.

    Parâmetros:
        access_token (str): Token de acesso obtido via Azure AD para autenticação na API do Power BI.
        group_id (str): Identificador único do workspace no qual os datasets serão listados.

    Retorna:
        list: Uma lista de dicionários contendo informações dos datasets disponíveis.
        Cada dataset pode conter chaves como:
            - 'id': Identificador único do dataset.
            - 'name': Nome do dataset.
            - 'isRefreshable': Indica se o dataset pode ser atualizado.
            - 'configuredBy': Usuário que configurou o dataset.

    Tratamento de erros:
        - Se a API retornar erro 401 (Token inválido), exibe uma mensagem informando falta de permissão.
        - Se a resposta da API não for um JSON válido, exibe um aviso e retorna uma lista vazia.
        - Se a API retornar outro erro, exibe o código e a mensagem de erro.

    Dependências:
        - O usuário ou aplicação precisa ter permissão para acessar os datasets no workspace.
        - O token de acesso deve ser válido e conter a permissão `Dataset.Read.All`.

    Exemplo de uso:
        access_token = request_access_token()
        group_id = "d975d1c2-9dcf-401a-b794-8f158c51a4e1"
        datasets = list_datasets(access_token, group_id)
        for dataset in datasets:
            print(f"ID: {dataset['id']} - Nome: {dataset['name']} - Atualizável: {dataset['isRefreshable']}")
    """
    endpoint = f"{POWER_BI_BASE_URL}/groups/{group_id}/datasets"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        try:
            datasets = response.json().get("value", [])
            return datasets
        except requests.exceptions.JSONDecodeError:
            print("❌ Erro ao decodificar JSON: resposta vazia.")
            return []
    elif response.status_code == 401:
        print("❌ Erro 401: Token inválido ou sem permissão.")
        print(
            "Verifique se as permissões do aplicativo estão configuradas corretamente no Azure."
        )
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")

    return []


# Função para listar tabelas de um dataset (Modelos Semânticos)
def get_dataset_tables(access_token, group_id, dataset_id):
    """
    Obtém as tabelas associadas a um modelo semântico dentro de um workspace específico.

    :param access_token: Token de autenticação
    :param group_id: ID do workspace (group)
    :param dataset_id: ID do dataset (modelo semântico)
    :return: Lista de tabelas do modelo semântico
    """
    endpoint = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/lineage"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200:
        lineage_data = response.json()
        tables = [
            item["name"]
            for item in lineage_data.get("datasetSchema", {}).get("tables", [])
        ]
        return tables
    elif response.status_code == 403:
        print(f"🚫 Permissão negada para acessar o dataset {dataset_id}.")
        print(f"Erro 403: {response.text}")
    else:
        print(
            f"❌ Erro ao obter tabelas do dataset {dataset_id}: {response.status_code} - {response.text}"
        )

    return []


# Função para imprimir datasets no console
def print_datasets_table(datasets):
    """
    Exibe uma lista de datasets (modelos semânticos) formatada em tabela no console.

    Esta função recebe uma lista de datasets e os exibe de forma organizada usando a
    biblioteca `tabulate`. Se a lista estiver vazia, exibe uma mensagem informando
    que nenhum dataset foi encontrado.

    Parâmetros:
        datasets (list): Lista de dicionários contendo informações dos datasets.
        Cada dataset pode conter as seguintes chaves:
            - 'id' (str): Identificador único do dataset.
            - 'name' (str): Nome do dataset.
            - 'webUrl' (str): URL para acessar o dataset no Power BI Service.
            - 'isRefreshable' (bool): Indica se o dataset pode ser atualizado.
            - 'configuredBy' (str): Usuário que configurou o dataset.

    Retorno:
        None: A função apenas exibe os dados no console e não retorna valores.

    Dependências:
        - A biblioteca `tabulate` deve estar instalada (`pip install tabulate`).
        - A função deve receber uma lista válida de datasets, obtida via API.

    Exemplo de uso:
        datasets = [
            {
                "id": "1234",
                "name": "Dataset Vendas",
                "webUrl": "https://app.powerbi.com/dataset/1234",
                "isRefreshable": True,
                "configuredBy": "admin@empresa.com"
            }
        ]
        print_datasets_table(datasets)

    """
    if not datasets:
        print("Nenhum dataset encontrado.")
        return

    table_data = []
    for ds in datasets:
        table_data.append(
            [
                ds.get("id", ""),
                ds.get("name", ""),
                ds.get("webUrl", ""),
                ds.get("isRefreshable", ""),
                ds.get("configuredBy", ""),
            ]
        )

    headers = ["ID", "Nome", "WebUrl", "isRefreshable", "configuredBy"]
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))


# Função para exibir relatórios e tabelas associadas
def list_reports_and_tables(access_token, group_id):
    """
    Lista todos os relatórios disponíveis em um workspace do Power BI e exibe
    as tabelas associadas aos datasets de cada relatório.

    Esta função obtém a lista de relatórios dentro de um workspace e, para
    cada relatório, verifica se há um dataset vinculado. Se houver, tenta
    listar as tabelas associadas ao dataset.

    Parâmetros:
        access_token (str): Token de acesso obtido via Azure AD para autenticação na API do Power BI.
        group_id (str): Identificador único do workspace no qual os relatórios serão listados.

    Retorno:
        None: A função apenas exibe os dados no console e não retorna valores.

    Tratamento de erros:
        - Se o workspace não contiver relatórios, exibe uma mensagem e retorna.
        - Se um relatório não possuir dataset associado, exibe uma mensagem informativa.
        - Se houver erro ao buscar tabelas do dataset, exibe um aviso.

    Dependências:
        - O usuário ou aplicação precisa ter permissão para acessar os relatórios e datasets no workspace.
        - O token de acesso deve ser válido e conter as permissões `Report.Read.All` e `Dataset.Read.All`.

    Exemplo de uso:
        access_token = request_access_token()
        group_id = "d975d1c2-9dcf-401a-b794-8f158c51a4e1"
        list_reports_and_tables(access_token, group_id)

    """
    reports = list_reports(access_token, group_id)

    if not reports:
        print("Nenhum relatório encontrado.")
        return

    for report in reports:
        report_name = report.get("name")
        dataset_id = report.get("datasetId")

        print(f"\n📊 Relatório: {report_name}")
        print(f"  Dataset ID: {dataset_id}")

        if dataset_id:
            tables = get_dataset_tables(access_token, group_id, dataset_id)
            if tables:
                print("  🔍 Tabelas utilizadas:")
                for table in tables:
                    print(f"    - {table}")
            else:
                print("  🚫 Nenhuma tabela encontrada.")
        else:
            print("  🚫 Este relatório não tem um dataset vinculado.")


# Atualiza o modelo semântico (antigo dataset)
def update_semantic_model(group_id, dataset_id, access_token):
    """
    Inicia a atualização de um modelo semântico no Power BI.

    Esta função faz uma requisição à API do Power BI para iniciar o refresh de um
    dataset (modelo semântico) dentro de um workspace específico.

    Parâmetros:
        group_id (str): Identificador único do workspace onde o dataset está localizado.
        dataset_id (str): Identificador único do dataset a ser atualizado.
        access_token (str): Token de acesso obtido via Azure AD para autenticação na API do Power BI.

    Retorno:
        None: A função apenas exibe no console se a atualização foi iniciada com sucesso ou se houve erro.

    Tratamento de erros:
        - Se a atualização for iniciada corretamente (`status_code 202`), exibe uma mensagem de sucesso.
        - Se houver erro na requisição, exibe o código do erro e a mensagem retornada pela API.

    Dependências:
        - O usuário ou aplicação precisa ter permissão para atualizar modelos semânticos no Power BI.
        - O token de acesso deve ser válido e conter a permissão `Dataset.ReadWrite.All`.

    Exemplo de uso:
        access_token = request_access_token()
        group_id = "d975d1c2-9dcf-401a-b794-8f158c51a4e1"
        dataset_id = "a1fc762a-4d1b-486b-b147-fa7db3d8d1bf"
        update_semantic_model(group_id, dataset_id, access_token)
    """
    endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/refreshes"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.post(endpoint, headers=headers)

    if response.status_code == 202:
        print("✅ Atualização do modelo semântico iniciada com sucesso!")
    else:
        print(
            f"❌ Erro ao atualizar o modelo semântico: {response.status_code} - {response.text}"
        )


# Função principal
def main():
    access_token = request_access_token()
    workspaces = list_workspaces(access_token)

    if not workspaces:
        print("Nenhum workspace encontrado.")
        return

    print("\n🌐 Lista de Workspaces:")
    for i, ws in enumerate(workspaces):
        print(f"{i+1}. {ws['name']} (ID: {ws['id']})")

    choice = (
        int(input("\nDigite o número do workspace para listar os relatórios: ")) - 1
    )
    selected_workspace = workspaces[choice]["id"]

    datasets = list_datasets(access_token, selected_workspace)
    print("\n📂 Datasets Disponíveis:")
    print_datasets_table(datasets)

    list_reports_and_tables(access_token, selected_workspace)

    # Opção para atualizar dataset
    update = input("\nDeseja atualizar algum dataset? (s/n): ").strip().lower()
    if update == "s":
        dataset_id = input("Digite o ID do dataset a ser atualizado: ").strip()
        update_semantic_model(selected_workspace, dataset_id, access_token)


# Executa o script
if __name__ == "__main__":
    main()
