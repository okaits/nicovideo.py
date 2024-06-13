"""
このモジュールは、ニコニコのユーザを扱います。

"""
from __future__ import annotations

import typing
import urllib.error
import urllib.request
import collections.abc

import bs4
import json5

from . import errors
from . import apirawdicts
from . import video

NICOVIDEO_USERPAGE_URL = "https://www.nicovideo.jp/user/{}/video"

class APIResponse():
    """
    ユーザの詳細 (e.g. ニックネーム, 投稿動画, etc.) を格納するクラスです。

    Attributes:
        user_id (int): ニコニコ動画でのID (e.g. 9003560)
        nickname (str): ニックネーム
        description (tuple[typing.Annoatated[str, "HTML"], typing.Annotated[str, "Plain"]]): ユーザ説明欄
        subscription (typing.Literal["premium", "general"]): 会員種別 (プレミアム会員もしくは一般会員)
        version (str): 登録時のニコニコのバージョン (e.g. eR)
        followee (int): フォロイー数 (フォロー数)
        follower (int): フォロワー数
        level (int): ユーザレベル
        exp (int): ユーザEXP
        sns (frozenset[tuple[typing.Annotated[str, "SNSの名前"], typing.Annotated[str, "SNSのユーザ名"], typing.Annotated[str, "SNSのアイコン (PNG)"]]]): 連携されているSNS
        cover (typing.Optional[tuple[typing.Annotated[str, "PC用画像のURL"], typing.Annotated[str, "OGP用画像のURL"], typing.Annotated[str, "SP用画像のURL"]]]): ユーザのカバー画像
        icon (tuple[typing.Annotated[str, "小アイコン画像のURL"], typing.Annotated[str, "大アイコン画像のURL"]]): ユーザアイコン
    """
    __slots__ = ("user_id", "nickname", "description", "subscription", "version", "followee",
                 "follower", "level", "exp", "sns", "cover", "icon", "_rawdict")
    user_id: int
    nickname: str
    description: tuple[typing.Annotated[str, "HTML"], typing.Annotated[str, "Plain"]]
    subscription: typing.Literal["premium", "general"]
    version: str
    followee: int
    follower: int
    level: int
    exp: int
    sns: frozenset[
        tuple[
            typing.Annotated[str, "SNSの名前"],
            typing.Annotated[str, "SNSのユーザ名"],
            typing.Annotated[str, "SNSのアイコン (PNG)"]
        ]
    ]
    cover: typing.Optional[
        tuple[
            typing.Annotated[str, "PC用画像のURL"],
            typing.Annotated[str, "OGP用画像のURL"],
            typing.Annotated[str, "SP用画像のURL"]
        ]
    ]
    icon: tuple[typing.Annotated[str, "小アイコン画像のURL"], typing.Annotated[str, "大アイコン画像のURL"]]

    def __init__(self, user_id: int) -> None:
        """
        ニコニコのAPIサーバからユーザ情報を取得します。

        Args:
            user_id (int): 対象となるユーザの、ニコニコ動画でのID (e.g. 9003560)
        Raises:
            errors.ContentNotFoundError: 指定された動画が存在しなかった場合に送出。
            errors.APIRequestError: ニコニコのAPIサーバへのリクエストに失敗した場合に送出。
        Example:
            >>> APIResponse(9003560)
        """
        try:
            with urllib.request.urlopen(url=NICOVIDEO_USERPAGE_URL.format(user_id)) as res:
                response_text = res.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise errors.ContentNotFoundError from exc
            raise errors.APIRequestError from exc
        except urllib.error.URLError as exc:
            raise errors.APIRequestError from exc

        soup = bs4.BeautifulSoup(markup=response_text, features="html.parser")
        self._rawdict: apirawdicts.UserAPIRawDicts.RawDict
        super().__setattr__("_rawdict", json5.loads(
            str(object=soup.select("#js-initial-userpage-data")[0]["data-initial-data"])
        ))
        if self._rawdict is None:
            raise errors.APIRequestError("Invalid response from server.")
        rawdict_userdata = self._rawdict["state"]["userDetails"]["userDetails"]["user"]
        self.nickname: str
        super().__setattr__("nickname", rawdict_userdata["nickname"])
        super().__setattr__("description", (rawdict_userdata["decoratedDescriptionHtml"],
                                            rawdict_userdata["strippedDescription"]))
        super().__setattr__("subscription",
                            "premium" if rawdict_userdata["isPremium"] else "general")
        super().__setattr__("version", rawdict_userdata["registeredVersion"])
        super().__setattr__("followee", rawdict_userdata["foloweeCount"])
        super().__setattr__("follower", rawdict_userdata["folowerCount"])
        super().__setattr__("level", rawdict_userdata["userLevel"]["currentLevel"])
        super().__setattr__("exp", rawdict_userdata["userLevel"]["currentLevelExperience"])
        super().__setattr__("sns", frozenset(
            [(sns["type"], sns["label"], sns["iconUrl"]) for sns in rawdict_userdata["sns"]]
        ))
        super().__setattr__("cover", (
            rawdict_userdata["coverImage"]["pcUrl"],
            rawdict_userdata["coverImage"]["ogpUrl"],
            rawdict_userdata["coverImage"]["smartphoneUrl"]
        ))
        super().__setattr__("icon", (
            rawdict_userdata["icons"]["small"],
            rawdict_userdata["icons"]["large"]
        ))

    @property
    def videolist(self) -> collections.abc.Generator[video.APIResponse, None, None]:
        """
        ユーザが投稿した動画を一つずつ、video.APIResponseにしてからyieldします。
        nextごとにニコニコ動画でのAPIリクエストが発生するため、注意してください。

        Yields:
            video.APIResponse: ユーザの投稿動画
        """
        rawdict_videolist = self._rawdict["nvapi"]["data"][0]["items"]
        for rawdict_video in rawdict_videolist:
            yield video.APIResponse(rawdict_video["essential"]["id"])

    def __setattr__(self, _, name) -> typing.NoReturn:
        raise errors.FrozenInstanceError(f"cannot assign to field '{name}'")
    def __delattr__(self, name) -> typing.NoReturn:
        raise errors.FrozenInstanceError(f"cannot delete field {name}")
    def __repr__(self) -> str:
        return f"user.APIResponse(user_id={self.user_id})"
    def __str__(self) -> str:
        return self.nickname
    def __hash__(self) -> int:
        return self.user_id
