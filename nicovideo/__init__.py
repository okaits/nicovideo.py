""" nicovideo.py (video) """
from __future__ import annotations

import datetime
import pprint
import urllib.error
import urllib.request
from functools import cache
from html import unescape
from typing import Type, Union

import json5
from bs4 import BeautifulSoup as bs

__version__ = '0.0.7'

class Error():
    """ Errors """
    class NicovideoClientError(Exception):
        """ urllib error """
        class VideoNotFound(Exception):
            """ Video not found or deleted """
        class ConnectionError(Exception):
            """ Connection error """

@cache
def _urllib_request_with_cache(url: str) -> str:
    with urllib.request.urlopen(url) as response:
        return response.read()

class Video():
    """ Video """
    def __init__(self, videoid: str) -> Video:
        self.videoid: str  = videoid
        self.rawdict: dict = {}

    class Metadata():
        """ Meta data """

        class User():
            """ User data """
            def __init__(self, nickname: str, userid: str) -> Video.Metadata.User:
                self.nickname: str = nickname
                self.id      : str = userid #pylint: disable=C0103
            def __str__(self) -> str:
                return f'{self.nickname} [ID: {self.id}]'

        class Counts():
            """ Counts data """
            def __init__(self, comments: int, likes: int, mylists: int, views: int)\
                    -> Video.Metadata.Counts:
                self.comments: int = comments
                self.likes   : int = likes
                self.mylists : int = mylists
                self.views   : int = views
            def __str__(self) -> str:
                returndata = f'Views: {self.views}\n'
                returndata += f'Comments: {self.comments}\n'
                returndata += f'Mylists: {self.mylists}\n'
                returndata += f'Likes: {self.likes}'
                return returndata

        class Genre():
            """ Genre data """
            def __init__(self, label: str, key: str) -> Video.Metadata.Genre:
                self.label   : str = label
                self.key     : str = key
            def __str__(self):
                return self.label

        class Tag():
            """ Tag data """
            def __init__(self, name: str, locked: bool) -> Video.Metadata.Tag:
                self.name  : str  = name
                self.locked: bool = locked
            def __str__(self):
                return f'{self.name}{" [Locked]" if self.locked else ""}'

        class Ranking():
            """ Ranking data """
            class Genre():
                """ Genre ranking data """
                def __init__(
                        self,
                        genre: Video.Metadata.Genre,
                        rank : int,
                        time : datetime.datetime
                        ) -> Video.Metadata.Ranking.Genre:
                    self.genre: Video.Metadata.Genre = genre
                    self.rank : int                  = rank
                    self.time : datetime.datetime    = time
            class Tag():
                """ Tag ranking data """
                def __init__(
                        self,
                        tag : Video.Metadata.Tag,
                        rank: int,
                        time: datetime.datetime
                        ) -> Video.Metadata.Ranking.Tag:
                    self.tag : Video.Metadata.Tag  = tag
                    self.rank: int                 = rank
                    self.time: datetime.datetime   = time

            def __init__(
                    self,
                    genreranking: Union[Video.Metadata.Ranking.Genre, None],
                    tagrankings: list[Video.Metadata.Ranking.Tag]
                    ) -> Video.Metadata.Ranking:
                self.genreranking: Union[Video.Metadata.Ranking.Genre, None] = genreranking
                self.tagrankings : list[Video.Metadata.Ranking.Genre]        = tagrankings

        class Series():
            """ Series data """
            def __init__(
                    self,
                    seriesid   : int,
                    title      : str,
                    description: str,
                    thumbnail  : str,
                    prev_video : Union[Video, type(None)] = None,
                    next_video : Union[Video, type(None)] = None,
                    first_video: Union[Video, type(None)] = None
                    ) -> Video.Metadata.Series:
                self.id         : int                      = seriesid #pylint: disable=C0103
                self.title      : str                      = title
                self.description: str                      = description
                self.thumbnail  : str                      = thumbnail
                self.prev_video : Union[Video, type(None)] = prev_video
                self.next_video : Union[Video, type(None)] = next_video
                self.first_video: Union[Video, type(None)] = first_video

        class Thumbnail():
            """ Thumbnail data """
            def __init__(
                    self,
                    small_url : Union[str, type(None)],
                    middle_url: Union[str, type(None)],
                    large_url : Union[str, type(None)],
                    player_url: Union[str, type(None)],
                    ogp_url   : Union[str, type(None)]
                    ) -> Video.Metadata.Thumbnail:
                self.small_url : Union[str, type(None)] = small_url
                self.middle_url: Union[str, type(None)] = middle_url
                self.large_url : Union[str, type(None)] = large_url
                self.player_url: Union[str, type(None)] = player_url
                self.ogp_url   : Union[str, type(None)] = ogp_url

        def __init__(
                self,
                videoid    : str,
                title      : str,
                description: str,
                owner      : User,
                counts     : Counts,
                duration   : int,
                postdate   : datetime.datetime,
                genre      : Union[Genre, type(None)],
                tags       : list[Tag],
                ranking    : Ranking,
                series     : Series,
                thumbnail  : Thumbnail
                ) -> Video.Metadata:
            self.videoid    : str                           = videoid #pylint: disable=C0103
            self.title      : str                           = title
            self.description: str                           = description
            self.owner      : self.User                     = owner
            self.counts     : self.Counts                   = counts
            self.duration   : int                           = duration
            self.postdate   : datetime.datetime             = postdate
            self.genre      : Union[self.Genre, type(None)] = genre
            self.tags       : list[self.Tag]                = tags
            self.ranking    : self.Ranking                  = ranking
            self.series     : self.Series                   = series
            self.thumbnail  : self.Thumbnail                = thumbnail
            self.url        : str                           = \
                f'https://www.nicovideo.jp/watch/{videoid}'

    def get_metadata(self, use_cache: bool = False) -> Video.Metadata:
        """ Get video's metadata """
        watch_url = f"https://www.nicovideo.jp/watch/{self.videoid}"
        try:
            if use_cache:
                text = _urllib_request_with_cache(watch_url)
            else:
                with urllib.request.urlopen(watch_url) as response:
                    text = response.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise Error.NicovideoClientError.VideoNotFound("Video not found or deleted.")\
                    from exc
            else:
                raise Error.NicovideoClientError.ConnectionError(
                    f"Unexpected HTTP Error: {exc.code}"
                ) from exc
        except urllib.error.URLError as exc:
            raise Error.NicovideoClientError.ConnectionError("Connection error.") from exc

        soup = bs(text, "html.parser")
        self.rawdict = json5.loads(
            str(soup.find("div", id="js-initial-watch-data")["data-api-data"])
        )

        # Tags
        tags = []
        for tag in self.rawdict['tag']['items']:
            tags.append(
                self.Metadata.Tag(
                    name=tag['name'],
                    locked=tag['isLocked']
                )
            )

        # Ranking
        ranking_tags = []
        for ranking_tag in self.rawdict['ranking']['popularTag']:
            for tag in tags:
                if tag.name == ranking_tag['tag']:
                    ranking_tags.append(
                        self.Metadata.Ranking.Tag(
                            tag,
                            ranking_tag['rank'],
                            datetime.datetime.fromisoformat(ranking_tag['dateTime'])
                        )
                    )
                    break
        ranking_genre = self.Metadata.Ranking.Genre(
            self.rawdict['ranking']['genre']['genre'],
            self.rawdict['ranking']['genre']['rank'] ,
            datetime.datetime.fromisoformat(self.rawdict['ranking']['genre']['dateTime'])
        ) if self.rawdict['ranking']['genre'] else None

        data = self.Metadata(
            videoid     = self.rawdict['video']['id'],
            title       = self.rawdict['video']['title'],
            description = self.rawdict['video']['description'],
            owner       = self.Metadata.User(
                           nickname = self.rawdict['owner']['nickname'],
                           userid   = self.rawdict['owner']['id']
                          ),
            counts      = self.Metadata.Counts(
                           comments = self.rawdict['video']['count']['comment'],
                           likes    = self.rawdict['video']['count']['like'],
                           mylists  = self.rawdict['video']['count']['mylist'],
                           views    = self.rawdict['video']['count']['view']
                          ),
            duration    = self.rawdict['video']['duration'],
            postdate    = datetime.datetime.fromisoformat(
                           self.rawdict['video']['registeredAt']
                          ),
            genre       = self.Metadata.Genre(
                           label    = self.rawdict['genre']['label'],
                           key      = self.rawdict['genre']['key']
                          ),
            ranking     = self.Metadata.Ranking(ranking_genre, ranking_tags),
            series      = self.Metadata.Series(
                           seriesid = self.rawdict['series']['id'],
                           title = self.rawdict['series']['title'],
                           description= self.rawdict['series']['description'],
                           thumbnail = self.rawdict['series']['thumbnailUrl'],
                           prev_video = Video(self.rawdict['series']['video']['prev']['id'])
                               if self.rawdict['series']['video']['prev'] else None,
                           next_video = Video(self.rawdict['series']['video']['next']['id'])
                               if self.rawdict['series']['video']['next'] else None,
                           first_video = Video(self.rawdict['series']['video']['first']['id'])
                               if self.rawdict['series']['video']['first'] else None
               ) if self.rawdict['series'] else None,
            thumbnail   = self.Metadata.Thumbnail(
                           small_url  = self.rawdict['video']['thumbnail']['url'],
                           middle_url = self.rawdict['video']['thumbnail']['middleUrl'],
                           large_url  = self.rawdict['video']['thumbnail']['largeUrl'],
                           player_url = self.rawdict['video']['thumbnail']['player'],
                           ogp_url    = self.rawdict['video']['thumbnail']['ogp']
                ),
            tags        = tags
        )
        return data
