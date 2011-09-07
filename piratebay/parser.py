# Copyright (c) Alexander Borgerth 2010
# See LICENSE for details.
import datetime
from urllib2 import unquote
from urlparse import urljoin
from piratebay import exceptions
from piratebay.constants import categories as cat

class BaseParser(object):
    """Base parser for all specific parsers.
    
    Every parser are to derive from this, so as to keep the
    interface the same for all parsing.
    """
    def run(self):
        raise NotImplementedError

class TorrentTableParser(BaseParser):
    """TorrentTableParser
    
    The TorrentTableParser is the base-class for parsing tables on the
    Search and User page.
    """
    _xpath_table = ".//div[@id='content']/div[@id='main-content']/table[@id='searchResult']"
    _xpath_amount_of_pages = ".//div[@align='center']"
    
    def __init__(self, doc):
        self.doc = doc
        self.rows = []
    
    def find_table(self):
        """Search for the result table on any page on piratebay.

        Raise TableNotFound to indicate error.
        """
        table = self.doc.xpath(self._xpath_table)
        if len(table) <= 0:
            raise exceptions.ElementNotFound("Unable to find table")
        return table[0]
    
    def get_table_rows(self):
        """Return table rows.

        Raise InvalidTable to indicate error.
        """
        table = self.find_table()
        if table.tag != 'table':
            raise exceptions.InvalidTable("Invalid table found")
        return [row for row in table.iterchildren() if row.tag == 'tr']
    
    def process_page_numbers(self):
        """Parse the index.
        
        Parses the index from the page, that'll say the number of the page
        we're currently visiting. And the number of pages available as far
        as the index is showing.
        
        *Returns*
            tuple with (current_page, number_of_pages)
        """
        element = self.doc.xpath(self._xpath_amount_of_pages)
        def find_last_link(links):
            links.reverse()
            for link in links:
                if len(link.getchildren()) == 0:
                    return link
        def find_current_page(links):
            if element.text and element.text.strip().isdigit():
                return int(element.text.strip())
            for link in links:
                text = link.tail
                if len(text.strip()) > 0:
                    return int(unquote(text))
        if len(element) != 1:
            raise exceptions.ElementNotFound("Correct element for page numbers not found")
        element = element[0]
        a_eles = element.findall('a')
        current_page = find_current_page(a_eles)
        if len(a_eles) <= 0:
            raise exceptions.ElementNotFound("Incorrect element found")
        
        num_pages = int(find_last_link(a_eles).text_content())
        return current_page, num_pages
    
    def process_datetime_string(self, string):
        """Process the datetime string from a torrent upload.
    
        *Returns*
            Tuple with (datetime, (size, unit))
        """
        def process_datetime(part):
            if part.startswith("Today"):
                h, m = part.split()[1].split(':')
                return datetime.datetime.now().replace(
                    hour=int(h), minute=int(m))
            elif part.startswith("Y-day"):
                h, m = part.split()[1].split(':')
                d = datetime.datetime.now()
                return d.replace(
                    hour=int(h), minute=int(m),
                    day=d.day-1
                )
            elif part.endswith("ago"):
                amount, unit = part.split()[:2]
                d = datetime.datetime.now()
                if unit == "mins":
                    d = d.replace(minute=d.minute - int(amount))
                return d
            else:
                d = datetime.datetime.now()
                if ':' in part:
                    current_date, current_time = part.split()
                    h, m = current_time.split(':')
                    month, day = current_date.split('-')
                    d = d.replace(hour=int(h), minute=int(m), month=int(month), day=int(day))
                else:
                    current_date, year = part.split()
                    month, day = current_date.split('-')
                    d = d.replace(year=int(year), month=int(month), day=int(day))
                return d
        def process_size(part):
            size, unit = part.split()[1:]
            return (float(size), unit)
        string = string.replace(u"\xa0", " ")
        results = [x.strip() for x in string.split(',')]
        date = process_datetime(' '.join(results[0].split()[1:]))
        size = process_size(results[1])
        return (date, size)
    
    def parse_row_columns(self, columns):
        """Parse the columns of a table row.
        
        *Returns*
            a dictionary with parsed data.
        """
        data = {}
        for ele in columns[0].iterchildren():
            if ele.tag == 'div' and ele.get('class') == 'detName':
                a = ele.find('a')
                data["torrent_info_url"] = urljoin(ele.base, a.get('href'))
                data["name"] = a.text_content()
            elif ele.tag == 'a':
                if ele.get('title') == "Download this torrent":
                    data["torrent_url"] = ele.get("href")
                elif ele.get('title') == "Download this torrent using magnet":
                    data["magnet_url"] = ele.get("href")
            elif ele.tag == 'font':
                a = ele.find('a')
                if a is None:
                    data['user'] = "Anonymous"
                else:
                    data['user'] = urljoin(ele.base, a.get('href'))
                data["uploaded_at"], data["size_of"] = self.process_datetime_string(ele.text_content())
        data['seeders'] = int(columns[1].text_content().strip())
        data['leechers'] = int(columns[2].text_content().strip())
        return data
    
    def run(self):
        """Run the parser.
        
        Call the subclass _process_row() to process each row of the table, then
        append all parsed row data into a list. That will be returned with the other
        data such as current page and number of pages.
                
        *Returns*
            tuple with, (current_page, num_pages, [dict_with_row_data, ...]).
        """
        rows = self.get_table_rows()
        row_data = []
        for row in rows:
            row_data.append(self.process_row(row))
        current_page, num_pages = self.process_page_numbers()
        return current_page, num_pages, row_data
    
    def process_row(self, row):
        """Should be implemented by the subclass."""
        raise NotImplementedError

class SearchPageParser(TorrentTableParser):
    """SearchPageParser
    
    Is the specific parser for the search page. We keep this one separate
    from the user page parsing, because they differ abit yet have a huge
    similar dataset.
    """
    def process_row(self, row):
        """Process one row of the table."""
        columns = row.getchildren()[1:]
        if len(columns) != 3:
            raise exceptions.InvalidRow("Row isn't valid or it doesn't contain the columns it should.")
        return self.parse_row_columns(columns)

class UserPageParser(TorrentTableParser):
    """UserPageParser
    
    Is the specific parser for the user page.
    """
    _xpath_amount_of_pages = ".//tr/td[@colspan='9']"
    def process_row(self, row):
        """Process one row of the table."""
        columns = row.getchildren()[1:]
        if len(columns) == 3:
            return self.parse_row_columns(columns)

class TorrentInfoParser(BaseParser):
    """TorrentInfoParser
    
    Parsers the torrent-info-url, which displays torrent information, comments
    and more.
    TODO: Add parsing for the comments.
    """
    _xpath_details_frame = ".//div[@id='content']/div[@id='main-content']/div/div[@id='detailsouterframe']/div[@id='detailsframe']"
    _xpath_details_title = "./div[@id='title']"
    _xpath_details_start = "./div[@id='details']"
    _xpath_details_dl1 = "./dl[@class='col1']"
    _xpath_details_dl2 = "./dl[@class='col2']"
    _xpath_details_nfo = "./div[@class='nfo']/pre"
    
    def __init__(self, doc):
        self.doc = doc
    
    def run(self):
        """Run the parser."""
        result = {}
        result.update(self.parse_title())
        result.update(self.parse_description())
        result.update(self.parse_definition_list())
        return result
    
    def locate_element_with_xpath(self, xpath_list, err_msg="Element not found in xpath expression!"):
        """Locate an element, from a list of xpath expressions.
        
        Raise exceptions.ElementNotFound with err_msg if the xpath expression wasn't found.
        """
        ele = self.doc
        for xpath in xpath_list:
            ele = ele.xpath(xpath)
            if len(ele) <= 0:
                raise exceptions.ElementNotFound(err_msg)
            ele = ele[0]
        return ele

    def parse_title(self):
        """Parse the title of the torrent page.
        
        *Returns*
            a dictionary with a key with name 'name'.
        """
        title = self.locate_element_with_xpath([
            self._xpath_details_frame,
            self._xpath_details_title
        ], "Div element for the title not found, wrong page?")
        return dict(name = title.text.strip())

    def parse_description(self):
        """Parse the description of the torrent page.
        
        *Returns*
            a dictionary with a key named 'description'.
        """
        nfo = self.locate_element_with_xpath([
            self._xpath_details_frame,
            self._xpath_details_start,
            self._xpath_details_nfo
        ], "Div element for the description not found, wrong page?")
        return dict(description = nfo.text_content().strip())

    def parse_definition_list(self):
        """Parse the definition list that is inside a div on the page.
        
        The definition list contains information such as:
            * categor(y/ies).
            * number of files.
            * size of the torrent.
            * tags.
            * rating (how good is the torrent?)
            * uploaded at date.
            * who uploaded it.
            * is the uploader a trusted user?
            * seeders & leechers statistics.
        *Returns*
            a dictionary with the possible keys:
                * category
                * files
                * size_of
                * tags
                * rating
                * uploaded_at
                * user
                * trusted
                * seeders
                * leechers
        """
        def parse_dl(dl):
            data = {}
            for child in dl.iterchildren(tag="dt"):
                label = child.text.strip().lower().replace(":", "")
                dd = child.getnext()
                if label == "type":
                    a_link = dd.find("a")
                    if a_link is not None:
                        category = a_link.text.lower().split(">")
                        if len(category) > 1:
                            data["category"] = cat[category[0].strip()][category[1].strip()]
                        else:
                            data["category"] = cat[category[0].strip()]
                elif label == "files":
                    a_link = dd.find("a")
                    if a_link is not None:
                        data[label] = int(a_link.text)
                elif label == "size":
                    size, unit = dd.text_content().strip().replace(u"\xa0", " ").split(" ")[:2]
                    size = float(size)
                    data["size_of"] = (size, unit)
                elif label.startswith("tag"):
                    a_links = dd.findall("a")
                    tags = []
                    for link in a_links:
                        tags.append(link.text_content().strip())
                    data["tags"] = tags
                elif label == "quality":
                    quality_text = dd.text.strip()
                    for skip in "()/":
                        quality_text = quality_text.replace(skip, "")
                    quality_text = [int(num) for num in quality_text.split()]
                    data["rating"] = tuple(quality_text)
                elif label == "uploaded":
                    date = datetime.datetime.strptime(dd.text.strip(), "%Y-%m-%d %H:%M:%S %Z")
                    data["uploaded_at"] = date
                elif label == "by":
                    a_link = dd.find("a")
                    if a_link is not None:
                        data["user"] = a_link.text.strip()
                    img_link = dd.find("img")
                    if img_link is not None and img_link.get("alt") == "Trusted":
                        data["trusted"] = True
                    else:
                        data["trusted"] = False
                elif label == "seeders":
                    data["seeders"] = int(dd.text.strip())
                elif label == "leechers":
                    data["leechers"] = int(dd.text.strip())
            return data     
        dl1 = self.locate_element_with_xpath([
            self._xpath_details_frame,
            self._xpath_details_start,
            self._xpath_details_dl1
        ], "Div element for the definition list not found, wrong page?")
        data = parse_dl(dl1)
        try:
            dl2 = self.locate_element_with_xpath([
                self._xpath_details_frame,
                self._xpath_details_start,
                self._xpath_details_dl2
            ])
        except exceptions.ElementNotFound, err:
            pass
        else:
            data.update(parse_dl(dl2))
        return data
                    