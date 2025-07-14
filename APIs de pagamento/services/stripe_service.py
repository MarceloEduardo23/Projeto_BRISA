"""
Módulo de serviço para integração com a API do Stripe.

Responsável por:
- Criar sessões de checkout, que fornecem uma URL segura para o cliente pagar.
- Processar e validar webhooks enviados pelo Stripe para confirmar eventos de pagamento.
"""

import stripe
# Importa as chaves e URLs do arquivo de configuração.
from config import STRIPE_SECRET_KEY, PUBLIC_URL, STRIPE_WEBHOOK_SECRET

# Configura a chave secreta da API do Stripe globalmente.
stripe.api_key = STRIPE_SECRET_KEY

def criar_checkout_stripe(items_data, valor_imposto, user_data):
    """
    Cria uma sessão de checkout no Stripe.

    Args:
        items_data (list): Lista de dicionários com dados dos itens (name, quantity).
        valor_imposto (float): Valor do imposto a ser adicionado como um item separado.
        user_data (dict): Dados do cliente (pelo menos o email).

    Returns:
        str: A URL da sessão de checkout para redirecionar o cliente.
    """
    # Simula um banco de dados de preços para obter os valores dos produtos.
    precos_db = {
        "Smartphone Premium": 899.99,
        "Fones de Ouvido Bluetooth": 199.99
    }

    line_items = []

    # Monta a lista de itens no formato exigido pela API do Stripe.
    for item in items_data:
        price = precos_db.get(item['name'])
        if price:
            line_items.append({
                'price_data': {
                    'currency': 'brl',
                    'product_data': {'name': item['name']},
                    # O valor deve ser em centavos (inteiro).
                    'unit_amount': int(price * 100),
                },
                'quantity': item['quantity'],
            })

    # Adiciona o valor do imposto como um item separado na sessão.
    line_items.append({
        'price_data': {
            'currency': 'brl',
            'product_data': {'name': 'Impostos'},
            'unit_amount': int(valor_imposto * 100),
        },
        'quantity': 1,
    })

    # Cria a sessão de checkout na API do Stripe.
    checkout_session = stripe.checkout.Session.create(
        line_items=line_items,
        mode='payment',
        success_url=f"{PUBLIC_URL}/compracerta?status=approved&session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{PUBLIC_URL}/pagamento_falhou",
        customer_email=user_data.get('email')
    )

    # Retorna a URL da sessão criada.
    return checkout_session.url

def processar_webhook_stripe(payload, sig_header):
    """
    Valida e interpreta um evento vindo do Webhook do Stripe.

    Args:
        payload (bytes): O corpo (raw) da requisição do webhook.
        sig_header (str): O valor do cabeçalho 'Stripe-Signature' da requisição.

    Returns:
        stripe.Event: O objeto de evento decodificado e validado se a assinatura for correta.
    
    Raises:
        ValueError: Se o payload ou a assinatura forem inválidos.
        stripe.error.SignatureVerificationError: Se a assinatura não puder ser verificada.
    """
    try:
        # Constrói e valida o evento do webhook usando o segredo.
        # Isso garante que a requisição veio de fato do Stripe.
        event = stripe.Webhook.construct_event(
            payload=payload, sig_header=sig_header, secret=STRIPE_WEBHOOK_SECRET
        )
        return event
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        print(f"Erro ao validar webhook: {e}")
        raise e