import datetime
import pickle

class Article:
    """
    セール記事のクラス
    """

    def __init__(self, title, url, description, date, term, thumbnail, website_name, website_url):
        """
        コンストラクタ

        Args:
            title (str): タイトル
            url (str): URL
            description (str): 説明文
            date (str): 掲載日
            term (str): セール期間
            thumbnail (str): サムネイルURL
            website_name (str): サイト名
            website_url (str): サイトURL
        """
        self.title = title
        self.url = url
        self.description = description
        self.date = date
        self.term = term
        self.thumbnail = thumbnail
        self.website_name = website_name
        self.website_url = website_url
        self.tags = []

    def extract_tags(self, tags):
        """
        説明文の中からタグを抽出して付与する

        Args:
            tags (list<str>): 検索するタグのリスト
        """
        extracted_tags = []
        # タイトルと説明文からタグを抽出
        for tag in tags:
            title = self.title
            description = self.description
            if (tag.lower() in title.lower()) or (tag.lower() in description.lower()):
                extracted_tags.append(tag)
        # 1つもタグがつかなかったらNoneタグをつける
        if not extracted_tags:
            extracted_tags.append('None')
        # 昇順にソート
        self.tags = sorted(extracted_tags)

    def truncate_description(self, length):
        """
        指定文字数で切り捨てた説明文を返す

        Args:
            length (int): 切り捨てる文字数

        Returns:
            指定文字数で切り捨てた説明文
        """
        if len(self.description) > length:
            return self.description[:length] + ' …' # 切り捨てた場合"..."をつける
        else:
            return self.description

class Articles(list):
    """
    セール記事群のクラス
    """

    def __init__(self):
        """
        コンストラクタ
        """
        list.__init__(self)

    def filter_by_tag(self, filter_tag):
        """
        指定タグを持つ記事のみを返す

        Args:
            filter_tag (str): フィルタリングに使うタグ

        Returns:
            指定タグを持つ記事
        """
        filtered_articles = Articles()
        for article in self:
            tags = [tag.lower() for tag in article.tags]
            if filter_tag.lower() in tags:
                filtered_articles.append(article)
        return filtered_articles

    def sort_by_date(self):
        """
        全記事を日付が新しい順に並び替える
        """
        self.sort(
            key=lambda entry: datetime.date(
                datetime.datetime.strptime(entry.date, '%Y/%m/%d').year,
                datetime.datetime.strptime(entry.date, '%Y/%m/%d').month,
                datetime.datetime.strptime(entry.date, '%Y/%m/%d').day
            ),
            reverse = True # 日付が新しい順にソートする
        )

    @classmethod
    def read_from_pickle(cls, path):
        """
        記事群のデータをpickleオブジェクトから読み込む

        Args:
            path (str): 読み込み先ファイルパス
        """
        with open(path, 'rb') as file:
            return pickle.load(file)

    def write_to_pickle(self, path):
        """
        記事群のデータをpickleオブジェクトに保存する

        Args:
            path (str): 保存先ファイルパス
        """
        with open(path, 'wb') as file:
            pickle.dump(self, file)
