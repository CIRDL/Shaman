import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


course_initials = ['ame', 'bme', 'che', 'cees',
                   'cs', 'dsa', 'ece', 'engr', 'ephy', 'ise']

links = {
    'ame': 'https://ou-public.courseleaf.com/gallogly-engineering/aerospace-mechanical-engineering/#coursestext',
    'bme': 'https://ou-public.courseleaf.com/gallogly-engineering/stephenson-biomedical-engineering/#coursestext',
    'che': 'https://ou-public.courseleaf.com/gallogly-engineering/chemical-biological-materials-engineering/#coursestext',
    'cees': 'https://ou-public.courseleaf.com/gallogly-engineering/civil-engineering-environmental-science/',
    'cs': 'https://ou-public.courseleaf.com/gallogly-engineering/computer-science/#coursestext',
    'dsa': 'https://ou-public.courseleaf.com/gallogly-engineering/program-data-science-analytics/#coursestext',
    'ece': 'https://ou-public.courseleaf.com/gallogly-engineering/electrical-computer-engineering/#coursestext',
    'engr': 'https://ou-public.courseleaf.com/gallogly-engineering/engineering/#coursestext',
    'ephy': 'https://ou-public.courseleaf.com/gallogly-engineering/engineering-physics/#coursestext',
    'ise': 'https://ou-public.courseleaf.com/gallogly-engineering/industrial-systems-engineering/#coursestext'
}

df_courses = pd.DataFrame(index=course_initials, columns=['data'])

courses = {}

# Modify data frame to contain columns class_code, class_name, and credit_hours
# TODO - Replace loop below by initializing data frame
# TODO - Create separate data frame (and/or for loop) for prerequisites
for course in course_initials:
    courses[course] = pd.DataFrame()

for course in ['cees', 'ise', 'cs']:

    source = links[course]

    r = requests.get(source)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Initialize empty lists
    class_codes = []
    class_names = []
    credit_hours = []
    df_course = pd.DataFrame(
        columns=['class_code', 'class_name', 'credit_hours'])
    prereqs = []

    main_body = soup.find_all(class_='courseblock')

    for element in main_body:

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
        df_course.loc[-1] = [class_code, class_name, credit_hours]
        df_course.index += 1
        df_course = df_course.sort_index()

    df_courses.loc[course] = [df_course]

    body = element.find(class_='courseblockdesc')
    if body:
        prerequisites = re.findall(r'Prerequisite:([^\.]*)\.', body.text)
        if prerequisites:
            for prereq in prerequisites:
                print(f"Prerequisites found: {prereq}")
        else:
            print("No prerequisites found")

    for index in range(len(class_codes)):
        print(class_codes[index], " ", class_names[index],
              " ", credit_hours[index])

print(df_courses.loc[0].at['data'])
print(df_courses['ise'])
