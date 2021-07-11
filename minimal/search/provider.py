# ===============
# === Imports ===
# ===============
from datetime import timedelta
from time import strptime

# ! Just for static typing
from typing import List

# ! the following are for the search provider to function
from rapidfuzz.fuzz import partial_ratio
from youtubesearchpython import CustomSearch, VideoSortOrder

# ================================
# === Note to readers / Coders ===
# ================================

# ! YTM search (the actual POST request), courtesy of Elliot G. (@rocketinventor)
# ! result parsing and song matching system by @Mikhail-Zex
# !
# ! Essentially, Without Elliot, you wouldn't have a YTM search provider at all.


# =======================
# === helper function ===
# =======================


def match_percentage(str1: str, str2: str, score_cutoff: float = 0) -> float:
    """
    `str` `str1` : a random sentence

    `str` `str2` : another random sentence

    `float` `score_cutoff` : minimum score required to consider it a match
                             returns 0 when similarity < score_cutoff

    RETURNS `float`

    A wrapper around `rapidfuzz.fuzz.partial_ratio` to handle UTF-8 encoded
    emojis that usually cause errors
    """

    # ! this will throw an error if either string contains a UTF-8 encoded emoji
    try:
        return partial_ratio(str1, str2, score_cutoff=score_cutoff)

    # ! we build new strings that contain only alphanumerical characters and spaces
    # ! and return the partial_ratio of that
    except:
        newStr1 = ""

        for eachLetter in str1:
            if eachLetter.isalnum() or eachLetter.isspace():
                newStr1 += eachLetter

        newStr2 = ""

        for eachLetter in str2:
            if eachLetter.isalnum() or eachLetter.isspace():
                newStr2 += eachLetter

        return partial_ratio(newStr1, newStr2, score_cutoff=score_cutoff)


# ========================================================================
# === Background functions/Variables (Not meant to be called directly) ===
# ========================================================================

# ! YTMusic api client



def __parse_duration(duration: str) -> float:
    try:
        if len(duration) > 5:
            padded = duration.rjust(8, "0")
            x = strptime(padded, "%H:%M:%S")
        elif len(duration) > 2:
            padded = duration.rjust(5, "0")
            x = strptime(padded, "%M:%S")
        else:
            x = strptime(duration, "%S")

        return timedelta(
            hours=x.tm_hour, minutes=x.tm_min, seconds=x.tm_sec
        ).total_seconds()
    except (ValueError, TypeError):
        return 0.0


def __map_result_to_song_data(result: dict) -> dict:
    song_data = {
        "name": result["title"],
        "length": __parse_duration(result["duration"]),
        "link": result["link"],
    }
    return song_data



def __query_and_simplify(searchTerm: str) -> List[dict]:
    """
    `str` `searchTerm` : the search term you would type into YTM's search bar

    RETURNS `list<dict>`

    For structure of dict, see comment at function declaration
    """

    # ! For dict structure, see end of this function (~ln 268, ln 283) and chill, this
    # ! function ain't soo big, there are plenty of comments and blank lines


    result = CustomSearch(searchTerm, VideoSortOrder.relevance, limit= 5, region="KE").result()
    searchResult = result['result']
    return list(map(__map_result_to_song_data, searchResult))


# =======================
# === Search Provider ===
# =======================



def search_and_order_ytm_results(
    songName: str,
    songArtists: List[str],
    songDuration: int,
) -> dict:
    """
    `str` `songName` : name of song

    `list<str>` `songArtists` : list containing name of contributing artists

    `str` `songAlbumName` : name of song's album

    `int` `songDuration`

    RETURNS `dict`

    each entry in the result if formated as {'$YouTubeLink': $matchValue, ...}; Match value
    indicates how good a match the result is the the given parameters. THe maximum value
    that $matchValue can take is 100, the least value is unbound.
    """
    # Query YTM
    results = __query_and_simplify(
        get_ytm_search_query(songName, songArtists),
    )

    # Assign an overall avg match value to each result
    linksWithMatchValue = {}

    for result in results:
        # ! If there are no common words b/w the spotify and YouTube Music name, the song
        # ! is a wrong match (Like Ruelle - Madness being matched to Ruelle - Monster, it
        # ! happens without this conditional)

        # ! most song results on youtube go by $artist - $songName, so if the spotify name
        # ! has a '-', this function would return True, a common '-' is hardly a 'common
        # ! word', so we get rid of it. Lower-caseing all the inputs is to get rid of the
        # ! troubles that arise from pythons handling of differently cased words, i.e.
        # ! 'Rhino' == 'rhino' is false though the word is same... so we lower-case both
        # ! sentences and replace any hypens(-)
        lowerSongName = songName.lower()
        lowerResultName = result["name"].lower()

        sentenceAWords = lowerSongName.replace("-", " ").split(" ")

        commonWord = False

        # ! check for common word
        # ! break if there's any shared commonWord
        for word in sentenceAWords:
            if word != "" and word in lowerResultName:
                commonWord = True
                break

        # ! if there are no common words, skip result
        if not commonWord:
            continue


        # Find name match
        nameMatch = round(match_percentage(result["name"], songName), ndigits=3)

        # Find duration match
        # ! time match = 100 - (delta(duration)**2 / original duration * 100)
        # ! difference in song duration (delta) is usually of the magnitude of a few
        # ! seconds, we need to amplify the delta if it is to have any meaningful impact
        # ! wen we calculate the avg match value
        delta = result["length"] - songDuration
        nonMatchValue = (delta ** 2) / songDuration * 100

        timeMatch = 100 - nonMatchValue
        
        # the results along with the avg Match
        avgMatch = (nameMatch + timeMatch*3) / 4

        linksWithMatchValue[result["link"]] = avgMatch

    return linksWithMatchValue


def get_ytm_search_query(songName: str, songArtists: List[str]) -> str:
    joined_artists = songArtists[0]
    return f"{joined_artists} - {songName}"


def search_and_get_best_match(
    songName: str,
    songArtists: List[str],
    songDuration: int,
) -> str:
    """
    `str` `songName` : name of song

    `list<str>` `songArtists` : list containing name of contributing artists

    `str` `songAlbumName` : name of song's album

    `int` `songDuration` : duration of the song

    RETURNS `str` : link of the best match
    """

    # ! This is lazy coding, sorry.
    results = search_and_order_ytm_results(
        songName, songArtists, songDuration,
    )

    if len(results) == 0:
        return None

    resultItems = list(results.items())
    sortedResults = sorted(resultItems, key=lambda x: x[1], reverse=True)

    # ! In theory, the first 'TUPLE' in sortedResults should have the highest match
    # ! value, we send back only the link
    return sortedResults[0][0]