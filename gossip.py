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

EXPECTED_FROM = '"Benjamin F. Kuo" <ben@socaltech.com>'
EXPECTED_SUBJ = 'socaltech.com TechNews'

def parse_email(f,dump=False):
    print("parse_email")
    p = email.message_from_file(f, policy=email.policy.SMTPUTF8)

    to, frm, subj = p.get("To"), p.get("From"), p.get("Subject")

    if frm == EXPECTED_FROM and subj.startswith(EXPECTED_SUBJ):
        pass
    else:
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
#    href = soup.find('li').find('a', href=re.compile("https://labusinessjournal.*")).attrs["href"]
#    print("fetching ", href)
#    page = requests.get(href)
#    soup = bs4.BeautifulSoup(page.content, 'html.parser')
#    p = soup.find('div', 'article')('p')
    a = soup.findAll(text="Headlines")[0].parent.parent.findNext("ul").findAll('a')[:3]
    items = []
    for i in a:
        hl = i.text
        art = soup.find('a',{'name':i.attrs['href'][1:]}) # follow <a href="#xxxx"> to <a name="xxxx">
        more = art.find_next_sibling('a', text='More...')
        href = more.attrs['href']
        snippet = more.previous_sibling
        items.append({'hl':hl, 'href':href, 'snippet':snippet})
    return items

def process_items(items, handler):
    for i in items:
        handler("<%(href)s|%(hl)s> %(snippet)s" % i)


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

