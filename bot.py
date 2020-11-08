import os
import threading
import requests
import bs4
import re
import datetime


# Author : Alex Nguetcha <nguetchaalex@gmail.com>

class ImageDownloaderBot:
    def __init__(self, maxDownloads=10, maxDownloadSize=500*1024, verbose=True, logout=True):
        """ 
          download many image from google by keywords automatically
          
        """
        self.chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        self.downloadUrl = "https://www.google.com/search?hl=FR&tbm=isch&sxsrf=ALeKk03l4GEjAQ_pXcHJVQx82f600TdJGQ%3A1604864286245&source=hp&biw=1366&bih=625&ei=HkmoX6b1C4q4lwTp4KmoAg&q=[|key|]&oq=[|key|]&gs_lcp=CgNpbWcQAzIECCMQJzICCAAyAggAMgIIADICCAAyAggAMgIIADICCAAyAggAMgIIADoHCCMQ6gIQJzoFCAAQsQNQvCVYrShgyjJoAXAAeAKAAcgEiAHhDJIBCTItMS4xLjAuMpgBAKABAaoBC2d3cy13aXotaW1nsAEK&sclient=img&ved=0ahUKEwim_MOt2fPsAhUK3IUKHWlwCiUQ4dUDCAc&uact=5"  # the search engine to perform research
        self.keys = []  # research keys for search engine
        self.maxDownloads = maxDownloads  # max image downloads per key
        self.maxDownloadSize = maxDownloadSize  # max file size for download in octet
        # google image extension seems be .jpeg only
        # self.acceptExtensions = ["png", "jpg", "jpeg"]  # list of image extension who can be download
        self.botDir = "bot-downloads"
        self.counter = 0  # donwload counter
        self.verbose = verbose # allow to print the log output
        self.logout = logout # allow create a logout file
        # create the download folder if doesn't exist
        if not os.path.exists(self.botDir):
            os.mkdir(self.botDir)
        # create the log file if doesn't exist
        if not os.path.exists("log"):
            log = open("log", "w+")
            log.close()

    def log(self, message: str):
        """ write in the log file """
        if not self.logout:
            return False
        t = str(datetime.datetime.now()).split(" ")[1]
        t = str(t).split(".")[0]
        self.m(message)
        file = open("log", "a+")
        file.write("[{}] {}\n".format(t, message))
        file.close()

    def m(self, message: str):
        if self.verbose == True:
            print(message)
        
    def start(self, keys=None):
        if keys is None:
            keys = []
        if not isinstance(keys, list):
            self.log("keys must be an instance of list object")
            raise Exception("keys must be an instance of list object")
        elif len(keys) == 0:
            self.log("no keywords found for research")
            raise Exception("no keywords found for research")
        else:
            for key in keys:
                if self.counter >= self.maxDownloads:
                    return False
                url = self.downloadUrl.replace("[|key|]", key)
                key = key.lower()
                # create a custom doc name
                # from key
                path_name = "bot-"
                for k in key:
                    if k not in self.chars:
                        key.replace(k, "-")
                path_name = path_name + key
                # create directory into bot-downloads folder
                path_name = os.path.join("bot-downloads", path_name)
                # create directory if
                if not os.path.exists(path_name):
                    os.mkdir(path_name)
                else:
                    self.log("warning '" + path_name + "' already exist")
                # start downloading every image url in different thread
                self.log("start getting image links from {}".format(url))
                threading.Thread(target=self.download, args=(url, path_name), daemon=False).start()
                

    def download(self, url: str, output: str):
        try:
            request = requests.request("GET", url)
        except :
            self.log("failed to open url {}".format(url))
            return False
        
        image_links = []
        if request.status_code == 200:
            image_links = self.extract_img_links(str(request.content))
            self.log("{} links found ".format(len(image_links)))
            for link in image_links:
                self.log("downloading {}".format(link))
                threading.Thread(target=self._download, args=(link, output), daemon=False).start()

    def _download(self, url: str, output: str):
        if self.counter >= self.maxDownloads:
            return False
        try:
            request = requests.get(url)
        except:
            self.log("failed to download {}".format(url))
            return False
        # GET THE FILENAME
        # try to get the file size and name via header
        try:
            content_length = request.headers["Content-Length"]
            if content_length > self.maxDownloadSize:
                self.log("cannot be download, file size = {}".format(content_length))
                return False
        except:
            self.log("unable to get file size from header")
        filenames = re.findall("filename=(.+)", "-".join(request.headers))
        filename = ""
        if len(filenames) == 0:
            filename = str(datetime.datetime.now()).replace(" ", "-").replace(":", "-").replace(".", "-")
            filename += ".jpeg"
        else:
            filename = filenames[0]
        self.log("filename : {}".format(filename))
        open(os.path.join(output, filename), "wb+").write(request.content)
        self.log("downloaded!")
        self.counter += 1
        # #

    def extract_img_links(self, html: str):
        links = []
        soup = bs4.BeautifulSoup(html)
        for img in soup.find_all("img"):
            links.append(img["src"])
        return links


bot = ImageDownloaderBot()
bot.start(["cat", "dog", "lion"])