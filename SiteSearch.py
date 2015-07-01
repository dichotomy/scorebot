#!/bin/python

__author__ = 'DigitalFlame'

"""
    SiteSearch.py
    Written by DigitalFlame for the Scorebot Project

    Scans through a site looking for <a href=""> (links) internal to the site.
    Pages that are scaned are added to the 'pages' var.  Pages that have failed or are unreachable are in 'failed_pages'

    A page is considered 'unreachable' if any of the following conditions occur:
        - A HTTP Response that is NOT 200 is received
        - The page URL is located on a seperate domain or subdomain that the sitebase
        - The page URL is higher up in the URL structure that the sitebase
        - The page is not a text or html based file

    The search is threaded, so you can come back to check when it is done once starting the scan.
    The Debug flag will just output all actions that the search is doing to standard output.

    Usage:
        a = SiteSearch(site='URL/IP TO SITE', debug=(True|False))
        a.start()

        #// Use one of the above {
        While a.isAlive():
            None
        #// Or
        While Not a.isDone():
            None
        }

        print("Results %s" % a.pages)

"""

import threading
import urllib.request


from bs4 import BeautifulSoup


class SiteSearch(threading.Thread):
    """
        Main Constructor
    """
    def __init__(self, site, debug=False):
        threading.Thread.__init__(self)
        self.pages = []
        self.debug = debug
        self.__tosearch = []
        self.failed_pages = []
        self.url = site.rstrip("/")
        self.__tosearch.append(self.url)
    """
        Thread main hook
    """
    def run(self):
        if self.debug:
            print("[DEBUG SiteSearch] (%s) Started Search for '%s'" % (self.url, self.url))
        # Simple loop until job is done
        while len(self.__tosearch) > 0:
            # Remove first site from stack
            a = self.__tosearch.pop()
            # Try to get links
            b = self.__getpage(a)
            if b:
                # We got links
                # It through links
                for c in b:
                    # Strip trailing slash
                    d = c.get("href")
                    if d:
                        # Sanity check: nul value
                        d = d.rstrip("/")
                        if not self.__shouldadd(d):
                            # Don't add out of scope
                            if self.debug:
                                print("[DEBUG SiteSearch] (%s) Page '%s' is unreachable (out of scope)" % (self.url, d))
                            self.failed_pages.append(d)
                        else:
                            if not d.startswith(self.url):
                                # Sanity check: No starting '/'
                                if len(d) > 1 and d[0] != '/':
                                    d = self.url + '/' + d
                                else:
                                    d = self.url + d
                            if not self.__isalreadysearched(d):
                                # Add to pages to search
                                if self.debug:
                                    print("[DEBUG SiteSearch] (%s) Added page '%s'" % (self.url, d))
                                self.__tosearch.append(d)
            print("[DEBUG SiteSearch] (%s) %d pages searched, %d left to search" %
                  (self.url, len(self.pages), len(self.__tosearch)))
    """
        Check for Status
        Returns True/False on status of search
    """
    def isDone(self):
        return len(self.__tosearch) == 0
    """
        Page Getter
        Will return list of links on page or None 'nul' depending on page state
    """
    def __getpage(self, pageurl):
        # Sanity check: Empty string (I hope this dosen't happen)
        if len(pageurl) <= 0:
            return None
        # Check page first
        if not self.__shouldadd(pageurl):
            if self.debug:
                print("[DEBUG SiteSearch] (%s) Page '%s' is unreachable (out of scope)" % (self.url, pageurl))
            self.failed_pages.append(pageurl)
            # We got nothing
            return None
        else:
            # Lets do some simple page fixing (Fixes Relative Paths)
            # Creating a var to prevent modifying param
            if not pageurl.startswith(self.url):
                # Sanity check: No starting '/'
                if len(pageurl) > 1 and pageurl[0] != '/':
                    a = self.url + '/' + pageurl
                else:
                    a = self.url + pageurl
            else:
                a = pageurl
            if self.debug:
                print("[DEBUG SiteSearch] (%s) Opening page '%s'" % (self.url, a))
            # Lets open the page now that we have a proper URL
            try:
                # use urllib to read page contents
                with urllib.request.urlopen(a) as response:
                    # Check for non text files
                    if not ("text" in response.info()['Content-Type']):
                        if self.debug:
                            print("[DEBUG SiteSearch] (%s) Page '%s' is unreachable (no text file)" %
                                  (self.url, pageurl))
                        return None
                    b = response.read()
                # Add to finished pages as it passed
                self.pages.append(a)
                # Convert page to BeautifulSoup page
                c = BeautifulSoup(b)
                # return all the a's
                return c.find_all("a")
            except UnicodeError:
                self.failed_pages.append(a)
                if self.debug:
                    print("[DEBUG SiteSearch] (%s) Page '%s' is unreachable (exception occurred [encode])" %
                          (self.url, pageurl))
                return None
            except urllib.error.HTTPError:
                self.failed_pages.append(a)
                if self.debug:
                    print("[DEBUG SiteSearch] (%s) Page '%s' is unreachable (exception occurred [http])" %
                          (self.url, pageurl))
                return None
    """
        Page Verifier
        Determines page out of reach status
    """
    def __shouldadd(self, siteurl):
        if (siteurl.startswith("http://") or siteurl.startswith("https://") or siteurl.startswith("mailto:")) \
                and not siteurl.startswith(self.url):
            # Catch Sites outside our URL zone, Email links & Sites not in our search domain
            return False
        return True
    """
        Page Status Check
        Determins if page has been index already
    """
    def __isalreadysearched(self, siteurl):
        return siteurl in self.pages or siteurl in self.__tosearch or siteurl in self.failed_pages
if __name__ == "__main__":
  ss = SiteSearch("http://cyberwildcats.net/ctf/", True)
  ss.start()
  while ss.isAlive():
      var = None
  print("Done %s" % ss.pages)
  print("Failed %s" % ss.failed_pages)
