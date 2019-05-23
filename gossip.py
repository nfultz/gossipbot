#!/usr/bin/python3
# coding: utf-8
import boto3
import bs4
import email, email.policy
import os
import requests

INCOMING = 'neal.news.testing'
SLACK_WEBHOOK = os.environ["SLACK_WEBHOOK"]

def parse_email(f,dump=False):
    print("parse_email")
    p = email.message_from_file(f, policy=email.policy.SMTPUTF8)

    frm, subj = p.get("From"), p.get("Subject")
        
    e = p.get_body("html")
    html = e.get_payload(decode=True)

    if dump:
        with open('em.html', 'wb') as f:
            f.write(html)

    return bs4.BeautifulSoup(html, 'html.parser'), d


def lambda_handler(event, context):
    ses =  event['Records'][0]['ses'];
    print(f"handling {ses['mail']}")
    id =  ses['mail']['messageId']
    print(f"handling {id}")

    f = fetch_s3("alerts/"+id)
    soup = parse_email(f)
    items = extract_items(soup)
    process_items(items, post_slack)

def extract_items(soup):
    href = soup.find('span', string=re.compile("Silicon Beach.*:")).parent.attrs["href"]
    page = requests.get(href)
    soup = bs4.BeautifulSoup(page.content, 'html.parser')
    p = soup.find('div', 'article')('p')
    return p

def process_items(items, handler):
    link = None
    for elem in items:
        a = elem.find('a')
        if a:
            link = '<%s|%s>' % (a.attrs['href'], a.string)
        elif link:
            post_slack(link, elem.string)
            link = None


def post_slack(*args):
    txt = " ".join(args)
    print(txt)
    requests.post(SLACK_WEBHOOK, json={"text": txt})

if __name__ == '__main__' :
    import sys
    with open(sys.argv[1]) as f:
        soup = parse_email(f, True)
    items = extract_items(soup)
    process_items(items, post_slack)

