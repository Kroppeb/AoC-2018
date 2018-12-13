from typing import Callable, IO, Iterable, Optional, List, Tuple

inp  : Callable[[],IO[str]] = lambda: open("inputs/13.txt", 'r')
test1: Callable[[],IO[str]] = lambda: open("inputs/13_test1.txt", 'r')
test2: Callable[[],IO[str]] = lambda: open("inputs/13_test2.txt", 'r')


class Minecart:
	inter = [3, 0, 1]  # left, straight, right
	moves: List[Tuple[int, int]] = [(1, 0), (0, 1), (-1, 0), (0, -1)]

	def __init__(self, direction: int, tile: 'Tile', x: int, y: int):
		self.direction = direction
		self.tile = tile
		self.interindex = 0
		self.x: int = x
		self.y: int = y
		self.map = None
		self.latest = 0
		self.crashed = False

	def set_map(self, mp: 'Map') -> None:
		self.map = mp

	def move(self):
		self.x += self.moves[self.direction][0]
		self.y += self.moves[self.direction][1]
		self.tile = self.map.get_tile(self.x, self.y)
		self.tile.add_minecart(self)

	def tick(self, cur:int):
		if cur > self.latest:
			self.tile.clear_minecart()
			self.move()
			self.latest = cur

	def get_char(self) -> str:
		return ">v<^"[self.direction]

	def mirror(self, value:int) -> None:
		self.direction ^= value

	def turn(self) -> None:
		self.direction += self.inter[self.interindex]
		self.direction %= 4
		self.interindex += 1
		self.interindex %= 3


class Tile:
	def __init__(self, x: int, y: int):
		self.x: int = x
		self.y: int = y
		self.minecart: Optional[Minecart] = None

	@classmethod
	def parse(cls, c: str, x: int, y: int) -> Tuple[Optional['Tile'], Optional[Minecart]]:
		i = ">v<^-|/\\+".find(c)
		if i == -1:
			return None, None

		mc: Optional[Minecart] = None
		if i < 6:
			tile = StraightTrack(x, y, i % 2)
			if i < 4:
				mc = Minecart(i, tile, x, y)
				tile.add_minecart(mc)
		elif i < 8:
			tile = CurvedTrack(x, y, i % 2)
		else:
			tile = Intersection(x, y)
		return tile, mc

	def add_minecart(self, minecart: Minecart):
		if self.has_minecart():
			print("Crash: ({x},{y})".format(x=minecart.x, y=minecart.y))
			self.minecart.crashed = True
			minecart.crashed = True
			self.minecart = None
		else:
			self.minecart = minecart

	def has_minecart(self) -> bool:
		return self.minecart is not None

	def get_minecart(self) -> Optional[Minecart]:
		return self.minecart

	def clear_minecart(self) -> None:
		self.minecart = None

	def tick(self, cur:int) -> None:
		if self.has_minecart():
			self.get_minecart().tick(cur)

	@classmethod
	def to_char(cls, tile: 'Tile') -> str:
		if tile is None:
			return ' '
		elif tile.has_minecart():
			return tile.get_minecart().get_char()
		else:
			return tile.get_char()

	def get_char(self) -> str:
		raise RuntimeError("No char")


class StraightTrack(Tile):
	def __init__(self, x, y, direction):
		Tile.__init__(self, x, y)
		self.direction: int = direction

	def get_char(self) -> str:
		return "-|"[self.direction]


class CurvedTrack(Tile):
	def __init__(self, x, y, direction):
		Tile.__init__(self, x, y)
		self.direction: int = direction

	def add_minecart(self, minecart: Minecart):
		super(CurvedTrack, self).add_minecart(minecart)
		minecart.mirror([3,1][self.direction])

	def get_char(self) -> str:
		return "/\\"[self.direction]


class Intersection(Tile):

	def add_minecart(self, minecart: Minecart):
		super(Intersection, self).add_minecart(minecart)
		minecart.turn()

	def get_char(self) -> str:
		return '+'


class Map:
	def __init__(self, mp: List[List[Optional[Tile]]], minecarts:List[Minecart]):
		self.map: List[List[Optional[Tile]]] = mp
		self.height = len(mp)
		self.width = len(mp[0])
		self.minecarts = minecarts

		for i in minecarts:
			i.set_map(self)

	def get_tile(self, x: int, y: int) -> Tile:
		return self.map[y][x]

	@classmethod
	def parse(cls, s: Iterable[str]) -> 'Map':
		mp = []
		y = 0
		minecarts: List[Minecart] = []
		for line in s:
			x = 0
			ln = []
			for i in line:
				if i == '\n':
					break
				tile, mc = Tile.parse(i, x, y)
				if mc is not None:
					minecarts.append(mc)
				ln.append(tile)
				x += 1
			mp.append(ln)
			y += 1
		return Map(mp, minecarts)


	def tick(self, cur:int) -> None:
		for line in self.map:
			for i in line:
				if i is not None:
					i.tick(cur)

		self.minecarts = [i for i in self.minecarts if not(i.crashed)]

	def get_minecart_count(self):
		return len(self.minecarts)

	def print(self) -> None:
		for line in self.map:
			print(*map(Tile.to_char, line), sep='')


def day13(inpt: Callable[[], IO[str]], verbose:bool):
	s = inpt()
	mp = Map.parse(s)
	i = 1
	if verbose: print("initial:")
	try:
		while mp.get_minecart_count()>1:
			if verbose:
				mp.print()
				print()
				print("step", i)
			mp.tick(i)
			i += 1

	except RuntimeError:
		if verbose:
			mp.print()
	print(mp.minecarts[0].x, mp.minecarts[0].y)


day13(inp, verbose=False)
