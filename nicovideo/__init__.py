""" nicovideo.py (video) """
from __future__ import annotations

import datetime
import urllib.error
import urllib.request
from functools import cache
from typing import Literal, Optional, TypedDict, Final, overload
from dataclasses import dataclass

import json5
from bs4 import BeautifulSoup as bs

__version__ = '2.0.0'

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

        def __post_init__(self):
            self.url: Final[str] = f'https://www.nicovideo.jp/watch/{self.videoid}'

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

class _ReturnDataWithRawdict(TypedDict):
    data   : Video.Metadata
    rawdict: dict

@overload
def get_metadata(videoid: str, *, use_cache: bool = False) -> Video.Metadata: ...

@overload
def get_metadata(videoid: str, *, return_rawdict: Literal[False], use_cache: bool = False) \
        -> Video.Metadata: ...

@overload
def get_metadata(videoid: str, *, return_rawdict: Literal[True], use_cache: bool = False) \
        -> _ReturnDataWithRawdict: ...

def get_metadata(videoid: str, *, return_rawdict: bool = False, use_cache: bool = False): #pylint: disable=C0301
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
            raise Error.NicovideoClientError.VideoNotFound("Video not found or deleted.")\
                from exc
        else:
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
    tags = []
    for tag in rawdict['tag']['items']:
        tags.append(
            Video.Metadata.Tag(
                name   = tag['name'],
                locked = tag['isLocked']
            )
        )

    # Ranking
    ranking_tags = []
    for ranking_tag in rawdict['ranking']['popularTag']:
        for tag in tags:
            if tag.name == ranking_tag['tag']:
                ranking_tags.append(
                    Video.Metadata.Ranking.Tag(
                        tag,
                        ranking_tag['rank'],
                        datetime.datetime.fromisoformat(ranking_tag['dateTime'])
                    )
                )
                break
    ranking_genre = Video.Metadata.Ranking.Genre(
        rawdict['ranking']['genre']['genre'],
        rawdict['ranking']['genre']['rank'] ,
        datetime.datetime.fromisoformat(rawdict['ranking']['genre']['dateTime'])
    ) if rawdict['ranking']['genre'] else None

    data = Video.Metadata(
        videoid     = rawdict['video']['id'],
        title       = rawdict['video']['title'],
        description = rawdict['video']['description'],
        owner       = Video.Metadata.User(
                        nickname = rawdict['owner']['nickname'],
                        userid   = rawdict['owner']['id']
                        ),
        counts      = Video.Metadata.Counts(
                        comments = rawdict['video']['count']['comment'],
                        likes    = rawdict['video']['count']['like'],
                        mylists  = rawdict['video']['count']['mylist'],
                        views    = rawdict['video']['count']['view']
                        ),
        duration    = rawdict['video']['duration'],
        postdate    = datetime.datetime.fromisoformat(
                        rawdict['video']['registeredAt']
                        ),
        genre       = Video.Metadata.Genre(
                        label    = rawdict['genre']['label'],
                        key      = rawdict['genre']['key']
                        ),
        ranking     = Video.Metadata.Ranking(ranking_genre, ranking_tags),
        series      = Video.Metadata.Series(
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
        thumbnail   = Video.Metadata.Thumbnail(
                        small_url  = rawdict['video']['thumbnail']['url'],
                        middle_url = rawdict['video']['thumbnail']['middleUrl'],
                        large_url  = rawdict['video']['thumbnail']['largeUrl'],
                        player_url = rawdict['video']['thumbnail']['player'],
                        ogp_url    = rawdict['video']['thumbnail']['ogp']
            ),
        tags        = tags
    )
    if return_rawdict:
        return _ReturnDataWithRawdict(data=data, rawdict=rawdict)
    else:
        return data
