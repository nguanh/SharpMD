import requests
import os

url = "http://localhost:8080/processReferences"
os
# open pdf file

with open("grobid1.pdf", "rb") as f:
    x= requests.post(url, files={"input":f})
    print (x.text)