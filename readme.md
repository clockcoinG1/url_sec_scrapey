## README 
# How to activate pyenv, install lxml, and activate env

## Activate pyenv

```
$ virtualenv --python=${which python3.10} .
```

## Install lxml

```
$ pip install lxml bs4 requests 
```

## Activate env

```
$ source .env
```

## add your own secsites.txt
```
cat ${url list with forms and shit} > secsites.txt
```

## it will add all scrapes into temp dir homie

todo

```
import requests
from bs4 import BeautifulSoup
import re
import sys


def get_forms(url):
    """
    This function will take a url and return a list of forms on that page
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup.find_all('form')


def get_form_details(form):
    """
    This function will take a form and return a dictionary of the form details
    """
    details = {}
    # get the form action (target url)
    action = form.attrs.get('action').lower()
    # get the form method (POST, GET, etc.)
    method = form.attrs.get('method', 'get').lower()
    # get all the input details such as type and name
    inputs = []
    for input_tag in form.find_all('input'):
        input_type = input_tag.attrs.get('type', 'text')
        input_name = input_tag.attrs.get('name')
        inputs.append({'type': input_type, 'name': input_name})
    # put everything to the dictionary
    details['action'] = action
    details['method'] = method
    details['inputs'] = inputs
    return details


def print_form_details(form_details):
    """
    This function will print the form details in a user friendly format
    """
    print('action:', form_details['action'])
    print('method:', form_details['method'])
    print('inputs:')
    for input in form_details['inputs']:
        print('\t', input['type'], input['name'])


def main():
    """
    This function will be called if the script is directly ran
    """
    # get the url from the command line
    url = sys.argv[1]
    # get all the forms from the url
    forms = get_forms(url)
    # print the number of forms on the page
    print('num of forms:', len(forms))
    # iterate over the forms
    for i, form in enumerate(forms):
        print('form', i)
        # get the form details
        form_details = get_form_details(form)
        # print the form details
        print_form_details(form_details)
        print()


if __name__ == '__main__':
    main()


```
