# load libraries
import random
import re
import string
from nltk import bigrams
from nltk import sent_tokenize
import Database

# read file of blacklisted terms
#inputFile = open("C:/Kandra DSI Program/Module 3/Project/code/Message_Screener/blacklist.txt", mode = 'r')
#inputFile = open("Message_Screener/blacklist.txt", mode = 'r')
#blacklist = [line.strip() for line in inputFile]
#inputFile.close()

#read blacklist words from database
db = Database.database()

 # populate blacklist with newly added terms
inputFile = open("blacklist.txt", mode = 'r')
for line in inputFile:
    db.insert_new_blacklist_word(line.strip())
    
blacklist = db.get_blacklist_list()

# functions
def profanityscreen(inputMessage, filterList, mask = False, replacements="$@#"):
    ''' Input: a message (str), a list of profane words to check against, optionally if the
     input message should be edited to censor/mask profane words (bool),
     optionally, replacement symbols for masking (str)
     Body: Compare unique words (unigram) in input message to the profanity list; optionally
     revise input message to mask profane words
     Output: tuple containing the original/revised message (str) and list of profane words that match
     the blacklist '''

    #clean message by removing any multiple spaces
    no_doublespace = re.sub(r"\s+", " ", inputMessage)
    # convert message to lower case
    lowerMessage = no_doublespace.lower()
    # tokenise the sentences so that searching does not run over sentences
    sentences = sent_tokenize(lowerMessage)

    # create different versions of the hyphen in the messages
    # convert hyphen to a single space and remove all other punctuation; rejoin sentences using a fullstop and a space
    sentences_splitHyphen_no_punctuation = [sentence.replace("-", " ").translate(str.maketrans('', '', string.punctuation)) for sentence in sentences]
    message_splitHyphen_no_punctuation = ". ".join(sentences_splitHyphen_no_punctuation)

    # keep hyphens but remove all other punctuation; rejoin sentences using a fullstop and a space
    sentences_keepHyphen_no_punctuation = [sentence.translate(str.maketrans('', '', string.punctuation.replace("-", ""))) for sentence in sentences]
    message_keepHyphen_no_punctuation = ". ".join(sentences_keepHyphen_no_punctuation)

    #remove all punctuations (hyphenated words become concatenated into one word); rejoin sentences using a fullstop and a space
    sentences_no_punctuation = [sentence.translate(str.maketrans('', '', string.punctuation)) for sentence in sentences]
    message_no_punctuation = ". ".join(sentences_no_punctuation)

    # collect message permutations into a list
    messages = [message_splitHyphen_no_punctuation, message_keepHyphen_no_punctuation, message_no_punctuation]

    # generate bigrams without spaces to scan
    created_bigrams = [list(bigrams(sentence.split())) for sentence in sentences_no_punctuation]
    final_grams = {}
    for bigram in created_bigrams:
        for word1, word2 in bigram:
            new_word = word1 + word2
            final_grams[new_word] = word1 + " " + word2

    #augment blacklist by manipulating hyphenated words as done for the message
    def augement_blacklist(filterList):
        blacklist = filterList
        remove_space_two_words = [word.replace(" ", "") for word in blacklist if len(word.split()) == 2]
        separate_hyphen_words = [word.replace("-", " ") for word in blacklist if bool(re.search(r"-", word))]
        collapse_hyphen_words = [word.replace("-", "") for word in blacklist if bool(re.search(r"-", word))]

        blacklist.extend(remove_space_two_words)
        blacklist.extend(separate_hyphen_words)
        blacklist.extend(collapse_hyphen_words)

        return blacklist

    # create regex for the blacklist terms to scan the messages; indifferent to trailing or leading digits as well as common prefixes and suffixes
    blacklist_terms = [r"\b(?:\d)*(?:anti)*(?:de)*(?:dis)*(?:hyper)*(?:inter)*(?:intra)*(?:mal)*(?:mis)*(?:multi)*(?:non)*(?:poly)*(?:pre)*(?:pro)*(?:re)*(?:semi)*(?:sub)*(?:super)*(?:supra)*(?:trans)*(?:ultra)*(?:un)*({term})(?:s)*(?:er)*(?:ing)*(?:es)*(?:ful)*(?:full)*(?:fuly)*(?:ion)*(?:ity)*(?:ment)*(?:nes)*(?:ness)*(?:ship)*(?:sion)*(?:able)*(?:ible)*(?:ary)*(?:ious)*(?:ous)*(?:ive)*(?:les)*(?:less)*(?:ed)*(?:ise)*(?:ize)*(?:ly)*(?:ward)*(?:wise)*(?:\d)*\b".format(term=term) for term in augement_blacklist(filterList)]
    regexes = [re.compile(term) for term in blacklist_terms]
    find_list = [regex.search(message) for message in messages for regex in regexes if regex.search(message) != None]

    # create list of black words found in all the permutations of the message
    black_words = list(set([hit.group() for hit in find_list]))

    #add blackwords found in bigrams
    for key, value in final_grams.items():
        if any([regex.search(key) for regex in regexes if regex.search(key) != None]):
            black_words.append(value)

    black_words = list(set(black_words))

    ## create final list of black words in the format (insofar as the hyphen) that they appear in the message
    # find black words that appear as-is in base form (not before or after a hyphen; separate words)
    shortlist = [r"\b(?<!-)({term})(?!-)\b".format(term=term) for term in black_words]
    shortlist_regexes = [re.compile(term) for term in shortlist]
    find_shortlist = [regex.search(message_keepHyphen_no_punctuation) for regex in shortlist_regexes if regex.search(message_keepHyphen_no_punctuation) != None]

    #add the terms to the final list
    final_terms = list(set([hit.group() for hit in find_shortlist]))

    # remaining terms are probably partial matches that appear as part of hyphenated words
    remaining_terms = [term for term in black_words if term not in final_terms]

    # find the hyphenated terms that the base profane word appears in
    remaining1 = [r"(\b{term}-\w+\b)".format(term=term) for term in remaining_terms] #match word before hyphen
    remaining2 = [r"(\b\w+-{term}\b)".format(term=term) for term in remaining_terms] #match word after hyphen
    remaining = remaining1 + remaining2
    remaining_regex = [re.compile(word) for word in remaining]
    remaining_list = [regex.search(message_keepHyphen_no_punctuation) for regex in remaining_regex if
                      regex.search(message_keepHyphen_no_punctuation) != None]

    # add the unique hyphenated profane words to the final terms list
    final_terms.extend(list(set([hit.group().strip() for hit in remaining_list])))

    # terms that still remain are either not in the list because they were one part of
    # a hyphenated word or it is a multiple word term that is hyphenated in the message
    still_remaining = [term for term in black_words if term not in final_terms]

    # create regex to scan terms that may contain hyphens between the words
    still = []
    for term in still_remaining:
        if bool(re.search(r"\s", term)):
            split_term = term.split()
            regex_builder = split_term[0]
            for i in range(1, len(split_term)):
                regex_builder += "-?\s?" + split_term[i]
            still.append(regex_builder)

    still_regex = [re.compile(word) for word in still]
    still_list = [regex.search(message_keepHyphen_no_punctuation) for regex in still_regex if
                  regex.search(message_keepHyphen_no_punctuation) != None]

    # add the multiple hyphenated profane words to the final terms list
    final_terms.extend(list(set([hit.group().strip() for hit in still_list])))

    #define function that masks words
    def cleaner(black_word, replacements=replacements):
        ''' Input: a word to be masked and a set of replacement symbols
        Body: substitutes every second letter character, excluding
        the first and last characters, of a black word with random symbols
        ignoring any symbols between the letters
        Output: masked word '''

        # convert the word to a list of letters
        input_list = list(black_word)
        # convert the list of letters to a dictionary where the character indices are the keys
        input_dic = dict(enumerate(input_list))
        # delete the first and last entry of the dictionary for the first and last letter of the word
        del input_dic[0]
        del input_dic[len(input_list) - 1]
        # find the remaining indices for the letters in the word (ie exclude any internal punctuation)
        valid_positions = [key for key in input_dic if input_dic[key].isalpha()]
        # randomly select 50% of the valid letters to convert to a symbol
        selected_positions = [item for index, item in enumerate(valid_positions) if index % 2 == 0]

        # subsitute the randomly selected positions with randomly selected replacement symbols
        return ''.join([random.choice(replacements) if i in selected_positions else input_list[i] for i in range(len(black_word))])

    #censor flagged words
    if mask:
        # create regex to match the black words from the final terms list as the appear in the message
        # allow for any letter to be upper or lower case; allow non-word characters between the letters of the word
        masker = []
        for term in final_terms:
            regex_builder = "[" + term[0] + "|" + term[0].upper() + "]"
            for i in range(1, len(term)):
                regex_builder += "\W*" + "[" + term[i] + "|" + term[i].upper() + "]"
            regex_builder = r"\b({})\b".format(regex_builder)
            regex_builder = re.compile(regex_builder)
            masker.append(regex_builder)

        # run the regex over the message and substitute matches with censored version by calling the `cleaner` function
        new_message = inputMessage
        for regex in masker:
            new_message = re.sub(regex, lambda x: cleaner(x.group()), new_message)

        return (new_message, final_terms)
    else:
        return (inputMessage, final_terms)

### Tests ###
print(profanityscreen("Bastard begot, bastard instructed, bastard in mind,... in everything illegitimate.", blacklist, mask=True))
print(profanityscreen("Son and heir of a mongrel bitch.", blacklist, mask=True))
print(profanityscreen("Thou bitch-wolf's son!", blacklist, mask=True))
print(profanityscreen("You are a motherfucker", blacklist, mask=True))
print(profanityscreen("You are a motherfucker!", blacklist, mask=True))
print(profanityscreen("You are a daddy-fucker!", blacklist, mask=True))
print(profanityscreen("You $%&*bastard!$%&*'", blacklist, mask=True))
print(profanityscreen("The Scunthorpe problem is that our town's name is censored because it contains the substring 'cunt'. No fair you mother-fucker!", blacklist, mask=True))
print(profanityscreen("The Scunthorpe problem is that our town's name is censored because it contains the substring cunt. No fair!", blacklist, mask=True))
print(profanityscreen("Have you seen the video 2 girls 1 cup? No, but one guy one jar is a must-see!", blacklist, mask=True))
print(profanityscreen("Have you seen the video 2 girls 1 cup? No, but one-guy one-jar is a must-see!", blacklist, mask=True))
print(profanityscreen("you are a dumb-ass.", blacklist, mask=True))
print(profanityscreen("dumb-ass you are", blacklist, mask=True))
print(profanityscreen("6Ass-dumb4 Ass-dumb5 you are", blacklist, mask=True))
print(profanityscreen("python-whORe4", blacklist, mask=True))
print(profanityscreen("Thou wolf-bitch wolf-bitch", blacklist, mask=True))
print(profanityscreen("Thou 4bitch-wolf5", blacklist, mask=True))
print(profanityscreen("Give me a hand. Job is a great author.", blacklist, mask=True))
print(profanityscreen("The Scunthorpe problem is that our town's name is   censored because it contains the substring 'Cunt'. No fair you f.u.c.k.e.r! What a dumb-ass controversy.", blacklist, mask=True))
print(profanityscreen("Do not censor the word cunt. Only a Cunt does that.", blacklist, mask=True))
print(profanityscreen("whore4manic.", blacklist, mask=True))
print(profanityscreen("No swear words", blacklist, mask=True))





