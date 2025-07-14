"""
Arquivo principal da aplicação Flask.

Este módulo inicializa a aplicação Flask e registra os Blueprints
que contêm as rotas de pagamento e webhooks.
"""

from flask import Flask
from routes.webhook_routes import payment_bp
from routes.webhook_routes import webhook_bp

# Cria a instância da aplicação Flask.
app = Flask(__name__)

# Registra os Blueprints na aplicação.
# Todas as rotas definidas em 'payment_routes.py' serão adicionadas.
app.register_blueprint(payment_bp)
# Todas as rotas definidas em 'webhook_routes.py' serão adicionadas.
app.register_blueprint(webhook_bp)

# Bloco de execução principal:
# Roda o servidor de desenvolvimento do Flask.
# debug=True ativa o modo de depuração para facilitar o desenvolvimento.
if __name__ == '__main__':
    app.run(debug=True, port=5000)