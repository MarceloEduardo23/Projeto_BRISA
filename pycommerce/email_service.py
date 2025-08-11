import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self, smtp_server, port, email_address, email_password):
        self.smtp_server = smtp_server
        self.port = port
        self.email_address = email_address
        self.email_password = email_password

    def enviar_email_confirmacao(self, destinatario, nome_cliente, detalhes_pedido):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = destinatario
        msg['Subject'] = "Confirmação de Pedido"

        corpo = f"Olá {nome_cliente}, seu pedido foi confirmado!\n\nDetalhes:\n{detalhes_pedido}"
        msg.attach(MIMEText(corpo, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            print(f"E-mail de confirmação enviado para {destinatario}")
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")