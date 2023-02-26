from dff.script import Actor, TRANSITIONS, RESPONSE, Message, Context, NodeLabel3Type
import dff.script.labels as lbl
from dff.pipeline import Pipeline
import dff.script.conditions as cnd
from dff.messengers.telegram import PollingTelegramInterface
from conf import BOT_TOKEN

from api import get_songs_formated, get_song_info, search_artists

### Transitions

def request_song_transition(ctx: Context, actor: Actor, *args, **kwargs) -> NodeLabel3Type:
    message = ctx.last_request.text
    if message == 'cancel':
        return ('greeting_flow', 'request_task', 1.0)
    search_result = get_songs_formated(message)
    if search_result['status'] == 0:
        return ('song_search_flow', 'no_songs_found', 1.0)
    else:
        ctx.misc['song_search_res'] = search_result
        return ('song_search_flow', 'print_results', 1.0)

def request_artist_transition(ctx: Context, actor: Actor, *args, **kwargs) -> NodeLabel3Type:
    message = ctx.last_request.text
    if message == 'cancel':
        return ('greeting_flow', 'request_task', 1.0)
    search_result = search_artists(message)
    if search_result['status'] == 0:
        return ('artist_search_flow', 'no_songs_found', 1.0)
    else:
        ctx.misc['artist_search_res'] = search_result
        return ('artist_search_flow', 'print_results', 1.0)

### Responses

def print_song_search_results(ctx: Context, actor: Actor, *args, **kwargs) -> Message:
    response = 'Here\'s what i\'ve found:\n'
    response += ctx.misc['song_search_res']['formated'] + '\n\n'
    response += 'print song number if you\'d like to get more information about it'
    return Message(text = response)

def print_artist_search_results(ctx: Context, actor: Actor, *args, **kwargs) -> Message:
    response = 'Here\'s what i\'ve found:\n'
    response += ctx.misc['artist_search_res']['formated']
    return Message(text = response)

def print_song_info(ctx: Context, actor: Actor, *args, **kwargs) -> Message:
    msg = ctx.last_request.text
    try: 
        song_num = int(msg)
    except Exception as e:
        return Message(text = 'ooops')
    song_num = int(msg) - 1
    id = ctx.misc['song_search_res']['ids'][song_num]
    return Message(text = get_song_info(id))

### Conditions

def is_number_given(min = 1, max = 10):
    def check_num(ctx: Context, actor: Actor, *args, **kwargs) -> bool:
        msg = ctx.last_request.text
        try:
            index = int(msg)
        except Exception as e:
            return False
        return min <= index and index <= max

    return check_num

    
toy_script = {
    "greeting_flow": {
        'start_node': {
            RESPONSE: Message(),
            TRANSITIONS: {'request_task' : cnd.exact_match(Message(text="/start"))}
        },
        "request_task": {
            RESPONSE: Message(text="Hi, i can get information about songs from Genius.com.\
                               What would you like to find a song or an artist?"),
            TRANSITIONS: {('song_search_flow', 'start_node', 2.0) : cnd.exact_match(Message(text="Song")),
                          ('artist_search_flow', 'start_node', 2.0) : cnd.exact_match(Message(text="Artist")),
                          'fallback_node' : cnd.true()},
        },
        "fallback_node": {
            RESPONSE: Message(text="Sorry, i dont understand you. Specify type of content you would like to find (Artist/Song)"),
            TRANSITIONS: {('song_search_flow', 'start_node', 2.0) : cnd.exact_match(Message(text="Song")),
                          ('artist_search_flow', 'start_node', 2.0) : cnd.exact_match(Message(text="Artist")),
                          'fallback_node' : cnd.true()},
        }
    },
    "song_search_flow" : {
        "start_node": {
            RESPONSE: Message(text = 'Input lyrics you would like to find'),
            TRANSITIONS: {request_song_transition : cnd.true()}
        },
        'no_songs_found': {
            RESPONSE: Message(text = 'I couldn\'t find any songs with such lyrics, try something else'),
            TRANSITIONS: {request_song_transition: cnd.true()}
        },
        'print_results': {
            RESPONSE: print_song_search_results, 
            TRANSITIONS: {('song_search_flow', 'print_info', 2) : is_number_given(1,10),
                          ('greeting_flow', 'request_task', 1.5) : cnd.true()}
        },
        'print_info' : {
            RESPONSE: print_song_info,
            TRANSITIONS: {('greeting_flow', 'request_task', 1) : cnd.true()}
        }
    },
    "artist_search_flow": {
        "start_node": {
            RESPONSE: Message(text ="What artist would you like to find?"),
            TRANSITIONS: {request_artist_transition : cnd.true()}
        },
        'print_results': {
            RESPONSE : print_artist_search_results,
            TRANSITIONS: {('greeting_flow', 'request_task', 1) : cnd.true()}
        },
        'no_artist_found': {
            RESPONSE: Message(text = 'I couldn\t find any artists, try something else'),
            TRANSITIONS: {request_artist_transition : cnd.true()}
        }
    }
}

interface = PollingTelegramInterface(BOT_TOKEN)

pipeline = Pipeline.from_script(
    toy_script,
    start_label=("greeting_flow", "start_node"),
    fallback_label=("greeting_flow", "fallback_node"),
    messenger_interface=interface
)


if __name__ == "__main__":
    pipeline.run()