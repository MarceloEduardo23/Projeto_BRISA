# Arquivo: main.py

import sqlite3
from prettytable import PrettyTable
from pycommerce.payment_gateways import StripeGateway, MercadoPagoGateway, PayPalGateway
from config import (
    STRIPE_SECRET_KEY, MERCADO_PAGO_ACCESS_TOKEN,
    PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PUBLIC_URL
)

DB_PATH = 'produtos.db'

def mostrar_produtos():
    """Busca produtos no BD e os exibe em uma tabela bonita."""
    print("\n--- 📜 Nossos Produtos Disponíveis ---")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM produtos ORDER BY name")
    produtos = cursor.fetchall()
    conn.close()
    
    tabela = PrettyTable()
    tabela.field_names = ["ID do Produto", "Nome", "Preço (R$)"]
    tabela.align["Nome"] = "l"
    tabela.align["Preço (R$)"] = "r"

    for produto in produtos:
        tabela.add_row([produto['id'], produto['name'], f"{produto['price']:.2f}"])
    
    print(tabela)
    return {produto['id'] for produto in produtos}

def mostrar_carrinho(carrinho, conn):
    """Exibe o conteúdo atual do carrinho de compras."""
    print("\n--- 🛒 Seu Carrinho de Compras ---")
    if not carrinho:
        print("Seu carrinho está vazio.")
        return 0.0

    tabela = PrettyTable()
    tabela.field_names = ["Produto", "Qtd.", "Preço Unit.", "Subtotal"]
    tabela.align["Produto"] = "l"
    tabela.align["Subtotal"] = "r"
    total_carrinho = 0

    cursor = conn.cursor()
    for item in carrinho:
        cursor.execute("SELECT name, price FROM produtos WHERE id = ?", (item['id'],))
        produto = cursor.fetchone()
        subtotal = produto['price'] * item['quantity']
        total_carrinho += subtotal
        tabela.add_row([produto['name'], item['quantity'], f"{produto['price']:.2f}", f"{subtotal:.2f}"])
    
    print(tabela)
    print(f"VALOR TOTAL: R$ {total_carrinho:.2f}")
    return total_carrinho

def iniciar_loja():
    """Função principal que executa a loja interativa."""
    carrinho = []
    ids_validos = mostrar_produtos()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    while True:
        print("\nO que você deseja fazer?")
        print("1 - Adicionar produto ao carrinho")
        print("2 - Ver carrinho")
        print("3 - Ir para o pagamento (Checkout)")
        print("4 - Sair")
        escolha = input("Digite o número da sua escolha: ")

        if escolha == '1':
            id_produto = input("Digite o ID do produto que deseja adicionar: ").strip()
            if id_produto not in ids_validos:
                print("❌ ID de produto inválido. Tente novamente.")
                continue
            
            while True:
                try:
                    quantidade = int(input(f"Digite a quantidade para '{id_produto}': "))
                    if quantidade > 0:
                        break
                    else:
                        print("❌ A quantidade deve ser maior que zero.")
                except ValueError:
                    print("❌ Por favor, digite um número válido.")
            
            # Verifica se o item já está no carrinho para atualizar a quantidade
            item_encontrado = False
            for item in carrinho:
                if item['id'] == id_produto:
                    item['quantity'] += quantidade
                    item_encontrado = True
                    break
            if not item_encontrado:
                carrinho.append({'id': id_produto, 'quantity': quantidade})
            print(f"✅ Produto '{id_produto}' adicionado ao carrinho!")

        elif escolha == '2':
            mostrar_carrinho(carrinho, conn)

        elif escolha == '3':
            if not carrinho:
                print("❌ Seu carrinho está vazio! Adicione produtos antes de ir para o pagamento.")
                continue
            
            print("\n--- 🚀 Gerando Links de Pagamento ---")
            total = mostrar_carrinho(carrinho, conn)
            
            # --- Gerar links ---
            try:
                # Stripe
                stripe_service = StripeGateway(secret_key=STRIPE_SECRET_KEY, db_path=DB_PATH)
                stripe_url = stripe_service.criar_checkout(carrinho, f"{PUBLIC_URL}/sucesso", f"{PUBLIC_URL}/cancelado")
                print(f"\n✅ [STRIPE] Link gerado: {stripe_url}")
                
                # Mercado Pago
                mp_service = MercadoPagoGateway(access_token=MERCADO_PAGO_ACCESS_TOKEN, db_path=DB_PATH)
                mp_url = mp_service.criar_preferencia(carrinho, 'comprador@email.com', {"success": f"{PUBLIC_URL}/sucesso", "failure": f"{PUBLIC_URL}/cancelado"})
                print(f"✅ [MERCADO PAGO] Link gerado: {mp_url}")
                
                # PayPal
                paypal_service = PayPalGateway(client_id=PAYPAL_CLIENT_ID, client_secret=PAYPAL_CLIENT_SECRET, db_path=DB_PATH, mode='sandbox')
                paypal_url = paypal_service.criar_pedido(carrinho, f"{PUBLIC_URL}/sucesso", f"{PUBLIC_URL}/cancelado")
                print(f"✅ [PAYPAL] Link gerado: {paypal_url}")

            except Exception as e:
                print(f"❌ Ocorreu um erro ao gerar os links: {e}")
            
            break # Encerra o loop da loja após o checkout

        elif escolha == '4':
            print("Obrigado por visitar nossa loja. Volte sempre!")
            break
        else:
            print("❌ Opção inválida. Por favor, escolha um número de 1 a 4.")
    
    conn.close()

if __name__ == "__main__":
    iniciar_loja()