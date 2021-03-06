import logging
import re
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from lyricsifier.core.utils import connection, normalization as nutils


class URLError(Exception):
    pass


class BaseExtractor(ABC):

    def __init__(self, regex):
        self.urlCheckRegex = re.compile(regex)
        self.log = logging.getLogger(__name__)

    def __str__(self):
        return self.__class__.__name__

    @abstractmethod
    def extractFromHTML(self, html):
        pass

    def canExtractFromURL(self, url):
        return self.urlCheckRegex.match(url)

    def extractFromURL(self, url):
        if not self.canExtractFromURL(url):
            raise URLError('{} cannot extract from URL {}'.format(self, url))
        self.log.info('loading page at URL {}'.format(url))
        request = urllib.request.Request(url)
        response = connection.open(request)
        if url != response.geturl():
            self.log.warning('redirected to {}'.format(response.geturl()))
        html = connection.read(response)
        return self.extractFromHTML(html)


class MetroLyricsExtractor(BaseExtractor):

    def __init__(self):
        BaseExtractor.__init__(
            self,
            '^http://www.metrolyrics.com/[a-z0-9-]+-lyrics-[a-z0-9-]+\.html'
        )

    def extractFromHTML(self, html):
        self.log.info('parsing html')
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find(id='lyrics-body-text')
        if not div:
            self.log.warning('unable to extract')
            return None
        lyrics = b' '.join(
            [nutils.encode(p.get_text())
             if p.get('id') != 'mid-song-discussion' else b''
             for p in div.findChildren('p')])
        self.log.info('lyrics extracted')
        self.log.debug('{}'.format(lyrics))
        return lyrics


class LyricsComExtractor(BaseExtractor):

    def __init__(self):
        BaseExtractor.__init__(
            self,
            '^http://www.lyrics.com/[a-z0-9-]+-lyrics-[a-z0-9-]+\.html'
        )

    def extractFromHTML(self, html):
        self.log.info('parsing html')
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find(id='lyrics')
        if not div:
            self.log.warning('unable to extract')
            return None
        lyrics = nutils.encode(div.get_text())
        self.log.info('lyrics extracted')
        self.log.debug('{}'.format(lyrics))
        return lyrics


class LyricsModeExtractor(BaseExtractor):

    def __init__(self):
        BaseExtractor.__init__(
            self,
            '^http://www.lyricsmode.com/lyrics/([a-z]|0-9)/[a-z0-9_]+/[a-z0-9_]+\.html'
        )

    def extractFromHTML(self, html):
        self.log.info('parsing html')
        soup = BeautifulSoup(html, 'html.parser')
        p = soup.find(id='lyrics_text')
        if not p:
            self.log.warning('unable to extract')
            return None
        lyrics = nutils.encode(p.get_text())
        self.log.info('lyrics extracted')
        self.log.debug('{}'.format(lyrics))
        return lyrics


class AZLyricsExtractor(BaseExtractor):

    def __init__(self):
        BaseExtractor.__init__(
            self,
            '^http://www.azlyrics.com/lyrics/[a-z0-9]+/[a-z0-9]+\.html'
        )

    def extractFromHTML(self, html):
        self.log.info('parsing html')
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find(class_='lyricsh').find_next('div', class_=None)
        if not div:
            self.log.warning('unable to extract')
            return None
        lyrics = nutils.encode(div.get_text())
        self.log.info('lyrics extracted')
        self.log.debug('{}'.format(lyrics))
        return lyrics
