import config
from pycommerce import EmailService, MercadoPagoService, PayPalService, StripeService

# --- Inicialização dos Serviços ---
# As chaves e URLs são carregadas do config.py e passadas para cada serviço

email_service = EmailService(
    smtp_host='smtp.gmail.com', # <-- Dizendo para se conectar ao servidor do Gmail
    smtp_port=587,              # <-- Dizendo para usar a porta 587 para uma conexão segura (TLS)
    email_address=config.EMAIL_ADDRESS,
    email_password=config.EMAIL_PASSWORD
)

mp_service = MercadoPagoService(
    access_token=config.MERCADO_PAGO_ACCESS_TOKEN,
    public_url=config.PUBLIC_URL
)

paypal_service = PayPalService(
    client_id=config.PAYPAL_CLIENT_ID,
    client_secret=config.PAYPAL_CLIENT_SECRET,
    public_url=config.PUBLIC_URL,
    mode='sandbox'  # ou 'live' para produção
)

stripe_service = StripeService(
    secret_key=config.STRIPE_SECRET_KEY,
    public_url=config.PUBLIC_URL,
    webhook_secret=config.STRIPE_WEBHOOK_SECRET
)

# --- Exemplo de Uso ---

def executar_compra_exemplo():
    # 1. Dados do pedido
    cliente = {"nome": "João Silva", "email": "joao.silva@example.com"}
    itens_pedido = [
        {"name": "Smartphone Premium", "quantity": 1, "unit_price": 899.99},
        {"name": "Fones de Ouvido Bluetooth", "quantity": 1, "unit_price": 199.99}
    ]
    detalhes_str = "\n".join([f"- {item['quantity']}x {item['name']}" for item in itens_pedido])

    # 2. Criar pagamentos (descomente o que quiser testar)
    
    # Exemplo Mercado Pago (Pix)
    try:
        mp_items = [{"title": item["name"], "quantity": item["quantity"], "unit_price": item["unit_price"]} for item in itens_pedido]
        link_mp = mp_service.create_payment_preference(mp_items, cliente['email'], payment_method='pix')
        print(f"Link de pagamento Mercado Pago: {link_mp}")
    except Exception as e:
        print(f"Erro ao criar preferência do Mercado Pago: {e}")

    # Exemplo Stripe
    try:
        # No Stripe, 'unit_price' já é o valor final do item. Impostos podem ser adicionados como um item separado.
        stripe_items = [
            {"name": item["name"], "quantity": item["quantity"], "unit_price": item["unit_price"], "currency": "brl"} for item in itens_pedido
        ]
        stripe_items.append({"name": "Impostos", "quantity": 1, "unit_price": 50.00, "currency": "brl"}) # Exemplo de imposto
        
        link_stripe = stripe_service.create_checkout_session(stripe_items, cliente['email'])
        print(f"Link de pagamento Stripe: {link_stripe}")
    except Exception as e:
        print(f"Erro ao criar checkout do Stripe: {e}")

    # Exemplo PayPal
    try:
        total_usd = 220.00 # PayPal geralmente opera em USD
        link_paypal = paypal_service.create_order(total_value=total_usd, currency="USD")
        print(f"Link de pagamento PayPal: {link_paypal}")
    except Exception as e:
        print(f"Erro ao criar ordem do PayPal: {e}")

    # 3. Enviar e-mail de confirmação (após pagamento confirmado)
    try:
        email_service.send_confirmation_email(
            recipient=cliente['email'],
            customer_name=cliente['nome'],
            order_details=detalhes_str
        )
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")


if __name__ == '__main__':
    executar_compra_exemplo()