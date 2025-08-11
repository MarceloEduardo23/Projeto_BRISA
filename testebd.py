import sqlite3
import os

# Define o nome do arquivo do banco de dados
DB_FILE = "produtos.db"

# Apaga o banco de dados antigo, se existir, para começar do zero
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# Conecta ao banco de dados (isso criará o arquivo)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Cria a tabela de produtos
print("Criando tabela 'produtos'...")
cursor.execute("""
CREATE TABLE produtos (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL
);
""")

# Lista de produtos para inserir
produtos_para_inserir = [
    ("prod_sm_01", "Smartphone XPTO 9", 2999.90),
    ("prod_fn_02", "Fone Bluetooth Bass", 350.00),
    ("prod_ms_03", "Mouse Gamer Pro", 450.50),
    ("prod_tc_04", "Teclado Mecânico RGB", 680.00)
]

# Insere os produtos na tabela
print("Inserindo produtos de teste...")
cursor.executemany("INSERT INTO produtos (id, name, price) VALUES (?, ?, ?)", produtos_para_inserir)

# Confirma as mudanças e fecha a conexão
conn.commit()
conn.close()

print(f"\nBanco de dados '{DB_FILE}' criado com sucesso e populado com {len(produtos_para_inserir)} produtos!")
print("Você já pode rodar o 'main.py'.")