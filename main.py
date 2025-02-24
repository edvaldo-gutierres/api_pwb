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


# 🔄 Atualiza o dataset
def refresh_dataset(dataset_id, access_token):
    """
    Inicia a atualização de um dataset no Power BI.

    :param dataset_id: ID do dataset a ser atualizado.
    :param access_token: Token de acesso.
    """
    endpoint = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes"
    headers = {"Authorization": f"Bearer " + access_token}

    response = requests.post(endpoint, headers=headers)
    if response.status_code == 202:
        print("✅ Dataset atualizado com sucesso!")
    else:
        print(
            f"❌ Erro ao atualizar o dataset: {response.status_code} - {response.text}"
        )


# 🔄 Atualiza o modelo semântico
def update_semantic_model(group_id, dataset_id, access_token):
    """
    Dispara o refresh do dataset (atualiza o modelo semântico) dentro de um workspace.

    :param group_id: ID do workspace onde o dataset está.
    :param dataset_id: ID do dataset a ser atualizado.
    :param access_token: Token de acesso.
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
