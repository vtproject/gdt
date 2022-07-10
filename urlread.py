import urllib.request
import re
import full_link_generator

source_list = ["https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/master/doc/settings/dns.md",
               "https://gitlab.com/gitlab-org/omnibus-gitlab/-/blob/master/doc/update/convert_to_omnibus.md"]

regex_md = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

with open("output.md", "w") as output: #delete previous instance of file 
    output.close()
    
for source in source_list:
    with urllib.request.urlopen(source.replace("blob", "raw")) as response:
        source_data = response.read().decode("utf-8")
    
    source_links = list(regex_md.findall(source_data))
    
    for link in source_links:
        if ".md" in link[1]:
            full_link = full_link_generator.main(source, link[1])
            with urllib.request.urlopen(full_link.replace("blob", "raw")) as response:
                link_data = "\n\n\n[- start of linked file " + full_link + " -] \n" + response.read().decode("utf-8") + "[- end of linked file -]\n\n\n"
                source_data = source_data.replace(link[1], link_data)
    
    with open("output.md", "a", encoding = "utf-8") as output:
        output_header = "[- source file " + source + " -]\n"
        output.write(output_header)
        output.write(source_data)
        output.write("\n\n\n[- end of source file -]\n\n\n")

output.close()          
