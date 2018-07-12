from urllib.request import urlopen, Request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import socket
import smtplib
import dns.resolver
import csv
import time
import os

in_path = "Y Combinator.csv"
out_path = "Y Combinator result.csv"

headers = {"User-Agent": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Trident/5.0)"}


def getinternalLinks(bsObj, includeUrl):
    includeUrl = urlparse(includeUrl).scheme + "://" + urlparse(includeUrl).netloc
    internalLinks = []

    for link in bsObj.findAll("a", href=re.compile("^(/|.*" + includeUrl + ")")):
        if link.attrs['href'] is not None:
            if link.attrs['href'].startswith("/"):
                internalLinks.append(includeUrl + link.attrs['href'])
            else:
                internalLinks.append(link.attrs['href'])
    return internalLinks


def getAllInternalLinks(siteUrl):
    req = Request(siteUrl, headers=headers)
    try:
        html = urlopen(req)
        domain = urlparse(siteUrl).scheme + "://" + urlparse(siteUrl).netloc
        bsObj = BeautifulSoup(html, "html.parser")
        internalLinks = getinternalLinks(bsObj, domain)

        for link in internalLinks:
            if link not in allIntLinks:
                allIntLinks.add(link)
                print(link)
    except:
        pass


def verify_email(email):
    records = dns.resolver.query(email.split('@')[-1], 'MX')
    mxRecord = records[0].exchange
    mxRecord = str(mxRecord)

    host = socket.gethostname()

    server = smtplib.SMTP()
    server.set_debuglevel(0)

    server.connect(mxRecord)
    server.helo(host)
    server.mail('me@domain.com')
    code, message = server.rcpt(str(email))
    server.quit()

    if code == 250:
        return True
    else:
        return False


def extractEmails(siteUrl):
    req = Request(siteUrl, headers=headers)
    try:
        html = urlopen(req).read().decode("utf-8")
        regex = r"([a-zA-Z0-9_.+-]+@[a-pr-zA-PRZ0-9-]+\.[a-zA-Z0-9-.]+)"
        for email in re.findall(regex, html):
            if email.lower() not in allEmails:
                if not email.endswith(('.', '.png', '.jpg', '.JPG', '.jpeg')):
                    # if verify_email(email): # takes a long time
                        allEmails.add(email.lower())
    except:
        pass

with open(in_path) as f:
    fieldnames = ['profolio', 'website', 'year', 'summary']
    reader = csv.DictReader(f, fieldnames=fieldnames)

    exists = False
    number_of_rows_to_skip = 1
    if os.path.isfile(out_path):
        exists = True
        length = len(list(csv.reader(open(out_path))))
        number_of_rows_to_skip = length if length > 1 else 1 # length + 1 ??? to skip the last row that might have taken too long

    with open(out_path, "a+") as f1:
        fieldnames1 = ['profolio', 'website', 'year', 'emails', 'summary']
        writer = csv.DictWriter(f1, fieldnames=fieldnames1)

        if not exists:
            writer.writeheader()

        print("number of rows to skip: " + str(number_of_rows_to_skip))
        for i in range(number_of_rows_to_skip):
            next(reader)

        idx = 1
        for row in reader:
            print(str(idx) + '. ' + time.strftime("%H:%M:%S", time.localtime()))
            allIntLinks = set()
            allEmails = set()
            print(row['website'])
            if len(row['website']):
                allIntLinks.add(row['website'])
                getAllInternalLinks(row['website'])

                for intLink in allIntLinks:
                    extractEmails(intLink)

                emails = "\n".join(list(allEmails))
                row['emails'] = emails
                row['profolio'] = row['profolio'].strip()
                writer.writerow(row)
                f1.flush()
                print(emails)
            idx+=1