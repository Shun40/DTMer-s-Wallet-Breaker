import argparse
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import os
import time

from website import CMJ, Sleepfreaks, MeloDealer, SawayakaTrip
from article import Articles

PICKLE = os.path.abspath('articles.pickle')

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', help='Number of retrieval for each website (default is 10)', default=10, type=int)
    parser.add_argument('-s', '--serial', help='Run scraping serially (default is parallelly)', action='store_true')
    return parser.parse_args()

def main():
    args = get_args()
    number = args.number
    serial = args.serial
    
    if not 1 <= number <= 100:
        print('Number of retrieval : 1 <= N <= 100')
        return

    # 各サイトをスクレイピングしてセール記事を集める
    # 処理時間の参考:
    # 直列 39.3976 [sec] (N=10)
    # 並列 19.1955 [sec] (N=10)
    # 直列 199.0781 [sec] (N=50)
    # 並列 96.5753 [sec] (N=50)
    # 並列 175.1684 [sec] (N=100)
    websites = [CMJ(), Sleepfreaks(), MeloDealer(), SawayakaTrip()]
    all_articles = Articles()
    if serial: # 直列実行
        print('> Scraping is started. (Run serially)')
        start_time = time.time()
        for website in websites:
            all_articles += website.get_articles(number)
        end_time = time.time()
        print('> Scraping finished. Scraping takes {} [sec]'.format(end_time - start_time))
    else: # 並列実行
        print('> Scraping is started. (Run parallelly)')
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=len(websites)) as executor:
            futures = [executor.submit(website.get_articles, number) for website in websites]
        for future in concurrent.futures.as_completed(futures):
            all_articles += future.result()
        end_time = time.time()
        print('> Scraping finished. Scraping takes {} [sec]'.format(end_time - start_time))

    # pickleに出力してセール記事を保存
    all_articles.write_to_pickle(PICKLE)
    print('> Results saved to {}'.format(PICKLE))

if __name__ == '__main__':
    main()
