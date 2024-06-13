# nicovideo package

## Submodules

## nicovideo.apirawdicts module

このモジュールでは、ニコニコのAPIから取得した生データのTypedDictを定義します。
モジュール内部での型ヒント用のため、通常利用時に考慮する必要はありません。

## nicovideo.errors module

このモジュールは、nicovideo.py全般にて送出される例外を定義します。

### *exception* nicovideo.errors.APIRequestError

Bases: `RuntimeError`

ニコニコのAPIサーバへのリクエストに失敗した。

### *exception* nicovideo.errors.ContentNotFoundError

Bases: [`APIRequestError`](#nicovideo.errors.APIRequestError)

指定されたコンテンツが見つからなかった。

### *exception* nicovideo.errors.FrozenInstanceError

Bases: `AttributeError`

イミュータブルなオブジェクトの属性に代入しようとした。

## nicovideo.user module

このモジュールは、ニコニコのユーザを扱います。

### *class* nicovideo.user.APIResponse(user_id: int)

Bases: `object`

ユーザの詳細 (e.g. ニックネーム, 投稿動画, etc.) を格納するクラスです。

#### user_id

ニコニコ動画でのID (e.g. 9003560)

* **Type:**
  int

#### nickname

ニックネーム

* **Type:**
  str

#### description

ユーザ説明欄

* **Type:**
  tuple[*Annoatated*[str, “HTML”], *Annotated*[str, “Plain”]]

#### subscription

会員種別 (プレミアム会員もしくは一般会員)

* **Type:**
  *Literal*[“premium”, “general”]

#### version

登録時のニコニコのバージョン (e.g. eR)

* **Type:**
  str

#### followee

フォロイー数 (フォロー数)

* **Type:**
  int

#### follower

フォロワー数

* **Type:**
  int

#### level

ユーザレベル

* **Type:**
  int

#### exp

ユーザEXP

* **Type:**
  int

#### sns

連携されているSNS

* **Type:**
  frozenset[tuple[*Annotated*[str, “SNSの名前”], *Annotated*[str, “SNSのユーザ名”], *Annotated*[str, “SNSのアイコン (PNG)”]]]

#### cover

ユーザのカバー画像

* **Type:**
  *Optional*[tuple[*Annotated*[str, “PC用画像のURL”], *Annotated*[str, “OGP用画像のURL”], *Annotated*[str, “SP用画像のURL”]]]

#### icon

ユーザアイコン

* **Type:**
  tuple[*Annotated*[str, “小アイコン画像のURL”], *Annotated*[str, “大アイコン画像のURL”]]

#### *property* videolist *: Generator[[APIResponse](#nicovideo.video.APIResponse), None, None]*

ユーザが投稿した動画を一つずつ、video.APIResponseにしてからyieldします。
nextごとにニコニコ動画でのAPIリクエストが発生するため、注意してください。

* **Yields:**
  *video.APIResponse* – ユーザの投稿動画

## nicovideo.video module

このモジュールは、ニコニコの動画を取り扱います。

### *class* nicovideo.video.APIResponse(video_id: str)

Bases: `object`

動画の詳細（e.g. タイトル, 概要, etc.）を格納するクラスです。

#### nicovideo_id

ニコニコ動画での動画ID (e.g. sm9)

* **Type:**
  str

#### title

動画のタイトル

* **Type:**
  str

#### update

このオブジェクトに格納されている情報の取得時刻

* **Type:**
  datetime.datetime

#### description

動画説明欄

* **Type:**
  str

#### duration

動画の長さ

* **Type:**
  str

#### upload_date

動画の投稿時間

* **Type:**
  datetime.datetime

#### *property* cached_uploader *: [APIResponse](#nicovideo.user.APIResponse)*

動画の投稿者を取得する。（初回にキャッシュするので最新ではない可能性がある。）

#### *property* uploader *: [APIResponse](#nicovideo.user.APIResponse)*

動画の投稿者を取得する。

## Module contents

nicovideo.py: nicovideo API wrapper for Python3.
