# DTMer's-Wallet-Breaker
WebサイトからDTMプラグインセール記事をスクレイピングし、結果をHTMLに出力します。

<img width="600" alt="dwb_ss1" src="https://user-images.githubusercontent.com/2443513/48303816-d0535000-e552-11e8-8ba5-655b2d396ba8.png">

### 概要
DTMプラグインセール記事をまとめている複数のWebサイトをスクレイピングし、セール記事を収集します。
以下のWebサイトからセール記事を集めます。
* [Computer Music Japan](https://computermusic.jp/category/セール/ "Computer Music Japan")
* [Sleepfreaks](https://sleepfreaks-dtm.com/category/sale/ "Sleepfreaks")
* [MeloDealer](http://melodealer.com/category/dtm/sale-promotion/ "MeloDealer")
* [Sawayaka Trip!](https://sawayakatrip.com/category/dtm・daw関連記事/sale "Sawayaka Trip!")

収集したセール記事には以下の処理がおこなわれます。
* タグの自動付与
* セール期限の自動抽出
* 日付順ソート

収集結果はHTMLで出力されるので、Webブラウザでセール情報を閲覧できます。

### 必要なもの
* Python 3.7.0以上の実行環境
* Pythonサードパーティパッケージ
  * Requests
  * Beautiful Soup 4

### 使い方
#### 1. スクレイピング
`web_scraper.py`を実行し、スクレイピングをおこないます。`-n`オプションで、各サイトからのセール記事取得件数`N`を指定できます。スクレイピングするWebサイトの数を`M`とすると、`N * M`個のセール記事を収集した後、そこから終了済みのセール記事を差し引いたものが最終的な収集結果となります。収集結果は`articles.pickle`へ出力されます。
```
$ python3 script/web_scraper.py -n 100
> Scraping is started. (Run parallelly)
> HTTP GET Request takes 0.353474 [sec] (source : https://computermusic.jp/category/セール/)
> HTTP GET Request takes 0.348843 [sec] (source : https://sawayakatrip.com/category/dtm・daw関連記事/sale)
> HTTP GET Request takes 0.546751 [sec] (source : https://computermusic.jp/category/%E3%82%BB%E3%83%BC%E3%83%AB/page/2/)
⋮
> HTTP GET Request takes 1.683039 [sec] (source : http://melodealer.com/vstbuzz-bigkick-by-plugin-boutique-50per-off-sale/)
> HTTP GET Request takes 1.492022 [sec] (source : http://melodealer.com/vstbuzz-96-off-ultimate-rmx-30k-bundle/)
> HTTP GET Request takes 1.583438 [sec] (source : http://melodealer.com/ik-multimedia-20year/)
> Scraping finished. Scraping takes 189.67374396324158 [sec]
> Results saved to DTMer's-Wallet-Breaker/articles.pickle
```
#### 2. HTML生成
`html_generater.py`を実行し、収集結果を表示するためのHTMLを生成します。生成の際、1.で出力された`articles.pickle`が必要です。`-ob(open browser)`オプションをつけると、生成されたHTMLをWebブラウザで自動で開いてくれます。なお、HTMLファイルは`html`ディレクトリの下に生成されます。
```
$ python3 script/html_generater.py -ob
```
#### 3. Webブラウザで閲覧
2.で`-ob`オプションをつけると、全セール記事のページが表示されます。

<img width="600" alt="dwb_ss2" src="https://user-images.githubusercontent.com/2443513/48304115-3b068a80-e557-11e8-9973-c75025b4d60d.png">

右側に表示されているタグをクリックすると、タグによる絞り込み結果が表示されます。絞り込みに使ったタグは、セール記事件数の右側に表示されます。

<img width="600" alt="dwb_ss3" src="https://user-images.githubusercontent.com/2443513/48304133-aa7c7a00-e557-11e8-9f41-c5b4e56c1274.png">

各タグの()内の数字は、そのタグが付与されたセール記事の件数です。

タグ付けについては、`tags.txt`に書かれたタグ文字列が読み込まれ、記事のタイトルまたは説明文にタグ文字列が含まれているとそのタグが付与されます。どのタグにもマッチしなかった記事には"None"タグが付与されます。

ユーザによって`tags.txt`へ新しいタグを追記することも可能です。
```
None
Ableton
Ableton Live
Accusonus
Addictive Drums
Addictive Keys
⋮
ドラム
バイオリン
ブラックフライデー
ベース
ボーカル
ピアノ
```

ページのフッターにはスクレイピングしたデータの最終更新日時が表示されます。データが古いと感じたら1.のスクレイピングを実行しましょう。

<img width="600" alt="dwb_ss4" src="https://user-images.githubusercontent.com/2443513/48304225-b79a6880-e559-11e8-9a55-b1e459e09131.png">
