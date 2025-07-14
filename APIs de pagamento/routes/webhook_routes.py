from flask import Blueprint, request, jsonify
from services import stripe_service
from config import STRIPE_WEBHOOK_SECRET

webhook_bp = Blueprint('webhook_bp', __name__)

@webhook_bp.route('/webhook-stripe', methods=['POST'])
def webhook_stripe():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe_service.processar_webhook_stripe(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        return f"Erro no webhook: {e}", 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(f"SUCESSO (Webhook Stripe): Sessão {session['id']} paga!")
        # Aqui você poderia disparar email ou atualizar banco de dados

    return jsonify(status='received'), 200
