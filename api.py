from lyricsgenius import Genius
from conf import GENIOUS_TOKEN

token = GENIOUS_TOKEN
genius = Genius(token)


def get_songs_formated(search_text: str):
    results = genius.search_songs(search_text)
    num_results = len(results["hits"])
    if num_results == 0:
        return {"status": 0}
    else:
        response = "Here's top 10 results:\n"
        formated_songs = []
        ids = []
        for i in range(min(num_results, 10)):
            cur_res = results["hits"][i]["result"]
            title = cur_res["title"]
            artist = cur_res["primary_artist"]["name"]
            formated_songs.append(f"{i + 1}. {title} by {artist}")
            ids.append(cur_res["id"])
        response += "\n".join(formated_songs)
    return {"status": 1, "formated": response, "ids": ids}

def get_song_info(song_id : int):
    song = genius.song(song_id)['song']
    title = song['title']
    author = song['primary_artist']['name']
    album = song['album']['name']
    views = song['stats']['pageviews']
    url = song['url']
    return f'artist: {author}\ntitle: {title}\nalbum: {album}\nviews: {views}\nurl: {url}'


def search_artists(search_text : str):
    res = genius.search_artists(search_text, per_page = 10)['sections'][0]['hits']
    if len(res) == 0:
        return {'status' : 0}
    formated_artists = []
    ids = []
    for i in range(len(res)):
        cur_artist = res[i]['result']
        ids.append(cur_artist['id'])
        formated_artists.append(f'{i+1}. {cur_artist["name"]}')
    res_str = "\n".join(formated_artists)
    return {'status' : 1, 'formated' : res_str, 'ids' : ids}