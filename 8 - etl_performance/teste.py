from tunnel import start_tunnel, kill_existing_tunnel
import psycopg2

start_tunnel()

print("tunnel aberto")

conn = psycopg2.connect(
        host="127.0.0.1",
        port=26017,
        dbname="reports",
        user="robbyson_view",
        password="juleH7JHZUnzYQBE"
    )

print("conexão criada")

cur = conn.cursor()

print("cursor aberto")

cur.execute("""
SELECT 
	chave_externa_diretor_atendimento
FROM "views".performance_view
where data between '2026-07-01' and '2026-07-31'
and chave_externa = 6241
"""
)
print("query executada")

print(cur.fetchall())

cur.close()
conn.close()

kill_existing_tunnel()