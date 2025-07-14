"""
Módulo de serviço para integração com a API v2 de Checkout do PayPal.

Funções:
- Obter um token de acesso OAuth2.
- Criar um pedido de pagamento (Order).
- Capturar o pagamento após a aprovação do cliente.
"""

import requests
# Importa as credenciais e URLs do arquivo de configuração.
from config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_BASE_URL, PUBLIC_URL

def get_paypal_access_token():
    """
    Obtém um token de acesso da API do PayPal usando as credenciais do cliente.

    Returns:
        str: O token de acesso Bearer para ser usado em requisições subsequentes.
    """
    url = f"{PAYPAL_BASE_URL}/v1/oauth2/token"
    data = {'grant_type': 'client_credentials'}
    # A autenticação é feita via HTTP Basic Auth com o Client ID e Client Secret.
    response = requests.post(url, data=data, auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET))
    response.raise_for_status()  # Lança uma exceção se a requisição falhar.
    return response.json()['access_token']

def create_paypal_order(access_token, items, total_usd):
    """
    Cria um pedido (Order) no PayPal.

    Args:
        access_token (str): O token de acesso obtido de get_paypal_access_token().
        items (list): Uma lista de itens do pedido (atualmente não usada na montagem do corpo).
        total_usd (float): O valor total do pedido em dólares americanos.

    Returns:
        str: O link de aprovação para onde o cliente deve ser redirecionado.
    """
    url = f"{PAYPAL_BASE_URL}/v2/checkout/orders"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    # Define a estrutura do pedido. "INTENT: CAPTURE" significa que o valor será capturado
    # em um passo posterior, após a aprovação do cliente.
    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD", # Moeda deve ser USD para o PayPal
                "value": f"{total_usd:.2f}"
            }
        }],
        "application_context": {
            "return_url": f"{PUBLIC_URL}/paypal/success",
            "cancel_url": f"{PUBLIC_URL}/pagamento_falhou"
        }
    }

    response = requests.post(url, headers=headers, json=order_data)
    response.raise_for_status()
    
    # Extrai o link de "approve" da resposta da API.
    approval_link = next(link['href'] for link in response.json()['links'] if link['rel'] == 'approve')
    return approval_link

def capture_paypal_order(access_token, order_id):
    """
    Captura o pagamento de um pedido previamente aprovado pelo cliente.

    Args:
        access_token (str): O token de acesso da API.
        order_id (str): O ID do pedido do PayPal (obtido na URL de retorno).

    Returns:
        dict: A resposta completa da API de captura, contendo os detalhes da transação.
    """
    url = f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()