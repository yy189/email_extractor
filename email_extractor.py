from urllib.request import urlopen, Request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import socket
import smtplib
import dns.resolver

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


allIntLinks = set()
allEmails = set()


def getAllInternalLinks(siteUrl):
    req = Request(siteUrl, headers=headers)
    html = urlopen(req)
    domain = urlparse(siteUrl).scheme + "://" + urlparse(siteUrl).netloc
    bsObj = BeautifulSoup(html, "html.parser")
    internalLinks = getinternalLinks(bsObj, domain)

    for link in internalLinks:
        if link not in allIntLinks:
            allIntLinks.add(link)
            print(link)


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
            if email not in allEmails:
                if verify_email(email):
                    allEmails.add(email)
    except:
        pass





siteUrl = "https://onupkeep.com/"
allIntLinks.add(siteUrl)
getAllInternalLinks(siteUrl)

for intLink in allIntLinks:
    extractEmails(intLink)

emails = "\n".join(list(allEmails))
print(emails)