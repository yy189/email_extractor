from urllib.request import urlopen, Request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import socket
import smtplib
import dns.resolver
import csv
import multiprocessing

TIMEOUT = 120

in_path = "acceleprise.csv"
out_path = "acceleprise_result.csv"

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
        html = urlopen(req, timeout=20)
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


def extractEmails(allIntLinks, return_dict):
    for intLink in allIntLinks:
        req = Request(intLink, headers=headers)
        try:
            html = urlopen(req, timeout=20).read().decode("utf-8")
            regex = r"([a-zA-Z0-9_.+-]+@[a-pr-zA-PRZ0-9-]+\.[a-zA-Z0-9-.]+)"
            for email in re.findall(regex, html):
                email = email.lower()
                if email not in allEmails:
                    if not (email.endswith(('.', '.png', '.jpg', '.JPG', '.jpeg', '.gif', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.x', '.webm', '.webp', '.svg', "example.com", "email.com", "yourdomain.com", "yourself.com", "domain.com")) or "sentry" in email):
                        # if verify_email(email): # takes a long time
                            allEmails.add(email)
        except:
            pass
    return_dict[0] = "\n".join(list(allEmails))



with open(in_path, "r") as f:
    fieldnames = ['portfolio', 'website', 'year', 'summary']
    reader = csv.DictReader(f, fieldnames=fieldnames)
    next(reader)

    with open(out_path, "w") as f1:
        fieldnames1 = ['portfolio', 'website', 'year', 'emails', 'summary']
        writer = csv.DictWriter(f1, fieldnames=fieldnames1)
        writer.writeheader()

        idx = 1
        for row in reader:
            print(str(idx) + ". " + row['portfolio'])
            allIntLinks = set()
            allEmails = set()
            print(row['website'])

            if len(row['website']):
                allIntLinks.add(row['website'])
                getAllInternalLinks(row['website'])

                manager = multiprocessing.Manager()
                return_dict = manager.dict()
                return_dict[0] = ""
                p = multiprocessing.Process(target=extractEmails, args=(allIntLinks, return_dict))
                p.start()

                p.join(TIMEOUT)

                if p.is_alive():
                    print("Time out!")
                    p.terminate()

            emails = return_dict.values()[0]
            row['emails'] = emails
            row['portfolio'] = row['portfolio'].strip()
            writer.writerow(row)
            f1.flush()
            print(emails)
            idx += 1