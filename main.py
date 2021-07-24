import requests
from bs4 import BeautifulSoup

KEYWORDS = ['дизайн', 'фото', 'web', 'python']


class HabrParser():
    HOST = 'https://habr.com'

    def __init__(self, keywords, scaning='simple'):
        self.keywords = set(keywords)
        case = {'simple': self.simple_scan,
                'advenced': self.advenced_scan
                }
        self.actual_list = case.get(scaning, self.simple_scan)()

    def __str__(self):
        out = str()
        if self.actual_list:
            for line in self.actual_list:
                out += line + '\n'
        else:
            out = 'list is empty'
        return out

    def __repr__(self):
        return self.actual_list

    def get_articles(self):
        req = requests.get(self.HOST + '/ru/top/daily/')
        soup = BeautifulSoup(req.text, features='html.parser')
        return soup.find_all('article')

    def get_words(self, article):
        preview = article.find(class_="article-formatted-body " +
                               "article-formatted-body_version-1") or\
                               article.find(class_="article-formatted-body " +
                                            "article-formatted-body_version-2")
        if preview:
            return {word.lower() for word in preview.text.split()}
        else:
            return {}

    def get_link(self, article):
        return self.HOST + article.find('h2').find('a').attrs.get('href')

    def get_date(self, article):
        return article.find('time').attrs.get('title').split(',')[0]

    def get_title(self, article):
        return article.find('h2').find('span').text

    def simple_scan(self):
        out = []
        articles = self.get_articles()
        for article in articles:
            preview = self.get_words(article)
            if preview & self.keywords:
                date = self.get_date(article)
                title = self.get_title(article)
                link = self.get_link(article)
                out.append(f"{date} - {title} - {link}")
        return out

    def advenced_scan(self):
        out = []
        articles = self.get_articles()
        for article in articles:
            link = self.get_link(article)
            if link:
                req = requests.get(link)
                soup = BeautifulSoup(req.text, features='html.parser')
                article_text = self.get_words(soup)
                if article_text & self.keywords:
                    date = self.get_date(article)
                    title = self.get_title(article)
                    out.append(f"{date} - {title} - {link}")
        return set(out + self.simple_scan())


if __name__ == '__main__':
    print(HabrParser(KEYWORDS, "advenced"))
