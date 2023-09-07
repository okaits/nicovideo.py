# nicovideo.py
## What's this
ニコニコ動画に投稿された動画の情報を取得するライブラリです。動画をダウンロードすることはできません。

## 使い方
### 初期設定
Python3を使える環境を作り、こんな感じにインストールしてください。

```bash
python3 -m pip install nicovideo.py
```

### 情報取得
このようにすると、動画やユーザーの情報を取得できます。

```python3
import nicovideo

# 動画: sm9（新・豪血寺一族 -煩悩解放 - レッツゴー！陰陽師）
sm9 = nicovideo.Video.get_metadata("sm9")
print(f"タイトル: {sm9.title}")
print(f"再生数: {sm9.counts.views}")

# ユーザー: user/9003560（くりたしげたか）
kurita = nicovideo.User.get_metadata(9003560)
print(f"ニックネーム: {kurita.nickname}")
print(f"ユーザーレベル: {kurita.user_level}")

```

## クラス・関数やその返り値など
凡例:  
`class クラス名(初期化時の引数: 型ヒント = デフォルト値, ...)`  
`def   関数名(引数: 型ヒント = デフォルト値, ...) -> 返り値型ヒント`

### `class Video()`
動画のクラスです。

#### `(classmethod) def Video.get_metadata(videoid: str, *, use_cache: bool = False)`
動画のメタデータを取得するメソッドです。  
  
返り値: `Video.Metadata`

#### `class Video.Metadata(...)`
動画のメタデータを格納するクラスです。`Video.get_metadata()`の返り値です。   

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
rawdict    : dict                            = サーバーから取得した加工前生データ（デバッグ用）
```

##### `class Video.Metadata.User(...)`
ユーザーのクラスです。投稿者などを表します。（`User`クラスの簡易版です。）
  
インスタンス変数一覧:
```
nickname: str = ユーザーニックネーム
userid  : int = ユーザーID
```

###### `def Video.Metadata.User.get_metadata() -> User.Metadata`
`Video.Metadata.User`インスタンスを`User.Metadata`インスタンスに変換します。

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
genreranking: Optional[Video.Metadata.Ranking.Genre] = ジャンルのランキング情報
tagrankings : list[Video.Metadata.Ranking.Tag]       = タグ別のランキング情報
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

##### `class Video.Metadata.Series(...)`
シリーズのクラスです。  
  
```
seriesid   : int             = シリーズID
title      : str             = シリーズタイトル
description: str             = シリーズ概要
thumbnail  : str             = サムネイルURL
prev_video : Optional[Video] = 前動画
next_video : Optional[Video] = 次動画
first_video: Optional[Video] = 最初の動画
```

##### `class Video.Metadata.Thumbnail(...)`
サムネイル画像のクラスです。  
  
```
small_url : str = サムネイル（小）URL
middle_url: str = サムネイル（中）URL
large_url : str = サムネイル（大）URL
player_url: str = サムネイル（プレイヤー用）URL
ogp_url   : str = サムネイル（OGP表示用）URL
```

### `class User()`
ユーザーのクラスです。

#### `(classmethod) def User.get_metadata(userid: int, *, use_cache: bool = False)`
ユーザーのメタデータを取得するメソッドです。  
  
返り値: `User.Metadata`

#### `class User.Metadata(...)`
動画のメタデータを格納するクラスです。`User.get_metadata()`の返り値です。   

インスタンス変数一覧:
```
nickname          : str                           = ユーザーニックネーム
userid            : int                           = ユーザーID
description       : User.Metadata.Description     = ユーザー説明欄（bio）
user_type         : Literal["Premium", "General"] = ユーザータイプ（Premium/General）
registered_version: str                           = 登録時バージョン
follow            : int                           = フォロー数
follower          : int                           = フォロワー数
user_level        : int                           = ユーザーレベル
user_exp          : int                           = ユーザーEXP
sns               : list[User.Metadata.SNS.User]  = SNS連携情報
cover             : Optional[User.Metadata.Cover] = カバー画像
icon              : User.Metadata.UserIcon        = アイコン画像
rawdict           : dict                          = サーバーから取得した加工前生データ（デバッグ用）
```

##### `class User.Description(...)`
ユーザーの説明文(bio)です。  
  
インスタンス変数一覧:
```
description_html : str = 説明欄（text/html）
description_plain: str = 説明欄（text/plain）
```

##### `class User.SNS(...)`
ユーザーのプロフィールに載ってるSNSについてのクラスです。

###### `class User.SNS.Service(...)`
SNSサービスの名称とかアイコンとかです。  
  
インスタンス変数一覧:
```
name: str = SNSサービス名称
key : str = SNSのタイプ
icon: str = SNSのロゴ（PNGファイルのURL）
```

###### `class User.SNS.User(...)`
SNSユーザーについてのクラスです。  
  
インスタンス変数一覧:
```
service: User.Metadata.SNS.Service = SNSサービス
name   : str                       = SNSユーザー名
url    : str                       = SNSプロフィールURL
```

##### `class User.Cover(...)`
ユーザーのカバー画像についてのクラスです。  
  
インスタンス変数一覧:
```
ogp: str = OGP用カバー画像URL
pc : str = PCサイズカバー画像URL
sp : str = SP（スマートフォン）サイズカバー画像
```

##### `class User.UserIcon(...)`
ユーザーアイコンについてのクラスです。  
  
インスタンス変数一覧:
```
small: str = ユーザーアイコン（小）URL
large: str = ユーザーアイコン（大）URL
```

# License
適用ライセンス: LGPL 3.0  
Copyright © 2023 okaits#7534