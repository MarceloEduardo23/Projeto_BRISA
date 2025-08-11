import smtplib
import mercadopago
import requests
import stripe
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self, smtp_host, smtp_port, email_address, email_password):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.email_address = email_address
        self.email_password = email_password

    def send_confirmation_email(self, recipient, customer_name, order_details):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = recipient
        msg['Subject'] = "Confirmação de Pedido"

        body = f"Olá {customer_name}, seu pedido foi confirmado!\n\nDetalhes:\n{order_details}"
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
        print(f"E-mail de confirmação enviado para {recipient}")


class MercadoPagoService:
    def __init__(self, access_token, public_url):
        self.sdk = mercadopago.SDK(access_token)
        self.public_url = public_url

    def create_payment_preference(self, items, payer_email, payment_method='all'):
        preference_data = {
            "items": items,  
            "payer": {"email": payer_email},
            "back_urls": {
                "success": f"{self.public_url}/compracerta?status=approved",
                "failure": f"{self.public_url}/pagamento_falhou"
            },
            "auto_return": "approved"
        }

        if payment_method == 'pix':
            preference_data["payment_methods"] = {"excluded_payment_types": [{"id": "credit_card"}]}
        elif payment_method == 'card':
            preference_data["payment_methods"] = {"excluded_payment_types": [{"id": "ticket"}, {"id": "atm"}, {"id": "bank_transfer"}]}
        
        preference_response = self.sdk.preference().create(preference_data)
        return preference_response["response"]["init_point"]


class PayPalService:
    def __init__(self, client_id, client_secret, public_url, mode='sandbox'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.public_url = public_url
        self.base_url = "https://api-m.sandbox.paypal.com" if mode == 'sandbox' else "https://api-m.paypal.com"
        self._access_token = None

    def _get_access_token(self):
        url = f"{self.base_url}/v1/oauth2/token"
        data = {'grant_type': 'client_credentials'}
        response = requests.post(url, data=data, auth=(self.client_id, self.client_secret))
        response.raise_for_status()
        self._access_token = response.json()['access_token']
        return self._access_token

    def create_order(self, total_value, currency="USD"):
        token = self._get_access_token()
        url = f"{self.base_url}/v2/checkout/orders"
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
        
        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {"currency_code": currency, "value": f"{total_value:.2f}"}
            }],
            "application_context": {
                "return_url": f"{self.public_url}/paypal/success",
                "cancel_url": f"{self.public_url}/pagamento_falhou"
            }
        }
        
        response = requests.post(url, headers=headers, json=order_data)
        response.raise_for_status()
        approval_link = next(link['href'] for link in response.json()['links'] if link['rel'] == 'approve')
        return approval_link

    def capture_order(self, order_id):
        token = self._get_access_token()
        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
        
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json()


class StripeService:
    def __init__(self, secret_key, public_url, webhook_secret=None):
        stripe.api_key = secret_key
        self.public_url = public_url
        self.webhook_secret = webhook_secret

    def create_checkout_session(self, line_items, customer_email):
        formatted_items = []
        for item in line_items:
            formatted_items.append({
                'price_data': {
                    'currency': item.get('currency', 'brl'),
                    'product_data': {'name': item['name']},
                    'unit_amount': int(item['unit_price'] * 100),
                },
                'quantity': item['quantity'],
            })

        checkout_session = stripe.checkout.Session.create(
            line_items=formatted_items,
            mode='payment',
            success_url=f"{self.public_url}/compracerta?status=approved&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{self.public_url}/pagamento_falhou",
            customer_email=customer_email
        )
        return checkout_session.url

    def process_webhook(self, payload, sig_header):
        """Valida e processa um evento de webhook do Stripe."""
        if not self.webhook_secret:
            raise ValueError("O segredo do webhook do Stripe não foi configurado.")
        try:
            event = stripe.Webhook.construct_event(payload, sig_header, self.webhook_secret)
            return event
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            print(f"Erro ao processar webhook do Stripe: {e}")
            raise