"""
このモジュールは、ニコニコの動画を取り扱います。

"""
from __future__ import annotations

import datetime
import functools
import typing
import urllib.error
import urllib.request

import bs4
import json5

from . import apirawdicts, errors, user

NICOVIDEO_VIDEOPAGE_URL = "https://www.nicovideo.jp/watch/{}"

class APIResponse():
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
        genre (dict[typing.Literal["label", "key"], str]): 動画ジャンル
    """
    __slots__ = ("nicovideo_id", "title", "update", "description",
                 "duration", "upload_date", "_rawdict")
    nicovideo_id: str
    _rawdict: apirawdicts.VideoAPIRawDicts.RawDict
    title: str
    update: datetime.datetime
    description: str
    duration: int
    upload_date: datetime.datetime
    thumbnails: dict[typing.Literal["large", "middle", "ogp", "player", "small"], str]
    counters: dict[typing.Literal["comment", "like", "mylist", "view"], str]
    genre: dict[typing.Literal["label", "key"], str]

    def __init__(self, video_id: str):
        """
        ニコニコのAPIサーバから動画情報を取得します。

        Args:
            video_id (str): 対象となる動画の、ニコニコ動画での動画ID (e.g. sm9)
        Raises:
            errors.ContentNotFoundError: 指定された動画が存在しなかった場合に送出。
            errors.APIRequestError: ニコニコのAPIサーバへのリクエストに失敗した場合に送出。
        Example:
            >>> APIResponse("sm9")
        """
        super().__setattr__("nicovideo_id", video_id)

        try:
            with urllib.request.urlopen(url=NICOVIDEO_VIDEOPAGE_URL.format(video_id)) as res:
                response_text = res.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise errors.ContentNotFoundError from exc
            raise errors.APIRequestError from exc
        except urllib.error.URLError as exc:
            raise errors.APIRequestError from exc

        soup = bs4.BeautifulSoup(markup=response_text, features="html.parser")
        super().__setattr__("_rawdict", json5.loads(
            str(object=soup.select(selector="#js-initial-watch-data")[0]["data-api-data"])
        ))
        if self._rawdict is None:
            raise errors.APIRequestError("Invalid response from server.")

        super().__setattr__("title", self._rawdict["video"]["title"])
        super().__setattr__("update", datetime.datetime.now())
        super().__setattr__("description", self._rawdict["video"]["description"])
        super().__setattr__("duration", self._rawdict["video"]["duration"])
        super().__setattr__("upload_date", datetime.datetime.fromisoformat(
            self._rawdict["video"]["registeredAt"]
        ))
        super().__setattr__("thumbnail", {
            "large": self._rawdict["video"]["thumbnail"]["largeUrl"],
            "middle": self._rawdict["video"]["thumbnail"]["middleUrl"],
            "ogp": self._rawdict["video"]["thumbnail"]["ogp"],
            "player": self._rawdict["video"]["thumbnail"]["player"],
            "small": self._rawdict["video"]["thumbnail"]["url"]
        })
        super().__setattr__("counters", {
            "comment": self._rawdict["video"]["count"]["comment"],
            "like": self._rawdict["video"]["count"]["like"],
            "mylist": self._rawdict["video"]["count"]["mylist"],
            "view": self._rawdict["video"]["count"]["view"]
        })
        super().__setattr__("genre", {
            "label": self._rawdict["genre"]["label"],
            "key": self._rawdict["genre"]["key"]
        })

    @property
    def uploader(self) -> user.APIResponse:
        """動画の投稿者を取得する。"""
        return user.APIResponse(user_id=int(self._rawdict["owner"]["id"]))

    @functools.cached_property
    def cached_uploader(self) -> user.APIResponse:
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
