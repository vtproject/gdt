import urllib.request
import re

with open("output.md", "w") as output: #delete previous instance of file 
    output.close()

source_list = ["https://raw.githubusercontent.com/wiki/vtproject/gdt/Test-file-A.md",
               "https://raw.githubusercontent.com/wiki/vtproject/gdt/Test-file-B.md"]

data_list = []
for url in source_list:
    with urllib.request.urlopen(url) as response:
        url_data = response.read().decode("utf-8") 
        data_list.append(url_data)
        
with open("output.md", "a", encoding = "utf-8") as output:
    for text in data_list:
        output.write(text)
        output.write("\n")
    output.close()

with open("output.md") as file:
    output_data = file.read()

print(output_data)    

regularex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))))+(?:(([^\s()<>]+|(([^\s()<>]+))))|[^\s`!()[]{};:'\".,<>?«»“”‘’]))"
urlsrc = re.findall(regularex,output_data)
    
linked_sources = []
for url in urlsrc:
    linked_sources.append(url[0])

for url in linked_sources:
    with urllib.request.urlopen(url) as response:
        url_data = response.read().decode("utf-8")
        output_data = output_data.replace(url, url_data)    

print(output_data)

  