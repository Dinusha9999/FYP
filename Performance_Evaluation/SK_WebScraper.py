import bs4
import requests
import lxml
import html5lib
import pandas as pd
import re
import csv

#Varible and arrays
argument_array = []
argument_desc_array = []
value = []

#get gata from web
res = requests.get('https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html')
soup = bs4.BeautifulSoup(res.text, 'html5lib')
argument = soup.find('td',class_='field-body')

#Extract arguments
for arg in argument.find_all('strong'):
    argument_array.append(arg.text)

#Extract argument description
for arg in argument.find_all('dd'):
    argument_desc_array.append(arg.text.replace('\n',' ').replace('\t', ''))

#Extract default value with argument
for val in argument.find_all('dt'):
    value.append(val.text)

regex = r"\(default=.*?\)|(default:.*)|(default=.*)|\(default =.*?\)|(default.*)"

default_value = [None] * len(argument_array)

#Extract default values
for i, val in enumerate(value):
    if(val.count('default')==1):
        temp = re.search(regex, value[i]).group()
        temp = temp.replace('default','').replace('=','').replace('(','').replace(')','').replace(':','')
        default_value[i] = temp

#save data
df = pd.DataFrame({"Argument" : argument_array, "Description" : argument_desc_array, "Default_value" : default_value})
df.to_csv("SK_output.csv", index=False )
