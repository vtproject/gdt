import urllib.request
import re

source_list = ["https://gitlab.com/gitlab-org/gitlab/blob/master/doc/install/relative_url.md",
               "https://gitlab.com/gitlab-org/omnibus-gitlab/blob/master/doc/index.md"]

data_list = []
for url in source_list:
    with urllib.request.urlopen(url.replace("blob", "raw")) as response:
        url_data = response.read().decode("utf-8") 
        data_list.append(url_data)
merged_file = "\n\n\n >>>>>>> next source file <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n\n\n".join(data_list) 


regex_http = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))))+(?:(([^\s()<>]+|(([^\s()<>]+))))|[^\s`!()[]{};:'\".,<>?«»“”‘’]))"
regex_md = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')


url_list = re.findall(regex_http,merged_file)
md_links = list(regex_md.findall(merged_file))

for item in md_links:
    if ".md" in item[1]:
        print(item)

linked_files = []
for url in url_list:
    linked_files.append(url[0])

for url in linked_files:
    if ".md" in url:
        print(url)
        with urllib.request.urlopen(url.replace("blob", "raw")) as response:
            link_data = "\n\n\n >>>>>>> start of linked file <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n\n\n" + response.read().decode("utf-8") + "\n\n\n***** end of linked file **************************************************************************\n\n\n"
            merged_file = merged_file.replace(url, link_data)    

with open("output.md", "w") as output: #delete previous instance of file 
    output.close()
    
with open("output.md", "a", encoding = "utf-8") as output:
    output.write(merged_file)
    output.close()

  