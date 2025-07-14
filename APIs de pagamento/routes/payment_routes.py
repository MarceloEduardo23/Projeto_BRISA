from flask import Blueprint, request, jsonify, render_template, url_for
from services import mercadopago_service, paypal_service, stripe_service

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/')
def carrinho_page():
    return render_template('carrinho.html')

@payment_bp.route('/checkout')
def checkout_page():
    return render_template('checkout.html')

@payment_bp.route('/compracerta')
def compracerta_page():
    payment_id = request.args.get('payment_id') or request.args.get('token') or request.args.get('session_id')
    status = request.args.get('status')
    return render_template('compracerta.html', payment_id=payment_id, status=status)

@payment_bp.route('/pagamento_falhou')
def pagamento_falhou_page():
    message = request.args.get('message', "Ocorreu um erro. Tente novamente.")
    return render_template('checkout.html', payment_status='error', message=message)

@payment_bp.route('/create_payment', methods=['POST'])
def create_payment():
    try:
        data = request.get_json()
        payment_method = data.get('payment_method')
        items_data = data.get('items')
        user_data = data.get('user_data')

        if not all([payment_method, items_data, user_data]):
            return jsonify({"mensagem": "Dados da requisição incompletos."}), 400

        precos_db = {
            "Smartphone Premium": 899.99,
            "Fones de Ouvido Bluetooth": 199.99
        }
        tax_rate = 0.08
        subtotal = sum(precos_db.get(item['name'], 0) * item['quantity'] for item in items_data)
        valor_imposto = subtotal * tax_rate
        total_brl = subtotal + valor_imposto

        # PayPal
        if payment_method == 'paypal':
            from config import BRL_TO_USD_RATE
            access_token = paypal_service.get_paypal_access_token()
            total_usd = total_brl / BRL_TO_USD_RATE
            approval_link = paypal_service.create_paypal_order(access_token, items_data, total_usd)
            return jsonify({"approval_url": approval_link})

        # Stripe
        elif payment_method == 'stripe':
            redirect_url = stripe_service.criar_checkout_stripe(items_data, valor_imposto, user_data)
            return jsonify({"redirect_url": redirect_url})

        # Mercado Pago (cartão ou pix)
        elif payment_method in ['card', 'pix']:
            for item in items_data:
                item['unit_price'] = precos_db.get(item['name'], 0)

            items = items_data + [{
                "name": "Impostos",
                "quantity": 1,
                "unit_price": valor_imposto
            }]

            init_point = mercadopago_service.criar_preferencia_mercadopago(items, user_data, payment_method)
            return jsonify({"init_point": init_point})

        return jsonify({"mensagem": "Método de pagamento não suportado."}), 400

    except Exception as e:
        print(f"Erro inesperado em /create_payment: {e}")
        return jsonify({"mensagem": "Erro interno ao processar o pagamento."}), 500
