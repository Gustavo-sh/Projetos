import uuid
import psycopg2


class Postgres:

    def __init__(self, config):

        self.conn = psycopg2.connect(
            host=config.LOCAL_HOST,
            port=config.LOCAL_PORT,
            dbname=config.POSTGRES_DATABASE,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD
        )

    def cursor(self):

        return self.conn.cursor(name=f"performance_{uuid.uuid4().hex}")