#! Basic necessities to get the CLI running
from minimal.search.spotifyClient import initialize
from sys import argv as cliArgs

#! Song Search from different start points
from minimal.search.utils import get_playlist_tracks, get_album_tracks, search_for_song, get_artist_tracks
from minimal.search.songObj import SongObj

#! The actual download stuff
from minimal.download.downloader import DownloadManager

#! to avoid packaging errors
from multiprocessing import freeze_support

#! used to quiet the output
from io import StringIO as quiet
import sys

#! Script Help
help_notice = '''
To download a song run,
    minimal $trackUrl
    eg. minimal https://open.spotify.com/track/08mG3Y1vljYA6bvDt4Wqkj?si=SxezdxmlTx-CaVoucHmrUA

To download a album run,
    minimal $albumUrl
    eg. minimal https://open.spotify.com/album/2YMWspDGtbDgYULXvVQFM6?si=gF5dOQm8QUSo-NdZVsFjAQ

To download a playlist run,
    minimal $playlistUrl
    eg. minimal https://open.spotify.com/playlist/37i9dQZF1DWXhcuQw7KIeM?si=xubKHEBESM27RqGkqoXzgQ

To download an artist's songs run,
    minimal $artistUrl
    eg. minimal https://open.spotify.com/artist/6fOMl44jA4Sp5b9PpYCkzz

To search for and download a song (not very accurate) run,
    minimal $songQuery
    eg. minimal 'The HU - Sugaan Essenna'

To resume a failed/incomplete download run,
    minimal $pathToTrackingFile
    eg. minimal 'Sugaan Essenna.minimalTrackingFile'

    Note, '.minimalTrackingFiles' are automatically created during download start, they are deleted on
    download completion

You can chain up download tasks by seperating them with spaces:
    minimal $songQuery1 $albumUrl $songQuery2 ... (order does not matter)
    eg. minimal 'The Hu - Sugaan Essenna' https://open.spotify.com/playlist/37i9dQZF1DWXhcuQw7KIeM?si=xubKHEBESM27RqGkqoXzgQ ...

minimal downloads up to 4 songs in parallel - try to download albums and playlists instead of
tracks for more speed
'''

def console_entry_point():
    '''
    This is where all the console processing magic happens.
    Its super simple, rudimentary even but, it's dead simple & it works.
    '''

    if '--help' in cliArgs or '-h' in cliArgs:
        print(help_notice)

        #! We use 'return None' as a convenient exit/break from the function
        return None

    if '--quiet' in cliArgs:
        #! removing --quiet so it doesnt mess up with the download
        cliArgs.remove('--quiet')
        #! make stdout & stderr silent
        sys.stdout = quiet()
        sys.stderr = quiet()

    initialize(
        clientId     = '4fe3fecfe5334023a1472516cc99d805',
        clientSecret = '0f02b7c483c04257984695007a4a8d5c'
        )

    downloader = DownloadManager()

    for request in cliArgs[1:]:
        if ('open.spotify.com' in request and 'track' in request) or 'spotify:track:' in request:
            print('Fetching Song...')
            song = SongObj.from_url(request)

            if song.get_youtube_link() != None:
                downloader.download_single_song(song)
            else:
                print('Skipping %s (%s) as no match could be found on youtube' % (
                    song.get_song_name(), request
                ))

        elif ('open.spotify.com' in request and 'album' in request) or 'spotify:album:' in request:
            print('Fetching Album...')
            songObjList = get_album_tracks(request)

            downloader.download_multiple_songs(songObjList)

        elif ('open.spotify.com' in request and 'playlist' in request) or 'spotify:playlist:' in request:
            print('Fetching Playlist...')
            songObjList = get_playlist_tracks(request)

            downloader.download_multiple_songs(songObjList)

        elif ('open.spotify.com' in request and 'artist' in request) or 'spotify:artist:' in request:
            print('Fetching Artist\'s Tracks...')
            songObjList = get_artist_tracks(request)

            downloader.download_multiple_songs(songObjList)

        elif request.endswith('.txt'):
            print('Fetching songs from %s...' % request)
            songObjList = []

            with open(request, 'r') as songFile:
                for songLink in songFile.readlines():
                    song = SongObj.from_url(songLink)
                    songObjList.append(song)

            downloader.download_multiple_songs(songObjList)

        elif request.endswith('.minimalTrackingFile'):
            print('Preparing to resume download...')
            downloader.resume_download_from_tracking_file(request)

        else:
            print('Searching for song "%s"...' % request)
            try:
                song = search_for_song(request)
                downloader.download_single_song(song)

            except Exception:
                print('No song named "%s" could be found on spotify' % request)

    downloader.close()

if __name__ == '__main__':
    freeze_support()

    console_entry_point()
