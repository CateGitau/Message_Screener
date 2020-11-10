__import__ ("Profanity Screener")
import pandas as pd
import streamlit as st
import Database

import re

from flair.data import Sentence
from flair.models import TextClassifier
PS = __import__ ("Profanity Screener")

SentClassifier = TextClassifier.load('twitter_sentiment/model-saves/final-model.pt')

def load_screener():
    

    # read file of blacklisted terms
    db = Database.database()
    blacklist = db.get_blacklist_list()

    return blacklist




def preprocess(text):
    allowed_chars = ' AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789~`!@#$%^&*()-=_+[]{}|;:",./<>?'
    punct = '!?,.@#'
    maxlen = 280
    return ''.join([' ' + char + ' ' if char in punct else char for char in [char for char in re.sub(r'http\S+', 'http', text, flags=re.MULTILINE) if char in allowed_chars]])[:maxlen]


def publish_tweet(sentiment, sentence):
    st.write("The tweet has been published!!!")
    db1 =  Database.database()
    db1.insert_new_sentiment_query(sentiment)
    db1.insert_new_test_message_query(sentence)
    #db1.insert_new_message_query(sentence,label_dict[sentimentTweet.labels[0].value])


def main(SentClassifier):
    st.title("Tweet Screener")
    st.subheader("*Guaranteeing 2020 proof tweets to the masses*")
    st.sidebar.write("Africa DSI NLP Project by Team 2")
    st.sidebar.write("Catherine, Fanamby, Malcolm, and Martin")
    section = st.sidebar.selectbox('Sections to Visit',('Swear Word Analyser', 'Sentiment Analyser', 'Topic Identifier'))

    publish = st.button(label = "Publish Tweet!")

    if section == 'Swear Word Analyser':
        blacklist = load_screener()


        sentence = st.text_area('Input your message/tweet here:')
       

        if sentence:
            # Pre-process tweet
            answer = PS.profanityscreen(sentence, blacklist, True)

            label_dict = {'0': 'Negative', '4': 'Positive'}
            # Show predictions

            st.write('Swear Words Found:')
            st.dataframe(pd.DataFrame(answer[1], columns=["Swear Words"]))

            st.write('Your Censored Tweet:')
            st.write(answer[0])

            
                
    if section == "Sentiment Analyser":
        sentSentence = st.text_area('Input your message/tweet here:')
        
        if sentSentence:
            sentimentTweet = Sentence(preprocess(sentSentence))

            with st.spinner('Predicting...'):
                SentClassifier.predict(sentimentTweet)

            st.write("Sentiment analysis prediction:")

            pred = sentimentTweet.labels[0]
            predText = label_dict[pred.value]
            st.write('Your sentence is ' + str(predText) + ' with ', "{.2f}".format(pred.score*100), '% confidence')

    if publish:
        publish_tweet(predText, sentence)

if __name__ == "__main__":
    main(SentClassifier)
