# import discord
from sqlite3 import connect
import discord
import asyncio
import configparser
from discord import app_commands
import json
from discord.ext import tasks

# create discord bot class
class DiscordBot(discord.Client):
    # constructor
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents ,*args, **kwargs)
        self.synced = False
    # on ready function
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        if not self.synced:
            await tree.sync()
            self.synced = True
        update_channel_members.start()
    # on message function
    async def on_message(self, message):
        if message.author.bot:
            return
        
data = None

# save data
def save_data():
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=2)
        print('Saved data')
        print('------')

# load data
# if file exists, load data
def load_data():
    try:
        with open('data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

config = configparser.ConfigParser()
config.read('discord_stats_config.ini')
token = config['AUTH']['bot_token']

data = load_data()

# run bot
bot = DiscordBot(command_prefix='!')

@tasks.loop(minutes=10)
async def update_channel_members():
    channel_members = await bot.fetch_channel(data['channels']['channel_members'])
    bots = channel_members.guild.get_role(data['bots'])
    await channel_members.edit(name=f'MEMBERS: {channel_members.guild.member_count - len(bots.members)}')
    channel_dao_members = await bot.fetch_channel(data['channels']['channel_payed'])
    dao_members_role = channel_dao_members.guild.get_role(data['dao_members'])
    await channel_dao_members.edit(name=f'DAO MEMBERS: {len(dao_members_role.members)}')
    channel_dbs_ogs = await bot.fetch_channel(data['channels']['channel_dbs_ogs'])
    dbs_ogs_role = channel_dbs_ogs.guild.get_role(data['dbs_ogs'])
    await channel_dbs_ogs.edit(name=f'DBS OGs: {len(dbs_ogs_role.members)}')
    channel_dao_ogs = await bot.fetch_channel(data['channels']['channel_dao_ogs'])
    dao_ogs_role = channel_dao_ogs.guild.get_role(data['dao_ogs'])
    await channel_dao_ogs.edit(name=f'DAO OGs: {len(dao_ogs_role.members)}')
    save_data()

@update_channel_members.before_loop
async def before_update_channel_members():
    await bot.wait_until_ready()
    while True:
        if ('channels' in data) and ('dao_ogs' in data) and ('dbs_ogs' in data) and ('dao_members' in data) and ('bots' in data):
            if ('channel_members' in data['channels']) and (data['dao_ogs']) and (data['dbs_ogs']) and (data['dao_members']) and (data['bots'] is not None):
                break
        await asyncio.sleep(10)

tree = app_commands.CommandTree(bot)

@tree.command(name='init', description='Initialize basic category and channel for stats')
async def init(interaction: discord.Interaction, position : int = 0):
    if not interaction.user.guild_permissions.administrator:
        return
    await interaction.response.send_message('Initializing...', ephemeral=True)
    # create category stats
    if 'category_stats' not in data:
        category_stats = await interaction.guild.create_category('📈Stats')
        await category_stats.set_permissions(
            interaction.guild.default_role,
            view_channel=True,
            connect=False,
            send_messages=False
            )
        data['category_stats'] = category_stats.id
        await category_stats.move(beginning=True, offset=position)
    else:
        category_stats = await interaction.guild.fetch_channel(data['category_stats'])
    if 'channels' not in data:
        data['channels'] = {}
    
    # create channel stats
    if 'channel_partnerships' not in data['channels']:
        if 'partnerships' not in data:
            data['partnerships'] = {}
        channel_partnerships = await interaction.guild.create_voice_channel(f'PARTNERSHIPS: {len(data["partnerships"])}', category=category_stats)
        data['channels']['channel_partnerships'] = channel_partnerships.id
    else:
        channel_partnerships = await interaction.guild.fetch_channel(data['channels']['channel_partnerships'])
        if channel_partnerships.name != f'PARTNERSHIPS: {len(data["partnerships"])}':
            await channel_partnerships.edit(name=f'PARTNERSHIPS: {len(data["partnerships"])}')
    if 'channel_members' not in data['channels']:
        channel_members = await interaction.guild.create_voice_channel(f'MEMBERS: {interaction.guild.member_count}', category=category_stats)
        data['channels']['channel_members'] = channel_members.id
    else:
        channel_members = await interaction.guild.fetch_channel(data['channels']['channel_members'])
        if channel_members.name != f'MEMBERS: {interaction.guild.member_count}':
            await channel_members.edit(name=f'MEMBERS: {interaction.guild.member_count}')
    if 'channel_payed' not in data['channels']:
        if 'dao_members' not in data:
            data['dao_members'] = 0
        channel_payed = await interaction.guild.create_voice_channel(f'DAO MEMBERS: 0', category=category_stats)
        data['channels']['channel_payed'] = channel_payed.id
    else:
        channel_payed = await interaction.guild.fetch_channel(data['channels']['channel_payed'])
        if channel_payed.name != f'DAO MEMBERS: 0':
            await channel_payed.edit(name=f'DAO MEMBERS: 0')
    if 'channel_dbs_ogs' not in data['channels']:
        if 'dbs_ogs' not in data:
            data['dbs_ogs'] = 0
        channel_dbs_ogs = await interaction.guild.create_voice_channel(f'DBS OGs: {data["dbs_ogs"]}', category=category_stats)
        data['channels']['channel_dbs_ogs'] = channel_dbs_ogs.id
    else:
        channel_dbs_ogs = await interaction.guild.fetch_channel(data['channels']['channel_dbs_ogs'])
        if channel_dbs_ogs.name != f'DBS OGs: 0':
            await channel_dbs_ogs.edit(name=f'DBS OG: 0')
    if 'channel_dao_ogs' not in data['channels']:
        if 'dao_ogs' not in data:
            data['dao_ogs'] = 0
        channel_dao_ogs = await interaction.guild.create_voice_channel(f'DAO OGs: 0', category=category_stats)
        data['channels']['channel_dao_ogs'] = channel_dao_ogs.id
    else:
        channel_dao_ogs = await interaction.guild.fetch_channel(data['channels']['channel_dao_ogs'])
        if channel_dao_ogs.name != f'DAO O: 0':
            await channel_dao_ogs.edit(name=f'DAO OGS: 0')
    if 'channel_rewards' not in data['channels']:
        if 'rewards' not in data:
            data['rewards'] = 0.0
        channel_rewards = await interaction.guild.create_voice_channel(f'REWARDS: {data["rewards"]:.1f} k$', category=category_stats)
        data['channels']['channel_rewards'] = channel_rewards.id
    else:
        channel_rewards = await interaction.guild.fetch_channel(data['channels']['channel_rewards'])
        if channel_rewards.name != f'REWARDS: {data["rewards"]}':
            await channel_rewards.edit(name=f'REWARDS: {data["rewards"]:.1f} k$')
    save_data()

# create command add_partnership
@tree.command(name='add_partnership', description='Add a partnership')
async def add_partnership(interaction: discord.Interaction, partnership_name : str, partnership_url : str):
    if not interaction.user.guild_permissions.administrator:
        return
    if 'partnerships' not in data:
        data['partnerships'] = {}
    if partnership_name not in data['partnerships']:
        if 'https://' not in partnership_url:
            partnership_url = f'https://{partnership_url}'
        data['partnerships'][partnership_name] = partnership_url
        channel_partnerships = await interaction.guild.fetch_channel(data['channels']['channel_partnerships'])
        await channel_partnerships.edit(name=f'PARTNERSHIPS: {len(data["partnerships"])}')
        await interaction.response.send_message(f'Added partnership {partnership_name}')
    else:
        await interaction.response.send_message(f'Partnership {partnership_name} already exists', ephemeral=True)
    save_data()

# create command remove_partnership
@tree.command(name='remove_partnership', description='Remove a partnership')
async def remove_partnership(interaction: discord.Interaction, partnership_name : str):
    if not interaction.user.guild_permissions.administrator:
        return
    if 'partnerships' not in data:
        data['partnerships'] = {}
    if partnership_name in data['partnerships']:
        data['partnerships'].pop(partnership_name)
        channel_partnerships = await interaction.guild.fetch_channel(data['channels']['channel_partnerships'])
        await channel_partnerships.edit(name=f'PARTNERSHIPS: {len(data["partnerships"])}')
        await interaction.response.send_message(f'Removed partnership {partnership_name}')
    else:
        await interaction.response.send_message(f'Partnership {partnership_name} does not exist', ephemeral=True)
    save_data()

# print list of partnerships
@tree.command(name='list_partnerships', description='List partnerships')
async def list_partnerships(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return
    if 'partnerships' not in data:
        data['partnerships'] = {}
    embed = discord.Embed(
        title='Partnerships',
        url='https://www.dbsdao.com/',
        description="↑Full list can be found on our website↑\nOur latest partnerships:",
        color=0x0055e8
        )
    embed.set_author(
        name="DBS DAO",
        icon_url="https://pbs.twimg.com/profile_images/1528813629788790785/9nJ95kjl_400x400.jpg",
        url="https://twitter.com/DBSdao"
    )
    # add fields for each partnership
    for partnership in data['partnerships']:
        embed.add_field(name=partnership, value=f"[{data['partnerships'][partnership]}]({data['partnerships'][partnership]})", inline=True)
    embed.set_footer(text=f'DBS DAO is a way to be in the black.')
    await interaction.response.send_message(embed=embed)

# create command add_rewards
@tree.command(name='add_rewards', description='Add a reward')
async def add_rewards(interaction: discord.Interaction, reward_amount : int):
    if not interaction.user.guild_permissions.administrator:
        return
    if 'rewards' not in data:
        data['rewards'] = 0.0
    data['rewards'] += reward_amount/1000
    channel_rewards = await interaction.guild.fetch_channel(data['channels']['channel_rewards'])
    await channel_rewards.edit(name=f'REWARDS: {data["rewards"]:.1f} k$')
    await interaction.response.send_message(f'Added {reward_amount} REWARDS', ephemeral=True)
    save_data()

# create command remove_rewards
@tree.command(name='remove_rewards', description='Remove a reward')
async def remove_rewards(interaction: discord.Interaction, reward_amount : int):
    if not interaction.user.guild_permissions.administrator:
        return
    if 'rewards' not in data:
        data['rewards'] = 0.0
    data['rewards'] -= reward_amount/1000
    channel_rewards = await interaction.guild.fetch_channel(data['channels']['channel_rewards'])
    await channel_rewards.edit(name=f'REWARDS: {data["rewards"]:.1f} k$')
    await interaction.response.send_message(f'Removed {reward_amount} REWARDS', ephemeral=True)
    save_data()

# add dao ogs role
@tree.command(name='add_dao_ogs', description='Add DAO OGS role')
async def add_dao_ogs(interaction: discord.Interaction, role : discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return
    if 'dao_ogs' not in data:
        data['dao_ogs'] = None
    if role.id != data['dao_ogs']:
        data['dao_ogs'] = role.id
        await interaction.response.send_message(f'Added {role.name} to DAO OGS stats', ephemeral=True)
    else:
        await interaction.response.send_message(f'{role.name} is already in DAO OGS stats', ephemeral=True)
    save_data()

# add dbs ogs role
@tree.command(name='add_dbs_ogs', description='Add DBS OGS role')
async def add_dbs_ogs(interaction: discord.Interaction, role : discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return
    if 'dbs_ogs' not in data:
        data['dbs_ogs'] = None
    if role.id != data['dbs_ogs']:
        data['dbs_ogs'] = role.id
        await interaction.response.send_message(f'Added {role.name} to DBS OGS stats', ephemeral=True)
    else:
        await interaction.response.send_message(f'{role.name} is already in DBS OGS stats', ephemeral=True)
    save_data()

# add dao members role
@tree.command(name='add_dao_members', description='Add DAO members role')
async def add_dao_members(interaction: discord.Interaction, role : discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return
    if 'dao_members' not in data:
        data['dao_members'] = None
    if role.id != data['dao_members']:
        data['dao_members'] = role.id
        await interaction.response.send_message(f'Added {role.name} to DAO members stats', ephemeral=True)
    else:
        await interaction.response.send_message(f'{role.name} is already in DAO members stats', ephemeral=True)
    save_data()

# add bot role
@tree.command(name='add_bots', description='Add bots role')
async def add_bots(interaction: discord.Interaction, role : discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return
    if 'bots' not in data:
        data['bots'] = None
    if role.id != data['bots']:
        data['bots'] = role.id
        await interaction.response.send_message(f'Added {role.name} to bot stats', ephemeral=True)
    else:
        await interaction.response.send_message(f'{role.name} is already in bot stats', ephemeral=True)
    save_data()

bot.run(token)
save_data()
