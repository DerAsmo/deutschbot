import logging

from communitybot.settings import THRESHOLD_OPTION_ID, BOT_ACCOUNT
from communitybot.utils import (
    is_authorized,
    add_to_blacklist,
    remove_from_blacklist,
    username_is_valid,
    add_to_curators,
    remove_from_curators,
    get_curators,
    get_help_message,
    get_option,
    set_option,
    start_game
)
from communitybot.playgame import Game

from discord.ext.commands import Bot

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig()

description = '''**```-- deutschbot --
Below a list of available commands:```**
'''

bot = Bot(
    description=description,
    command_prefix="$",
    pm_help=False)
bot.remove_command('help')


@bot.event
async def on_ready():
    logger.info("Logged in")


@bot.command()
async def help():
    await bot.say(get_help_message(description))


@bot.group(pass_context=True)
async def blacklist(ctx):
    if ctx.invoked_subcommand is None:
        await bot.say('Usage: $blacklist add username or $blacklist'
                      ' remove username')


@blacklist.command(pass_context=True)
async def add(ctx, account):

    if not is_authorized(ctx.message.author):
        await bot.say('You are not authorized to do that.')
        return

    if not username_is_valid(account):
        await bot.say('%s is not a valid username.' % account)
        return

    added = add_to_blacklist(account, str(ctx.message.author))
    if added:
        message = "%s added to blacklist." % account
    else:
        message = "%s is already on the blacklist." % account

    await bot.say(message)


@blacklist.command(pass_context=True)
async def remove(ctx, account):

    if not is_authorized(ctx.message.author):
        await bot.say('You are not authorized to do that.')
        return

    if not username_is_valid(account):
        await bot.say('%s is not a valid username.' % account)
        return

    removed = remove_from_blacklist(account)
    if removed:
        message = "%s removed from blacklist." % account
    else:
        message = "%s is not on the blacklist!" % account

    await bot.say(message)


@bot.group(pass_context=True)
async def curators(ctx):
    if ctx.invoked_subcommand is None:
        await bot.say('Usage: $curators add username or $curators'
                      ' remove username')


@curators.command(pass_context=True)
async def add(ctx, account):

    if not is_authorized(ctx.message.author):
        await bot.say('You are not authorized to do that.')
        return

    if not username_is_valid(account):
        await bot.say('%s is not a valid username.' % account)
        return

    added = add_to_curators(account, str(ctx.message.author))
    if added:
        message = "%s added to curators." % account
    else:
        message = "%s is already on the curators." % account

    await bot.say(message)


@curators.command(pass_context=True)
async def remove(ctx, account):

    if not is_authorized(ctx.message.author):
        await bot.say('You are not authorized to do that.')
        return

    if not username_is_valid(account):
        await bot.say('%s is not a valid username.' % account)
        return

    removed = remove_from_curators(account)
    if removed:
        message = "%s removed from curators." % account
    else:
        message = "%s is not on the curators!" % account

    await bot.say(message)


@curators.command()
async def list():
    curators = [c["account"] for c in get_curators()]
    await bot.say("**Current active curators**: " + ", ".join(curators))

@bot.group(pass_context=True)
async def game(ctx):
    if ctx.invoked_subcommand is None:
        await bot.say('Usage: $game start')

@game.command()
async def start():
    start_game(bot)
    await bot.say("**Game started**")

@bot.group(pass_context=True)
async def threshold(ctx):

    if ctx.invoked_subcommand is None:
        await bot.say('Usage: $threshold get or $threeshold set 1000')


@threshold.command(pass_context=True)
async def set(ctx, threshold):

    if not is_authorized(ctx.message.author):
        await bot.say('You are not authorized to do that.')
        return

    try:
        threshold = int(threshold)
        if threshold > 100000:
            await bot.say('Treshold can\'t be greater than 100000')
            return
    except ValueError:
        await bot.say('Treshold must be integer.')
        return

    set_option(THRESHOLD_OPTION_ID, threshold)
    await bot.say('Threshold updated as %s' % threshold)


@threshold.command()
async def get():
    threshold_value = get_option(THRESHOLD_OPTION_ID)
    if threshold_value:
        await bot.say('Treshold is currently %s.' % threshold_value["value"])
    else:
        await bot.say('Treshold is undefined at the moment!')
