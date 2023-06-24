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
### class Video
動画のクラスです。  
  
インスタンス変数一覧:
```
videoid: str = 動画ID
rawdict: dict = 取得した生データ（Video.get_metadataを実行するまではNone）
```

#### def Video.get_metadata() -> Video.Metadata
動画のメタデータを取得するメソッドです。

#### class Video.Metadata
動画のメタデータのクラスです。   

インスタンス変数一覧:
```
videoid: str = 動画ID
title: str = 動画タイトル
owner: Video.Metadata.User = 投稿者
counts: Video.Metadata.Counts = 各種カウンター
duration: int = 動画長（秒）
postdate: datetime.datetime = 投稿日時
genre: Video.Metadata.Genre = ジャンル
tags: list[Video.Metadata.Tag] = タグ一覧
```

##### class Video.Metadata.User
ユーザーのクラスです。投稿者などを表します。  
  
インスタンス変数一覧:
```
nickname: str = ユーザーニックネーム
id: int = ユーザーID
```

##### class Video.Metadata.Counts
各種カウンターのクラスです。再生数などのカウンターを表します。  
  
インスタンス変数一覧:
```
comments: int = コメント数
likes: int = いいね！数
mylists: int = マイリスト数
views: int = 再生数
```

##### class Video.Metadata.Genre
ジャンルのクラスです。  
  
インスタンス変数一覧:
```
label: str = ジャンル名
key: str = 内部識別キー
```

##### class Video.Metadata.Tag
タグのクラスです。  
  
インスタンス変数一覧:
```
name: str = タグ名
locked: bool = タグロック
```

# License
適用ライセンス: LGPL 3.0  
Copyright © 2023 okaits#7534