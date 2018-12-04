import os
import time
from enum import Enum
from slackclient import SlackClient
import re

# instantiate Slack client
slack_client = SlackClient("xoxb-283048524000-383343305728-Q39KhMKxPfcY1a3g4XJThCiM")
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1  # 1 second delay between reading from RTM
FOODCON_BOT_VERSION = "v0.2 - Early Alpha - Now with crappy food and location commands!"
FOODCON_HELP_COMMAND = "help"
FOODCON_SET_COMMAND = "set "
FOODCON_LOG_COMMAND = "log "
FOODCON_STATUS_COMMAND = "status"
FOODCON_SET_FOOD_DETAILS = "food "
FOODCON_SET_FOOD_LOCATION = "location "
BOI_DOT_GIF = "https://i.imgur.com/rLgVcmk.gif"
foodcon_food = None
foodcon_level = None
foodcon_location = None

MENTION_REGEX = "^<@(|[WU].+?)>(.*)"


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Stop it. Get some help, try *{}*.".format(FOODCON_HELP_COMMAND)

    # Variables for storing various foodcon details

    response = None
    global foodcon_level
    global foodcon_food
    global foodcon_location

    # This is where you start to implement more commands!

    # ========================================= LOG ====================================================================

    if command.casefold().startswith(FOODCON_LOG_COMMAND):

            command_parameters = command.split(" ", 3)

            if len(command_parameters) is not 4:
                response = "Incorrect number of arguments. Please try again with: log payer payee amount reason"
            else:
                foodcon_level = command_parameters[1]
                foodcon_food = command_parameters[2]
                foodcon_location = command_parameters[3]

                response = "FOODCON " + foodcon_level + ": " + foodcon_food + " available at " + foodcon_location + "! Enjoy!"

    # ========================================= SET ====================================================================

    if command.casefold().startswith(FOODCON_SET_COMMAND):
        option = command.casefold().split(FOODCON_SET_COMMAND)[1]
        one_to_four = ["1", "2", "3", "4"]
        if option in one_to_four:
            response = ":alert: FOODCON RAISED TO FOODCON " + option + ". I REPEAT. *FOODCON " + option + " *. :alert:"
            foodcon_level = option

    if command.casefold().startswith(FOODCON_SET_COMMAND) and option == "5":
        response = "FOODCON SET TO FOODCON5. I REPEAT. *FOODCON 5*. STAND DOWN."
        foodcon_level = str(5)
        foodcon_food = 'No food'
        foodcon_location = 'No location'

    # ========================================= BOI ====================================================================

    if command == "boi":
        response = BOI_DOT_GIF

    # ========================================= FOOD_DETAILS ===========================================================

    if command.casefold().startswith(FOODCON_SET_FOOD_DETAILS):
        foodcon_food = command.casefold().split("food", 1)[1]
        response = "OK, got it. Sounds tasty :eyes:"

    # ========================================= FOOD_LOCATION ==========================================================

    if command.casefold().startswith(FOODCON_SET_FOOD_LOCATION):
        foodcon_location = command.casefold().split("location", 1)[1]
        response = "OK, got it. I'll be paying a visit :eyes:"

    # ========================================= STATUS =================================================================

    if command.casefold() == FOODCON_STATUS_COMMAND:  # & foodcon_level is '1' or '2' or '3' or '4' or '5':

        try:
            if foodcon_level is None:
                foodcon_level = '5'
            if foodcon_food is None:
                foodcon_food = 'No food'
            if foodcon_location is None:
                foodcon_location = 'No location'

            response = "WE ARE CURRENTLY AT *FOODCON " + foodcon_level + "* | *LOCATION*: " + foodcon_location + " *FOOD*: " + foodcon_food + ""
        except NameError:
            response = "If you're seeing this, a NameError exception has occured. Shit's fucked yo."

    # ========================================= HELP ===================================================================

    if command.casefold() == FOODCON_HELP_COMMAND:  # monstrosity
        response = "FOODCON App - " + FOODCON_BOT_VERSION + "\n This is currently a primitive bot, all commands must " \
                                                            "be " \
                                                            "'@foodcon `command`'\n Commands: \n \n *" + FOODCON_STATUS_COMMAND + \
                   "* - Returns the current FOODCON level. \n *" + FOODCON_SET_COMMAND + \
                   "* `1`, `2`, `3`, `4` or `5` - Sets the FOODCON level " \
                   "to the specified value. \n *" + FOODCON_SET_FOOD_DETAILS + "* " \
                                                                               "`name/types of food` - Adds this to " \
                                                                               "the `status` command \n *" \
                   + FOODCON_SET_FOOD_LOCATION + "* `location of food` - Adds this to the `status` command"

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
