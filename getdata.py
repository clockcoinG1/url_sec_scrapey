import requests
import json
import time
import os
import sys
import re
import argparse
import base64
import mechanize
from bs4 import BeautifulSoup as BS
from mechanize import Browser


with open('secsites.txt', 'r') as f:
    for line in f:
        if not line.startswith("#"):  # skip comments in file...

            # strip trailing \n from each site before appending to list...
            url = line[:-1]

            try:

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'}

                # make request, check status code is 200, parse html using BeautifulSoup, find all form tags on page...
                r = requests.get(url, headers=headers)
                if r.status_code == 200:
                    soup = BS(r.text, 'html.parser')
                    formsList = soup.find_all('form')

                    for form in formsList:
                        print(form)

                    formFields = {}

                    for field in form.findAll("input"):

                        formFields[field.get("name")] = field.get("type")

                    print("\nForm action: "+form.get("action"))

                    print("Form fields: "+str(formFields))
        # uncomment this when ready to scrape live data! ###
                    response = requests.get(url, headers=headers)
        # comment this out when ready to scrape live data! ###
        # response = urllib2.urlopen(url)

        # check status code returned by server is OK i . e . 200 ...
                    if response.getcode() == 200:

                        # create BS object from HTML source code of web page...
                        soup = BeautifulSoup(response, "html5lib")
                        # find all <form> tags on the page and store them in a list variable called formsList ...
                        formsList = soup.findAll("form")
                        print("Found "+str(len(formsList))+" forms on " +
                              url+". Searching through them now...")

                    for form in formsList:

                        formFields = {}

                        for field in form.findAll("input"):

                            formFields[field.get(
                                "name")] = field.get("type")

                        print("\nForm action: "+form.get("action"))

                        print("Form fields: "+str(formFields))

                        if form.get("action") == "/search" or form.get("action") == "/search.php" or form.get("action") == "/search.asp" or form.get("action") == "/search.aspx" or form.get("action") == "/search.jsp" or form.get("action") == "/search.html" or form.get("action") == "/search.htm":

                            print("\nFound search form on "+url+"\n")

                            print("Creating request...")

                            payload = {'url': 'https://opensea.io'}

                            r = requests.get(url, params=payload)

                            print("Request sent.\n")

                            print("Response code: " +
                                  str(r.status_code))

                            print("Response headers: " +
                                  str(r.headers))

                            print("Response content: " +
                                  str(r.content))

                            print("\n")

                        else:

                            print(
                                "\nNo search form found on "+url+"\n")

                else:

                    print("\nError: Status code " +
                          str(response.getcode())+" returned by server.\n")

            except Exception as e:
                print(e)
