import argparse
import sys
import logging

import communitybot.settings
from communitybot.curate import Curator
from communitybot.playgame import Game
from communitybot.utils import add_discord_user, get_steem_conn
from communitybot.utils import get_option

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig()

runners = ["discordbot", "curate", "playgame"]


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--run")
    parser.add_argument("--add-discord-user")
    parser.add_argument("--start-block")

    args = parser.parse_args()
    runner = args.run
    start_block = args.start_block

    if args.add_discord_user:
        added = add_discord_user(*args.add_discord_user.split("#"))
        if added:
            sys.exit("%s added to the authorized discord users." %
                     args.add_discord_user)
        else:
            sys.exit("%s is already an authorized discord user." %
                     args.add_discord_user)

    if runner and runner not in runners:
        sys.exit(
            "%s is not in available runners. Options: %s" % (
                args.run, runners)
        )

    if runner == "discordbot":
        from communitybot.discordbot import bot
        bot.run(communitybot.settings.BOT_TOKEN)
    elif runner == "curate":
        c = Curator(
            get_steem_conn(),
            communitybot.settings.TAGS,
            communitybot.settings.BOT_ACCOUNT,
        )
        starting_point = None
        if start_block:
            starting_point = int(start_block)
        else:
            # get the starting point
            option = get_option(communitybot.settings.LAST_BLOCK_ID)
            if option:
                starting_point = int(option["value"])

        logger.info("Starting from block %s", starting_point)
        c.listen_blocks(starting_point=starting_point)
    elif runner == "playgame":
        c = Game(
            get_steem_conn(),
            communitybot.settings.BOT_ACCOUNT,
        )
        c.start_game();

if __name__ == '__main__':
    main()
