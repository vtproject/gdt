#How to Extract URL from a string in Python?
 
import re
 
def URLsearch(stringinput):
 
  #regular expression
 
 regularex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))))+(?:(([^\s()<>]+|(([^\s()<>]+))))|[^\s`!()[]{};:'\".,<>?«»“”‘’]))"
 
 #finding the url in passed string
 
 urlsrc = re.findall(regularex,stringinput)
 
 #return the found website url
 
 return [url[0] for url in urlsrc]
 
textcontent = 'text :a software website find contents related to technology https://devenum.com/test.md'
 
#using the above define function
 
print("Urls found: ", URLsearch(textcontent))