# Copyright (c) Alexander Borgerth 2010
# See LICENSE for details.
import time
import urllib2
import socket
from lxml import html
from piratebay.utils import open_url_with_request
from piratebay.page import SearchPage, UserPage, PageCollection, PageItem
from piratebay.constants import search_page_url, user_page_url, order
from piratebay.parser import TorrentInfoParser

def search_main(term, category=0, page=0, order_by=order["seeders"], timeout=None):
    """Search the main piratebay website for the term 'term'.
    
    *Arguments*
        term = search with term.
        category = category from piratebay.categories.categories dict.
        page = the number of the search page to visit.
        order_by = the order of which piratebay should order it's results.(default being piratebay.page.order["seeders"])
    *Returns*
        a SearchPage() object.
    """
    if page < 0:
        page = 0
    form_data = { "q": term, "category": category,
                "page": page, "orderby": order_by }
    url = open_url_with_request(search_page_url, form_data=form_data, timeout=timeout)
    doc = html.parse(url).getroot()
    return SearchPage(doc, form_data=form_data)

def search_user(user, page=0, order_by=order["seeders"], timeout=None):
    """Search the entries on a users page on piratebay.
    
    It is not an actual search, it basically just queries the users page
    to get all the releases from that user. Then order it by seeders as default,
    but can be changed with the order_by argument.
    """
    url = open_url_with_request(user_page_url % (user, page, order_by), timeout=timeout)
    doc = html.parse(url).getroot()
    return UserPage(doc)

def search_main_pages(term, pages, category=0, order_by=order["seeders"], timeout=None, wait_time=3, callback=None):
    """Search the main piratebay website for the term 'term'.
    
    Search all the page numbers in `pages', and wait for `wait_time' seconds between each request. If callback is
    specified then call the callback with the page object. If timeout is specified, time out a request after `timeout'
    seconds.
    """
    collection = PageCollection()
    for page_number in pages:
        try:
            page = search_main(term, page=page_number, category=category, order_by=order_by, timeout=timeout)
        except socket.timeout, err:
            continue
        except urllib2.URLError, err:
            continue
        if callback is not None:
            callback(page)
        collection.add_page(page)
        # Don't sleep if we're at the last page
        if page_number != pages[-1]:
            time.sleep(wait_time)
    return collection

def query_torrent_info_page(url, timeout=None):
    """Query a torrent info page.
    
    Queries a torrent info page, returns a PageItem object with the result. It
    has for example the description of the torrent, if the uploader is a trusted user
    and alot more.
    """
    data = open_url_with_request(url, timeout)
    document = html.parse(data).getroot()
    parser = TorrentInfoParser(document)
    return PageItem(parser.run())