from requests import session
from rauth import OAuth2Service

masterSession = None
geniusSession = None


def get_session():
    global masterSession
    if masterSession:
        # print('session already initialized')
        return masterSession
    else:
        masterSession = session()
        masterSession.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; FriendlyLilBot/0.1; +https://github.com/brayo-pip)"
            }
        )
        return masterSession


def get_genius_session():
    global geniusSession
    if geniusSession:
        return geniusSession
    else:
        client = OAuth2Service(
            client_id="NWIr1nGkiXORidM-uPg3vJCkunxpRt6KW8GLBISTI72RHNbJ9pNI9uNojMk7T2mL",
            client_secret="llFZD5kU4hEG-8H8nEo9ircddUFkVPdPTtIP5f-VWzM2fI84mrHRKtqq0V31euKKqQyN4lrUKJZMVjAAx972cg",
        )
        geniusSession = client.get_session(
            token="1jQVW-1UtzCluk1DEVKHTzbsZpHegvK1VMXTtJDebF_vQKhDHgUpcqdv1eyFtj4k"
        )
        return geniusSession
