import urllib

file1 = open("file1.md", "r", encoding = "utf-8")
content1 = file1.read()
file1.close()

file2 = open("file2.md", "r", encoding = "utf-8")
content2 = file2.read()
file2.close()

content_merge = content1 + "\n\n" + content2

output = open("output.md", "w") #delete previous instance of file 
output.close()

output = open("output.md", "a", encoding = "utf-8") 

output.write(content_merge)

print(content_merge)
