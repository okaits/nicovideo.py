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

### nicovideo.user.get_metadata(user_id: int)

ニコニコのAPIサーバからユーザ情報を取得します。

* **Parameters:**
  **user_id** (*int*) – 対象となるユーザの、ニコニコ動画でのID (e.g. 9003560)
* **Returns:**
  取得結果
* **Return type:**
  APIResponse
* **Raises:**
  * [**errors.ContentNotFoundError**](#nicovideo.errors.ContentNotFoundError) – 指定された動画が存在しなかった場合に送出。
  * [**errors.APIRequestError**](#nicovideo.errors.APIRequestError) – ニコニコのAPIサーバへのリクエストに失敗した場合に送出。

### Example

```pycon
>>> get_metadata(9003560)
```

## nicovideo.video module

このモジュールは、ニコニコの動画を取り扱います。

### nicovideo.video.get_metadata(video_id: str)

ニコニコのAPIサーバから動画情報を取得します。

* **Parameters:**
  **video_id** (*str*) – 対象となる動画の、ニコニコ動画での動画ID (e.g. sm9)
* **Returns:**
  取得結果
* **Return type:**
  APIResponse
* **Raises:**
  * [**errors.ContentNotFoundError**](#nicovideo.errors.ContentNotFoundError) – 指定された動画が存在しなかった場合に送出。
  * [**errors.APIRequestError**](#nicovideo.errors.APIRequestError) – ニコニコのAPIサーバへのリクエストに失敗した場合に送出。

### Example

```pycon
>>> get_metadata("sm9")
```

## Module contents

nicovideo.py: nicovideo API wrapper for Python3.
