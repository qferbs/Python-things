import crawler
##input
print("Enter list of webpages:")
inString = input()
pages = inString.split()
print("Enter list of search terms:")
inString = input()
searchTerms = inString.split()
print("Enter maximum number of pages to crawl:")
try:
    maxIter = int(input())
except:
    maxIter = None

##crawl start
spider = crawler.Spider()
crawlIter = spider.crawl(pages, searchTerms, maxIter, "STRICT")

print("Done.")
