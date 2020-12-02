from bidder import ScytheBidder

class BiddingRoom:
	def __init__(self, name, owner):
		self.name = name
		self.owner = owner
		self.bidder = ScytheBidder()

	def add_player(self, player):
		self.bidder.add_player(player)

	def start_bidding(self):
		self.bidder.start_bidding()
