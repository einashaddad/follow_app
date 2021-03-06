#!/usr/bin/env python
# This Python file uses the following encoding: utf-8

import requests
import pyquery as pq
import sys
import getpass

class Error(Exception):
    def __init__(self, code):
        self.code = code
    def __str__(self):
        return repr(self.code)

def scrape_hs(hs_email, hs_password, host):
    """
    Returns a response object after creating an authenticated session with 
    hackerschool 
    """
    session = requests.session()

    #retrieving the csrf-token from the html
    page = pq.PyQuery(url = host+'/login')
    meta_content = page('meta')

    for m in pq.PyQuery(meta_content):
        if pq.PyQuery(m).attr('name') == 'csrf-token':
            csrf_token = pq.PyQuery(m).attr('content')

    payload = {
        'authenticity_token': csrf_token,
        'email': hs_email,
        'password': hs_password,
        'commit': 'Log In',
        'utf8' : u'✓'
    }

    request = session.post(host+'/sessions', data=payload, verify=False)

    resp = session.get(host+'/private') 

    return resp

def extract_githubs(resp):
    """
    Returns a dictionary of people to follow with their github usernames as values
    """
    content = resp.text
    content = pq.PyQuery(content)
    people = content('#batch7 .person')
    if not people:
        raise Error("Incorrect hacker-school username and/or password") 
    people_to_follow = {}

    for person in people:
        person = pq.PyQuery(person)
        person_class = person('div.name')
        person_endpoint = person_class('a').attr('href')

        icon_links = person('div.icon-links')
        first_link = icon_links('a').attr('href')
        

        if 'github' in first_link:
            just_user = first_link[18:]
            people_to_follow[person_endpoint] = just_user
    
    return people_to_follow


def follow_users(gh_username, gh_password, people_to_follow):
    """
    Follows the users given in the dictionary by sending a put request to the github API 
    """
    url = "https://api.github.com/user/following" 

    s = requests.Session()
    s.auth = gh_username, gh_password
    followed, not_followed = [], []

    for user_to_follow in people_to_follow.values():
        if user_to_follow != '/'+gh_username: # we do not want to follow ourselves
            
            is_following = s.get(url+user_to_follow)

            if is_following.status_code != 204: #if not following user

                r = s.put(url+user_to_follow)

                if r.status_code == 204:
                    followed.append(user_to_follow)
                elif r.status_code == 401:
                    raise Error("Incorrect GitHub username and/or password") 
                else:  # page on github is not found
                    not_followed.append(user_to_follow)
            
            else:
                not_followed.append(user_to_follow)
    return followed, not_followed

def render(hs_email, hs_password, gh_username, gh_password):
    host = 'https://www.hackerschool.com'
    response = scrape_hs(hs_email, hs_password, host)
    try:
        people_to_follow = extract_githubs(response)
    except Error as e:
        return e.code
    try:
        return follow_users(gh_username, gh_password, people_to_follow)
    except Error as e:
        return e.code

if __name__ == '__main__':
    host = 'https://www.hackerschool.com'

    hs_email =  raw_input("Hacker-School username: ")
    hs_password = getpass.getpass(prompt='Hacker-School password: ')
    gh_username = raw_input("GitHub username: ")
    gh_password = getpass.getpass(prompt='GitHub password: ')
    
    response = scrape_hs(hs_email, hs_password, host)
    try:
        people_to_follow = extract_githubs(response)
    except Error as e:
        print e.code
        sys.exit()
    try:
        follow_users(gh_username, gh_password, people_to_follow)
    except Error as e:
        print e.code
        sys.exit()
