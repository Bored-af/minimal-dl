from youtubesearchpython import CustomSearch, VideoSortOrder
from typing import List


def search_and_get_best_match(
    songName: str,
    songArtists: List[str],
    songAlbumName: str,
    songDuration: int,
    explicit: bool,
) -> str:
    """
    `str` `songName` : name of song

    `list<str>` `songArtists` : list containing name of contributing artists

    `str` `songAlbumName` : name of song's album

    `int` `songDuration` : duration of the song

    RETURNS `str` : link of the best match
    """

    return CustomSearch(f"{songName} - {songArtists[0]}",VideoSortOrder.viewCount).result()["result"][0]["link"]