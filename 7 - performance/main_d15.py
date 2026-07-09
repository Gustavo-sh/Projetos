import config

from tunnel import Tunnel
from postgres import Postgres
from sqlserver import SqlServer
from sync import PerformanceSync


def main():

    tunnel = Tunnel()

    tunnel.start()

    try:

        pg = Postgres(config)

        sql = SqlServer(config)

        sync = PerformanceSync(
            pg,
            sql,
            config.FETCH_SIZE
        )

        sync.run(16)

    finally:

        try:
            pg.conn.close()
        except:
            pass

        try:
            sql.conn.close()
        except:
            pass

        tunnel.stop()


if __name__ == "__main__":

    main()