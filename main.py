from dotenv import load_dotenv
from tabulate import tabulate
import requests
import msal
import os

# Carrega variáveis de ambiente
load_dotenv()


# Função para imprimir a tabela de datasets
def print_datasets_table(datasets):
    if not datasets:
        print("Nenhum dataset encontrado.")
        return

    # Monta uma lista de listas, cada sublista é uma linha da tabela
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

    # Cabeçalhos das colunas
    headers = ["ID", "Nome", "WebUrl", "isRefreshable", "configuredBy"]

    # Imprime a tabela no console
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))


# Solicita o token de acesso
def request_access_token(app_id, client_secret, tenant_id):
    authority_url = f"https://login.microsoftonline.com/{tenant_id}"
    scopes = ["https://analysis.windows.net/powerbi/api/.default"]

    client = msal.ConfidentialClientApplication(
        app_id, authority=authority_url, client_credential=client_secret
    )
    token_response = client.acquire_token_for_client(scopes=scopes)

    if "access_token" not in token_response:
        raise Exception(
            f"Erro na autenticação: {token_response.get('error_description', 'Desconhecido')}"
        )

    return token_response["access_token"]


# Lista dos workspaces
def list_workspaces(access_token):
    endpoint = "https://api.powerbi.com/v1.0/myorg/groups"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        workspaces = response.json().get("value", [])
        for ws in workspaces:
            print("Nome:", ws.get("name"), "- ID:", ws.get("id"))
        return workspaces
    else:
        print(response.reason)
        print(response.json())
        return None


# Lista dos report
def list_reports(access_token, groupId):
    endpoint = f"https://api.powerbi.com//v1.0/myorg/groups/{groupId}/reports"
    headers = {"Authorization": f"Bearer " + access_token}
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        reports = response.json().get("value", [])
        for report in reports:
            print("Nome:", report.get("name"), "- ID:", report.get("id"))
    else:
        print(response.reason)
        print(response.json())


# Lista dos datasets
def list_datasets(access_token, groupId):
    endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{groupId}/datasets"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(endpoint, headers=headers)

    # print(f"Status Code: {response.status_code}")  # Mostra o código HTTP
    # print(f"Resposta da API: {response.text}")  # Exibe o conteúdo da resposta

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


# Atualiza o dataset
def refresh_dataset(dataset_id, access_token):
    endpoint = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes"
    headers = {"Authorization": f"Bearer " + access_token}

    response = requests.post(endpoint, headers=headers)
    if response.status_code == 202:
        print("Dataset refreshed")
    else:
        print(response.reason)
        print(response.json())


def update_semantic_model(group_id, dataset_id, access_token):
    """
    Dispara o refresh do dataset (atualiza o modelo semântico) para um dataset que está em um workspace.

    Parâmetros:
      - group_id: ID do workspace onde o dataset está.
      - dataset_id: ID do dataset a ser atualizado.
      - access_token: Token de acesso obtido via MSAL.
    """
    endpoint = f"https://api.powerbi.com/v1.0/myorg/groups/{group_id}/datasets/{dataset_id}/refreshes"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.post(endpoint, headers=headers)

    if response.status_code == 202:
        print("Atualização do modelo semântico iniciada com sucesso!")
    else:
        print(
            f"Erro ao atualizar o modelo semântico ({response.status_code}):",
            response.text,
        )


# Função principal
def main():
    # Variáveis de ambiente
    app_id = os.getenv("APP_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    tenant_id = os.getenv("TENANT_ID")
    groupId = "d975d1c2-9dcf-401a-b794-8f158c51a4e1"  # Workspace ID
    datasetId = "a1fc762a-4d1b-486b-b147-fa7db3d8d1bf"  # Dataset ID

    # Debug: Verificar se as variáveis foram carregadas
    # print(f"APP_ID: {app_id}")
    # print(f"CLIENT_SECRET: {'OK' if client_secret else '❌ NÃO ENCONTRADO'}")
    # print(f"TENANT_ID: {tenant_id}")

    # Acessa o Power BI
    access_token = request_access_token(app_id, client_secret, tenant_id)

    # Exibir os primeiros caracteres do token para verificar se foi gerado corretamente
    # print(f"Access Token: {access_token[10:]}...") if access_token else print("❌ Token não foi gerado!")

    # Lista os workspaces
    print(list_workspaces(access_token))

    # Lista os reports
    print(list_reports(access_token, groupId))

    # Lista os datasets
    print_datasets_table(list_datasets(access_token, groupId))

    # Atualiza o dataset
    update_semantic_model(groupId, datasetId, access_token)


# Executa o script
if __name__ == "__main__":
    main()
