# -*- coding: utf-8 -*-
"""
Módulo de serviço para integração com a API do Mercado Pago.

Responsável por criar preferências de pagamento (Checkout Pro), que geram
um link para que o cliente realize o pagamento diretamente na página do Mercado Pago.
"""

import mercadopago
# Importa as credenciais e a URL pública do arquivo de configuração.
from config import MERCADO_PAGO_ACCESS_TOKEN, PUBLIC_URL

# 1. Inicializa o SDK do Mercado Pago com o Access Token.
sdk = mercadopago.SDK(MERCADO_PAGO_ACCESS_TOKEN)

def criar_preferencia_mercadopago(items, user_data, payment_method):
    """
    Cria uma preferência de pagamento no Mercado Pago.

    Args:
        items (list): Uma lista de dicionários, onde cada um representa um item da compra.
                      Ex: [{"name": "Produto 1", "quantity": 1, "unit_price": 100.50}]
        user_data (dict): Dicionário com dados do cliente (ex: {"email": "cliente@email.com"}).
        payment_method (str): O método de pagamento desejado ('pix' ou 'card').

    Returns:
        str: A URL de "init_point" para redirecionar o cliente para o checkout.
    """
    # 2. Monta o dicionário com os dados da preferência.
    preference_data = {
        "items": [{
            "title": item["name"],
            "quantity": item["quantity"],
            "unit_price": item["unit_price"]
        } for item in items],
        "payer": {
            "email": user_data["email"]
        },
        # URLs de retorno após o pagamento.
        "back_urls": {
            "success": f"{PUBLIC_URL}/compracerta?status=approved",
            "failure": f"{PUBLIC_URL}/pagamento_falhou"
        },
        # Redireciona automaticamente o cliente de volta para o site após aprovação.
        "auto_return": "approved"
    }

    # 3. Filtra os métodos de pagamento com base na escolha do usuário.
    if payment_method == 'pix':
        # Se for PIX, exclui pagamentos com cartão de crédito.
        preference_data["payment_methods"] = {
            "excluded_payment_types": [{"id": "credit_card"}]
        }
    elif payment_method == 'card':
        # Se for cartão, exclui boleto e outros meios.
        preference_data["payment_methods"] = {
            "excluded_payment_types": [{"id": "ticket"}, {"id": "atm"}, {"id": "bank_transfer"}]
        }

    # 4. Cria a preferência usando o SDK.
    preference_response = sdk.preference().create(preference_data)
    
    # 5. Retorna o link de pagamento (init_point) gerado pela API.
    return preference_response["response"]["init_point"]