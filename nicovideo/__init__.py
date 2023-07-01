""" nicovideo.py (video) """
from __future__ import annotations

import datetime
import pprint
import urllib.request
from html import unescape
from typing import Type, Union

import json5
from bs4 import BeautifulSoup as bs

__version__ = '0.0.4'

class Video():
    """ Video """
    def __init__(self, videoid: str) -> Video:
        self.videoid       = videoid
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
                    self.genre = genre
                    self.rank  = rank
                    self.time  = time
            class Tag():
                """ Tag ranking data """
                def __init__(
                        self,
                        tag : Video.Metadata.Tag,
                        rank: int,
                        time: datetime.datetime
                        ) -> Video.Metadata.Ranking.Tag:
                    self.tag  = tag
                    self.rank = rank
                    self.time = time

            def __init__(
                    self,
                    genreranking: Video.Metadata.Ranking.Genre,
                    tagrankings: list[Video.Metadata.Ranking.Genre]
                    ) -> Video.Metadata.Ranking:
                self.genreranking = genreranking
                self.tagrankings  = tagrankings

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
                self.id          = seriesid #pylint: disable=C0103
                self.title       = title
                self.description = description
                self.thumbnail   = thumbnail
                self.prev_video  = prev_video
                self.next_video  = next_video
                self.first_video = first_video

        def __init__(
                self,
                videoid    : str,
                title      : str,
                description: str,
                owner      : User,
                counts     : Counts,
                duration   : int,
                postdate   : datetime.datetime,
                genre      : Genre,
                tags       : list[Tag],
                ranking    : Ranking,
                series     : Series
                ) -> Video.Metadata:
            self.videoid    : str               = videoid #pylint: disable=C0103
            self.title      : str               = title
            self.description: str               = description
            self.owner      : self.User         = owner
            self.counts     : self.Counts       = counts
            self.duration   : int               = duration
            self.postdate   : datetime.datetime = postdate
            self.genre      : self.Genre        = genre
            self.tags       : list[self.Tag]    = tags
            self.ranking    : self.Ranking      = ranking
            self.series     : self.Series       = series
            self.url        : str               = f'https://www.nicovideo.jp/watch/{videoid}'

    def get_metadata(self) -> Video.Metadata:
        """ Get video's metadata """
        watch_url = f"https://www.nicovideo.jp/watch/{self.videoid}"
        with urllib.request.urlopen(watch_url) as response:
            text = response.read()

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
        )

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
               ),
            tags        = tags
        )
        return data
