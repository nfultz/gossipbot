#!/usr/bin/python3
# coding: utf-8
import boto3
import bs4
import email, email.policy
import io
import os
import re
import requests

INCOMING = 'neal.news.testing'
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK")

EXPECTED_FROM = "Los Angeles Business Journal <newsletter@news.labusinessjournal.com>"
EXPECTED_SUBJ = 'Silicon Beach Report'

def parse_email(f,dump=False):
    print("parse_email")
    p = email.message_from_file(f, policy=email.policy.SMTPUTF8)

    frm, subj = p.get("From"), p.get("Subject")

    if frm != EXPECTED_FROM or not subj.startswith(EXPECTED_SUBJ):
        return None

        
    e = p.get_body("html")
    html = e.get_payload(decode=True)

    if dump:
        with open('em.html', 'wb') as f:
            f.write(html)

    return bs4.BeautifulSoup(html, 'html.parser')

def fetch_s3(id):
    print("fetch_s3")
    client = boto3.client('s3')
    obj = client.get_object(Bucket=INCOMING, Key=id)
    f = io.StringIO(obj['Body'].read().decode('utf-8'))
    return f

def lambda_handler(event, context):
    ses =  event['Records'][0]['ses'];
    print(f"handling {ses['mail']}")
    id =  ses['mail']['messageId']
    print(f"handling {id}")

    f = fetch_s3("silliconbeach/"+id)
    soup = parse_email(f)
    if soup is None:
        print("did not pass header checks?")
        return
    items = extract_items(soup)
    process_items(items, post_slack)

def extract_items(soup):
    href = soup.find('li').find('a', href=re.compile("https://labusinessjournal.*")).attrs["href"]
    print("fetching ", href)
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
            if elem.text:
                post_slack(link, elem.text)
            link = None


def post_slack(*args):
    txt = " ".join(args)
    print(txt)
    if SLACK_WEBHOOK:
        requests.post(SLACK_WEBHOOK, json={"text": txt})

if __name__ == '__main__' :
    import sys
    with open(sys.argv[1]) as f:
        soup = parse_email(f, True)
    if soup is not None:
        items = extract_items(soup)
        process_items(items, post_slack)

