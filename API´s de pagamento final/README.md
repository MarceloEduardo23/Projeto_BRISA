# Biblioteca de Serviços para E-commerce

Esta biblioteca fornece uma interface simplificada e unificada para interagir com serviços comuns de e-commerce, como gateways de pagamento (Stripe, Mercado Pago, PayPal) e notificação por e-mail.

## Instalação

1.  Certifique-se de ter o Python 3.6+ instalado.
2.  Crie um arquivo `requirements.txt` na raiz do seu projeto com o seguinte conteúdo:
    ```txt
    mercadopago
    requests
    stripe
    ```
3.  Instale as dependências executando o comando:
    ```bash
    pip install -r requirements.txt
    ```

## Configuração

1.  Crie um arquivo `config.py` na raiz do seu projeto. Este arquivo conterá todas as suas chaves de API e segredos. **Nunca adicione este arquivo ao controle de versão (ex: .gitignore)**.

    ```python
    # config.py

    # GERAL
    PUBLIC_URL = "http://localhost:8000" # URL base do seu site

    # E-MAIL (ex: Gmail com senha de app)
    EMAIL_ADDRESS = "seu-email@gmail.com"
    EMAIL_PASSWORD = "sua-senha-de-app"

    # MERCADO PAGO
    MERCADO_PAGO_ACCESS_TOKEN = "SEU_ACCESS_TOKEN_DO_MERCADO_PAGO"

    # PAYPAL (Sandbox ou Live)
    PAYPAL_CLIENT_ID = "SEU_CLIENT_ID_DO_PAYPAL"
    PAYPAL_CLIENT_SECRET = "SEU_CLIENT_SECRET_DO_PAYPAL"

    # STRIPE
    STRIPE_SECRET_KEY = "sk_test_SUA_CHAVE_SECRETA"
    STRIPE_WEBHOOK_SECRET = "whsec_SEU_SEGREDO_DE_WEBHOOK"
    ```

## Estrutura da Biblioteca

A biblioteca é organizada em classes, onde cada classe representa um serviço específico. Para usar um serviço, você deve primeiro instanciar sua classe, fornecendo as credenciais necessárias a partir do seu arquivo `config.py`.

```python
from ecom_services import EmailService, MercadoPagoService, PayPalService, StripeService
import config

# Instanciando os serviços
email_svc = EmailService(
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    email_address=config.EMAIL_ADDRESS,
    email_password=config.EMAIL_PASSWORD
)

mp_svc = MercadoPagoService(
    access_token=config.MERCADO_PAGO_ACCESS_TOKEN,
    public_url=config.PUBLIC_URL
)
```

## Referência da API

### `EmailService`
Gerencia o envio de e-mails.

-   **`__init__(self, smtp_host, smtp_port, email_address, email_password)`**: Inicializa o serviço de e-mail.
-   **`send_confirmation_email(self, recipient, customer_name, order_details)`**: Envia um e-mail de confirmação.
    -   `recipient` (str): E-mail do destinatário.
    -   `customer_name` (str): Nome do cliente.
    -   `order_details` (str): String com os detalhes do pedido.

### `MercadoPagoService`
Gerencia pagamentos via Mercado Pago.

-   **`__init__(self, access_token, public_url)`**: Inicializa o serviço.
-   **`create_payment_preference(self, items, payer_email, payment_method='all')`**: Cria um link de pagamento.
    -   `items` (list): Lista de dicionários, cada um com `title`, `quantity`, `unit_price`.
    -   `payer_email` (str): E-mail do pagador.
    -   `payment_method` (str, opcional): `pix`, `card` ou `all`.
    -   **Retorna**: (str) A URL `init_point` para o checkout.

### `PayPalService`
Gerencia pagamentos via PayPal.

-   **`__init__(self, client_id, client_secret, public_url, mode='sandbox')`**: Inicializa o serviço. `mode` pode ser `sandbox` ou `live`.
-   **`create_order(self, total_value, currency="USD")`**: Cria uma ordem de pagamento.
    -   `total_value` (float): Valor total do pedido.
    -   `currency` (str): Código da moeda (ex: "USD", "BRL").
    -   **Retorna**: (str) O link de aprovação para o cliente.
-   **`capture_order(self, order_id)`**: Captura um pagamento após aprovação do cliente.
    -   `order_id` (str): ID da ordem do PayPal.
    -   **Retorna**: (dict) A resposta da API de captura.

### `StripeService`
Gerencia pagamentos via Stripe.

-   **`__init__(self, secret_key, public_url, webhook_secret=None)`**: Inicializa o serviço.
-   **`create_checkout_session(self, line_items, customer_email)`**: Cria uma sessão de checkout.
    -   `line_items` (list): Lista de dicionários, cada um com `name`, `quantity`, `unit_price` e `currency` (opcional).
    -   `customer_email` (str): E-mail do cliente.
    -   **Retorna**: (str) A URL para a página de checkout do Stripe.
-   **`process_webhook(self, payload, sig_header)`**: Valida e retorna um evento de webhook do Stripe.
    -   `payload` (bytes): O corpo bruto da requisição do webhook.
    -   `sig_header` (str): O valor do cabeçalho `Stripe-Signature`.
    -   **Retorna**: (stripe.Event) O objeto de evento validado.