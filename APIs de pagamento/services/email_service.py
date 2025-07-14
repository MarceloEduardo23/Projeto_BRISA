"""
Módulo para o envio de e-mails transacionais.

Este serviço utiliza o protocolo SMTP para se conectar a um servidor de e-mail
(neste caso, o Gmail) e enviar mensagens, como confirmações de pedido,
para os clientes.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Importa as credenciais de e-mail do arquivo de configuração central.
from config import EMAIL_ADDRESS, EMAIL_PASSWORD

def enviar_email_confirmacao(destinatario, nome_cliente, detalhes_pedido):
    """
    Envia um e-mail de confirmação de pedido para o cliente.

    Args:
        destinatario (str): O endereço de e-mail do destinatário.
        nome_cliente (str): O nome do cliente para personalizar a saudação.
        detalhes_pedido (str): Uma string formatada com os detalhes do pedido.
    """
    # Cria o corpo do e-mail (MIMEMultipart).
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = destinatario
    msg['Subject'] = "Confirmação de Pedido"

    # Define a mensagem de texto do e-mail.
    corpo = f"Olá {nome_cliente}, seu pedido foi confirmado!\n\nDetalhes:\n{detalhes_pedido}"
    msg.attach(MIMEText(corpo, 'plain'))

    # Bloco para garantir que a conexão com o servidor SMTP seja fechada corretamente.
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        # Inicia a conexão segura com o servidor.
        server.starttls()
        # Realiza o login no servidor de e-mail.
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        # Envia a mensagem.
        server.send_message(msg)