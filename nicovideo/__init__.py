""" nicovideo.py (video) """
from __future__ import annotations

import datetime
import urllib.error
import urllib.request
from functools import cache
from typing import Literal, Optional, Final, Annotated
from types import EllipsisType
from dataclasses import dataclass

import json5
from bs4 import BeautifulSoup as bs

__version__ = '3.0.1'

class Error():
    """ Errors """
    class NicovideoClientError(Exception):
        """ urllib error """
        class ContentNotFound(Exception):
            """ Video not found or deleted """
        class ConnectionError(Exception):
            """ Connection error """

@cache
def _urllib_request_with_cache(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read()


class Video():
    """ Video Classes/Methods """

    @dataclass
    class Metadata(): # pylint: disable=R0902
        """ Meta data """
        videoid    : str
        title      : str
        description: str
        owner      : Video.Metadata.User
        counts     : Video.Metadata.Counts
        duration   : int
        postdate   : datetime.datetime
        genre      : Optional[Video.Metadata.Genre]
        tags       : list[Video.Metadata.Tag]
        ranking    : Video.Metadata.Ranking
        series     : Optional[Video.Metadata.Series]
        thumbnail  : Video.Metadata.Thumbnail
        rawdict    : dict

        def __post_init__(self):
            self.url: str = f'https://www.nicovideo.jp/watch/{self.videoid}'

        def refresh(self):
            """ Refresh data """ # TODO: もっといい書き方を考える
            refreshed_data = Video.get_metadata(self.videoid)
            self.videoid     = refreshed_data.videoid
            self.title       = refreshed_data.title
            self.description = refreshed_data.description
            self.owner       = refreshed_data.owner
            self.counts      = refreshed_data.counts
            self.duration    = refreshed_data.duration
            self.postdate    = refreshed_data.postdate
            self.genre       = refreshed_data.genre
            self.tags        = refreshed_data.tags
            self.ranking     = refreshed_data.ranking
            self.series      = refreshed_data.series
            self.thumbnail   = refreshed_data.thumbnail
            self.rawdict     = refreshed_data.rawdict

        @dataclass
        class User():
            """ User data """
            nickname: str
            userid  : int

            def get_metadata(self) -> User.Metadata:
                """ Convert to User.Metadata """
                return User.get_metadata(int(self.userid))

        @dataclass
        class Counts():
            """ Counts data """
            comments: int
            likes   : int
            mylists : int
            views   : int

        @dataclass
        class Genre():
            """ Genre data """
            label   : str
            key     : str

        @dataclass
        class Tag():
            """ Tag data """
            name  : str
            locked: bool

        @dataclass
        class Ranking():
            """ Ranking data """
            genreranking: Optional[Video.Metadata.Ranking.Genre]
            tagrankings : list[Video.Metadata.Ranking.Tag]

            @dataclass
            class Genre():
                """ Genre ranking data """
                genre: Video.Metadata.Genre
                rank : int
                time : datetime.datetime
            @dataclass
            class Tag():
                """ Tag ranking data """
                tag : Video.Metadata.Tag
                rank: int
                time: datetime.datetime

        @dataclass
        class Series():
            """ Series data """
            seriesid   : int
            title      : str
            description: str
            thumbnail  : str
            prev_video : Optional[str]
            next_video : Optional[str]
            first_video: Optional[str]

        @dataclass
        class Thumbnail():
            """ Thumbnail data """
            small_url : Optional[str]
            middle_url: Optional[str]
            large_url : Optional[str]
            player_url: Optional[str]
            ogp_url   : Optional[str]

    @classmethod
    def get_metadata(cls, videoid: str, *, use_cache: bool = False): #pylint: disable=C0301
        """ Get video's metadata """
        watch_url = f"https://www.nicovideo.jp/watch/{videoid}"
        try:
            if use_cache:
                text = _urllib_request_with_cache(watch_url)
            else:
                with urllib.request.urlopen(watch_url) as response:
                    text = response.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise Error.NicovideoClientError.ContentNotFound("Video not found or deleted.")\
                    from exc
            raise Error.NicovideoClientError.ConnectionError(
                f"Unexpected HTTP Error: {exc.code}"
            ) from exc
        except urllib.error.URLError as exc:
            raise Error.NicovideoClientError.ConnectionError("Connection error.") from exc

        soup = bs(text, "html.parser")
        rawdict = json5.loads(
            str(soup.select("#js-initial-watch-data")[0]["data-api-data"])
        )

        # Tags
        tags = [
            cls.Metadata.Tag(
                name   = tag["name"],
                locked = tag["isLocked"]
            ) for tag in rawdict["tag"]["items"]]

        # Ranking
        ranking_tags = [
            cls.Metadata.Ranking.Tag(
                tag,
                ranking_tag["rank"],
                datetime.datetime.fromisoformat(ranking_tag["dateTime"])
            ) for tag in tags if tag.name == ranking_tag['tag'] # type: ignore
              for ranking_tag in rawdict['ranking']['popularTag']
        ]
        ranking_genre = cls.Metadata.Ranking.Genre(
            rawdict['ranking']['genre']['genre'],
            rawdict['ranking']['genre']['rank'] ,
            datetime.datetime.fromisoformat(rawdict['ranking']['genre']['dateTime'])
        ) if rawdict['ranking']['genre'] else None

        return cls.Metadata(
            videoid     = rawdict['video']['id'],
            title       = rawdict['video']['title'],
            description = rawdict['video']['description'],
            owner       = cls.Metadata.User(
                            nickname = rawdict['owner']['nickname'],
                            userid   = int(rawdict['owner']['id'])
                            ),
            counts      = cls.Metadata.Counts(
                            comments = rawdict['video']['count']['comment'],
                            likes    = rawdict['video']['count']['like'],
                            mylists  = rawdict['video']['count']['mylist'],
                            views    = rawdict['video']['count']['view']
                            ),
            duration    = rawdict['video']['duration'],
            postdate    = datetime.datetime.fromisoformat(
                            rawdict['video']['registeredAt']
                            ),
            genre       = cls.Metadata.Genre(
                            label    = rawdict['genre']['label'],
                            key      = rawdict['genre']['key']
                            ),
            ranking     = cls.Metadata.Ranking(ranking_genre, ranking_tags),
            series      = cls.Metadata.Series(
                            seriesid    = rawdict['series']['id'],
                            title       = rawdict['series']['title'],
                            description = rawdict['series']['description'],
                            thumbnail   = rawdict['series']['thumbnailUrl'],
                            prev_video  = rawdict['series']['video']['prev']['id']
                                if rawdict['series']['video']['prev'] else None,
                            next_video  = rawdict['series']['video']['next']['id']
                                if rawdict['series']['video']['next'] else None,
                            first_video = rawdict['series']['video']['first']['id']
                                if rawdict['series']['video']['first'] else None
                ) if rawdict['series'] else None,
            thumbnail   = cls.Metadata.Thumbnail(
                            small_url  = rawdict['video']['thumbnail']['url'],
                            middle_url = rawdict['video']['thumbnail']['middleUrl'],
                            large_url  = rawdict['video']['thumbnail']['largeUrl'],
                            player_url = rawdict['video']['thumbnail']['player'],
                            ogp_url    = rawdict['video']['thumbnail']['ogp']
                ),
            tags        = tags,
            rawdict     = rawdict
        )

class User():
    """ User classes/methods """

    @dataclass
    class Metadata():
        """ Meta data """
        nickname          : str
        userid            : int
        description       : User.Metadata.Description
        user_type         : Literal["Premium", "General"]
        registered_version: str
        follow            : int
        follower          : int
        user_level        : int
        user_exp          : int
        sns               : list[User.Metadata.SNS.User]
        cover             : Optional[User.Metadata.Cover]
        icon              : User.Metadata.UserIcon
        videolist         : list[Video.Metadata]|EllipsisType
        rawdict           : dict

        def refresh(self):
            """ Update data """
            refreshed_data = User.get_metadata(self.nickname)
            self.nickname           = refreshed_data.nickname
            self.userid             = refreshed_data.userid
            self.description        = refreshed_data.description
            self.user_type          = refreshed_data.user_type
            self.registered_version = refreshed_data.registered_version
            self.follow             = refreshed_data.follow
            self.follower           = refreshed_data.follower
            self.user_level         = refreshed_data.user_level
            self.user_exp           = refreshed_data.user_exp
            self.sns                = refreshed_data.sns
            self.cover              = refreshed_data.cover
            self.icon               = refreshed_data.icon
            self.videolist          = refreshed_data.videolist
            self.rawdict            = refreshed_data.rawdict

        @dataclass
        class Description():
            """ User description """
            description_html : str
            description_plain: str

            def __str__(self):
                return self.description_html


        class SNS():
            """ SNS services / user """
            @dataclass
            class Service():
                """ SNS service (e.g. Twitter) """
                name: str
                key : str
                icon: Annotated[str, "Image URL (PNG)"]

                def __str__(self):
                    return self.name

            @dataclass
            class User():
                """ SNS user """
                service: User.Metadata.SNS.Service
                name   : str
                url    : str

        @dataclass
        class Cover():
            """ Cover (Header) image of user """
            ogp: Annotated[str, "Image URL"]
            pc : Annotated[str, "Image URL"] #pylint: disable=C0103
            sp : Annotated[str, "Image URL"] #pylint: disable=C0103

        @dataclass
        class UserIcon():
            """ User icon """
            small: Annotated[str, "Image URL"]
            large: Annotated[str, "Image URL"]

        @dataclass
        class Video():
            """ Video data """
            videoid : str
            title   : str
            owner   : Video.Metadata.User
            counts  : Video.Metadata.Counts
            duration: int
            postdate: datetime.datetime
            series  : Video.Metadata.Series

            def get_metadata(self) -> Video.Metadata:
                """ Convert to Video.Metadata """
                return Video.get_metadata(self.videoid)

    @classmethod
    def get_metadata(cls,
                     userid: int,
                     detail: Literal["videolist", "minimal"] = "videolist",
                     *,
                     use_cache: bool = False):
        """ Get user's metadata """

        if detail == "videolist":
            userpage_url = f"https://www.nicovideo.jp/user/{userid}/video"
        else:
            userpage_url = f"https://www.nicovideo.jp/user/{userid}"

        try:
            if use_cache:
                text = _urllib_request_with_cache(userpage_url)
            else:
                with urllib.request.urlopen(userpage_url) as response:
                    text = response.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise Error.NicovideoClientError.ContentNotFound("User not found or deleted.")\
                    from exc
            raise Error.NicovideoClientError.ConnectionError(
                f"Unexpected HTTP Error: {exc.code}"
            ) from exc
        except urllib.error.URLError as exc:
            raise Error.NicovideoClientError.ConnectionError("Connection error.") from exc

        soup = bs(text, "html.parser")
        rawdict = json5.loads(
            str(soup.select("#js-initial-userpage-data")[0]["data-initial-data"])
        )
        rawdict_userdata  = rawdict["state"]["userDetails"]["userDetails"]["user"]
        rawdict_videodata = rawdict["nvapi"][0]["body"]["data"]["items"] \
            if detail == "videolist" else Ellipsis

        return cls.Metadata(
            nickname           = rawdict_userdata["nickname"],
            userid             = rawdict_userdata["id"],
            description        = cls.Metadata.Description(
                rawdict_userdata["decoratedDescriptionHtml"],
                rawdict_userdata["strippedDescription"]
            ),
            user_type          = "Premium" if rawdict_userdata["isPremium"] else "General",
            registered_version = rawdict_userdata["registeredVersion"],
            follow             = rawdict_userdata["followeeCount"],
            follower           = rawdict_userdata["followerCount"],
            user_level         = rawdict_userdata["userLevel"]["currentLevel"],
            user_exp           = rawdict_userdata["userLevel"]["currentLevelExperience"],
            sns                = [
                cls.Metadata.SNS.User(
                    cls.Metadata.SNS.Service(
                        account["label"],
                        account["type"],
                        account["iconUrl"]
                    ),
                    account["screenName"],
                    account["url"]
                ) for account in rawdict_userdata["sns"]
            ],
            cover              = cls.Metadata.Cover(
                rawdict_userdata["coverImage"]["ogpUrl"],
                rawdict_userdata["coverImage"]["pcUrl"],
                rawdict_userdata["coverImage"]["smartphoneUrl"]
            ) if rawdict_userdata["coverImage"] else None,
            icon               = cls.Metadata.UserIcon(
                rawdict_userdata["icons"]["small"],
                rawdict_userdata["icons"]["large"]
            ),
            videolist          = [
                cls.Metadata.Video(
                    videoid     = videodata["essential"]["id"],
                    title       = videodata["essential"]["title"],
                    owner       = Video.Metadata.User(
                        nickname = rawdict_userdata["nickname"],
                        userid   = int(rawdict_userdata["id"])
                    ),
                    counts      = Video.Metadata.Counts(
                        comments = videodata["essential"]["count"]["comment"],
                        likes    = videodata["essential"]["count"]["like"],
                        mylists  = videodata["essential"]["count"]["mylist"],
                        views    = videodata["essential"]["count"]["view"]
                    ),
                    duration    = videodata["essential"]["duration"],
                    postdate    = datetime.datetime.fromisoformat(
                        videodata["essential"]["registeredAt"]
                    ),
                    series      = Video.Metadata.Series(
                        seriesid    = videodata["series"]["id"],
                        title       = videodata["series"]["title"],
                        description = Ellipsis,
                        thumbnail   = Ellipsis,
                        prev_video  = Ellipsis,
                        next_video  = Ellipsis,
                        first_video = Ellipsis
                    ),
                ) for videodata in rawdict_videodata ] if detail == "videolist" else Ellipsis,
            rawdict            = rawdict_userdata
        )

