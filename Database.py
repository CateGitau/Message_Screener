import sqlite3
import pandas as pd

from sqlite3 import Error

class database():
    """
    this is the class that contains functions to interact with the database 
    """

    def __init__(self):
        self.con = sqlite3.connect(r"C:/Kandra DSI Program/Module 3/Project/code/Message_Screener/db_msg_screener.sqlite3")
        self.cur = self.con.cursor()

    def query_table(self):
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print(self.cur.fetchall())

     ############## CREATE QUERY ###################
    def create_sentiment_table(self):
        """ allows to create the sentiment table """
        sentiment_sql = """
        CREATE TABLE sentiment (
            id_sentiment integer PRIMARY KEY AUTOINCREMENT,
            type text NOT NULL)"""
        self.cur.execute(sentiment_sql)
    
    def create_blacklist_table(self):
        """ allows to create the blacklist table """
        blacklist_sql = """
            CREATE TABLE blacklist (
                id_word integer PRIMARY KEY AUTOINCREMENT,
                word text NOT NULL)"""
        self.cur.execute(blacklist_sql)

    def create_test_message_table(self):
        """ allows to create the test message table """
        test_msg_sql = """
            CREATE TABLE test_msg (
                id_msg integer PRIMARY KEY AUTOINCREMENT,
                text text NOT NULL)"""
        self.cur.execute(test_msg_sql)

    def create_message_table(self):
        """ allows to create the message table """
        msg_sql = """CREATE TABLE message (
            id_msg   integer PRIMARY KEY AUTOINCREMENT,
            text text    NOT NULL,
            id_sentiment  integer  NOT NULL,
            FOREIGN KEY (id_sentiment)
                REFERENCES sentiment (id_sentiment) 
        )"""
        self.cur.execute(msg_sql)

     ############## INSERT QUERY  ###################

    def insert_new_sentiment(self,type):
        """ insert new data into the sentiment table """
        sql = 'INSERT INTO sentiment (type) VALUES(?)'
        self.cur.execute(sql, (type,))
        return self.cur.lastrowid

    def insert_new_blacklist_word(self,word):
        """ insert new data into the blacklist table """
        sql = 'INSERT INTO blacklist (word) VALUES(?)'
        self.cur.execute(sql, (word,))
        return self.cur.lastrowid

    def insert_new_test_message(self, text):
        """ insert new data into the test_msg table """
        sql = 'INSERT INTO test_msg (text) VALUES(?)'
        self.cur.execute(sql, (text,))
        return self.cur.lastrowid

    def insert_new_message(self, text,sentiment):
        """ insert new data into the message table """
        sql = 'INSERT INTO message (text,id_sentiment) VALUES(?)'
        self.cur.execute(sql, (text,sentiment))
        return self.cur.lastrowid

    ############## READ QUERY  ###################
    def get_blacklist_list(self):
        """ access the list of blacklist words 
            return : 
            df : pandas dataframe (the list of blacklist words)
        """
        # Store the result of SQL query  in the dataframe
        df = pd.read_sql_query("SELECT * FROM blacklist", self.con)
        
        return df

    def get_sentiment_list(self):
        """ access the list of sentiments 
            return : 
            df : pandas dataframe (the list of sentiment words)
        """
        # Store the result of SQL query  in the dataframe
        df = pd.read_sql_query("SELECT * FROM sentiment", self.con)
        
        return df

    def get_test_messages(self):
        """ access all the test messages 
            return : 
            df : pandas dataframe (the test messages)
        """
        # Store the result of SQL query  in the dataframe
        df = pd.read_sql_query("SELECT * FROM test_msg", self.con)
        
        return df


def main():
    db = database() 
    db.query_table()
    df_blacklist = db.get_blacklist_list()
    b_list = []
    b_list = df_blacklist['word']
    print(b_list)


if __name__ == "__main__":
    main()
