"""
このモジュールでは、ニコニコのAPIから取得した生データのTypedDictを定義します。
モジュール内部での型ヒント用のため、通常利用時に考慮する必要はありません。

"""
#pylint: disable=C0115

from __future__ import annotations
import typing

class VideoAPIRawDicts():
    class VideoCount(typing.TypedDict):
        comment: int
        like: int
        mylist: int
        view: int
    class VideoThumbnail(typing.TypedDict):
        url: str
        middleUrl: str
        largeUrl: str
        player: str
        ogp: str
    class Video(typing.TypedDict):
        id: str
        title: str
        description: str
        count: VideoAPIRawDicts.VideoCount
        duration: int
        registeredAt: typing.Annotated[str, "ISO 8601 datetime format"]
        thumbnail: VideoAPIRawDicts.VideoThumbnail
    class TagItems(typing.TypedDict):
        name: str
        isLocked: bool
    class Tag(typing.TypedDict):
        items: list[VideoAPIRawDicts.TagItems]
    class RankingPopularTag(typing.TypedDict):
        tag: str
        rank: int
        dateTime: typing.Annotated[str, "ISO 8601 datetime format"]
    class RankingGenre(typing.TypedDict):
        genre: str
        rank: int
        dateTime: typing.Annotated[str, "ISO 8601 datetime format"]
    class Ranking(typing.TypedDict):
        popularTag: list[VideoAPIRawDicts.RankingPopularTag]
        genre: typing.Optional[VideoAPIRawDicts.RankingGenre]
    class Owner(typing.TypedDict):
        nickname: str
        id: str
    class Genre(typing.TypedDict):
        label: str
        key: str
    class SeriesVideoRelatedVideo(typing.TypedDict):
        id: str
    class SeriesVideo(typing.TypedDict):
        prev: typing.Optional[VideoAPIRawDicts.SeriesVideoRelatedVideo]
        next: typing.Optional[VideoAPIRawDicts.SeriesVideoRelatedVideo]
        first: typing.Optional[VideoAPIRawDicts.SeriesVideoRelatedVideo]
    class Series(typing.TypedDict):
        id: int
        title: str
        video: VideoAPIRawDicts.SeriesVideo
        description: str
        thumbnailUrl: str
    class RawDict(typing.TypedDict):
        """RawDict TypedDict: Video._rawdictに格納されるdictの型ヒント"""
        video: VideoAPIRawDicts.Video
        tag: VideoAPIRawDicts.Tag
        ranking: VideoAPIRawDicts.Ranking
        owner: VideoAPIRawDicts.Owner
        genre: typing.Optional[VideoAPIRawDicts.Genre]
        series: typing.Optional[VideoAPIRawDicts.Series]

class UserAPIRawDicts():
    class UserDetailsUserDetailsUserUserLevel(typing.TypedDict):
        currentLevel: int
        currentLevelExperience: int
    class UserDetailsUserDetailsUserSNS(typing.TypedDict):
        label: str
        type: str
        iconUrl: str
    class UserDetailsUserDetailsUserCoverImage(typing.TypedDict):
        ogpUrl: str
        pcUrl: str
        smartphoneUrl: str
    class UserDetailsUserDetailsUserIcons(typing.TypedDict):
        small: str
        large: str
    class UserDetailsUserDetailsUser(typing.TypedDict):
        nickname: str
        id: str
        decoratedDescriptionHtml: str
        strippedDescription: str
        isPremium: bool
        registeredVersion: str
        foloweeCount: int
        folowerCount: int
        userLevel: UserAPIRawDicts.UserDetailsUserDetailsUserUserLevel
        sns: list[UserAPIRawDicts.UserDetailsUserDetailsUserSNS]
        coverImage: UserAPIRawDicts.UserDetailsUserDetailsUserCoverImage
        icons: UserAPIRawDicts.UserDetailsUserDetailsUserIcons
    class UserDetailsUserDetails(typing.TypedDict):
        user: UserAPIRawDicts.UserDetailsUserDetailsUser
    class UserDetails(typing.TypedDict):
        userDetails: UserAPIRawDicts.UserDetailsUserDetails
    class State(typing.TypedDict):
        userDetails: UserAPIRawDicts.UserDetails
    class NVAPIBodyDataItemsEssentialCount(typing.TypedDict):
        comment: int
        like: int
        mylist: int
        view: int
    class NVAPIBodyDataItemsEssential(typing.TypedDict):
        id: str
        title: str
        count: UserAPIRawDicts.NVAPIBodyDataItemsEssentialCount
        duration: int
        registeredAt: typing.Annotated[str, "ISO 8601 datetime format"]
    class NVAPIBodyDataItemsSeries(typing.TypedDict):
        id: int
        title: str
    class NVAPIBodyDataItems(typing.TypedDict):
        essential: UserAPIRawDicts.NVAPIBodyDataItemsEssential
        series: UserAPIRawDicts.NVAPIBodyDataItemsSeries
    class NVAPIBodyData(typing.TypedDict):
        items: list[UserAPIRawDicts.NVAPIBodyDataItems]
    class NVAPIBody(typing.TypedDict):
        data: list[UserAPIRawDicts.NVAPIBodyData]
    class RawDict(typing.TypedDict):
        """RawDict TypedDict: User._rawdictに格納されるdictの型ヒント"""
        state: UserAPIRawDicts.State
        nvapi: UserAPIRawDicts.NVAPIBody
