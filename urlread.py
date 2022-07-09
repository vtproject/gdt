import urllib.request
import re

file_list = ["https://raw.githubusercontent.com/wiki/vtproject/gdt/Test-file-A.md",
             "https://raw.githubusercontent.com/wiki/vtproject/gdt/Test-file-B.md"]

data_list = []
for url in file_list:
    with urllib.request.urlopen(url) as response:
        url_data = response.read().decode("utf-8") 
        data_list.append(url_data)
merged_file = "\n".join(data_list) 

regularex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))))+(?:(([^\s()<>]+|(([^\s()<>]+))))|[^\s`!()[]{};:'\".,<>?«»“”‘’]))"

url_list = re.findall(regularex,merged_file)
    
linked_files = []
for url in url_list:
    linked_files.append(url[0])

for url in linked_files:
    with urllib.request.urlopen(url) as response:
        url_data = response.read().decode("utf-8")
        merged_file = merged_file.replace(url, url_data)    

print(merged_file)

with open("output.md", "w") as output: #delete previous instance of file 
    output.close()
    
with open("output.md", "a", encoding = "utf-8") as output:
    output.write(merged_file)
    output.close()

  