from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import urllib.request
import json

# This removes the alphanumeric characters
def stripNonAlphaNum(text):
    import re
    return re.compile(r'\W+', re.UNICODE).split(text)

# This function is important because it helps us remove the frequency ranking numbers in the page
def num_there(s):
    return any(i.isdigit() for i in s)

# Copies the text from a webpage, removing all the useless html stuff in the middle. The header bypasses some security problems which yield html 403 error
def text_hook(url_page):

    req = Request(url_page, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, "html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return stripNonAlphaNum(text)

# This is the function that builds the pair (word, frequency)
def wordListToFreqDict(wordlist):
    
    wordfreq = [wordlist.count(p) for p in wordlist]

    return dict(list(zip(wordlist,wordfreq)))

# Used for the Anki API
def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

# We use this command to execute the API functions
def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']
