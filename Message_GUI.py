__import__ ("Profanity Screener")
import pandas as pd
import streamlit as st
import sqlite3

import re

from flair.data import Sentence
from flair.models import TextClassifier

PS = __import__ ("Profanity Screener")        
# read file of blacklisted terms
inputFile = open("blacklist.txt", mode = 'r')
blacklist = [line.strip() for line in inputFile]
inputFile.close()

classifier = TextClassifier.load('twitter_sentiment/model-saves/final-model.pt')

allowed_chars = ' AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789~`!@#$%^&*()-=_+[]{}|;:",./<>?'
punct = '!?,.@#'
maxlen = 280

def preprocess(text):
    return ''.join([' ' + char + ' ' if char in punct else char for char in [char for char in re.sub(r'http\S+', 'http', text, flags=re.MULTILINE) if char in allowed_chars]])[:maxlen]

add_selectbox = st.sidebar.write(
    "Africa DSI NLP Project by Team 2"
)
st.sidebar.write(
    "Catherine, Fanamby, Malcolm, and Martin"
)
label_dict = {'0': 'Negative', '4': 'Positive'}


st.title(" Message Screener")
st.subheader("*Guaranteeing 2020 proof tweets to the masses*")

sentence = st.text_area('Input your message/tweet here:')
if sentence:
    # Pre-process tweet
    #sentence = Sentence(preprocess(tweet_input))
    answer = PS.profanityscreen(sentence, blacklist, True)


    # Show predictions
    
    st.write('Swear Words Found:')
    st.write(pd.DataFrame(answer[1], columns=["Swear Words"]))
    
    st.write('Your Censored Tweet:')
    st.write(answer[0])
    
    sentimentTweet = Sentence(preprocess(sentence))
    
    with st.spinner('Predicting...'):
        classifier.predict(sentimentTweet)
        
    st.write("Sentiment analysis prediction:")

    st.write('Your sentence is ' + str(label_dict[sentimentTweet.labels[0].value]) + ' with ', sentimentTweet.labels[0].score*100, '% confidence')
    
publish = st.button(label = "Publish Tweet!")





if publish:
    st.write("The tweet has been published!!!")