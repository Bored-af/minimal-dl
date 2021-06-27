import concurrent.futures, threading

from minimal.search.spotifyClient import get_spotify_client
from minimal.search.songObj import SongObj

from typing import List
from bisect import bisect_left

import minimal.config

import os.path

path = minimal.config.path
skipFile = minimal.config.skipFile
if os.path.exists(path):
    file = open(path, "r")
else:
    file = open(path, "x")

links = [line[: len(line) - 1] for line in file]

links.sort()


def song_present(url: str, links: List):
    index = bisect_left(links,url)
    if index != len(links):
        if links[index] == url:
            return True
    return False


def search_for_song(query: str) -> SongObj:
    """
    `str` `query` : what you'd type into spotify's search box

    Queries Spotify for a song and returns the best match
    """

    # get a spotify client
    spotifyClient = get_spotify_client()

    # get possible matches from spotify
    result = spotifyClient.search(query, type="track")

    # return first result link or if no matches are found, raise and Exception
    if len(result["tracks"]["items"]) == 0:
        raise Exception("No song matches found on Spotify")
    else:
        for songResult in result["tracks"]["items"]:
            songUrl = "http://open.spotify.com/track/" + songResult["id"]
            if song_present(songUrl, links) and skipFile:
                "song matches skipped, already in skip file"
                continue
            song = SongObj.from_url(songUrl)

            if song.get_youtube_link() != None:
                return song

        raise Exception("Could not match any of the results on YouTube")


def get_album_tracks(albumUrl: str) -> List[SongObj]:
    """
    `str` `albumUrl` : Spotify Url of the album whose tracks are to be
    retrieved

    returns a `list<songObj>` containing Url's of each track in the given album
    """

    spotifyClient = get_spotify_client()
    albumTracks = []
    albumUrls = []
    trackResponse = spotifyClient.album_tracks(albumUrl)
    global skipFile
    skip = skipFile
    # while loop acts like do-while
    offset = 0
    while True:

        for track in trackResponse["items"]:
            url = "https://open.spotify.com/track/" + track["id"]
            if song_present(url, links) and skip:
                # the link is present in the skip file
                continue
            else:
                albumUrls.append(url)

        offset += 100
        # check if more tracks are to be passed
        if trackResponse["next"]:
            trackResponse = spotifyClient.album_tracks(albumUrl, offset=offset)
        else:
            break
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for url in albumUrls:
            futures.append(executor.submit(build_songObj, url))
    for future in concurrent.futures.as_completed(futures):
        if future.result() is not None:
            albumTracks.append(future.result())

    print(f"Downloading {len(albumTracks)} songs")
    return albumTracks


def get_playlist_tracks(playlistUrl: str) -> List[SongObj]:
    """
    `str` `playlistUrl` : Spotify Url of the album whose tracks are to be
    retrieved

    returns a `list<songObj>` containing Url's of each track in the given playlist
    """

    spotifyClient = get_spotify_client()
    playlistTracks = []
    playlistUrls = []

    playlistResponse = spotifyClient.playlist_tracks(playlistUrl)
    global skipFile
    skip = skipFile
    # while loop to mimic do-while
    offset = 0
    while True:
        for songEntry in playlistResponse["items"]:
            url = "https://open.spotify.com/track/" + songEntry["track"]["id"]
            if song_present(url, links) and skip:
                # the link is present in the skip file
                continue
            else:
                playlistUrls.append(url)
        offset += 100
        # check if more tracks are to be passed
        if playlistResponse["next"]:
            playlistResponse = spotifyClient.playlist_tracks(playlistUrl, offset=offset)
        else:
            break
    futures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for url in playlistUrls:
            futures.append(executor.submit(build_songObj, url))

    for future in concurrent.futures.as_completed(futures):
        if future.result() is not None:
            playlistTracks.append(future.result())

    print(f"Downloading {len(playlistTracks)} songs")
    return playlistTracks


def get_textfile_tracks(filename: str) -> List[SongObj]:
    if os.path.exists(filename):
        file = open(filename, "r")
        links = [link[:-1] for link in file]

        futures = []
        textfileTracks = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for url in links:
                futures.append(executor.submit(build_songObj, url))

        for future in concurrent.futures.as_completed(futures):

            if future.result() is not None:
                textfileTracks.append(future.result())

        print(f"Downloading {len(textfileTracks)} songs")
        return textfileTracks
    else:
        print("file does not exist")
        return None


def build_songObj(url: str) -> SongObj:
    song = SongObj.from_url(url)
    if song.get_youtube_link() != None:
        return song
    else:
        threading.Semaphore().acquire()
        print(
            f"No youtube link found for {song.get_primary_artist_name()} {song.get_song_name()}"
        )
        threading.Semaphore().release()
        return None


def get_artist_tracks(artistUrl: str) -> List[SongObj]:
    """
    `str` `artistUrl` : Spotify Url of the artist whose tracks are to be
    retrieved

    returns a `List` containing Url's of each track of the artist.
    """

    spotifyClient = get_spotify_client()
    artistAlbums = []
    artistTracks = []

    artistResponse = spotifyClient.artist_albums(artistUrl)
    artistName = spotifyClient.artist(artistUrl)["name"]

    while True:

        for album in artistResponse["items"]:
            albumUrl = album["external_urls"]["spotify"]

            artistAlbums.append(albumUrl)

        # Check if the artist has more albums.
        if artistResponse["next"]:
            artistResponse = spotifyClient.artist_albums(
                artistUrl, offset=len(artistAlbums)
            )
        else:
            break

    for album in artistAlbums:
        albumTracks = get_album_tracks(album)

        artistTracks += albumTracks

    #! Filter out the Songs in which the given artist has not contributed.
    artistTracks = [
        track
        for track in artistTracks
        if artistName in track.get_contributing_artists()
    ]

    return artistTracks
