from urllib.request import Request, urlopen
import urllib.request
from bs4 import BeautifulSoup
import json
from sudachipy import tokenizer
from sudachipy import dictionary
from deck_aux import *

# Functions from the sudachipy lib, the Japanese NLP Library
tokenizer_obj = dictionary.Dictionary().create()
# This is the split mode, which can be either A, B or C
mode = tokenizer.Tokenizer.SplitMode.B

#'https://yonde.itazuraneko.org/novelhtml/23917.html#calibre_link-15'
print("HTML page: ")

web_text = text_hook(input())

# All the words in the novel
entry_list = []

# web_text return a list of phrases, we scan over all these phrases and separate the words using the sudachipy 'tokenize' function
for phrase in web_text: 
    for word in tokenizer_obj.tokenize(phrase, mode):
        entry_list.append(word.normalized_form())
        
# We remove duplicates creating a frequency list
dictionary = wordListToFreqDict(entry_list)

# We build a html list from a corpus online with the 45k most frequent words in japanese
frequency_html = text_hook('http://corpus.leeds.ac.uk/frqc/internet-jp-forms.num')

# We store the words, removing all the trash, e.g. que frequency numbers using the function 'num_there'
wordfrequency_list = [entry for entry in frequency_html if num_there(entry) == False]

# We build a list with the intersection between the words in the novel and the 
# words in the frequency list, ignoring all the stop words
stop_words = open("jp_stop.txt", "r").read().split()
intersection_list = [word for word in dictionary if word in wordfrequency_list[4000:] and word not in stop_words]

# Dictionary entries
data = []

# There are 29 json entries, we scan all over them and build a big dictionary
for i in range(1, 30):
    with open('jmdict_english/term_bank_'+str(i)+'.json') as f:
      data = data + json.load(f)

dictoutput = json.dumps(data, indent = 2, sort_keys=True)
jpdict = json.loads(dictoutput)

# Writing to a txt file
f = open("jpdict.txt", "w")
for entry in jpdict:
    f.write(str(entry) + '\n')
f.close()

# We store all the notes in the deck
notes_in_deck = invoke('findNotes', query='"deck:JLPT N3 Vocab"') # Here we have to write '"Deck name"', with the "", otherwise deck names with spaces don't work
notes_in_deck = notes_in_deck + invoke('findNotes', query='"deck:JLPT N2 Vocab"')
# We read all the data from the notes
notes_data = invoke('notesInfo', notes=notes_in_deck)
# We build a list with the front of all cards
JLPT_words_list = [entry["fields"]["Expression"]["value"] for entry in notes_data]

# We remove all the words already in our deck
intersection_list = [word for word in intersection_list if word not in JLPT_words_list]

notes_in_deck = invoke('findNotes', query='"deck:Japanese - Browser"') # Here we have to write '"Deck name"', with the "", otherwise deck names with spaces don't work
notes_data = invoke('notesInfo', notes=notes_in_deck)
Personal_deck_words_list = [entry["fields"]["Expression"]["value"] for entry in notes_data if "Expression" in entry["fields"]]
Personal_deck_words_list = Personal_deck_words_list + [entry["fields"]["Spelling"]["value"] for entry in notes_data if "Spelling" in entry["fields"]]

# We remove all the words already in our deck
intersection_list = [word for word in intersection_list if word not in Personal_deck_words_list]

# Here we build the dictionary, taking care of duplicates

words, reading, meaning = [], [], []
previous_expression = ''

for dict_entry in jpdict:
    
    # We extract the word, its reading and the meaning from the dictionary
    expression = dict_entry[0]
    furigana = dict_entry[1]
    translation = dict_entry[5]
    
    # If the entry is not repeated, append it to the list
    if expression!= previous_expression:
        words.append(expression) 
        meaning.append(translation)
        reading.append(furigana)
    
    else:
        # We merge equal entries, putting all the meanings together
        meaning[-1] = meaning[-1] + translation
        # Avoid adding duplicate readings
        if furigana not in reading[-1]:
            reading[-1] = reading[-1] + ' - ' + furigana
            
    previous_expression=words[-1]

# A tuple with word, reading and meaning, in this order - our effective dictionary
jpdict_pair = list(zip(words, reading, meaning))
# A list with only the japanese words. We use it to retrieve its position in the list jpdict_pair, which works as our effective dictionary
jpdict_indexes = [entry[0] for entry in jpdict_pair]

# Words to be added in the deck
words_to_add = []

# Scan over the words in the intersection list
for entry in intersection_list:
    # If the word is in the dictionary
    if entry in jpdict_indexes:
        # Retrieves the word position in the dictionary and add it, along with its reading and meaning, in our list words_to_add
        words_to_add.append(jpdict_pair[jpdict_indexes.index(entry)])
        
print("Total words: ", len(words_to_add))

# Deck name
print("Deck name:")
deck_name = input()

# Creates the deck
invoke('createDeck', deck=deck_name)

# Scan over our list of words to add and add them to Anki
for entry in words_to_add:
    
    word = entry[0] #Expression
    meaning = "<br/>".join([entry[1], ', '.join(entry[2])]) #Reading and Meaning
    
    # Here we add the note, following the Basic model. This first line are just the note parameters
    new_note = {'deckName': deck_name, 'modelName': 'Basic', 'fields': {'Front': word, 'Back': meaning}, 'tags':['tag_teste']}
    try:
        invoke('addNote', note=new_note)

    except:
        pass
