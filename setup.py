from setuptools import setup

setup(
    name="minimal",
    packages=[
        "minimal",
        "minimal.search",
        "minimal.download",
    ],
    version="1.0.0",
    install_requires=[
        "spotipy",
        "pytube",
        "rapidfuzz",
        "rich",
        "requests",
        "mutagen",
        "ytmusicapi",
        "youtube-search-python",
        "rauth",
        "lxml",
        "pymongo",
        "dnspython",
    ],
    description="Downloads Spotify music from Youtube with metadata and album art",
    author="Brian Syuki",
    author_email="vukubrian@gmail.com",
    license="MIT",
    python_requires=">=3.6",
    url="https://github.com/brayo-pip",
    download_url="https://pypi.org/project/minimal-dl/",
    keywords=[
        "spotify",
        "downloader",
        "download",
        "music",
        "youtube",
        "mp3",
        "album",
        "metadata",
    ],
    classifiers=[
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Utilities",
    ],
    entry_points={"console_scripts": ["minimal = minimal.__main__:console_entry_point"]},
)
