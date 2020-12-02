import random
import itertools

factions = [
	'Albion',
	'Nordic',
	'Rusviet',
	'Togawa',
	'Crimea',
	'Saxony',
	'Polania'
]

player_mats = [
	'Industrial',
	'Engineering',
	'Militant',
	'Patriotic',
	'Innovative',
	'Mechanical',
	'Agricultural'
]

def generate_combinations(num_combinations, factions, player_mats):
	factions = factions.copy()
	player_mats = player_mats.copy()

	picked_factions = random.sample(factions, num_combinations)
	picked_player_mats = random.sample(player_mats, num_combinations)

	return list(zip(picked_factions, picked_player_mats))

def format_combination(combination):
	return '{0} - {1}'.format(*combination)

def print_bids(combinations, original_combinations, bids):
	bids_by_combination = {}
	for player in bids.keys():
		bid = bids[player]
		bids_by_combination[bid[0]] = (player, bid[1])

	for combination in combinations:
		if combination in bids_by_combination:
			print(
				'{0}: {1} for ${2} by {3}'.format(
					original_combinations.index(combination),
					format_combination(combination),
					bids_by_combination[combination][1],
					bids_by_combination[combination][0]
				)
			)
		else:
			print(
				'{0}: {1}'.format(
					original_combinations.index(combination),
					format_combination(combination)
				)
			)

def compute_available_combinations(combinations, original_combinations, bids):
	available_combinations = set(combinations)
	taken_combinations = set([bid[0] for bid in bids])
	available_combinations = list(available_combinations - taken_combinations)
	available_combinations.sort(key=lambda x : original_combinations.index(x))

	return available_combinations

def determine_next_player(players, bids, active_player):
	if not players: return None
	if not active_player: return players[0]

	num_players = len(players)
	active_player_index = players.index(active_player)
	for i in range(1, num_players - 1):
		player = players[(active_player_index + i) % num_players]
		if player not in bids:
			return player

	return None

def is_valid_bid(bid, bids):
	for existing_bid in bids.values():
		if existing_bid[0] != bid[0]: continue

		return bid[1] > existing_bid[1]

	return True

def process_bid(player, bid, bids):
	to_pop = None
	for bidder in bids:
		if bids[bidder][0] == bid[0]:
			to_pop = bidder
			break

	if to_pop in bids: bids.pop(to_pop)

	bids[player] = bid

def print_bid_history(bid_history):
	i = 1
	for bid_entry in bid_history:
		print('{0}: {1} bid ${2} on {3}'.format(i, bid_entry[0], bid_entry[1][1], format_combination(bid_entry[1][0])))
		i = i+1

# PROGRAM START
players = []

while True:
	print('Enter player {0}\'s name (leave blank to move on):'.format(len(players) + 1))
	player_name = input()
	if not player_name: break

	if player_name in players:
		print('Player {0} already exists!'.format(player_name))
		continue

	players.append(player_name)
	if len(players) >= 7: break

combinations = generate_combinations(len(players), factions, player_mats)

bid_history = []
bids = {}
available_combinations = combinations.copy()
active_player = None
while True:
	active_player = determine_next_player(players, bids, active_player)

	if not active_player:
		print('\nBidding complete!')
		print_bids(available_combinations, combinations, bids)

		print('\nBid history:')
		print_bid_history(bid_history)
		break

	print('\n{0}\'s turn to bid!'.format(active_player))
	available_combinations = compute_available_combinations(
		available_combinations,
		combinations,
		bids
	)

	print_bids(available_combinations, combinations, bids)

	bid = None
	while True:
		print('\nPlace your bid (e.g. 0 20 will place a bid of $20 on combination 0):')
		bid_input = input()

		try:
			bid_input = bid_input.split(' ')
			combination_index = int(bid_input[0])
			bid_amount = int(bid_input[1])
		except:
			print('Invalid input!')
			continue

		bid_combination = combinations[combination_index]
		print('Bid: {0} for ${1}'.format(format_combination(bid_combination), bid_amount))

		bid = (bid_combination, bid_amount)

		if is_valid_bid(bid, bids): break

		print('Bid is invalid!')


	bid_history.append((active_player, bid))

	process_bid(active_player, bid, bids)
