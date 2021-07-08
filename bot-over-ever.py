import time
import datetime
import requests
import discord


def get_info():
	response = requests.get(url="https://yobit.net/api/3/info")

	# with open('info.txt', 'w') as file:
	# 	file.write(response.text)

	return response.text


def get_ticker(coin1='btc', coin2='usd'):
	# response = requests.get(url="https://yobit.net/api/3/ticker/eth_btc-xrp_btc?ignore_invalid=1")
	response = requests.get(url=f"https://yobit.net/api/3/ticker/{coin1}_{coin2}?ignore_invalid=1")

	# with open('ticker.txt', 'w') as file:
	# 	file.write(response.text)

	return response.text


def get_depth(coin1='btc', coin2='usd', limit=150):
	response = requests.get(url=f"https://yobit.net/api/3/depth/{coin1}_{coin2}?limit={limit}&ignore_invalid=1")

	# with open('depth.txt', 'w') as file:
	# 	file.write(response.text)

	bids = response.json()[f'{coin1}_usd']['bids']

	ask = response.json()[f'{coin1}_usd']['asks'][0][0]
	bid = response.json()[f'{coin1}_usd']['bids'][0][0]

	total_bids_amount = 0
	for item in bids:
		price = item[0]
		coin_amount = item[1]

		total_bids_amount += price * coin_amount


	return f'Total bids: {total_bids_amount} $', ask, bid


async def get_trades(coin1='btc', coin2='usd', limit=150, idx=1):
	response = requests.get(url=f"https://yobit.net/api/3/trades/{coin1}_{coin2}?limit={limit}&ignore_invalid=1")

	# date = datetime.datetime.today()
	# date = date.strftime('%H_%M')
	# with open(f'trades_{date}.txt', 'w') as file:

	# with open('trades.txt', 'w') as file:
	# 	file.write(response.text)

	total_trade_ask = 0
	total_trade_bid = 0

	global last_price_ask
	global new_price_ask
	global last_price_bid
	global new_price_bid

	global balance_btc
	global balance_usd

	global last_event
	global new_event

	for item in response.json()[f'{coin1}_{coin2}']:
		if item['type'] == 'ask':
			total_trade_ask += item['price'] * item['amount']
		else:
			total_trade_bid += item['price'] * item['amount']

	info = f'[-] TOTAL {coin1} SELL: {round(total_trade_ask, 2)} $\n[+] TOTAL {coin1} BUY: {round(total_trade_bid, 2)} $'


	if (idx != 0):
		last_price_ask = new_price_ask
		last_price_bid = new_price_bid
	else:
		last_price_ask = total_trade_ask
		last_price_bid = total_trade_bid
	# print('i =', idx)

	new_price_ask = total_trade_ask
	new_price_bid = total_trade_bid

	# pump
	if (new_price_ask / last_price_ask > 1.1):
		# print('pump')
		# print(f'new price ask {round(new_price_ask, 2)} $\nlast price ask {round(last_price_ask, 2)}')
		compare = f'new price ask {round(new_price_ask, 2)} $\nlast price ask {round(last_price_ask, 2)} $'
		_, ask, _ = get_depth(coin1=coin1)
		deposite = 0.1 * balance_usd # 5%
		income  = deposite / ask
		balance_btc = balance_btc + income
		balance_usd = balance_usd - deposite
		# print(f'balance_btc = {balance_btc}')
		# print(f'balance_usd = {balance_usd}')
		ans1 = f'balance_btc = {balance_btc}'
		ans2 = f'balance_usd = {round(balance_usd, 2)} $'
		last_event = new_event
		new_event = 'event: pump'

		return info, new_event, compare, ans1, ans2 ###

	# dump
	elif (new_price_bid / last_price_bid < 0.9):
		# print('dump')
		# print('new_price_bid:', round(new_price_bid, 2), 'last_price_bid', round(last_price_bid, 2))
		compare = f'new price bid {round(new_price_bid, 2)} $\nlast price bid {round(last_price_bid, 2)} $'
		_, _, bid = get_depth(coin1=coin1)
		deposite = 0.1 * balance_btc # 5%
		income  = deposite * bid
		balance_btc = balance_btc - deposite
		balance_usd = balance_usd + income
		# print('balance_btc =', balance_btc)
		# print('balance_usd =', balance_usd)
		ans1 = f'balance_btc = {balance_btc}'
		ans2 = f'balance_usd = {round(balance_usd, 2)} $'
		last_event = new_event
		new_event = 'event: dump'

		return info, new_event, compare, ans1, ans2 ###

	### сделать условие продажи валюты после пампа и покупки после дампа

	last_event = new_event
	new_event = 'event: nothing'

	if (last_event == 'pump' and new_event == 'event: nothing'):
		# sell btc
		compare = f'new price bid {round(new_price_bid, 2)} $\nlast price bid {round(last_price_bid, 2)} $'
		_, _, bid = get_depth(coin1=coin1)
		deposite = 0.1 * balance_btc # 5%
		income  = deposite * bid
		balance_btc = balance_btc - deposite
		balance_usd = balance_usd + income
		# print('balance_btc =', balance_btc)
		# print('balance_usd =', balance_usd)
		ans1 = f'balance_btc = {balance_btc}'
		ans2 = f'balance_usd = {round(balance_usd, 2)} $'
		
		return info, new_event, compare, ans1, ans2 ###

	if (last_event == 'dump' and new_event == 'event: nothing'):
		# buy btc
		compare = f'new price ask {round(new_price_ask, 2)} $\nlast price ask {round(last_price_ask, 2)} $'
		_, ask, _ = get_depth(coin1=coin1)
		deposite = 0.1 * balance_usd # 5%
		income  = deposite / ask
		balance_btc = balance_btc + income
		balance_usd = balance_usd - deposite
		ans1 = f'balance_btc = {balance_btc}'
		ans2 = f'balance_usd = {round(balance_usd, 2)} $'

		return info, new_event, compare, ans1, ans2 ###

	return info, new_event, 'xyunya', 'xyunya', 'xyunya'


# def main():
# global balance_btc
# global balance_usd

balance_btc = 0

balance_usd = 1

# global last_price_ask
# global new_price_ask
# global last_price_bid
# global new_price_bid

last_price_ask = 0
new_price_ask = 0
last_price_bid = 0
new_price_bid = 0

last_event = ''
new_event = ''


client = discord.Client()

@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
	if message.author == client.user:
		return

	if message.content.startswith('!start-tracking-prices'):
		# await message.channel.send('')
		

		for i in range(40):
			date = datetime.datetime.today()
			# print(date.strftime('%H:%M'))
			await message.channel.send(date.strftime('%H:%M'))

			# print(get_info())
			# print(get_ticker())
			# print(get_ticker(coin1='eth'))

			# print(get_depth())

			info, event, compare, ans1, ans2 = await get_trades(idx=i)
			# print(event)
			if (compare != 'xyunya' and event != 'event: nothing'):
				await message.channel.send(info)
				time.sleep(0.5)
				await message.channel.send(event)
				time.sleep(0.5)
				await message.channel.send(compare)
				time.sleep(0.5)
				await message.channel.send(ans1)
				time.sleep(0.5)
				await message.channel.send(ans2)
			elif (compare != 'xyunya'):
				await message.channel.send(info)
				time.sleep(0.5)
				await message.channel.send('pump or dump ended')
				time.sleep(0.5)
				await message.channel.send(event)
				time.sleep(0.5)
				await message.channel.send(compare)
				time.sleep(0.5)
				await message.channel.send(ans1)
				time.sleep(0.5)
				await message.channel.send(ans2)
			else:
				await message.channel.send(info)

			await message.channel.send('======================')
			time.sleep(600)
		# print(f'balance_btc = {balance_btc} \nbalance_usd = {balance_usd}')
		balance = f'balance_btc = {balance_btc}\nbalance_usd = {round(balance_usd, 2)}\nцикл отработал'
		await message.channel.send(balance)

		# if __name__ == '__main__':
		# 	main()

client.run('ODI5NzE4ODgxOTEyMDk0NzQw.YG8N7A.TYGm5Zc-7Z9yUIr8LyBavknHT84') # поменять на файл!!!




# # def main():
# # global balance_btc
# # global balance_usd

# balance_btc = 0

# balance_usd = 1

# # global last_price_ask
# # global new_price_ask
# # global last_price_bid
# # global new_price_bid

# last_price_ask = 0
# new_price_ask = 0
# last_price_bid = 0
# new_price_bid = 0

# for i in range(40):
# 	date = datetime.datetime.today()
# 	print(date.strftime('%H:%M'))

# 	# print(get_info())
# 	# print(get_ticker())
# 	# print(get_ticker(coin1='eth'))

# 	# print(get_depth())

# 	print(get_trades(idx=i))
# 	# print(get_trades(coin1='btc'))
# 	# print(get_trades(coin1='doge'))

# 	time.sleep(900)
# print('balance_btc =', balance_btc)
# print('balance_usd =', balance_usd)


# # if __name__ == '__main__':
# # 	main()