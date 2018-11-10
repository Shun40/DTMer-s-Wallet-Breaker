import re

import requests
import bs4

from article import Article, Articles

class Website:
    def __init__(self, website_name, website_url, date_format, term_format):
        """
        コンストラクタ

        Args:
            website_name (str): Webサイト名
            website_url (str): WebサイトURL
            date_format (str): 日付フォーマット(正規表現)
            term_format (str): セール期間フォーマット(正規表現)
        """
        self.website_name = website_name
        self.website_url = website_url
        self.date_format = date_format
        self.term_format = term_format

    @classmethod
    def extract_urls(cls, number, soup, url_css_selector, pager_css_selector):
        """
        スープオブジェクトの中からセール記事のURLを抽出して返す

        Args:
            number (int): 取得件数
            soup (object): スープオブジェクト
            url_css_selector (str): URL検索用のCSSセレクタ文字列
            pager_css_selector (str): ページャ処理用のCSSセレクタ文字列

        Returns:
            セール記事のURLのリスト
        """
        urls = []
        while True:
            elements = soup.select(url_css_selector)
            for element in elements:
                urls.append(element.get('href'))
                if len(urls) == number:
                    break

            if len(urls) == number:
                break

            # ページャ処理
            element = soup.select_one(pager_css_selector)
            if element == None:
                break
            else:
                response = cls.get_response(element.get('href'))
                soup = cls.get_soup(response)

        return urls

    @classmethod
    def extract_term(cls, description, term_format):
        """
        説明文の中からセール期間を抽出して返す

        Args:
            description (str): 説明文
            term_format (str): セール期間フォーマット(正規表現)

        Returns:
            セール期間
        """
        if description == None:
            return

        if term_format == None:
            return

        search = re.search(term_format, description)
        if search:
            return search.group()
        else:
            return 'セール期間情報なし'

    @classmethod
    def get_response(cls, url):
        """
        レスポンスオブジェクトを取得する

        Args:
            url (str): URL

        Returns:
            レスポンスオブジェクト
        """
        response = requests.get(url)
        response.raise_for_status() # ステータスコードが200番台以外のときは例外を吐いて停止
        print('> HTTP GET Request takes {} [sec] (source : {})'.format(response.elapsed.total_seconds(), url))
        return response

    @classmethod
    def get_soup(cls, response):
        """
        スープオブジェクトを取得する

        Args:
            response (object): レスポンスオブジェクト

        Returns:
            スープオブジェクト
        """
        return bs4.BeautifulSoup(response.text, 'html.parser')


class CMJ(Website):
    """
    Computer Music Japanからセール記事を取得するクラス
    """

    def __init__(self):
        """
        コンストラクタ
        """
        Website.__init__(
            self,
            'Computer Music Japan',
            'https://computermusic.jp/category/セール/',
            '^(?P<YYYYmmdd>[0-9]{4}-[0-9]{2}-[0-9]{2})T([0-9]{2}:[0-9]{2}:[0-9]{2})Z$',
            '[0-9]+月[0-9]+日まで'
        )

    def get_articles(self, number):
        """
        セール記事を取得する

        Args:
            number (int): 取得件数

        Returns:
            セール記事のリスト
        """
        response = self.get_response(self.website_url)
        soup = self.get_soup(response)

        # セール記事のURLを取得
        urls = self.extract_urls(
            number,
            soup,
            'article[class="post-list animated fadeInUp"] > a',
            'a[class="next page-numbers"]'
        )

        # 各URL先から記事を取得
        articles = Articles()
        for url in urls:
            response = self.get_response(url)
            soup = self.get_soup(response)

            title = soup.find('meta', property='og:title').get('content')
            description = soup.find('meta', property='og:description').get('content')
            date = soup.find('meta', property='article:published_time').get('content')
            date = re.match(self.date_format, date).group('YYYYmmdd').replace('-', '/')
            term = self.extract_term(description, self.term_format)
            thumbnail = soup.find('meta', property='og:image').get('content')

            article = Article(title, url, description, date, term, thumbnail, self.website_name, self.website_url)
            articles.append(article)

        return articles


class Sleepfreaks(Website):
    """
    Sleepfreaksからセール記事を取得するクラス
    """

    def __init__(self):
        """
        コンストラクタ
        """
        Website.__init__(
            self,
            'Sleepfreaks',
            'https://sleepfreaks-dtm.com/category/sale/',
            '^(?P<YYYYmmdd>[0-9]{4}-[0-9]{2}-[0-9]{2})$',
            '[0-9]+月[0-9]+日まで'
        )

    def get_articles(self, number):
        """
        セール記事を取得する

        Args:
            number (int): 取得件数

        Returns:
            セール記事のリスト
        """
        response = self.get_response(self.website_url)
        soup = self.get_soup(response)

        # セール記事のURLを取得
        urls = self.extract_urls(
            number,
            soup,
            'h3 > a',
            None
        )

        # 各URL先から記事を取得
        articles = Articles()
        for url in urls:
            response = self.get_response(url)
            soup = self.get_soup(response)

            title = soup.find('meta', property='og:title').get('content')
            description = soup.find('meta', property='og:description').get('content')
            date = soup.find('time').get('datetime').replace('-', '/')
            term = self.extract_term(soup, self.term_format)
            thumbnail = soup.find('img', class_='sale_img').get('src')

            article = Article(title, url, description, date, term, thumbnail, self.website_name, self.website_url)
            articles.append(article)

        return articles

    def extract_term(self, soup, term_format):
        """
        説明文の中からセール期間を抽出する

        Args:
            soup (object): スープオブジェクト
            term_format (str): セール期間フォーマット(正規表現)

        Returns:
            セール期間
        """
        term = soup.find('div', class_='sale_term')
        if term == None:
            return 'セール期間情報なし'
        else:
            term = term.find('span').text
            search = re.search(term_format, term)
            if search:
                return search.group()
            else:
                return term


class MeloDealer(Website):
    """
    MeloDealerからセール記事を取得するクラス
    """

    def __init__(self):
        """
        コンストラクタ
        """
        Website.__init__(
            self,
            'MeloDealer',
            'http://melodealer.com/category/dtm/sale-promotion/',
            '^(?P<YYYYmmdd>[0-9]{4}-[0-9]{2}-[0-9]{2})T([0-9]{2}:[0-9]{2}:[0-9]{2})Z$',
            '[0-9]+月[0-9]+日まで'
        )

    def get_articles(self, number):
        """
        セール記事を取得する

        Args:
            number (int): 取得件数

        Returns:
            セール記事のリスト
        """
        response = self.get_response(self.website_url)
        soup = self.get_soup(response)

        # セール記事のURLを取得
        urls = self.extract_urls(
            number,
            soup,
            'h2.entry-title > a',
            'li.previous > a'
        )

        # 各URL先から記事を取得
        articles = Articles()
        for url in urls:
            response = self.get_response(url)
            soup = self.get_soup(response)

            title = soup.find('meta', property='og:title').get('content')
            description = soup.find('meta', property='og:description').get('content')
            date = soup.find('meta', property='article:published_time').get('content')
            date = re.match(self.date_format, date).group('YYYYmmdd').replace('-', '/')
            term = self.extract_term(description, self.term_format)
            thumbnail = soup.find('meta', property='og:image').get('content')

            # すでに終了したセールの情報はスキップする
            if '【終了】' in title:
                continue

            article = Article(title, url, description, date, term, thumbnail, self.website_name, self.website_url)
            articles.append(article)

        return articles


class SawayakaTrip(Website):
    """
    Sawayaka Trip!からセール記事を取得するクラス
    """

    def __init__(self):
        """
        コンストラクタ
        """
        Website.__init__(
            self,
            'Sawayaka Trip!',
            'https://sawayakatrip.com/category/dtm・daw関連記事/sale',
            '^(?P<YYYYmmdd>[0-9]{4}-[0-9]{2}-[0-9]{2})T([0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2})$',
            '[0-9]+月[0-9]+日まで'
        )

    def get_articles(self, number):
        """
        セール記事を取得する

        Args:
            number (int): 取得件数

        Returns:
            セール記事のリスト
        """
        response = self.get_response(self.website_url)
        soup = self.get_soup(response)

        # セール記事のURLを取得
        urls = self.extract_urls(
            number,
            soup,
            'h2 > a',
            'li.next > a'
        )

        # 各URL先から記事を取得
        articles = Articles()
        for url in urls:
            response = self.get_response(url)
            soup = self.get_soup(response)

            title = soup.find('meta', property='og:title').get('content')
            description = soup.find('meta', property='og:description').get('content')
            date = soup.find('time').get('datetime')
            date = re.match(self.date_format, date).group('YYYYmmdd').replace('-', '/')
            term = self.extract_term(description, self.term_format)
            thumbnail = soup.find('meta', property='og:image').get('content')

            article = Article(title, url, description, date, term, thumbnail, self.website_name, self.website_url)
            articles.append(article)

        return articles
