# nicovideo.py
## What's this
ニコニコ動画に投稿された動画の情報を取得するライブラリです。動画をダウンロードすることはできません。

## 使い方
### 初期設定
Python3を使える環境を作り、cloneしたらrequirements.txtから依存モジュールをインストールしてください。  

```bash
python3 -m pip install -r requirements.txt
```

### 情報取得
このようにすると、動画の情報を取得できます。

```python3
import nicovideo
video = nicovideo.Video('動画ID')
metadata = video.get_metadata()
```

## クラス・関数やその返り値など
### `class Video(videoid: str = 動画ID) -> Video`
動画のクラスです。  
  
インスタンス変数一覧:
```
videoid: str = 動画ID
rawdict: dict = 取得した生データ（Video.get_metadataを実行するまではNone）
```

#### `def Video.get_metadata() -> Video.Metadata`
動画のメタデータを取得するメソッドです。

#### `class Video.Metadata(長すぎるので省略) -> Video.Metadata`
動画のメタデータのクラスです。   

インスタンス変数一覧:
```
videoid: str = 動画ID
title: str = 動画タイトル
description: str = 動画概要
owner: Video.Metadata.User = 投稿者
counts: Video.Metadata.Counts = 各種カウンター
duration: int = 動画長（秒）
postdate: datetime.datetime = 投稿日時
genre: Video.Metadata.Genre = ジャンル
tags: list[Video.Metadata.Tag] = タグ一覧
ranking: Video.Metadata.Ranking = ランキングデータ
series: Video.Metadata.Series = シリーズ
thumbnail: Video.Metadata.Thumbnail = サムネイル
url: str = 視聴URL
```

##### `class Video.Metadata.User(nickname: str = ユーザーのニックネーム, id: str = ユーザーID) -> Video.Metadata.User`
ユーザーのクラスです。投稿者などを表します。  
  
インスタンス変数一覧:
```
nickname: str = ユーザーニックネーム
id: int = ユーザーID
```

##### `class Video.Metadata.Counts(comments: int = コメント数, likes: int = いいね！数, mylists: int = マイリス数, views: id = 再生数) -> Video.Metadata.Counts`
各種カウンターのクラスです。再生数などのカウンターを表します。  
  
インスタンス変数一覧:
```
comments: int = コメント数
likes: int = いいね！数
mylists: int = マイリスト数
views: int = 再生数
```

##### `class Video.Metadata.Genre(label: str = ジャンル名, key: ジャンルの内部キー) -> Video.Metadata.Genre`
ジャンルのクラスです。  
  
インスタンス変数一覧:
```
label: str = ジャンル名
key: str = 内部識別キー
```

##### `class Video.Metadata.Tag(name: str = タグ名, locked: bool = タグロック) -> Video.Metadata.Tag`
タグのクラスです。  
  
インスタンス変数一覧:
```
name: str = タグ名
locked: bool = タグロック
```
##### `class Video.Metadata.Ranking(genreranking: Union[Video.Metadata.Ranking.Genre, NoneType] = ジャンルのランキング情報, tagrankings: list[Video.Metadata.Ranking.Tag] = タグ別のランキング情報)`
ランキングのクラスです。  
  
インスタンス変数一覧:
```
genreranking: Union[Video.Metadata.Ranking.Genre, NoneType] = ジャンルのランキング情報
tagrankings: list[Video.Metadata.Ranking.Tag] = タグ別のランキング情報
```
###### `class Video.Metadata.Ranking.Genre(genre: Video.Metadata.Genre = ジャンル, rank: int = ランキング最高順位, time: datetime.datetime = 順位獲得日時)`
ランキング情報とジャンルをまとめて収納するクラスです。  
  
インスタンス変数一覧:
```
genre: Video.Metadata.Genre = ジャンル
rank: int = ランキング最高順位
time: datetime.datetime = 順位獲得日時
```
###### `class Video.Metadata.Ranking.Tag(tag: Video.Metadata.Tag = タグ, rank: int = ランキング最高順位, time: datetime.datetime - 順位獲得日時)`
Video.Metadata.Ranking.Genreと使い方は同じなのでカット。

##### `Class Video.Metadata.Series(seriesid: int = シリーズID, title: str = シリーズタイトル, description: str = シリーズ概要, thumbnail: str = サムネイルURL, prev_video: Union[Video, NoneType] = 前動画, next_video: Union[Video, NoneType] = 次動画, first_video: Union[Video, NoneType] = 最初の動画)`
シリーズのクラスです。  
  
```
id: int = シリーズID
title: str = シリーズタイトル
description: str = シリーズ概要
thumbnail: str = サムネイルURL
prev_video: Union[Video, NoneType] = 前動画
next_video: Union[Video, NoneType] = 次動画
first_video: Union[Video, NoneType] = 最初の動画
```

##### `Class Video.Metadata.Thumbnail(small_url: str = サムネイル（小）URL, middle_url: str = サムネイル（中）URL, large_url: str = サムネイル（大）URL, player_url: str = サムネイル（プレイヤー用）URL, ogp_url: str = サムネイル（OGP表示用）URL)`
サムネイル画像のクラスです。  
  
```
small_url: str = サムネイル（小）URL
middle_url: str = サムネイル（中）URL
large_url: str = サムネイル（大）URL
player_url: str = サムネイル（プレイヤー用）URL
ogp_url: str = サムネイル（OGP表示用）URL
```
# License
適用ライセンス: LGPL 3.0  
Copyright © 2023 okaits#7534