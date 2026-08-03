import psycopg2

conn = psycopg2.connect(
        host="35.245.101.215",
        port=27017,
        dbname="reports",
        user="robbyson_customer",
        password="TVnDKkxCX-8bPrbV"
    )

cur = conn.cursor()
cur.execute("""select * from public.notificacao_view	where data = '20260721'	limit 1000""")

results  = cur.fetchall()

print(results)