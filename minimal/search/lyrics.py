from bs4 import BeautifulSoup
from minimal.search.sessionClient import get_session
from rauth import OAuth2Service
from rapidfuzz.fuzz import partial_ratio

base_url = "https://genius.com"
base_search_url = "https://api.genius.com/search?q="
worker_url = "http://genius.brayo.workers.dev"

ses = get_session()


class Genius:
    @classmethod
    def get_session(self):
        client = OAuth2Service(
            client_id="NWIr1nGkiXORidM-uPg3vJCkunxpRt6KW8GLBISTI72RHNbJ9pNI9uNojMk7T2mL",
            client_secret="llFZD5kU4hEG-8H8nEo9ircddUFkVPdPTtIP5f-VWzM2fI84mrHRKtqq0V31euKKqQyN4lrUKJZMVjAAx972cg",
        )
        return client.get_session(
            token="1jQVW-1UtzCluk1DEVKHTzbsZpHegvK1VMXTtJDebF_vQKhDHgUpcqdv1eyFtj4k"
        )

    @classmethod
    def from_query(self, artist: str, song: str, lyric_fail=False) -> str:
        if "(" in song:
            song = song[: song.find("(")]
        artist.strip()
        song.strip()
        query = f"{artist} {song}"
        query.strip()
        song = song.lower()
        encoded_query = query.replace(" ", "+").replace("&", "+")
        search_url = base_search_url + encoded_query
        Ses = self.get_session()
        response_json = Ses.get(search_url).json()
        for i in range(0, len(response_json["response"]["hits"])):
            url = str(response_json["response"]["hits"][i]["result"]["path"])
            formatted_url = url.replace("-", " ").lower()
            if not url.endswith("lyrics") or partial_ratio(formatted_url, song) < 90:
                continue
            lyric_url = worker_url + url
            lyrics = self.from_url(lyric_url)
            if lyrics == "":
                continue
            return lyrics , url
        lyrics = ""
        url = ""
        return lyrics, url

    @classmethod
    def from_url(self, url: str):
        """
        Returns the lyrics as a string
        """
        if url == "":
            """return nil if url is nil"""
            return ""
        response = ses.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, features="lxml")
        retries = 3
        lyrics = soup.html.p.text
        while retries > 0 and len(lyrics) < 100:
            # time.sleep(0.2)
            response = ses.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, features="lxml")
            try:
                lyrics = soup.html.p.text
            except:
                pass
            retries -= 1
        if retries == 0 and len(lyrics) < 100:
            return ""
        return soup.html.p.text
    @classmethod
    def verify_status_code(self, response_json:dict):
        if response_json["meta"]["status"] != 200:
            print (f"error json_status_code is {response_json['meta']['status']}")

    @classmethod
    def get_url(self, artist: str, song: str) -> str:
        if "(" in song:
            song = song[: song.find("(")]
        artist.strip()
        song.strip()
        query = f"{artist} {song}"
        query.strip()
        song = song.lower()
        encoded_query = query.replace(" ", "+").replace("&", "+")
        search_url = base_search_url + encoded_query
        Ses = self.get_session()
        response_json = Ses.get(search_url).json()
        self.verify_status_code(response_json)
        for i in range(0, len(response_json["response"]["hits"])):
            url = str(response_json["response"]["hits"][i]["result"]["path"])
            formatted_url = url.replace("-", " ").lower()
            if not url.endswith("lyrics") or partial_ratio(formatted_url, song) < 90:
                continue
            # lyric_url = base_url + url
            return url

    @classmethod
    def lyrics_driver_method(self, primary_artist: str, song: str, artists:list = None)->str:
        lyrics, url = self.from_query(artist=primary_artist, song=song)
        if len(lyrics)==0 and artists != None:
            for artist in artists:
                lyrics, url = self.from_query(artist,song)
                if len(lyrics) == 0:
                    continue
                else:
                    return lyrics,url
            # repeat the process
            for artist in artists:
                lyrics, url = self.from_query(artist,song)
                if len(lyrics) == 0:
                    continue
                else:
                    return lyrics, url
        return lyrics, url
