from psycopg2 import connect, DatabaseError
from bot.modules.logger import LOGGER


class Database:
    def __init__(self):
        self.err=False
        self.connect()
        self.db_init()

    def connect(self):
        try:
            self.conn = connect("mongodb+srv://minato:minato5647@cluster0.mukmldp.mongodb.net/?retryWrites=true&w=majority")
            self.cur = self.conn.cursor()
        except DatabaseError as error:
            LOGGER.error(f"Error in DB connection: {error}")
            self.err = True

    def db_init(self):
        if self.err:
            return
        sql = """CREATE TABLE IF NOT EXISTS users (
                 uid bigint,
                 sudo boolean DEFAULT FALSE,
                 auth boolean DEFAULT FALSE,
                 media boolean DEFAULT FALSE,
                 doc boolean DEFAULT FALSE,
                 thumb bytea DEFAULT NULL,
              )
              """
        self.cur.execute(sql)
        self.conn.commit()
        LOGGER.info("Database Active!")