# Headers
import keep_alive

# --> Python Libraries
import flask
import os
import json
import requests
from requests import request, Session
from datetime import datetime

# --> Discord
import discord # Allows access to discord API
from discord.ext import tasks

# ---> Etherscan
from etherscan import etherscan

# ---> Core Variables
loop_timer = int(600) # seconds between gas bot updates
threshold = int(5) # main jacy-chat 1hr price change % alert threshold trigger
repeat_timer = int(6) # minimum numbr of bot updates before next jacy-chat alert

# ---> Fixed Variables
repeat_counter = repeat_timer + int(1) # Stays fixed

# ---> Etherscan API Key & URL
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
parameters = {'symbol': 'JACY', 'convert': 'USD'}
headers = {'Accepts': 'application/json','X-CMC_PRO_API_KEY':'[ADD KEY'}

# ---> Open Client
bot = discord.Client()  # Gets the client object from discord.py synonymous with bot

# ---> Tasks
@tasks.loop(seconds=loop_timer)
async def updateprice():

  # --->
  global repeat_timer
  global repeat_counter
  global threshold

  # --->
  token_burn_factor = float(1 - 0.565534)

  # ---> Discord Channels
  channel_price = bot.get_channel(id = 920367513378897950)
  channel_chat = bot.get_channel(id = 920360417874808935)

  # ---> Current Date & Time
  now = datetime.now()
  dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

  # ---> Initiate Session for Gas Prices
  session = Session()
  session.headers.update(headers)
  response = session.get(url, params=parameters)

  # ---> Price Information
  def get_time():
    updated = json.loads(response.text)['data']['JACY']['quote']['USD']['last_updated']
    return (updated)
  updated = get_time()

  def get_cap():
    cap = json.loads(response.text)['data']['JACY']['quote']['USD']['fully_diluted_market_cap']
    return (cap)
  cap_a = get_cap()
  cap_b = float(cap_a * token_burn_factor)
  cap_c = '{0:,.0f}'.format(cap_b)

  def get_price():
    price = json.loads(response.text)['data']['JACY']['quote']['USD']['price']
    return (price)
  price_a = get_price()
  price_b = float(price_a)
  price_c = '{0:,.15f}'.format(price_b)
  price_d = str(price_c)
  price_e = '0.' + price_d[2:5] + ' ' + price_d[5:8] + ' ' + price_d[8:11] + ' ' + price_d[11:14] + ' ' + price_d[14:17]
 
  def get_change1h():
    change1h = json.loads(response.text)['data']['JACY']['quote']['USD']['percent_change_1h']
    return (change1h)
  change1h_a = get_change1h()
  change1h_b = float(change1h_a) / float(100)
  change1h_c = '+{0:,.1%}'.format(change1h_b) if change1h_b >= 0 else '({0:,.1%})'.format(change1h_b * int(-1))
  
  def get_change24h():
    change24h = json.loads(response.text)['data']['JACY']['quote']['USD']['percent_change_24h']
    return (round(change24h, 1))
  change24h_a = get_change24h()
  change24h_b = float(change24h_a) / float(100)
  change24h_c = '+{0:,.1%}'.format(change24h_b) if change24h_b >= 0 else '({0:,.1%})'.format(change24h_b * int(-1))

  def get_change30d():
    change30d = json.loads(response.text)['data']['JACY']['quote']['USD']['percent_change_30d']
    return (round(change30d, 1))
  change30d_a = get_change30d()
  change30d_b = float(change30d_a) / float(100)
  change30d_c = '+{0:,.1%}'.format(change30d_b) if change30d_b >= 0 else '({0:,.1%})'.format(change30d_b * int(-1))

  def get_vol24h():
    vol24h = json.loads(response.text)['data']['JACY']['quote']['USD']['volume_24h']
    return (round(vol24h, 1))
  vol24h_a = get_vol24h()
  vol24h_b = float(vol24h_a)
  vol24h_c = '{0:,.0f}'.format(vol24h_b)

  def get_volchange24h():
    volchange24h = json.loads(response.text)['data']['JACY']['quote']['USD']['volume_change_24h']
    return (round(volchange24h, 1))
  volchange24h_a = get_volchange24h()
  volchange24h_b = float(volchange24h_a) / float(100)
  volchange24h_c = '+{0:,.1%}'.format(volchange24h_b) if volchange24h_b >= 0 else '({0:,.1%})'.format(volchange24h_b * int(-1))

  # ---> Price Message (Main)
  embed = discord.Embed(title="JACY @ CoinMarketCap.com",
    url="https://coinmarketcap.com/currencies/jacywaya/",
    description = '{} {}'.format(dt_string, 'UTC'),
    color=discord.Color.blue())
  embed.add_field(name="**Market Cap**",value = '{} {}'.format(cap_c, 'USD'), inline=False)
  embed.add_field(name="**Token Price**", value = '{} {}'.format(price_e, 'USD'), inline=False)
  embed.add_field(name="**Price Change (1hr)**",value=change1h_c,inline=False)
  embed.add_field(name="**Price Change (24hrs)**",value=change24h_c,inline=False)
  embed.add_field(name="**Price Change (30days)**",value=change30d_c,inline=False)
  embed.add_field(name="**Traded Volume (24hrs)**", value = '{} {}'.format(vol24h_c, 'USD'), inline=False)
  embed.add_field(name="**Volume Change (24hrs)**",value=volchange24h_c,inline=False)
  embed.set_footer(text="Market Cap removes burnt Tokens | Visit CoinMarketCap.com for more information")
  
  await channel_price.send(embed=embed)

  # ---> Gas Message (Alert)

  if change1h_a > threshold and repeat_counter > repeat_timer:

    embed = discord.Embed(title = '{} {} {}'.format('Price Jump:', change1h_c, 'in last 1 hr'),
      url="https://coinmarketcap.com/currencies/jacywaya/",
      description = "Visit CoinMarketCap.com for more information",
      color=discord.Color.blue()) 

    await channel_chat.send(embed=embed)

    repeat_counter = int(0) # reset the repeat counter

  # ---> Update old gas & counter variable
  repeat_counter = repeat_counter + int(1)

# -----> Continue the loop
@bot.event
async def on_ready():
  updateprice.start()

keep_alive.keep_alive()

my_secret = os.environ['TOKEN']
bot.run(my_secret)

# ---------- #
