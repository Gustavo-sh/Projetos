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
	min(data)
FROM "views".performance_view
"""
)
print("query executada")

print(cur.fetchone())

cur.close()
conn.close()

kill_existing_tunnel()