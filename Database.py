import sqlite3
import pandas as pd
import re

from sqlite3 import Error

class database():
    """
    this is the class that contains functions to interact with the database
    """

    def __init__(self):
        self.con = sqlite3.connect(r"db_msg_screener.sqlite3")
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

    def insert_new_sentiment_query(self,type):
        """ insert new data into the sentiment table """
        sql = 'INSERT INTO sentiment (type) VALUES(?)'
        self.cur.execute(sql, (type,))
        return self.cur.lastrowid

    def insert_new_blacklist_word_query(self,word):
        """ insert new data into the blacklist table """
        sql = 'INSERT INTO blacklist (word) VALUES(?)'
        self.cur.execute(sql, (word,))
        return self.cur.lastrowid

    def insert_new_test_message_query(self, text):
        """ insert new data into the test_msg table """
        sql = 'INSERT INTO test_msg (text) VALUES(?)'
        self.cur.execute(sql, (text,))
        return self.cur.lastrowid

    def insert_new_message_query(self, text,sentiment):
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
        # Retrieve all the records from the blacklist table into a list
        df = pd.read_sql_query("SELECT * FROM blacklist", self.con)
        new_list = df['word'].tolist()
        blacklist = [self.preprocess_term(term) for term in new_list] 
        return blacklist

    def get_sentiment_list(self):
        """ access the list of sentiments
            return :
            df : pandas dataframe (the list of sentiment words)
        """
        # Retrieve all the records from the sentiment table into a list
        df = pd.read_sql_query("SELECT * FROM sentiment", self.con)

        return df['type'].tolist()

    def get_test_messages(self):
        """ access all the test messages
            return :
            df : pandas dataframe (the test messages)
        """
        # Retrieve all the records from the test_msg table into a list
        df = pd.read_sql_query("SELECT * FROM test_msg", self.con)

        return df['text'].tolist()

    ################### POPULATE TABLE ###################
    def populate_blacklist(self):
        """ allows to populate the blacklist table from the text file"""
        try:
            inputFile = open("blacklist.txt", mode = 'r')
            for line in inputFile:
                #insert into the table
                term = line.strip() 
                word = self.preprocess_term(term)
                new_term = self.insert_new_blacklist_word_query(word)
                # commit the statements
                self.con.commit()
        except:
            # rollback all database actions since last commit
            self.con.rollback()
            raise RuntimeError("An error occurred ...")

    def insert_new_blacklist_word(self,word):
        """ allows to add new blacklist terms into the database
            params :
            word : string (the new word to insert into the database)
        """
        try:
            #get the current list of blacklist terms
            current_list = self.get_blacklist_list()

            #test if the word is does not already exists in the database
            if word not in current_list:
                print("****"+ word + "**** is not yet saved")
                #insert new word
                word = self.preprocess_term(word)
                test_msg = self.insert_new_blacklist_word_query(word)
                # commit the statements
                self.con.commit()
        except:
            # rollback all database actions since last commit
            self.con.rollback()
            raise RuntimeError("An error occurred ...")

    ################### DELETE TABLE ###################
    def clear_black_list_table(self):
        """ clear the blacklist table """
        sql = 'DELETE FROM blacklist'
        self.cur.execute(sql)

    ################### PREPROCESSING FUNCTION ###################
    def preprocess_term(self,term):
        """
            this function allows to preprocess a new term by:
            - lowering its case,
            - remove leading and trailing spaces,
            - and removing multiple internal spaces. 

            params:
            term (string) : the term to preprocess

            return:
            term (string) : the preprocessed term 
        """
        term = term.lower() # lower case
        term = term.strip() # remove leading and trailing spaces
        term = re.sub(' +', ' ', term) #remove multiple internal spaces
        return term
   
    
def main():
    db = database()
    db.query_table()

    df_blacklist = db.get_blacklist_list()
    print(df_blacklist)

    term = "BLACK"
    print(db.preprocess_term(term))
    
    # populate blacklist with newly added terms
    inputFile = open("blacklist.txt", mode = 'r')
    for line in inputFile:
        db.insert_new_blacklist_word(line.strip())

    df_blacklist = db.get_blacklist_list()
    print(df_blacklist.shape)

    df_blacklist = db.get_blacklist_list()
    print(df_blacklist.shape)
    

if __name__ == "__main__":
    main()
