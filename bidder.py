
import random
import itertools
from enum import IntEnum

class BidderState(IntEnum):
	WAITING = 1
	BIDDING = 2
	ENDED = 3

class ScytheBidder:
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

	def __init__(self):
		self.players = []
		self.combinations = []
		self.bids = {}
		self.active_player = None
		self.bid_history = []
		self.state = BidderState.WAITING

	def start_bidding(self):
		self.combinations = generate_combinations(len(self.players), self.factions, self.player_mats)
		self.active_player = determine_next_player(self.players, self.bids, None)

		if self.active_player:
			self.state = BidderState.BIDDING
		else:
			self.state = BidderState.ENDED

	def generate_state(self):
		return {
			'players': self.players,
			'combinations': self.combinations,
			'bids': self.bids,
			'activePlayer': self.active_player,
			'state': self.state,
			'bidHistory': self.bid_history
		}

	def process_bid(self, player, combination, amount):
		if self.state is not BidderState.BIDDING:
			# print('{0} bid when not in correct state'.format(player))
			return

		if player not in self.players or player != self.active_player:
			# print('{0} bidding out of turn'.format(player))
			return

		bid = (tuple(combination), amount)
		process_bid(player, bid, self.bids)
		self.active_player = determine_next_player(self.players, self.bids, player)

		self.bid_history.append((player, bid))

		if not self.active_player:
			self.state = BidderState.ENDED
		# print(self.active_player)

	def add_player(self, player):
		if player not in self.players and self.state == BidderState.WAITING:
			self.players.append(player)

	def remove_player(self, player):
		if player in self.players and self.state == BidderState.WAITING:
			self.players.remove(player)


def generate_combinations(num_combinations, factions, player_mats):
	factions = factions.copy()
	player_mats = player_mats.copy()

	picked_factions = random.sample(factions, num_combinations)
	picked_player_mats = random.sample(player_mats, num_combinations)

	return list(zip(picked_factions, picked_player_mats))

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
	for i in range(1, num_players):
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
