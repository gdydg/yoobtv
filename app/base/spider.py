# 这是一个模拟类，用于欺骗子类脚本，使其认为运行在 TVBox 环境中
class Spider:
    def __init__(self):
        self.extend = ""
        self.extendDict = {}

    def init(self, extend):
        pass

    def getName(self):
        return "BaseSpider"

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def homeContent(self, filter):
        return {}

    def homeVideoContent(self):
        return {}

    def categoryContent(self, cid, page, filter, ext):
        return {}

    def detailContent(self, did):
        return {}

    def searchContent(self, key, quick, page='1'):
        return {}

    def searchContentPage(self, keywords, quick, page):
        return {}

    def playerContent(self, flag, pid, vipFlags):
        return {}

    def liveContent(self, url):
        return ""

    def localProxy(self, params):
        return []

    def destroy(self):
        pass
