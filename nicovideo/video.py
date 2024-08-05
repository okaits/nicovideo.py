"""
このモジュールは、ニコニコの動画を取り扱います。

"""

#pylint: disable=W0212
from __future__ import annotations

import datetime
import functools
import typing
import urllib.error
import urllib.request

import json5

from . import apirawdicts, errors, user

NICOVIDEO_VIDEOPAGE_URL = "https://www.nicovideo.jp/watch/{}?responseType=json"

class _APIResponse():
    """
    動画の詳細（e.g. タイトル, 概要, etc.）を格納するクラスです。
    
    Attributes:
        nicovideo_id (str): ニコニコ動画での動画ID (e.g. sm9)
        title (str): 動画のタイトル
        update (datetime.datetime): このオブジェクトに格納されている情報の取得時刻
        description (str): 動画説明欄
        duration (str): 動画の長さ
        upload_date (datetime.datetime): 動画の投稿時間
        thumbnail (dict[typing.Literal["large", "middle", "ogp", "player", "small"], str]): サムネイル
        counters (dict[typing.Literal["comment", "like", "mylist", "view"], str]): 各種カウンタ
        genre (typing.Optional[dict[typing.Literal["label", "key"], str]]): 動画ジャンル
    """
    __slots__ = ("nicovideo_id", "title", "update", "description", "genre",
                 "duration", "upload_date", "thumbnails", "_rawdict", "counters")
    nicovideo_id: str
    _rawdict: apirawdicts.VideoAPIRawDicts.RawDict
    title: str
    update: datetime.datetime
    description: str
    duration: int
    upload_date: datetime.datetime
    thumbnails: dict[typing.Literal["large", "middle", "ogp", "player", "small"], str]
    counters: dict[typing.Literal["comment", "like", "mylist", "view"], str]
    genre: typing.Optional[dict[typing.Literal["label", "key"], str]]

    @property
    def uploader(self) -> user._APIResponse:
        """動画の投稿者を取得する。"""
        return user.get_metadata(user_id=int(self._rawdict["owner"]["id"]))

    @property
    @functools.cache
    def cached_uploader(self) -> user._APIResponse:
        """動画の投稿者を取得する。（初回にキャッシュするので最新ではない可能性がある。）"""
        return self.uploader

    def __setattr__(self, _, name) -> typing.NoReturn:
        raise errors.FrozenInstanceError(f"cannot assign to field '{name}'")
    def __delattr__(self, name) -> typing.NoReturn:
        raise errors.FrozenInstanceError(f"cannot delete field {name}")
    def __repr__(self) -> str:
        return f"video.APIResponse(video_id={self.nicovideo_id})"
    def __str__(self) -> str:
        return self.title
    def __hash__(self) -> int:
        return int("".join(
            [str(object=ord(character)) for character in self.nicovideo_id]
        ))

APIResponse = typing.NewType("APIResponse", _APIResponse)

def get_metadata(video_id: str) -> APIResponse:
    """
    ニコニコのAPIサーバから動画情報を取得します。

    Args:
        video_id (str): 対象となる動画の、ニコニコ動画での動画ID (e.g. sm9)
    Returns:
        APIResponse: 取得結果
    Raises:
        errors.ContentNotFoundError: 指定された動画が存在しなかった場合に送出。
        errors.APIRequestError: ニコニコのAPIサーバへのリクエストに失敗した場合に送出。
    Example:
        >>> get_metadata("sm9")
    """
    gotapiresponse = _APIResponse()
    object.__setattr__(gotapiresponse, "nicovideo_id", video_id)

    try:
        with urllib.request.urlopen(url=NICOVIDEO_VIDEOPAGE_URL.format(video_id)) as res:
            response_text = res.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise errors.ContentNotFoundError from exc
        raise errors.APIRequestError from exc
    except urllib.error.URLError as exc:
        raise errors.APIRequestError from exc

    object.__setattr__(gotapiresponse, "_rawdict", json5.loads(response_text)["data"]["response"])
    if gotapiresponse._rawdict is None:
        raise errors.APIRequestError("Invalid response from server.")

    object.__setattr__(gotapiresponse, "title", gotapiresponse._rawdict["video"]["title"])
    object.__setattr__(gotapiresponse, "update", datetime.datetime.now())
    object.__setattr__(gotapiresponse, "description",
                       gotapiresponse._rawdict["video"]["description"])
    object.__setattr__(gotapiresponse, "duration", gotapiresponse._rawdict["video"]["duration"])
    object.__setattr__(gotapiresponse, "upload_date", datetime.datetime.fromisoformat(
        gotapiresponse._rawdict["video"]["registeredAt"]
    ))
    object.__setattr__(gotapiresponse, "thumbnails", {
        "large": gotapiresponse._rawdict["video"]["thumbnail"]["largeUrl"],
        "middle": gotapiresponse._rawdict["video"]["thumbnail"]["middleUrl"],
        "ogp": gotapiresponse._rawdict["video"]["thumbnail"]["ogp"],
        "player": gotapiresponse._rawdict["video"]["thumbnail"]["player"],
        "small": gotapiresponse._rawdict["video"]["thumbnail"]["url"]
    })
    object.__setattr__(gotapiresponse, "counters", {
        "comment": gotapiresponse._rawdict["video"]["count"]["comment"],
        "like": gotapiresponse._rawdict["video"]["count"]["like"],
        "mylist": gotapiresponse._rawdict["video"]["count"]["mylist"],
        "view": gotapiresponse._rawdict["video"]["count"]["view"]
    })
    if gotapiresponse._rawdict["genre"]:
        object.__setattr__(gotapiresponse, "genre", {
            "label": gotapiresponse._rawdict["genre"]["label"],
            "key": gotapiresponse._rawdict["genre"]["key"]
        })
    else:
        object.__setattr__(gotapiresponse, "genre", None)
    return APIResponse(gotapiresponse)
