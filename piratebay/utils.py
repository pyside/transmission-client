# Copyright (c) Alexander Borgerth 2010
# See LICENSE for details.
from urllib2 import Request, urlopen
from urllib import urlencode
from os import path, getcwd
from random import choice

class RequestObject(object):
    user_agents = (
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'
    )

    def __init__(self):
        self.last_user_agent = None

    def get_random_user_agent(self):
        """Create a random user-agent string."""
        agent = None
        while True:
            agent = choice(self.user_agents)
            if agent == self.last_user_agent:
                continue
            self.last_user_agent = agent
            break
        return agent
    
    def __call__(self, url, form_data=None, get_request=True):
        """Create an urllib2.Request object.
        
        A smart method, creates a GET request if get_request is True
        otherwise a POST. If form_data isn't None, pass it along with
        the request.
        """
        header = { 'User-agent': self.get_random_user_agent() }
        if form_data is not None:
            if get_request:
                return Request( url=url+urlencode(form_data),
                                headers=header )
            return Request( url=url,
                            data=urlencode(form_data),
                            headers=header )
        return Request( url=url,
                        headers=header )
create_request_object = RequestObject()

def open_url_with_request(url, form_data=None, get_request=True, timeout=None):
    """Open an url with our own special request object.
    
    If timeout is specified, timeout after x amount of seconds.
    """
    if timeout is not None:
        return urlopen(create_request_object(url, form_data=form_data, get_request=get_request), timeout=timeout)
    return urlopen(create_request_object(url, form_data=form_data, get_request=get_request))

def download_file(url, location=getcwd()):
    """Download specified file from the web.
    
    If no location is given or '.' is given as location, use current dir as path.
    """
    if location == '.':
        location = getcwd()
    remote_file = urlopen(url)
    local_file = path.join(location, path.split(url)[-1])
    with open(local_file, "w") as f:
        f.write(remote_file.read())