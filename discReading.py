import hmac
import json
import logging
import time

import discord
from requests import Request

from client import FtxClient

logging.basicConfig(level=logging.INFO)

client = discord.Client()
guild = discord.Guild


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game('gettin moni'))


@client.event
async def on_message(message):
    if message.author.id != 812000184070176810:
        return
    else:

        # Acquiring the channel via the bot command
        listmessages = message.content.splitlines()
        action = listmessages[2]
        price = listmessages[3]
        market = listmessages[4]
        size = abs(float(listmessages[5]))
        market = market.replace('PERP', '-PERP')
        positions = clientFTX.get_open_orders()
        currentpos = clientFTX.get_position(name=market)
        jsondumppos = json.dumps(currentpos)
        jsonloadpos = json.loads(jsondumppos)
        if action == "buy" and len(positions) < 6 and (
                jsonloadpos == None or jsonloadpos['cost'] + (float(price) * size / 100) <= 25):
            resp = clientFTX.place_order(market=market, side=action, price=price, type="limit", size=size / 100)
            print(resp)
        elif action == "sell":
            resp = clientFTX.get_position(name=market)
            jsondump = json.dumps(resp)
            jsonload = json.loads(jsondump)
            if jsonload == None or (len(jsonload) == 0 or jsonload['size'] == 0):
                return
            else:
                resp = clientFTX.place_order(market=market, side="sell", price=None, type="market", size=size / 100)
                print(resp)
        else:
            return
        answer = discord.Embed(title="Processing trade signal",
                               description=f"""Time to make it happen.\n\n`Server` : **{message.guild.name}**\n`Action` : **{action}**\n`Price` : **"{price}"**"\n`Market` : **"{market}"**""",
                               colour=0x1a7794)

        await message.channel.send(embed=answer)


if __name__ == '__main__':
    clientFTX = FtxClient('API_PUBLIC', 'API_SECRET', subaccount_name="Bot")
    ts = int(time.time() * 1000)
    request = Request('GET', FtxClient._ENDPOINT)
    prepared = request.prepare()
    signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
    signature = hmac.new('API_SECRET'.encode(), signature_payload, 'sha256').hexdigest()
    request.headers['FTX-KEY'] = 'API_PUBLIC'
    request.headers['FTX-SIGN'] = signature
    response = request.headers['FTX-TS'] = str(ts)
    client.run('___')
