import requests
from PIL import Image
from io import BytesIO
from html.parser import HTMLParser

class Tree:
    def __init__(self,  name="root"):
        self.name = name
        self.children = []

    def addChild(self,  node):
        newTree = Tree(node)
        self.children.append(newTree)

class Parser(HTMLParser):
    data = set([])
    crawlData = set([])
    def handle_starttag(self,  tag,  attrs):
        if(tag == "img"):
            self.data |= set(attr[1] for attr in attrs if attr[0] == "src")
        elif(tag == "a"):
            for attr in attrs:
                if(attr[0] == "href"):
                    try:
                        x = attr[1][0] == "/" or attr.startswith("https")
                    except:
                        x = 0
                    if(x):
                        self.crawlData.add(attr[1])

class Spider:
    def __init__(self):
        self.urlList = set([])
        self.imageUrls = set([])

    def crawl(self, rootUrls, searchFor=None , maxIter=None, mode="NORMAL"):
        parser = Parser()
        self.urlList |= set(rootUrls)
        nodeList = [Tree(url) for url in rootUrls]
        
        for node in nodeList:
            try:
                page = requests.get(node.name)
                print("Parsing",  page.url)
                self.parse(parser,  page, searchFor,  node)
            except:
                print("Requests error in spider.crawl at",  node.name)
        
        i = 0
        while((maxIter == None or i < maxIter) and any(nodeList)):
            childList = []
            for node in nodeList:
                imgInChild = []
                
                print("checking %s children of" % len(node.children),  node.name)
                for child in node.children:
                    try:
                        page = requests.get(child.name)
                        print("%s: Parsing" % i,  page.url)
                        
                        hasImg = self.parse(parser,  page, searchFor,  child)
                        
                        if(mode == "STRICT" and hasImg):
                                childList.append(child)
                                print("image(s) found")
                        imgInChild.append(hasImg)
                            
                    except:
                        print("Requests error in spider.crawl at",  child.name)
                    
                    i += 1
                    if(maxIter != None and i >= maxIter):
                        break
                
                if(any(imgInChild)):
                    print("node successful")
                    if(mode != "STRICT"):
                        childList += node.children
                else:
                    print("node yielded nothing")
                if(maxIter != None and i >= maxIter):
                    break
            
            nodeList = childList
        
        ##if(self.imageUrls):
            ##print("retrieving images...")
            ##self.getImages()
        
        return i

    def parse(self, parser,  page,  searchFor, node):
        url = page.url
        parser.feed(page.text)
        
        foundUrls = set([imgUrl if imgUrl.startswith("https") else "https:" + imgUrl if imgUrl.startswith("//")
                                   else self.appendUrl(url, imgUrl) for imgUrl in parser.data if searchFor == None
                                   or any(search in imgUrl.lower()[imgUrl.rfind("/"):] for search in searchFor)])
        foundUrls -= self.imageUrls
        self.imageUrls |= foundUrls
        
        parsedUrls = set([cUrl if cUrl.startswith("https") else self.appendUrl(url,  cUrl) for cUrl in parser.crawlData])
        parsedUrls -= self.urlList
        self.urlList |= parsedUrls
        
        node.children = set([Tree(url) for url in parsedUrls])
        parser.data,  parser.crawlData = set([]), set([])
        self.getImages(foundUrls)
        
        return any(foundUrls)

    def getImages(self, images=None):
        if(images == None):
            images = self.imageUrls
            self.imageUrls = []
        for url in images:
            try:
                bin = requests.get(url)
                img = Image.open(BytesIO(bin.content))
                img.save("images" + bin.url[bin.url.rfind("/"):],  img.format)
            except:
                print("Could not process", url)

    def appendUrl(self, url,  app):
        x = [pos for pos, char in enumerate(url) if char == "/"]
        url = url[:x[2]]
        return url + app
