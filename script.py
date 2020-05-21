# created by aakash37
# download songs from databrainz database
# v4.1.1

import json
import multiprocessing
import time

try:
    import requests
    from playsound import playsound

except ModuleNotFoundError:
    print("please install the required modules from requirements.txt")
    exit(1)


search_response_items = 50  # number of response items

get_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) \
        Gecko/20100101 Firefox/72.0",
    "Accept": "*/*",
    "Referer": "http://musicpleer.cloud/",
}


def search_song(_srh):
    print("SEARCHING...")
    search_url = "https://databrainz.com/api/search_api.cgi"

    search_params = {
        "jsoncallback": "jQuery1111019191608358321144_1580929162911",
        "qry": _srh,  # song name goes here
        "format": "json",
        "mh": search_response_items,
        "where": "mpl",
    }

    try:
        search_resp = requests.get(
            search_url, headers=get_headers, params=search_params
        )

    except requests.exceptions.Timeout:
        print("\tconnection timed out RETRYING...\n ")
        search_song(_srh)

    except requests.exceptions.ConnectionError:
        print("\tconnection ERROR\n ")
        exit(1)

    if search_resp.text == "":
        print("no results found\n")
        main()

    else:
        search_json = json.loads(search_resp.text[43:-1])
        print("SONGS FOUND")
    return search_json


def progress(percent=0, width=35):
    left = width * percent // 100
    right = width - left
    print(
        "\r[",
        "#" * left,
        f"{percent:>3}%",
        " " * right,
        "]",
        sep="",
        end="",
        flush=True,
    )


# get the song data from database
def get_song(_search_json, i):
    song_url = "https://databrainz.com/api/data_api_new.cgi"

    while i <= search_response_items:
        song_params = {
            "jsoncallback": "jQuery1111019191608358321144_1580929162911",
            "id": _search_json["results"][i]["url"],  # song url goes here
            "r": "mpl",
            "format": "json",
            "_": int(round(time.time() * 1000)),
        }

        print(f"FETCHING SONG INFO[{i}]...")
        try:
            song_resp = requests.get(song_url, headers=get_headers, params=song_params)

        except requests.exceptions.ConnectionError:
            print("\tconnection ERROR\n ")
            exit(1)

        song_json = json.loads(song_resp.text[43:-1])

        if song_json["song"]["returncode"] != "200":
            print("\tnot found")
            i += 1
            continue

        else:
            print("\n---RESULT---")
            print(f"title: {song_json['song']['title']}")
            print(f"artist: {song_json['song']['artist']}")
            print(f"album: {song_json['song']['album']}")
            print(f"release date: {song_json['song']['date']}")
            print(f"size: {round((int(song_json['song']['size']) / 1000000), 2)} MB")
            return song_json


# download the song
def download_song(_song_json):
    print("\nDOWNLOADING...\n")
    try:
        file_resp = requests.get(_song_json["song"]["url"], stream=True)

    except requests.exceptions.ConnectionError:
        print("\tconnection ERROR\n ")
        exit(1)

    if _song_json["song"]["artist"] != "":
        file_name = (
            f"{_song_json['song']['artist']} - {_song_json['song']['title']}.mp3"
        )
    else:
        file_name = _song_json["song"]["title"] + ".mp3"

    total_size = int(file_resp.headers.get("content-length", 0))
    print(total_size)

    with open(file_name, "wb") as file:
        length = 0
        for data in file_resp.iter_content(1024):
            length += len(data)
            progress(int(length / total_size * 100))
            file.write(data)

    print("\nDOWNLOAD SUCESSFUL\n")

    main()


def main():
    i = 0

    print("\n===|Songs downloader|===\ntype 'exit' to terminate the " "program")

    srh = input("Name of the song: ")
    if srh.lower() == "exit":
        exit(0)
    else:
        search_json = search_song(srh)
        song_json = get_song(search_json, i)

    a = None
    while a != "q" or a != "r":

        print("\nEnter")
        print("    'q' to DOWNLOAD the song")
        print("    'w' to STREAM this song(under development)")
        print("    'e' for NEXT RESULT")
        print("    'r' to CANCEL")
        a = input("   > ").lower()
        print()

        if a == "q":
            download_song(song_json)
            break

        elif a == "w":
            print("\nSTREAMING...")
            p = multiprocessing.Process(
                target=playsound, args=(song_json["song"]["url"],)
            )
            p.start()
            input("press ENTER to stop playback")
            p.terminate()
            continue

        elif a == "e":
            i += 1
            song_json = get_song(search_json, i)
            continue

        elif a == "r":
            break

        else:
            continue


if __name__ == "__main__":
    main()
