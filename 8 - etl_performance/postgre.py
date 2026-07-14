import psycopg2

def create_connection(host, port, database, user, password):

    return psycopg2.connect(
        host=host,
        port=port,
        dbname=database,
        user=user,
        password=password
    )