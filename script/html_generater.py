import argparse
import datetime
import math
import os
import sys
import webbrowser

from article import Articles

TAGS = os.path.abspath('tags.txt')
PICKLE = os.path.abspath('articles.pickle')
HTML_DIR = os.path.abspath('html')
CSS_DIR = os.path.abspath('css')
IMG_DIR = os.path.abspath('img')

def generate_html(category, category_articles, tags, tagged_articles_count, update):
    min_page = 1
    max_page = math.ceil(len(category_articles) / 20) # ページ分割したときの最大ページ数を計算
    for current_page in range(1, max_page + 1):
        page_articles = category_articles[20 * (current_page - 1):20 * current_page]
        html = generate_page(
            category,
            page_articles,
            tags,
            tagged_articles_count,
            current_page,
            min_page,
            max_page,
            update
        )
        write_to_file(category, current_page, html)

def generate_page(category, page_articles, tags, tagged_articles_count, current_page, min_page, max_page, update):
    template = '''
    <!DOCTYPE html>
    <html lang="ja">
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <title>DTM Sale Scraper</title>
    <link rel="stylesheet" href="{css}" type="text/css"/>
    </head>
    <body>
    <header>
    <p class="header-description">複数サイトから収集したDTMセール情報を表示し、DTMerの破産を促進します。</p>
    <p class="header-title"><a class="header-title" href="{url}">DTMer's Wallet Breaker</a></p>
    </header>
    {content_elements}
    <footer>
    <div class="websites">
    <p>Webサイト</p>
    <ul>
    <li><a href="https://computermusic.jp/category/セール/">Computer Music Japan</a></li>
    <li><a href="https://sleepfreaks-dtm.com/category/sale/">Sleepfreaks</a></li>
    <li><a href="http://melodealer.com/category/dtm/sale-promotion/">MeloDealer</a></li>
    <li><a href="https://sawayakatrip.com/category/dtm・daw関連記事/sale">Sawayaka Trip!</a></li>
    </ul>
    </div>
    <div class="update">
    <p>データ最終更新日</p>
    {update}
    </div>
    </footer>
    </body>
    </html>
    '''
    return template.format(
        css = os.path.join(CSS_DIR, 'style.css'),
        url = os.path.join(HTML_DIR, 'all', '1.html'),
        content_elements = generate_content_elements(category, page_articles, tags, tagged_articles_count, current_page, min_page, max_page),
        update = update
    )

def generate_content_elements(category, page_articles, tags, tagged_articles_count, current_page, min_page, max_page):
    template = '''
    <div class="content">
    <div class="articles">
    <p><label class="caption-bold">セール記事</label><label class="caption">（<b>{count}件</b>）</label>{filtering}</p>
    <hr>
    {articles_elements}
    {pager_elements}
    </div>
    <div class="tags">
    <p><label class="caption-bold">タグ</label></p>
    <hr>
    {tags_elements}
    </div>
    </div>
    '''
    filtering = ''
    if category != 'all':
        filtering = generate_tag_elements(category, tagged_articles_count[category])

    return template.format(
        filtering = filtering,
        count = tagged_articles_count[category],
        articles_elements = generate_articles_elements(page_articles, tagged_articles_count),
        pager_elements = generate_pager_elements(category, current_page, min_page, max_page),
        tags_elements = generate_tags_elements(tags, tagged_articles_count)
    )

def generate_articles_elements(page_articles, tagged_articles_count):
    elements = ''
    for page_article in page_articles:
        elements += generate_article_elements(page_article, tagged_articles_count)
    return elements

def generate_article_elements(page_article, tagged_articles_count):
    template = '''
    <article>
    <p>{date_elements}{website_elements}{term_elements}</p>
    <p class="title article-large-text"><a class="article-large-text" href="{url}">{title}</a></p>
    <p class="tags">{tags_elements}</p>
    <div>
    <img class="thumbnail" src="{thumbnail}">
    <p class="description article-small-text">{description}</p>
    </div>
    </article>
    '''
    return template.format(
        date_elements = generate_date_elements(page_article.date),
        website_elements = generate_website_elements(page_article.website_url, page_article.website_name),
        term_elements = generate_term_elements(page_article.term),
        url = page_article.url,
        title = page_article.title,
        tags_elements = generate_tags_elements(page_article.tags, tagged_articles_count),
        thumbnail = page_article.thumbnail,
        description = page_article.truncate_description(400)
    )

def generate_date_elements(date):
    template = '''
    <span class="date">
    <img src="{icon}">
    <label><b>{date}</b></label>
    </span>
    '''
    return template.format(
        icon = os.path.join(IMG_DIR, 'date.png'),
        date = date
    )

def generate_website_elements(website_url, website_name):
    template = '''
    <span class="website">
    <img src="{icon}">
    <a href="{url}"><b>{name}</b></a>
    </span>
    '''
    return template.format(
        icon = os.path.join(IMG_DIR, 'website.png'),
        url = website_url,
        name = website_name
    )

def generate_term_elements(term):
    template = '''
    <span class="term">
    <img src="{icon}">
    <label><b>{term}</b></label>
    </span>
    '''
    return template.format(
        icon = os.path.join(IMG_DIR, 'term.png'),
        term = term
    )

def generate_tags_elements(tags, tagged_articles_count):
    elements = ''
    for tag in tags:
        elements += generate_tag_elements(tag, tagged_articles_count[tag])
    return elements

def generate_tag_elements(tag, count):
    template = '''
    <span class="tag">
    <img src="{icon}">
    <a href="{url}"><b>{tag}</b>({count})</a>
    </span>
    '''
    return template.format(
        icon = os.path.join(IMG_DIR, 'tag.png'),
        url = os.path.join(HTML_DIR, '{}'.format(tag), '1.html'),
        tag = tag,
        count = count
    )

def generate_pager_elements(category, current_page, min_page, max_page):
    template = '''
    <div class="pager">
    {page_elements}
    </div>
    '''
    elements = ''
    # [1][2][3] ... [max - 2][max - 1][max]
    for page in range(min_page, max_page + 1):
        url = os.path.join(HTML_DIR, '{}'.format(category), '{}.html'.format(page))
        current = ''
        if current_page == page:
            current = 'current'
        elements += '<div class="{current}"><a href="{url}">{page}</a></div>'.format(current=current, url=url, page=page)
    return template.format(
        page_elements = elements
    )

def write_to_file(category, current_page, html):
    file_path = os.path.join(HTML_DIR, '{}'.format(category), '{}.html'.format(current_page))
    dir_path = os.path.dirname(file_path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_path, 'w') as file:
        file.write(html)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-ob', '--open_browser', help='After HTML generation, open HTML in web browser.', action='store_true')
    return parser.parse_args()

def main():
    args = get_args()
    open_browser = args.open_browser

    if not os.path.exists(PICKLE):
        print('Not found {}'.format(PICKLE))
        return

    if not os.path.exists(TAGS):
        print('Not found {}'.format(TAGS))
        return

    # タグコレクションを読み込む
    with open(TAGS, 'r') as file:
        tags = [tag.strip() for tag in file.readlines()] # 改行削除

    # 全記事を読み込み
    articles = Articles.read_from_pickle(PICKLE)
    articles.sort_by_date() # 日付順にソート
    for article in articles:
        article.extract_tags(tags) # タグ付け

    # 各タグが付いた記事数を数える
    tagged_articles_count = {}
    tagged_articles_count['all'] = len(articles)
    for tag in tags:
        tagged_articles_count[tag] = len(articles.filter_by_tag(tag))

    # 記事データの最終更新日を取得
    update = datetime.datetime.fromtimestamp(os.stat(PICKLE).st_mtime)
    update = update.strftime('%Y/%m/%d  %H:%M:%S')

    # 全記事のHTMLを生成
    generate_html('all', articles, tags, tagged_articles_count, update)

    # 各タグでフィルタリングした記事のHTMLを生成
    for tag in tags:
        generate_html(tag, articles.filter_by_tag(tag), tags, tagged_articles_count, update)

    # 必要に応じてWebブラウザで開く
    if open_browser:
        url = 'file:///' + os.path.join(HTML_DIR, 'all', '1.html')
        webbrowser.open(url)

if __name__ == '__main__':
    main()
