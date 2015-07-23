#!/usr/bin/python

__author__ = 'iDigitalFlame'

"""
    SiteSearch.py
    Written by iDigitalFlame for the Scorebot Project

    Scans through a site looking for <a href=""> (links) internal to the site.
    Pages that are sccaned are added to the 'pages' var.  Pages that have failed or are unreachable are in 'failed'

    A page is considered 'unreachable' if any of the following conditions occur:
        - A HTTP Response that is NOT 200 is received
        - The page URL is located on a seperate domain or subdomain that the sitebase
        - The page URL is higher up in the URL structure that the sitebase
        - The page is not a text or html based file

    The search is threaded, so you can come back to check when it is done once starting the scan.
    The Debug flag will just output all actions that the search is doing to standard output.

    SiteSeach can also loginto web pages for ultimate searching:
        Just provide the URL to the login page (POST assumed),
        The login username and password
        and the text fields (inputs) that are used to login (the names)

    Paramaters:
        siteurl= (Base Search IP/Name)
        loginpage= (Default:None; The URL/URI to the login page (full path not needed))
        username= (Default:None; The username to login as)
        usernamefm= (Default:None; The input name of the username textbox)
        password= (Default:None; The password to use to login)
        passwordfm= (Default:None; The input name of the password textbox)
        debug= (Default:False; Shows Debug/Verbose messages on the console)
        forms= (Default:True; Searches and captures form paths/verbs/inputs with urls)
        timeout= (Default:6; The Cnnection and read timeouts used by Requests)
        keywords= (Default:10; The amount of keywords to gather)
        maxpages= (Default:0; The max amount of pages to gather (Login page does not count). 0 is no limit)

    Notes:
        maxpages will only stop the scan if the count of scanned pages equals this number.
        Pages with a smaller number will stop when they are done.  Form actions count aganist this value.

    Example with login:
        Scan and search a Orange HRM site with login. (Credentials in this example are admin/chiapet1)

        SiteSearch("<ip/hostname>", loginpage="/symfony/web/index.php/auth/validateCredentials", username="admin",
                    usernamefm="txtUsername", password="chiapet1", passwordfm="txtPassword")

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


    The script can also be ran to append searched entries to a CTF json file.
    Using this syntax

    python SiteSearch.py <jsonfile.json>
    -or-
    SiteSearch.py <jsonfile.json>

    Replace <jsonfile.json> with the full or absolute path to your file.
    The contents will be written in the same file and the original will be backed up and named <jsonfile.json>.bak

"""


import re
import sys
import DNS
import json
import random
import requests
import threading


from bs4 import BeautifulSoup

"""
    SSite
    Object that represents a Site (URLS/Forms and all)
"""


class SSite:
    def __init__(self, url, size):
        self.url = url
        self.form = []
        self.text = []
        self.size = size
    """
        json
        Convert this object to json
    """
    def json(self):
        ret = dict()
        ret["url"] = self.url
        ret["size"] = self.size
        if len(self.text) > 0:
            ret["keywords"] = self.text
        if len(self.form) > 0:
            arr = []
            for fv in self.form:
                arr.append(fv.json())
            ret["form"] = arr
        return ret

"""
    SForm
    Object that represents a form object on a page
"""


class SForm:
    def __init__(self, url, verb):
        self.url = url
        self.verb = verb
        self.args = dict()
    """
        json
        Convert this object to json
    """
    def json(self):
        ret = dict()
        ret["url"] = self.url
        ret["verb"] = self.verb
        if len(self.args) > 0:
            ret["params"] = self.args
        return ret

"""
    SiteSearch
    Thread based site indexing/searching
    Read notes above for more info
"""


class SiteSearch(threading.Thread):
    def __init__(self, siteurl, dns=None, loginpage=None, username=None, usernamefm=None,
                 password=None, passwordfm=None, debug=False, forms=True, timeout=6, keywords=10, maxpages=0):
        threading.Thread.__init__(self)
        if not siteurl.startswith("http"):
            raise Exception("Site URL is badly formatted!")
        self.__dns = dns
        self.__search = []
        self.__failed = []
        self.pages = dict()
        self.__ipaddr = None
        self.__debug = debug
        self.__forms = forms
        self.__basehost = None
        self.baseurl = siteurl.rstrip("/")
        self.__sessiond = None
        self.__timeout = timeout
        self.__loginparams = None
        self.__keywords = keywords
        self.__maxpages = maxpages
        self.__loginpage = loginpage
        self.__loginusernamefm = usernamefm
        self.__loginpasswordfm = passwordfm
        self.__search.append(self.baseurl)
        # Combine fields into a dictionary to make it easier to deploy
        if username and usernamefm and password and passwordfm and loginpage:
            self.__loginparams = dict()
            self.__loginparams[usernamefm] = username
            self.__loginparams[passwordfm] = password
        if self.__dns:
            dnshn = self.baseurl
            if "http" in dnshn:
                dnshn = dnshn.replace("https:","").replace("http:","").replace("//", "")
                if "/" in dnshn:
                    dnsind = dnshn.find("/")
                    dnshn = dnshn[:dnsind]
            if self.__debug:
                print("Search[%s] Using dns server '%s' to find ip address for '%s'" %
                      (self.baseurl, self.__dns, dnshn))
            self.__basehost = dnshn
            self.__ipaddr = dnslookup(dnshn, self.__dns)
            if self.__debug:
                print("Search[%s] Found IP '%s' for '%s'" %
                      (self.baseurl, self.__ipaddr, dnshn))

    """
        run
        Running method for while loop to scan URLs
    """
    def run(self):
        if self.__debug:
            print("Search[%s] Starting up." % self.baseurl)
        # Check for login if provided
        if self.__loginparams and self.__loginpage:
            if self.__debug:
                print("Search[%s] Login page present, attempting to login." % self.baseurl)
            self.__loginintopage()
        # Loop while we have things to search
        while len(self.__search) > 0 and (self.__maxpages == 0 or len(self.pages) < self.__maxpages):
            if self.__debug:
                print("Pages[%s] %d is max %d pages got!" %(self.baseurl, self.__maxpages, len(self.pages)))
            searchpage = self.__search.pop()
            if self.__debug:
                print("Search[%s] Popped out page '%s', '%d' left." % (self.baseurl, searchpage, len(self.__search)))
            # Check URL to make sure it is correct
            searchpage = self.__checkpageurl(searchpage)
            # If the URL has not been searched, poll the page
            if searchpage and not self.__isscanned(searchpage):
                if self.__debug:
                    print("Search[%s] Page '%s' is ok to search! running.." % (self.baseurl, searchpage))
                self.__pollpage(searchpage)
    """
        json
        Converts the captured data into JSON format
    """
    def json(self):
        ret = dict()
        if self.__loginparams:
            ret["loginpage"] = self.__loginpage
            ret["usernameform"] = self.__loginusernamefm
            ret["passwordform"] = self.__loginpasswordfm
            ret["username"] = self.__loginparams[self.__loginusernamefm]
            ret["password"] = self.__loginparams[self.__loginpasswordfm]
        retarr = []
        for page in self.pages.values():
            retarr.append(page.json())
        ret["pages"] = retarr
        return ret
    """
        logintopage
        Will try to log into a web page if the credentials are provided
    """
    def __loginintopage(self):
        # Check login url
        lurl = self.__checkpageurl(self.__loginpage)
        if self.__debug:
            print("Search[%s] Trying login page '%s' with creds provided." % (self.baseurl, lurl))
        # Do login (or try to)
        if self.__ipaddr:
            lurl = lurl.replace(self.__basehost, self.__ipaddr)
        try:
            loginpage = requests.post(lurl, data=self.__loginparams, timeout=self.__timeout)
        # Timeout
        except requests.exceptions.ReadTimeout:
            if self.__ipaddr:
                lurl = lurl.replace(self.__ipaddr, self.__basehost)
            if self.__debug:
                print("Search[%s] [ERROR] Page '%s' failed to download (time out)!." % (self.baseurl, lurl))
            self.__failed.append(lurl)
            return
        # Failure
        except requests.exceptions.ConnectionError:
            if self.__ipaddr:
                lurl = lurl.replace(self.__ipaddr, self.__basehost)
            if self.__debug:
                print("Search[%s] [ERROR] Page '%s' failed to download (refused)!." % (self.baseurl, lurl))
            self.__failed.append(lurl)
            return
        if self.__ipaddr:
            lurl = lurl.replace(self.__ipaddr, self.__basehost)
        # Did teh request work?
        if loginpage and loginpage.request.headers:
            if self.__debug:
                cookie = "None"
                if "Cookie" in loginpage.request.headers:
                    cookie = loginpage.request.headers["Cookie"]
                print("Search[%s] Login went through, cookie '%s' saved." % (self.baseurl, cookie))
            # Did we get a 200?
            if loginpage.status_code != 200:
                return
            # We only want text based pages
            if not ("text" in loginpage.headers['content-type']):
                return
            # Set cookie for subsequent page requests
            self.__sessiond = loginpage.request.headers
            # create page object (check if form one exists first)
            pageobject = None
            if self.__debug:
                print("Search[%s] Page '%s' passed.." % (self.baseurl, lurl))
            # Does page exist?
            if lurl in self.pages:
                self.pages[lurl].size = len(loginpage.text)
                # Update the current one if so
                pageobject = self.pages[lurl]
            else:
                # If not create a new reference
                pageobject = SSite(lurl, len(loginpage.text))
                self.pages[lurl] = pageobject
            # Create bs4 reference to look to objects
            bs4pagedata = BeautifulSoup(loginpage.text)
            # Send to be scanned
            self.__scanpage(bs4pagedata, pageobject)
            if self.__forms:
                # If forms are enabled, look for them
                self.__checkpage(bs4pagedata, pageobject)
    """
        pollpage
        Downloads a page and verifies it
    """
    def __pollpage(self, url):
        # assuming that page has been checked first (no dupes)
        # check the url
        geturl = self.__checkpageurl(url)
        if self.__debug:
            print("Search[%s] Polling page '%s'." % (self.baseurl, geturl))
        # Out of scope
        if not geturl:
            if self.__debug:
                print("Search[%s] [ERROR] Page '%s' failed scope test." % (self.baseurl, geturl))
            self.__failed.append(geturl)
            return
        if self.__ipaddr:
            geturl = geturl.replace(self.__basehost, self.__ipaddr)
        # Try to get the page (using login cookie also)
        try:
            pagedata = requests.get(geturl, headers=self.__sessiond, timeout=self.__timeout)
        # Timeout
        except requests.exceptions.ReadTimeout:
            if self.__ipaddr:
                geturl = geturl.replace(self.__ipaddr, self.__basehost)
            if self.__debug:
                print("Search[%s] [ERROR] Page '%s' failed to download (time out)!." % (self.baseurl, geturl))
            self.__failed.append(geturl)
            return
        # Refused
        except requests.exceptions.ConnectionError:
            if self.__ipaddr:
                geturl = geturl.replace(self.__ipaddr, self.__basehost)
            if self.__debug:
                print("Search[%s] [ERROR] Page '%s' failed to download (refused)!." % (self.baseurl, geturl))
            self.__failed.append(geturl)
            return
        if self.__ipaddr:
            geturl = geturl.replace(self.__ipaddr, self.__basehost)
        # No Data?
        if not pagedata:
            if self.__debug:
                print("Search[%s] [ERROR] Page '%s' failed to download!." % (self.baseurl, geturl))
            self.__failed.append(geturl)
            return
        # Check for error codes
        if pagedata.status_code != 200:
            if self.__debug:
                print("Search[%s] [ERROR] Page '%s' failed by status code." % (self.baseurl, geturl))
            self.__failed.append(geturl)
            return
        # Text only
        if not ("text" in pagedata.headers['content-type']):
            if self.__debug:
                print("Search[%s] [ERROR] Page '%s' is not a text file." % (self.baseurl, geturl))
            self.__failed.append(geturl)
            return
        # create page object (check if form one exists first)
        pageobject = None
        if self.__debug:
            print("Search[%s] Page '%s' passed.." % (self.baseurl, geturl))
        # Check if we have a page object
        if geturl in self.pages:
            # If so update the current one
            self.pages[geturl].size = len(pagedata.text)
            pageobject = self.pages[geturl]
        else:
            # If not create one
            pageobject = SSite(geturl, len(pagedata.text))
            self.pages[geturl] = pageobject
        # convert to bs4 for searching
        bs4pagedata = BeautifulSoup(pagedata.text)
        # Scan page for links
        self.__scanpage(bs4pagedata, pageobject)
        if self.__forms:
            # Scan for forms
            self.__checkpage(bs4pagedata, pageobject)
    """
        isscanned
        Quick check to determine if page has been scanned
        This method also checks for len of 0 (zero) as from(s) need a page reference
        Page refernces made by forms are made with a len of 0 and need to be updated when passed over
    """
    def __isscanned(self, url):
        # Check if this URL has been maked as failed
        if url in self.__failed:
            return True
        # Check if this URL is in the search Qeue
        if url in self.__search:
            return True
        # Check if it has already been searched
        if url in self.pages:
            page = self.pages[url]
            if page:
                # Is this a placeholder?
                if page.size > 0:
                    return True
            return False
        else:
            # Sanity check for already existing URLs
            # Some URLS can exist in pages and __search at one period of time, depending on form status
            # If a form adds a reference to a page, AND it is being searched at the same time, this will occur
            if url in self.__failed or url in self.__search:
                return True
        return False
    """
        checkpageurl
        Another sanity check to make sure that the URL is properly formatted (fixes absolute URLS)
    """
    def __checkpageurl(self, url):
        # Out of range?
        if (url.startswith("http") and (not url.startswith(self.baseurl))) or url.startswith("mailto:"):
            return None
        rurl = url.replace("#", "")
        # See if this is absolute
        if not url.startswith(self.baseurl):
            # Sanity check: No starting '/'
            if len(rurl) > 1 and rurl[0] != '/':
                rurl = self.baseurl + '/' + url
            else:
                rurl = self.baseurl + url
        return rurl
    """
        scanpage
        Checks page for links and adds them to the search qeue, also checks for text keywords
    """
    def __scanpage(self, page, pageobj):
        # check for a hrefs
        alist = page.find_all("a")
        if alist:
            # enum a hrefs
            for link in alist:
                # Get raw url
                href = link.get("href")
                if href:
                    if self.__ipaddr:
                        href = href.replace(self.__ipaddr, self.__basehost)
                    # Check url format
                    href = self.__checkpageurl(href)
                    if not href:
                        if self.__debug:
                            print("Search[%s] [ERROR] Link '%s' is not in scope!." % (self.baseurl, link.get("href")))
                    else:
                        # Not yet been searched, add to qeue
                        if not self.__isscanned(href):
                            if self.__debug:
                                print("Search[%s] Link '%s' added!." % (self.baseurl, href))
                            self.__search.append(href)
        # Check for divs
        # Lets keep track of the text count to only grab the max
        divcount = 0
        # Look at hs only (Thanks Gionne)
        for type in ["h1", "h2", "h3"]:
            dlist = page.find_all(type)
            if dlist:
                # Do we got stuff?
                for divs in dlist:
                    # Did we hit our limit?
                    if divcount >= self.__keywords:
                        break
                    # Get words, split by space
                    wrdlst = divs.text.split(" ")
                    for word in wrdlst:
                        # Did we hit our limt?
                        if divcount >= self.__keywords:
                            break
                        # Use random to determine words to pick
                        if divcount < self.__keywords and random.randrange(0, 10 * len(wrdlst)):
                            # Remove leading and trailing soaces
                            word = word.strip()
                            # Only letters and numbers (no special chars)
                            if re.match("^[A-Za-z0-9_-]*$", word) and len(word) > 0:
                                divcount += 1
                                # Append our count and add to array
                                pageobj.text.append(word)
    """
        checkpage
        Checks page for form values and inputs
    """
    def __checkpage(self, page, pageobj):
        # check for forms
        formlist = page.find_all("form")
        # Grab all inputs while we have them (Quicker)
        inputlist = page.find_all("input")
        # Create our input list first (dict (name/value))
        inputlistd = dict()
        # Do we have forms?
        if formlist:
            # Do we have inputs? (weird if not)
            if inputlist:
                for input in inputlist:
                    # Enum through and we don't care about submit buttons
                    if not ("ubmit" in input.get("type")):
                        inputlistd[input.get("name")] = input.get("value")
            # enum through our form list
            for form in formlist:
                # Get the action or pointing url
                act = form.get("action")
                if act:
                    if self.__ipaddr:
                        act = act.replace(self.__ipaddr, self.__basehost)
                    # Does the action exist? (Might be a dynamic action)
                    act = self.__checkpageurl(act)
                    if act:
                        # In scope!
                        verb = form.get("method")
                        # Lets get the verb data and create a instance
                        formv = SForm(pageobj.url, verb)
                        # Lets add our captured inputs
                        formv.args = inputlistd
                        if act in self.pages:
                            # target page has already been scanned, just add to its reference
                            self.pages[act].form.append(formv)
                        else:
                            # Target page has not been scanned yet, add a hollow reference for now (0 len)
                            pageobjn = SSite(act, 0)
                            pageobjn.form.append(formv)
                            self.pages[act] = pageobj

"""
    JSONLoader
    Takes JSON data and searches sites based on data
"""


class JSONLoader(threading.Thread):
    def __init__(self, index, host, serviceval, jsonval, dns):
        threading.Thread.__init__(self)
        self.__dns = dns
        self.index = index
        self.__host = host
        self.result = None
        self.__val = jsonval
        self.__svcval = serviceval
    """
        run
        Main thread method, gathers site data, calls SiteSearch.start()
    """
    def run(self):
        # Prep values from json
        uname = None
        upass = None
        unamefm = None
        upassfm = None
        uloginpage = None
        if self.__svcval:
            if "username" in self.__svcval:
                uname = self.__svcval["username"]
            if "password" in self.__svcval:
                upass = self.__svcval["password"]
        if self.__val:
            if "usernameform" in self.__val:
                unamefm = self.__val["usernameform"]
            if "passwordform" in self.__val:
                upassfm = self.__val["passwordform"]
            if "loginpage" in self.__val:
                uloginpage = self.__val["loginpage"]
        # Check for HTTP or HTTPS
        if not self.__host.startswith("http"):
            if self.__svcval["port"] == "80":
                self.__host = ("http://%s" % self.__host)
            if self.__svcval["port"] == "443":
                self.__host = ("https://%s" % self.__host)
        # Init search
        ssearch = SiteSearch(self.__host, self.__dns, uloginpage, uname, unamefm, upass, upassfm, forms=False, debug=False, keywords=6, maxpages=10)
        ssearch.start()
        # Wit for completion
        while ssearch.isAlive():
            var = None
        # Post results
        print("Site '%s' Finished! %d results returned." % (self.__host, len(ssearch.pages)))
        self.result = ssearch.json()


"""
    dnslookup
    Tries to use specified server to lookup a hostname to an IP
"""
def dnslookup(name, dns):
    # Do we have both
    if name and dns:
        try:
            # Use PyDNS to lookup ip addr
            dnsr = DNS.DnsRequest(name, qtype="A", server=[dns], protocol='udp', timeout=30)
            # Process our request
            request = dnsr.req()
            # Go through the responses
            for dnsans in request.answers:
                if dnsans["data"]:
                    # Return our IP addr
                    return dnsans["data"]
        except:
            return None
    return None
"""
    arethreaddone
    Returns true if all the threas are maked as complete
"""
def arethresddone(threads):
    if threads:
        for thread in threads:
            if thread.isAlive():
                return False
    return True
"""
    loadfromjson
    Loads a CTF file, backs it up and adds the scanned entries and saves it back into the supplied json
"""
def loadfromjson(jsonpath):
    print("Loading json file '%s'" % jsonpath)
    # Open the file
    jsonfile = open(jsonpath, "r")
    # JSON load the file
    jsondata = json.load(jsonfile)
    # Create a backup file
    jsonfilebk = open(("%s.bak" % jsonpath), "w")
    print("Creating backup at '%s" % ("%s.bak" % jsonpath))
    # Write the data to the backup
    json.dump(jsondata, jsonfilebk)
    # Close files
    jsonfilebk.close()
    jsonfile.close()
    print("Backup completed")
    # Create our index to find rows
    index = 0
    searchlist = []
    # Get services lists from hosts
    for blueteam in jsondata["blueteams"]:
        dnss = blueteam["dns"]
        for host in blueteam["hosts"]:
            # Need hostname to search
            hostname = host["hostname"]
            for service in host["services"]:
                # Web only
                if service["port"] == "80" or service["port"] == "443":
                    # Add index
                    service["index"] = index
                    # Start and create threat
                    print("Qeueing search on '%s'" % hostname)
                    content = None
                    if "content" in service:
                        content = service["content"]
                    thread = JSONLoader(index, hostname, service, content, dnss)
                    thread.start()
                    searchlist.append(thread)
                    index += 1
    #wait = True
    # Wait till done
    #while wait:
    #    for thread in searchlist:
    #        wait = thread.isAlive()
    while (not arethresddone(searchlist)):
        var = None
    # Once complete, re add the data to the json
    print("Search done, saving results")
    for blueteam in jsondata["blueteams"]:
        for host in blueteam["hosts"]:
            for service in host["services"]:
                if "index" in service:
                    for thread in searchlist:
                        # look for index
                        if thread.index == service["index"]:
                            # Add data to matched index
                            service["content"] = thread.result
                            service.pop("index", None)
                            break
                    if "uri" in service:
                        service.pop("uri", None)
    print("Writing data to %s" % jsonpath)
    # Save data
    jsonout = open(jsonpath, "w")
    json.dump(jsondata, jsonout)
    jsonout.close()
    print("Done!")

if __name__ == "__main__":
    """
    OHRM
    aaa = SiteSearch("", loginpage="/symfony/web/index.php/auth/validateCredentials",
                            username="admin", usernamefm="txtUsername", password="chiapet1", passwordfm="txtPassword", \
                             debug=True, forms=False)

    Simple Machines Form
    aaa = SiteSearch("", loginpage="index.php?action=login2", username="admin", usernamefm="user", \
                         password="241ccebca76e8ff221f9b5f15353cdb1af599667", passwordfm="hash_password", \
                         debug=True, forms=False)

    Google Chrome
    aaa = SiteSearch("http://google.com/chrome/", dns="8.8.8.8", debug=True)
    aaa.start()
    while aaa.isAlive():
        None
    print("Data: %s" % json.dumps(aaa.json()))
    """

    loadfromjson("V:\\bsidesde2014.json")

    if len(sys.argv) > 1:
        loadfromjson(sys.argv[1])
        sys.exit(0)
    else:
        print("Usage SiteSearch.py <jsonfile.json>")
        print("Scans and appends results to specified json file")
        sys.exit(-1)
