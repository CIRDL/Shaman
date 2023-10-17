import requests
from bs4 import BeautifulSoup
import re


source = 'https://ou-public.courseleaf.com/courses/ise/'

r = requests.get(source)
soup = BeautifulSoup(r.text, 'html.parser')

# Initialize empty lists
class_codes = []
class_names = []
credit_hours = []
prereqs = []

main_body = soup.find_all(class_='courseblock')

for element in main_body[0:10]:
        
    header = element.find('strong')
    if header:
        parser = header.text.split()
        class_code = ''.join(parser[0:2])[0:-1]
        class_name = ' '.join(parser[2:])[0:-1]
        class_codes.append(class_code)
        class_names.append(class_name)

    hours = element.find(class_='credits').text
    if hours:
        parser = hours.split()
        credit_hour = parser[0]
        credit_hours.append(credit_hour)
    
    body = element.find(class_='courseblockdesc')
    if body:
        prerequisites = re.findall(r'Prerequisite:([^\.]*)\.', body.text)
        if prerequisites:
            print(f"Prerequisites found: {prerequisites[0]}")
        else:
            print("No prerequisites found")

# for index in range(len(class_codes)):
#     print(class_codes[index], " ", class_names[index], " ", credit_hours[index])

