__import__ ("Profanity Screener")
import pandas as pd
import streamlit as st
import Database
import matplotlib.pyplot as plt

import re

from flair.data import Sentence
from flair.models import TextClassifier
PS = __import__ ("Profanity Screener")

import keras
import tensorflow as tf
from keras.models import Model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences




def preprocess_test(x_test):
  """ this function allows to preprocess the test sentence

      params : 
      x_test (string) : the test message

      return :
      test_x (vector) : the processed test message 
  """
  max_features=20000  
  max_len=100

  train = pd.read_csv('Topic Identifier/data/topic_identification_data.csv')
  train['comment_text'].fillna('fillna')
  x_train=train['comment_text'].str.lower()

  x_test = x_test.lower()
  x_test = [x_test]
  tokenizer= Tokenizer(num_words=max_features,lower= True)
  tokenizer.fit_on_texts(list(x_train))
  tokenized_test=tokenizer.texts_to_sequences(x_test)
  test_x=pad_sequences(tokenized_test,maxlen=max_len)

  return test_x
    
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


def main():
    st.title("Tweet Screener")
    st.subheader("*Guaranteeing 2020 proof tweets to the masses*")
    st.sidebar.subheader("Africa DSI NLP Project by Team 2")
    st.sidebar.write("Catherine, Fanamby, Malcolm, and Martin")
    section = st.sidebar.radio('Sections to Visit',('Swear Word Analyser', 'Sentiment Analyser', 'Topic Identifier'))

    
    publish = st.sidebar.button(label = "Publish Tweet!")
    
    st.sidebar.markdown("This application helps determine how problematic your tweet is before publishing it."
                    + " We utilise three main tools to achieve this."
                    +" A swear word analyser that checks your tweet for profanity and delivers a censored tweet."
                    +" A sentiment analyser that predicts the emotion in your tweet, to check if you were really being positive."
                    +" Finally a topic identifier which determines if you broke one of Twitter's policies with out knowing it!"
                    +" Once you have thouroughly scrubbed you tweet you may store your results for further analyses.")
    

    if section == 'Swear Word Analyser':
        blacklist = load_screener()


        sentence = st.text_area('Input your message/tweet here:')
       

        if sentence:
            # Pre-process tweet
            answer = PS.profanityscreen(sentence, blacklist, True)
            st.subheader("Swear Analysis Results:")
            
            # Show predictions

            st.write('Swear Words Found:')
            st.dataframe(pd.DataFrame(answer[1], columns=["Swear Words"]))

            st.write('Your Censored Tweet:')
            st.write(answer[0])

            
                
    if section == "Sentiment Analyser":
        sentSentence = st.text_area('Input your message/tweet here:')
        
        if sentSentence:
            sentimentTweet = Sentence(preprocess(sentSentence))
            emoteTweet = Sentence(preprocess(sentSentence))
            
            #Sentiment Dictionaries
            sentiment_dict = {'0': 'Negative', '4': 'Positive'}
            emote_dict = {'0': 'Anger', '1': 'Fear', '2': 'Joy', '3': 'Love', '4': 'Sadness', '5': 'Surprise'}
            
            with st.spinner('Predicting...'):
                SentClassifier = TextClassifier.load('twitter_sentiment/model-saves/final-model.pt')
                EmoteClassifier = TextClassifier.load('twitter_sentiment/model-saves/emotion-model.pt')
                SentClassifier.predict(sentimentTweet)
                EmoteClassifier.predict(emoteTweet)
                
            st.subheader("Sentiment Analysis Results:")

            predSent = sentimentTweet.labels[0]
            predSText = sentiment_dict[predSent.value[0]]
            st.write('Your sentence is ' + str(predSText) + ' with ', "{:.2f}".format(predSent.score*100), '% confidence')
            
            predEmote = emoteTweet.labels[0]
            predEText = emote_dict[predEmote.value[0]]
            st.write('Your sentence is predicted to portray ' + predEText + ' with', "{:.2f}".format(predEmote.score*100), ' % confidence')

    if section == "Topic Identifier":
        topicSentence = st.text_area('Input your message/tweet here:')
        st.subheader("Sensitivity Analysis Results:")
        if topicSentence:
            topicTweet = preprocess_test(topicSentence)
            
            topic_dict = {0: "obscenity", 1: "violence", 2: "verbal abuse", 3: "identity hate crime", 4: "hate crime", 5: "offense", 6: "neither"}
            
            policies_dict = {0 : "https://help.twitter.com/en/safety-and-security/offensive-tweets-and-content", 
                 1 : "https://help.twitter.com/en/rules-and-policies/violent-threats-glorification",
                 2 : "https://help.twitter.com/en/rules-and-policies/abusive-behavior",
                 3 : "https://help.twitter.com/en/rules-and-policies/hateful-conduct-policy",
                 4 : "https://help.twitter.com/en/rules-and-policies/hateful-conduct-policy",
                 5 : "https://help.twitter.com/en/safety-and-security/offensive-tweets-and-content"}

            twitter_rules = "https://help.twitter.com/en/rules-and-policies#general-policies"

            with st.spinner("Predicting..."):
                TopicClassifier =  tf.keras.models.load_model('Topic Identifier/model_saves/topic_identifier_model.h5')
                topic_pred = TopicClassifier.predict(topicTweet)
                
            topTopic = topic_pred.argmax(1)[0]
            topTopicText = topic_dict[topic_pred.argmax(1)[0]]
            
            if topic_pred.argmax(1)[0]!=6 :
              st.write("Your tweet may contain sentences that promote " + topTopicText+ " with  "+str(topic_pred[0][topTopic]*100) +" % confidence")
              st.write("Please review  Twitter Rules and policies: "+ twitter_rules)
              st.write("And Twiiter's "+ topTopicText + " policy: "+ policies_dict[topic_pred.argmax(1)[0]])
            else:
                st.write("Your tweet is fine in terms of policy.")
                st.write(topic_pred)
                    
    if publish:
        publish_tweet(predText, sentence)

if __name__ == "__main__":
    main()
