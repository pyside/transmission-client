# Copyright (c) Alexander Borgerth 2010
# See LICENSE for details.
import operator
from piratebay.parser import SearchPageParser, UserPageParser
from piratebay import exceptions

class SearchMixIn(object):
    
    def _list_with_limits(self, pages, limit=None):
        """Return a list with at most `limit' elements."""
        if limit is not None:
            if len(pages) > limit:
                return pages[:limit]
        return pages

    def get_page_items(self):
        """Return a list of PageItem objects.

        Should be implemented by the class being mixed into.
        """
        raise NotImplementedError

    def all(self, order_by=None, reversed=True, limit=None):
        """Get a list of PageItem() objects.

        The result may be ordered, and limited by specifying the parameters.
        """
        items = self.get_page_items()
        if order_by is not None:
            items = sorted(items, key=operator.attrgetter(order_by), reverse=reversed)
        return self._list_with_limits(items, limit)

    def search(self, key, value, comparator=None, order_by=None, reversed=True, limit=None):
        """Search through all results, and those matching a certain criteria(using a `comparator' function), will be
        collected and returned in the form of a generator.
        """
        if comparator is None:
            comparator = operator.eq
        items = self.all(order_by=order_by, reversed=reversed, limit=limit)
        for item in items:
            if comparator(getattr(item, key), value):
                yield item

class PageItem(object):
    def __init__(self, dct):
        self.data = dct

    def __getattr__(self, attr):
        if attr in self.data.keys():
            return self.data[attr]
        raise AttributeError("'PageItem' object has no attribute '%s'" % attr)

    def __str__(self):
        item = "    %s => %s\n"
        string = "<PageItem\n"
        for key, value in self.data.iteritems():
            string += (item % (key, value))
        string += ">"
        return string
 
class BasePage(SearchMixIn):
    """Base class of all Page types."""
    parser_type = None

    def __init__(self, document, form_data=None):
        self.form_data = form_data
        self.document = document
        self.list_of_rows = None
        self.current_page = 0
        self.max_page = 0
        self._process_document()
    
    def get_page_items(self):
        return self.list_of_rows

    def get_current_page(self):
        """Return the current page you're visiting."""
        return self.current_page
    
    def get_number_of_pages(self):
        """Return maximum number of pages available for your search."""
        return self.max_page
    
    def _process_document(self):
        parser = self.parser_type(self.document)
        self.current_page, self.max_page, rows =\
            parser.run()
        self.list_of_rows = [PageItem(row) for row in rows if row != None]

class SearchPage(BasePage):
    """The Page class.
    
    A Page object is returned by each search on the piratebay website,
    it lets you easily handle all the data. Each item returned by either
    all() or search() is a list of dictionary objects, that have these
    keys:
        * name = Name of the torrent.
        * torrent-info-url = (Full) url to the torrent info page.
        * torrent-url = (Full) url to the torrent file.
        * magnet-url = (Full) url to the magnet file.
        * user = (Full) url to the user page(shows all releases by the user).
        * seeders = Amount of people seeding the torrent.
        * leechers = Amount of people leeching the torrent.
    
    So to print all torrent-urls followed by the uploader you could do this:
        >>> from piratebay.page import search_main
        >>> page = search_main("some search term")
        >>> for row in page.all():
        ...     print "%s => %s" % (row["torrent-url"], row["user"])
    """
    parser_type = SearchPageParser

class UserPage(BasePage):
    parser_type = UserPageParser

class PageCollection(SearchMixIn):
    """PageCollection
    
    Is a collection of Page()/UserPage() objects, so that one can do several searches on thepiratebay
    and combine them into one collection. Then one can search all results, from all the page searches done.
    And order them however one may want, and limit the results.
    """

    def __init__(self):
        self.pages = []

    def add_page(self, page):
        """Add a Page/UserPage() object to the collection."""
        if page not in self.pages:
            self.pages.append(page)
    
    def get_page_items(self):
        """Collect all PageItem() objects from all pages."""
        items = []
        for page in self.pages:
            items.extend(page.all())
        return items
