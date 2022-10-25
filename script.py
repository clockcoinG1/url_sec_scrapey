import argparse
import base64
import json
import os
import re
import socket
import sys
import time
import urllib.parse
import urllib.request

import mechanize
import requests
from bs4 import BeautifulSoup
from mechanize import Browser


input_data = {}


def get_input_data(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    hidden_inputs = soup.find_all('input', type='hidden')
    for hidden_input in hidden_inputs:
        if hidden_input.has_attr('name') and hidden_input.has_attr('value'):
            input_data[hidden_input['name']] = hidden_input['value']
    script = soup.find('script', text=re.compile('SubmitForm'))
    if script:
        submit_regex = re.compile(r'SubmitForm\((.*)\)')
        submit_args = submit_regex.search(script.text).group(1)
        submit_args = submit_args.replace('\'', '').split(',')
        input_data['__EVENTTARGET'] = submit_args[0]
        input_data['__EVENTARGUMENT'] = submit_args[1]
    print("IMPUT: " + json.dumps(input_data))
    return input_data


def get_action_ep(form, url):
    soup = BeautifulSoup(form, 'lxml')
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action')
        if action:
            if action.startswith('/'):
                action = url + action
            print('action:', action)
        else:
            print('action:', url)
        inputs = form.find_all('input')
        for input in inputs:
            if input.get('type') == 'submit':
                print('input:', input.get('name'))


def get_action_ep_with_requests(form, url):
    fields = []
    soup = BeautifulSoup(form, 'lxml')
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action')
        if action:
            if action.startswith('/'):
                action = urllib.parse.urljoin(url, action)
                print('action:', action)
            else:
                print('action:', url)
                inputs = form.find_all('input')
        for input in inputs:
            input_type = input.get('type')
            input_name = input.get('name')
            fields.append((input_type, input_name))
            if input.get('type') == 'submit':
                print('submit input:', input.get('value'))
            if input.get('type') == 'text':
                print('name:', input.get('name'))
                print('attType:', input.get('type'))
                make_request(action, fields)
                print('loading request for ', action)


def make_request(url, fields):
    data = {}
    files = {}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    for field in fields:
        if field[0] == 'text' or field[0] == 'hidden':
            # input('Enter ' + field[1] + ': ')
            data[field[1]] = 'https://opensea.io'
        if field[0] == 'file' and field[1] != '__RequestVerificationToken':
            files[field[1]] = open(input('Enter ' + field[1] + ': '), 'rb')
        if field[0] == 'file' and field[1] == '__RequestVerificationToken':
            data[field[1]] = field[2]
    if files:
        r = requests.post(url, data=data, files=files)
    else:
        r = requests.post(url, data=data, headers=headers)
    domain = urllib.parse.urlparse(url).netloc
    if not os.path.exists('./temp/'):
        os.makedirs('./temp/')
    with open('./temp/' + domain, 'w') as f:
        f.write(r.text)
        f.write(json.dumps(data))


def get_fields(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    fields = []
    for input in soup.find_all('input'):
        if input.get('type') == 'text' or input.get('type') == 'hidden':
            fields.append(
                (input.get('type'), input.get('name'), input.get('value')))
        if input.get('type') == 'file':
            fields.append((input.get('type'), input.get('name')))
    return fields


def get_token(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for input in soup.find_all('input'):
        if input.get('name') == '__RequestVerificationToken':
            return input_data['__RequestVerificationToken']


def get_fields_with_token(url):
    fields = get_fields(url)
    token = get_token(url)
    for field in fields:
        if field[1] == '__RequestVerificationToken':
            field[2] = token
    return fields


def get_request_verification_token(form):
    soup = BeautifulSoup(form, 'lxml')
    inputs = soup.find_all('input')
    for input in inputs:
        if input.get('name') == '__RequestVerificationToken':
            return input_data['__RequestVerificationToken']


def get_form_fields(form):
    fields = []
    soup = BeautifulSoup(form, 'lxml')
    inputs = soup.find_all('input')
    for input in inputs:
        input_type = input.get('type')
        input_name = input.get('name')
        fields.append((input_type, input_name))
    return fields


def get_form_action(form, url):
    soup = BeautifulSoup(form, 'lxml')
    forms = soup.find_all('form')
    for form in forms:
        action = form.get('action')
        if action:
            if action.startswith('/'):
                action = urllib.parse.urljoin(url, action)
                return action


def get_form_data(form, url):
    fields = get_form_fields(form)
    action = get_form_action(form, url)
    token = get_request_verification_token(form)
    if token:
        fields.append(('hidden', '__RequestVerificationToken', token))
    return fields, action


def make_request_thread(form, url):
    fields, action = get_form_data(form, url)
    make_request(action, fields)


def make_requests(forms, url):
    threads = []
    for form in forms:
        t = threading.Thread(target=make_request_thread, args=(form, url))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


def get_request_data(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    hidden_inputs = soup.find_all('input', type='hidden')
    for hidden_input in hidden_inputs:
        if hidden_input.has_attr('name') and hidden_input.has_attr('value'):
            input_data[hidden_input['name']] = hidden_input['value']
    script = soup.find('script', text=re.compile(
        'SubmitForm\(.*\);', re.DOTALL))

    if script:
        submit_regex = re.compile(r'SubmitForm\((.*)\)')
        submit_args = submit_regex.search(script.text).group(1)
        submit_args = submit_args.replace('\'', '').split(',')
        input_data['__EVENTTARGET'] = submit_args[0]
        input_data['__EVENTARGUMENT'] = submit_args[1]
    print("IMPUT: " + json.dumps(input_data))
    return input_data


def __main__():
    with open('secsites.txt', 'r') as f:
        for line in f:
            if not line.startswith("#"):
                url = line[:-1]
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'}
                    r = requests.get(url, headers=headers)
                    if r.status_code == 200:
                        soup = BeautifulSoup(r.text, 'lxml')
                        get_input_data(url)
                        get_action_ep_with_requests(r.text, url)

                except Exception as e:
                    print(e)


__main__()
