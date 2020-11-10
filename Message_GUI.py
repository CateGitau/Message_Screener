__import__ ("Profanity Screener")
import pandas as pd
import streamlit as st
import Database

import re

from flair.data import Sentence
from flair.models import TextClassifier
PS = __import__ ("Profanity Screener")   


def load_models():
    with st.spinner('Loading Models...'):
        classifier = TextClassifier.load('twitter_sentiment/model-saves/final-model.pt')
        emotionClass = TextClassifier.load('twitter_sentiment/model-saves/emotion-model.pt')
     
    return classifier, emotionClass


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
    

def main(sentClassifier, emotionClass):
    st.title("Tweet Screener")
    st.subheader("*Guaranteeing 2020 proof tweets to the masses*")
    

    
    section = st.sidebar.selectbox('Sections to Visit',('Screener', 'Sentiment', 'Topic ID'))
    st.sidebar.write("Africa DSI NLP Project by Team 2")
    st.sidebar.write("Catherine, Fanamby, Malcolm, and Martin")

    if section == 'Screener':
        blacklist = load_screener()
        
        
        sentence = st.text_area('Input your message/tweet here:')
        publish = st.button(label = "Publish Tweet!")
        
        if sentence:
        # Pre-process tweet
            answer = PS.profanityscreen(sentence, blacklist, True)
        
            
            # Show predictions
            
            st.write('Swear Words Found:')
            st.dataframe(pd.DataFrame(answer[1], columns=["Swear Words"]))
            
            st.write('Your Censored Tweet:')
            st.write(answer[0])
            
            
             
    if section == "Sentiment":
        sentence = st.text_area('Input your message/tweet here:')
        publish = st.button(label = "Publish Tweet!")
        if sentence:
            
            
            sentimentTweet = Sentence(preprocess(sentence))
                
            with st.spinner('Predicting...'):
                sentClassifier.predict(sentimentTweet)
                label_dict = {'0': 'Negative', '4': 'Positive'}    
                    
            st.write("Sentiment Analysis Prediction:")
                
            predSent = sentimentTweet.labels[0]
            predText = label_dict[predSent.value]
            st.write('Your sentence is ' + str(predText) + ' with ', "{:.2f}".format(predSent.score*100), '% confidence')
                
                
            with st.spinner('Predicting...'):
                    
                emoteTweet = Sentence(preprocess(sentence))
                emotionClass.predict(emoteTweet)
                label_dict = {'0': 'Anger', '1': 'Fear', '2': 'Joy', '3': 'Love', '4': 'Sadness', '5': 'Surprise'}
                    
            st.write("Emotional analysis prediction:")
                
            if len(emoteTweet.labels) > 0:
                st.write('Your sentence is predicted to portray ' + label_dict[emoteTweet.labels[0].value[0]] + ' with', "{:.2f}".format(emoteTweet.labels[0].score*100), '% confidence')
                    
                
    if publish:
        publish_tweet(predText, sentence)

sentClassifier, emoteClassifier = load_models()
if __name__ == "__main__":
    main(sentClassifier, emoteClassifier)

    
    
    


    
        