"""
このモジュールは、ニコニコのユーザを扱います。

"""

#pylint: disable=W0212
from __future__ import annotations

import typing
import urllib.error
import urllib.request
import collections.abc

import json5
import bs4

from . import errors
from . import apirawdicts
from . import video

NICOVIDEO_USERPAGE_URL = "https://www.nicovideo.jp/user/{}/video?responseType=json"

class _APIResponse():
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
    _rawdict: apirawdicts.UserAPIRawDicts.RawDict
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

    @property
    def videolist(self) -> collections.abc.Generator[video.APIResponse, None, None]:
        """
        ユーザが投稿した動画を一つずつ、video.APIResponseにしてからyieldします。
        nextごとにニコニコ動画でのAPIリクエストが発生するため、注意してください。

        Yields:
            video.APIResponse: ユーザの投稿動画
        """
        rawdict_videolist = self._rawdict["nvapi"][0]["body"]["data"]["items"]
        for rawdict_video in rawdict_videolist:
            yield video.get_metadata(rawdict_video["essential"]["id"])

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

APIResponse = typing.NewType("APIResponse", _APIResponse)

def get_metadata(user_id: int) -> APIResponse:
    """
    ニコニコのAPIサーバからユーザ情報を取得します。

    Args:
        user_id (int): 対象となるユーザの、ニコニコ動画でのID (e.g. 9003560)
    Returns:
        APIResponse: 取得結果
    Raises:
        errors.ContentNotFoundError: 指定された動画が存在しなかった場合に送出。
        errors.APIRequestError: ニコニコのAPIサーバへのリクエストに失敗した場合に送出。
    Example:
        >>> get_metadata(9003560)
    """
    gotapiresponse = _APIResponse()
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
    object.__setattr__(gotapiresponse, "_rawdict", json5.loads(
        str(object=soup.select("#js-initial-userpage-data")[0]["data-initial-data"])
    ))

    if gotapiresponse._rawdict is None:
        raise errors.APIRequestError("Invalid response from server.")
    rawdict_userdata = gotapiresponse._rawdict["state"]["userDetails"]["userDetails"]["user"]
    object.__setattr__(gotapiresponse, "user_id", user_id)
    object.__setattr__(gotapiresponse, "nickname", rawdict_userdata["nickname"])
    object.__setattr__(gotapiresponse, "description",
                            (rawdict_userdata["decoratedDescriptionHtml"],
                             rawdict_userdata["strippedDescription"])
                      )
    object.__setattr__(gotapiresponse, "subscription",
                        "premium" if rawdict_userdata["isPremium"] else "general")
    object.__setattr__(gotapiresponse, "version", rawdict_userdata["registeredVersion"])
    object.__setattr__(gotapiresponse, "followee", rawdict_userdata["followeeCount"])
    object.__setattr__(gotapiresponse, "follower", rawdict_userdata["followerCount"])
    object.__setattr__(gotapiresponse, "level", rawdict_userdata["userLevel"]["currentLevel"])
    object.__setattr__(gotapiresponse, "exp",
                       rawdict_userdata["userLevel"]["currentLevelExperience"])
    object.__setattr__(gotapiresponse, "sns", frozenset(
        [(sns["type"], sns["label"], sns["iconUrl"]) for sns in rawdict_userdata["sns"]]
    ))
    if rawdict_userdata["coverImage"]:
        object.__setattr__(gotapiresponse, "cover", (
            rawdict_userdata["coverImage"]["pcUrl"],
            rawdict_userdata["coverImage"]["ogpUrl"],
            rawdict_userdata["coverImage"]["smartphoneUrl"]
        ))
    else:
        object.__setattr__(gotapiresponse, "cover", None)
    object.__setattr__(gotapiresponse, "icon", (
        rawdict_userdata["icons"]["small"],
        rawdict_userdata["icons"]["large"]
    ))
    return APIResponse(gotapiresponse)
