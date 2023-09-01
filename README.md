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
metadata = video.get_metadata()['data']
```

## クラス・関数やその返り値など
凡例:  
`class クラス名(初期化時の引数: 型ヒント = デフォルト値, ...)`  
`def   関数名(引数: 型ヒント = デフォルト値, ...) -> 返り値型ヒント`

### `def Video.get_metadata(videoid: str, return_rawdict: bool = False, use_cache: bool = False) -> ...`
動画のメタデータを取得する関数です。  
  
返り値:
```python3
# return_rawdictがTrueの場合:
{
    "data": 指定された動画の動画情報のパース結果（Video.Metadata）,
    "rawdict": パース前のウェブサイトから直接取得したデータ（dict）
}

# return_rawdictが未指定/Falseの場合:
指定された動画の動画情報のパース結果（Video.Metadata）
```

### `class Video(videoid: str = 動画ID)`
動画のクラスです。このクラスはネストされた物を含めてすべて`get_metadata()`が管理するので、基本的には手動で初期化することはありません。  

#### `class Video.Metadata(...)`
動画のメタデータを格納するクラスです。`get_metadata()`の返り値に含まれます。   

インスタンス変数一覧:
```
videoid    : str                             = 動画ID
title      : str                             = 動画タイトル
description: str                             = 動画概要
owner      : Video.Metadata.User             = 投稿者
counts     : Video.Metadata.Counts           = 各種カウンター
duration   : int                             = 動画長（秒）
postdate   : datetime.datetime               = 投稿日時
genre      : Optional[Video.Metadata.Genre]  = ジャンル
tags       : list[Video.Metadata.Tag]        = タグ一覧
ranking    : Video.Metadata.Ranking          = ランキングデータ
series     : Optional[Video.Metadata.Series] = シリーズ
thumbnail  : Video.Metadata.Thumbnail        = サムネイル
url        : str                             = 視聴URL
```

##### `class Video.Metadata.User(...)`
ユーザーのクラスです。投稿者などを表します。  
  
インスタンス変数一覧:
```
nickname: str = ユーザーニックネーム
userid  : int = ユーザーID
```

##### `class Video.Metadata.Counts(...)`
各種カウンターのクラスです。再生数などのカウンターを表します。  
  
インスタンス変数一覧:
```
comments: int = コメント数
likes   : int = いいね！数
mylists : int = マイリスト数
views   : int = 再生数
```

##### `class Video.Metadata.Genre(...)`
ジャンルのクラスです。  
  
インスタンス変数一覧:
```
label: str = ジャンル名
key  : str = ジャンルの内部識別キー
```

##### `class Video.Metadata.Tag(...)`
タグのクラスです。  
  
インスタンス変数一覧:
```
name  : str  = タグ名
locked: bool = タグロック
```

##### `class Video.Metadata.Ranking(...)`
ランキングのクラスです。  
  
インスタンス変数一覧:
```
genreranking: Union[Video.Metadata.Ranking.Genre, NoneType] = ジャンルのランキング情報
tagrankings : list[Video.Metadata.Ranking.Tag]              = タグ別のランキング情報
```
###### `class Video.Metadata.Ranking.Genre(...)`
ジャンル別ランキングを格納するクラスです。  
  
インスタンス変数一覧:
```
genre: Video.Metadata.Genre = ジャンル
rank : int                  = ランキング最高順位
time : datetime.datetime    = 順位獲得日時
```

###### `class Video.Metadata.Ranking.Tag(...)`
タグ別ランキングを格納するクラスです。  
  
インスタンス変数一覧:
```
tag : Video.Metadata.Tag = タグ
rank: int                = ランキング最高順位
time: datetime.datetime  = 順位獲得日時
```

##### `Class Video.Metadata.Series(...)`
シリーズのクラスです。  
  
```
seriesid   : int                    = シリーズID
title      : str                    = シリーズタイトル
description: str                    = シリーズ概要
thumbnail  : str                    = サムネイルURL
prev_video : Union[Video, NoneType] = 前動画
next_video : Union[Video, NoneType] = 次動画
first_video: Union[Video, NoneType] = 最初の動画
```

##### `Class Video.Metadata.Thumbnail(...)`
サムネイル画像のクラスです。  
  
```
small_url : str = サムネイル（小）URL
middle_url: str = サムネイル（中）URL
large_url : str = サムネイル（大）URL
player_url: str = サムネイル（プレイヤー用）URL
ogp_url   : str = サムネイル（OGP表示用）URL
```
# License
適用ライセンス: LGPL 3.0  
Copyright © 2023 okaits#7534