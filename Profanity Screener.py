# load libraries
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import random
import re

# read file of blacklisted terms
inputFile = open("DSI/Natural Language Processing Challenge/blacklist.txt", mode = 'r')
blacklist = [line.strip() for line in inputFile]
inputFile.close()

# functions
def profanityscreen(inputMessage, filterList, mask = False, replacements="$@#*"):
    ''' Input: a message (str), a list of profane words to check against, optionally if the
     input message should be edited to censor/mask profane words (bool),
     optionally, replacement symbols for masking (str)
     Body: Compare unique words (unigram) in input message to the profanity list; optionally
     revise input message to mask profane words
     Output: tuple containing the original/revised message (str) and list of profane words that match
     the blacklist '''

    # replace hyphen (-) with a space
    message = inputMessage.replace("-", " ")
    # break message into words (tokens - unigrams)
    tokens = [w for w in word_tokenize(message.lower()) if w.isalpha()]
    #remove stop words (like in, at, and, if)
    tokens_no_stops = [t for t in tokens if t not in stopwords.words('english')]
    #take only the unique words in the bag of words
    unique_tokens = list(set(tokens_no_stops))
    #find the base words in the message that match the words in the blacklist (one word comparison)
    black_words = [t for t in unique_tokens if t in filterList]

    def cleaner(black_word, replacements):
        ''' Input: a list of blacklisted words and a set of replacement symbols
        Body: substitutes every second character, excluding
        the first and last characters, of a black word with random symbols
        Output: masked word '''
        return ''.join([random.choice(replacements) if i % 2 == 1 and i != 0 and i != len (black_word)-1 and
                                                       black_word[i].isalnum() and black_word[i+1].isalnum()
                                                        else black_word[i] for i in range(len(black_word))])

    #censor flagged words
    if mask:
        #break message into list of words (punctuation is attached to the preceding word because split of the space)
        message_list = inputMessage.split()
        #take the black words found in the message and convert to regex where the word can be immediately followed
        # by a space, full stop, exlaimation mark or hyphen
        black_words_regex = [f"^(.*-)?\W*({word})\W*(-.+)?$" for word in black_words]
        regexes = [re.compile(word) for word in black_words_regex]
        #rewrite the original message, replacing the characters in words that match the blacklist with random symbols
        new_message = " ".join([cleaner(w, replacements) if any(regex.search(w.lower()) for regex in regexes) else w for w in message_list])
        return (new_message, black_words)
    else:
        return (inputMessage, black_words)


### Tests ###
inMsg1 = "Bastard begot, bastard instructed, bastard in mind,... in everything illegitimate."
print(profanityscreen(inMsg1, blacklist, mask=True))

inMsg2 = "Son and heir of a mongrel bitch."
print(profanityscreen(inMsg2, blacklist, mask=True))

inMsg3 = "Thou bitch-wolf's son!"
print(profanityscreen(inMsg3, blacklist, mask=True))

inMsg4 = "You are a motherfucker"
print(profanityscreen(inMsg4, blacklist, mask=True))

inMsg5 = "You are a motherfucker!"
print(profanityscreen(inMsg5, blacklist, mask=True))

inMsg6 = "You are a mother-fucker!"
print(profanityscreen(inMsg6, blacklist, mask=True))

inMsg7 = "You $%&*bastard!$%&*'"
print(profanityscreen(inMsg7, blacklist, mask=True))

inMsg8 = "The Scunthorpe problem is that our town's name is censored because it contains the substring 'cunt'. No fair!"
print(profanityscreen(inMsg8, blacklist, mask=True))
# ERROR: does not pick up word in quotes ('') - because of word_tokenizer

inMsg9 = "The Scunthorpe problem is that our town's name is censored because it contains the substring cunt. No fair!"
print(profanityscreen(inMsg9, blacklist, mask=True))

##improvement: currently the black-word output list is only the base terms; can improve by
## retunring a black-word output list that includes novel hyphenated swear words

##improvement + fix: change search stragtegy to search profane terms of multiple length - scan blacklist over message rather
## than message (broken into n-grams) over blacklist
