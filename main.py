import asyncio, random, string, json 
from discord.ext import commands, tasks
import re, discord

TOKEN = "" #user_token
SPAM_CHANNEL_id = 1185665668201320581
CAPTCHA_CHANNEL_id = 1186902971401895936
OWNER_id = 600675535772975105 #captcha_alert_channel_id 

with open('pokemon', 'r', encoding='utf8') as file: 
    pokemon_list = file.read()
    
client = commands.Bot(command_prefix='$')
client.remove_command('help')
captcha = True

def solve(message):
    hint = []
    for i in range(15, len(message) - 1):
        if message[i] != "\\":
            hint.append(message[i])
    hint_string = "".join(hint)
    hint_replaced = hint_string.replace("_", ".")
    solution = re.findall("^" + hint_replaced + "$", pokemon_list, re.MULTILINE)
    return solution

@client.event
async def on_ready():
    print(f'Logged into account: {client.user.name}')
    channel = client.get_channel(CAPTCHA_CHANNEL_id)
    await channel.send("I'm Ready Catch")

@tasks.loop(seconds=1)
async def spammer():
    channel = client.get_channel(SPAM_CHANNEL_id)
    if channel and captcha:
        await channel.send(''.join(random.sample(string.ascii_lowercase + string.digits, 15) * 5))
        await asyncio.sleep(random.randint(1, 3))
spammer.start()

@client.event
async def on_message(message):
    global captcha
    if message.author.id == 854233015475109888 and captcha:
        match = re.search(r'^(Possible Pokémon: )?(.+)\s?:', message.content)
        if match:
            possible_pokemon_prefix, pokemon = match.groups()
            if pokemon and "Possible Pokémon" not in pokemon:
                name = (possible_pokemon_prefix or '') + pokemon.strip()
                await asyncio.sleep(random.randint(1, 1))
                await message.channel.send(f'<@716390085896962058> c {name.lower()}')

    if message.author.id == 716390085896962058 and captcha:
        content = message.content
        if 'The pokémon is ' in content:
            if not len(solve(content)):
                print('Pokemon not found.')
            else:
                for i in solve(content):
                    await asyncio.sleep(random.randint(1, 1))
                    await message.channel.send(f'<@716390085896962058> c {i.lower()}')

        if 'That is the wrong pokémon!' in content:
            await asyncio.sleep(random.randint(1, 1))
            await message.channel.send(f'<@716390085896962058> h')

        elif 'human' in content:
            captcha = False
            channel = client.get_channel(CAPTCHA_CHANNEL_id)
            await channel.send(f"@everyone Please verify the Poketwo captcha asap! \nafter captcha solve type `$start` https://verify.poketwo.net/captcha/{client.user.id}")

    await client.process_commands(message)


@client.command()
async def start(ctx):
    global captcha
    if ctx.message.author.id == OWNER_id:
        captcha = True
        await ctx.send("Successfully started")

@client.command()
async def stop(ctx):
    global captcha
    if ctx.message.author.id == OWNER_id:
        captcha = False
        await ctx.send("Successfully stopped")

@client.command()
async def say(ctx, *, text):
    if ctx.message.author.id == OWNER_id:
        await ctx.send(text)

client.run(TOKEN)