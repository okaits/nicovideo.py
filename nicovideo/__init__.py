""" nicovideo.py (video) """

__version__ = '0.0.2'

import pprint
import urllib.request
from html import unescape
import datetime

import json5
from bs4 import BeautifulSoup as bs


class Video():
    """ Video """
    def __init__(self, videoid: str):
        self.videoid       = videoid
        self.rawdict: dict = {}

    class Metadata():
        """ Meta data """

        class User():
            """ User data """
            def __init__(self, nickname: str, videoid: str):
                self.nickname: str = nickname
                self.id      : str = videoid #pylint: disable=C0103

        class Counts():
            """ Counts data """
            def __init__(self, comments: int, likes: int, mylists: int, views: int):
                self.comments: int = comments
                self.likes   : int = likes
                self.mylists : int = mylists
                self.views   : int = views

        class Genre():
            """ Genre data """
            def __init__(self, label, key):
                self.label   : str = label
                self.key     : str = key

        class Tag():
            """ Tag data """
            def __init__(self, name: str, locked: bool):
                self.name  : str  = name
                self.locked: bool = locked

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
                ):
            self.videoid  : str               = videoid #pylint: disable=C0103
            self.title    : str               = title
            self.owner    : self.User         = owner
            self.counts   : self.Counts       = counts
            self.duration : int               = duration
            self.postdate : datetime.datetime = postdate
            self.genre    : self.Genre        = genre
            self.tags     : list[self.Tag]    = tags

    def get_metadata(self):
        """ Get video's metadata """
        watch_url = f"https://www.nicovideo.jp/watch/{self.videoid}"
        with urllib.request.urlopen(watch_url) as response:
            text = response.read()

        soup = bs(text, "html.parser")
        self.rawdict = json5.loads(str(soup.find("div", id="js-initial-watch-data")["data-api-data"]))

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
                        videoid  = self.rawdict['owner']['id']
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
