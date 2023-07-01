""" nicovideo.py (video) """
from __future__ import annotations

import datetime
import pprint
import urllib.request
from html import unescape
from typing import Type

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

        def __init__(
                self,
                videoid : str,
                title   : str,
                owner   : User,
                counts  : Counts,
                duration: int,
                postdate: datetime.datetime,
                genre   : Genre,
                tags    : list[Tag]
                ) -> Video.Metadata:
            self.videoid  : str               = videoid #pylint: disable=C0103
            self.title    : str               = title
            self.owner    : self.User         = owner
            self.counts   : self.Counts       = counts
            self.duration : int               = duration
            self.postdate : datetime.datetime = postdate
            self.genre    : self.Genre        = genre
            self.tags     : list[self.Tag]    = tags
            self.url      : str               = f'https://www.nicovideo.jp/watch/{videoid}'

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

        return self.Metadata(
            videoid  = self.rawdict['video']['id'],
            title    = self.rawdict['video']['title'],
            owner    = self.Metadata.User(
                        nickname = self.rawdict['owner']['nickname'],
                        userid   = self.rawdict['owner']['id']
                       ),
            counts   = self.Metadata.Counts(
                        comments = self.rawdict['video']['count']['comment'],
                        likes    = self.rawdict['video']['count']['like'],
                        mylists  = self.rawdict['video']['count']['mylist'],
                        views    = self.rawdict['video']['count']['view']
                       ),
            duration = self.rawdict['video']['duration'],
            postdate = datetime.datetime.fromisoformat(
                        self.rawdict['video']['registeredAt']
                       ),
            genre    = self.Metadata.Genre(
                        label    = self.rawdict['genre']['label'],
                        key      = self.rawdict['genre']['key']
                       ),
            tags     = tags
        )
