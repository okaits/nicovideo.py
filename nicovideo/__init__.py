""" nicovideo.py (video) """
from __future__ import annotations

import datetime
import pprint
import urllib.error
import urllib.request
from functools import cache
from html import unescape
from typing import Type, Union
from dataclasses import dataclass

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

@dataclass
class Video():
    """ Video """
    videoid: str

    def __post_init__(self):
        self.rawdict: dict = {}

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
        genre      : Union[Video.Metadata.Genre, type(None)]
        tags       : list[Video.Metadata.Tag]
        ranking    : Video.Metadata.Ranking
        series     : Video.Metadata.Series
        thumbnail  : Video.Metadata.Thumbnail

        def __post_init__(self):
            self.url: str = f'https://www.nicovideo.jp/watch/{self.videoid}'

        @dataclass
        class User():
            """ User data """
            nickname: str
            userid  : str

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
            genreranking: Union[Video.Metadata.Ranking.Genre, None]
            tagrankings : list[Video.Metadata.Ranking.Genre]

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
            prev_video : Union[Video, type(None)]
            next_video : Union[Video, type(None)]
            first_video: Union[Video, type(None)]

        @dataclass
        class Thumbnail():
            """ Thumbnail data """
            small_url : Union[str, type(None)]
            middle_url: Union[str, type(None)]
            large_url : Union[str, type(None)]
            player_url: Union[str, type(None)]
            ogp_url   : Union[str, type(None)]

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
