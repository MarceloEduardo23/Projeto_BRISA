# 📦 PyCommerce - Serviço de E-mail e Gateways de Pagamento

Biblioteca Python para integração simples com **serviço de e-mails** e múltiplos **gateways de pagamento** (Stripe, PayPal e Mercado Pago), ideal para uso em sistemas de e-commerce.

## 🚀 Funcionalidades

- **Envio de e-mails** de confirmação de pedido via SMTP.  
- **Stripe**:
  - Criação de sessões de checkout.
  - Processamento de webhooks.
- **PayPal**:
  - Criação e captura de pedidos.
- **Mercado Pago**:
  - Criação de preferências de pagamento para Pix, cartão e outros métodos.

---

## 📂 Estrutura do Projeto

```
pycommerce/
│
├── email_service.py # Serviço para envio de e-mails
├── payment_gateways.py # Integração com Stripe, PayPal e Mercado Pago
├── config.py # Configurações de chaves e credenciais
└── README.md # Este arquivo
```

---

## ⚙️ Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/MarceloEduardo23/Projeto_BRISA.git
   
2. **Crie um ambiente virtual**:
    ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/Mac
    venv\Scripts\activate      # Windows

3. **Instale as dependências**:
    ```bash
    pip install stripe mercadopago requests

## Configuração
No arquivo **config.py**, defina suas credenciais
```bash
EMAIL_ADDRESS = "seuemail@dominio.com"
EMAIL_PASSWORD = "senha_do_email"

STRIPE_SECRET_KEY = "sua_chave_secreta_stripe"

MERCADO_PAGO_ACCESS_TOKEN = "seu_access_token_mercadopago"

PAYPAL_CLIENT_ID = "seu_client_id_paypal"
PAYPAL_CLIENT_SECRET = "seu_client_secret_paypal"

PUBLIC_URL = "https://seudominio.com"
```
