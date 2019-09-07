##deprecated version
import requests
from PIL import Image
from io import BytesIO
from html.parser import HTMLParser

class Parser(HTMLParser):
    data = []
    crawlData = []
    def handle_starttag(self,  tag,  attrs):
        if(tag == "img"):
            for attr in attrs:
                if(attr[0] == "src"):
                    self.data.append(attr[1])
        elif(tag == "a"):
            for attr in attrs:
                if(attr[0] == "href"):
                    try:
                        x = attr[1][0] == "/"
                    except:
                        x = 0
                    if(x):
                        self.crawlData.append(attr[1])

class Spider:
    def __init__(self, urlList):
        self.urlList = urlList
        self.imageUrls = []

    def crawl(self,  Parser, searchFor=None , maxIter=100):
        i=0
        for url in self.urlList:
            try:
                page = requests.get(url)
                print("Parsing",  page.url)
                self.parse(Parser,  page,  page.url)
            except:
                print("Requests error in spider.crawl at",  url)
            i+=1
            if(i>=maxIter):
                break
        if(self.imageUrls):
            print("retrieving images...")
            self.getImages(searchFor)

    def parse(self, Parser,  page,  url):
        Parser.feed(page.text)
        
        parsedUrls = [imgUrl if imgUrl.startswith("https") else "https:" + imgUrl if imgUrl.startswith("//")
                              else self.appendUrl(url, imgUrl) for imgUrl in parser.data]
        self.imageUrls.extend([x for x in parsedUrls if x not in self.imageUrls])
        
        parsedUrls = [cUrl if cUrl.startswith("https") else self.appendUrl(url,  cUrl) for cUrl in parser.crawlData]
        self.urlList.extend([x for x in parsedUrls if x not in self.urlList])
        
        parser.data,  parser.crawlData = [],  []

    def getImages(self,  searchFor):
        for url in self.imageUrls:
            try:
                if(searchFor == None or any(search in url.lower()[url.rfind("/"):] for search in searchFor)):
                    bin = requests.get(url)
                    img = Image.open(BytesIO(bin.content))
                    img.save("images" + bin.url[bin.url.rfind("/"):],  img.format)
            except:
                print("Could not process", url)
        self.imageUrls = []

    def appendUrl(self, url,  app):
        x = [pos for pos, char in enumerate(url) if char == "/"]
        url = url[:x[2]]
        return url + app

print("Enter list of webpages:")
inString = input()
pages = inString.split()
print("Enter list of search terms:")
inString = input()
searchTerms = inString.split()
print("Enter maximum number of pages to crawl:")
maxIter = int(input())

parser = Parser()
spider = Spider(pages)
spider.crawl(parser, searchTerms, maxIter)

print("Done.")
