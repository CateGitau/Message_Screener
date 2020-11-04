# load libraries
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import random
import re
import string

# read file of blacklisted terms
#inputFile = open("C:/Kandra DSI Program/Module 3/Project/code/Message_Screener/blacklist.txt", mode = 'r')
#inputFile = open("Message_Screener/blacklist.txt", mode = 'r')
#blacklist = [line.strip() for line in inputFile]
#inputFile.close()

#read blacklist words from database
db = database()
df_blacklist = db.get_blacklist_list()
blacklist = df_blacklist['word'].tolist()

# functions
def profanityscreen(inputMessage, filterList, mask = False, replacements="$@#*"):
    ''' Input: a message (str), a list of profane words to check against, optionally if the
     input message should be edited to censor/mask profane words (bool),
     optionally, replacement symbols for masking (str)
     Body: Compare unique words (unigram) in input message to the profanity list; optionally
     revise input message to mask profane words
     Output: tuple containing the original/revised message (str) and list of profane words that match
     the blacklist '''

    # create different versions of the hyphen (convert hyphen to space, remove hyphen and keep hyphen) and remove all other punctuation
    lowerMessage = inputMessage.lower()
    message_splitHyphen_no_punctuation = lowerMessage.replace("-", " ").translate(str.maketrans('', '', string.punctuation))
    message_keepHyphen_no_punctuation = lowerMessage.translate(str.maketrans('', '', string.punctuation.replace("-","")))
    message_no_punctuation = lowerMessage.translate(str.maketrans('', '', string.punctuation))
    messages = [message_splitHyphen_no_punctuation, message_keepHyphen_no_punctuation, message_no_punctuation]

    # create regex for the blacklist terms to scan the messages
    blacklist_terms = [r"\b({term})\b".format(term=term) for term in filterList]
    regexes = [re.compile(term) for term in blacklist_terms]
    find_list = [regex.search(message) for message in messages for regex in regexes if regex.search(message) != None]

    # create list of black words found in all the permutations of the message (ie with manipulation of hyphenated words)
    black_words = list(set([hit.group() for hit in find_list]))

    ## create final list of black words in the format they appear in the message
    # find black words that appear as-is in base form
    shortlist = [r"\b(?<!-)({term})(?!-)\b".format(term=term) for term in black_words]
    shortlist_regexes = [re.compile(term) for term in shortlist]
    find_shortlist = [regex.search(message_keepHyphen_no_punctuation) for regex in shortlist_regexes if regex.search(message_keepHyphen_no_punctuation) != None]

    #final terms contains pure matches to the blacklist
    final_terms = list(set([hit.group() for hit in find_shortlist]))

    # remaining terms are probably partial matches that appear as part of hyphenated words
    remaining_terms = [term for term in black_words if term not in final_terms]

    # find the hyphenated words that the base term appears in
    remaining = [r"(\b{term}-\w+\b) | (\b\w+-{term}\b)".format(term=term) for term in remaining_terms]
    remaining_regex = [re.compile(word) for word in remaining]
    remaining_list = [regex.search(message_keepHyphen_no_punctuation) for regex in remaining_regex if
                      regex.search(message_keepHyphen_no_punctuation) != None]

    # add the unique hyphenated profane words to the final terms list
    final_terms.extend(list(set([hit.group().strip() for hit in remaining_list])))

    # terms that still remain are either no in the list because they were one part of
    # a hyphenated word or it is a multiple word term that is hyphenated in the message
    still_remaining = [term for term in black_words if term not in final_terms]

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
        return (new_message, final_terms)
    else:
        return (inputMessage, final_terms)


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

inMsg8 = "The Scunthorpe problem is that our town's name is censored because it contains the substring 'cunt'. No fair you mother-fucker!"
print(profanityscreen(inMsg8, blacklist, mask=True))
# ERROR: does not pick up word in quotes ('') - because of word_tokenizer

inMsg9 = "The Scunthorpe problem is that our town's name is censored because it contains the substring cunt. No fair!"
print(profanityscreen(inMsg9, blacklist, mask=True))

inMsg10 = "Have you seen the video 2 girls 1 cup? No, but one guy one jar is a must-see!"
print(profanityscreen(inMsg10, blacklist, mask=True))

inMsg11 = "Have you seen the video 2 girls 1 cup? No, but one-guy-one-jar is a must-see!"
print(profanityscreen(inMsg11, blacklist, mask=True))

##improvement: currently the black-word output list is only the base terms; can improve by
## retunring a black-word output list that includes novel hyphenated swear words

##improvement + fix: change search stragtegy to search profane terms of multiple length - scan blacklist over message rather
## than message (broken into n-grams) over blacklist
