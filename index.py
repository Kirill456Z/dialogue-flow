from dff.script import Actor, TRANSITIONS, RESPONSE, Message
from dff.pipeline import Pipeline
import dff.script.conditions as cnd
from dff.messengers.telegram import PollingTelegramInterface
from conf import BOT_TOKEN

from dff.utils.testing.common import (
    check_happy_path,
    is_interactive_mode,
    run_interactive_mode,
)

toy_script = {
    "greeting_flow": {
        "start_node": {  # This is the initial node,
            # it doesn't contain a `RESPONSE`.
            RESPONSE: Message(),
            TRANSITIONS: {"node1": cnd.exact_match(Message(text="Hi"))},
            # If "Hi" == request of the user then we make the transition.
        },
        "node1": {
            RESPONSE: Message(text="Hi, how are you?"),  # When the agent enters node1,
            # return "Hi, how are you?".
            TRANSITIONS: {"node2": cnd.exact_match(Message(text="I'm fine, how are you?"))},
        },
        "node2": {
            RESPONSE: Message(text="Good. What do you want to talk about?"),
            TRANSITIONS: {"node3": cnd.exact_match(Message(text="Let's talk about music."))},
        },
        "node3": {
            RESPONSE: Message(text="Sorry, I can not talk about music now."),
            TRANSITIONS: {"node4": cnd.exact_match(Message(text="Ok, goodbye."))},
        },
        "node4": {
            RESPONSE: Message(text="Bye"),
            TRANSITIONS: {"node1": cnd.exact_match(Message(text="Hi"))},
        },
        "fallback_node": {
            # We get to this node if the conditions
            # for switching to other nodes are not performed.
            RESPONSE: Message(text="Ooops"),
            TRANSITIONS: {"node1": cnd.exact_match(Message(text="Hi"))},
        },
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