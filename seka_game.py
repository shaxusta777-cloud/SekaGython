"""Offline Seka game rules and turn logic."""

from dataclasses import dataclass, field
import random


SUITS = ("♠", "♥", "♦", "♣")
RANKS = ("6", "7", "8", "9", "10", "J", "Q", "K", "A")
MAX_EXCHANGES = 3


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    @property
    def points(self) -> int:
        if self.rank == "A":
            return 11
        if self.rank in ("J", "Q", "K"):
            return 10
        return int(self.rank)

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"


@dataclass
class Player:
    name: str
    is_human: bool
    cards: list[Card] = field(default_factory=list)
    stood: bool = False
    exchanges: int = 0


def create_deck() -> list[Card]:
    return [Card(rank, suit) for suit in SUITS for rank in RANKS]


def hand_score(cards: list[Card]) -> int:
    """Score a hand by adding points of cards that share a suit."""
    totals = {suit: 0 for suit in SUITS}
    for card in cards:
        totals[card.suit] += card.points
    return max(totals.values(), default=0)


def hand_hint(cards: list[Card]) -> str:
    totals = {suit: 0 for suit in SUITS}
    for card in cards:
        totals[card.suit] += card.points
    best_suit = max(totals, key=totals.get)
    return f"Eng kuchli rang {best_suit}: {totals[best_suit]} ochko."


class SekaGame:
    def __init__(
        self,
        rng: random.Random | None = None,
        allow_exchanges: bool = True,
    ):
        self.rng = rng or random.Random()
        self.allow_exchanges = allow_exchanges
        self.players: list[Player] = []
        self.deck: list[Card] = []
        self.current_index = 0
        self.round_over = True

    def new_round(self) -> None:
        self.deck = create_deck()
        self.rng.shuffle(self.deck)
        self.players = [
            Player("Siz", True),
            Player("ILXOM", False),
            Player("XURSHID", False),
            Player("SHOVKAT", False),
        ]
        for _ in range(3):
            for player in self.players:
                player.cards.append(self.deck.pop())
        self.current_index = 0
        self.round_over = False

    @property
    def current_player(self) -> Player:
        return self.players[self.current_index]

    @property
    def winner(self) -> Player | None:
        if not self.round_over:
            return None
        return max(self.players, key=lambda player: hand_score(player.cards))

    def exchange(self, card_index: int) -> Card:
        player = self.current_player
        if self.round_over:
            raise ValueError("Raund tugagan.")
        if not self.allow_exchanges:
            raise ValueError("Bu o‘yin variantida karta almashtirish yo‘q.")
        if player.stood:
            raise ValueError("Bu o‘yinchi yurishni tugatgan.")
        if not 0 <= card_index < len(player.cards):
            raise ValueError("Karta tanlovi noto‘g‘ri.")
        if not self.deck:
            raise ValueError("Kolodada karta qolmagan.")
        if player.exchanges >= MAX_EXCHANGES:
            raise ValueError("Almashtirish limiti tugagan.")

        drawn = self.deck.pop()
        player.cards[card_index] = drawn
        player.exchanges += 1
        if player.exchanges >= MAX_EXCHANGES:
            player.stood = True
        self._advance()
        return drawn

    def stand(self) -> None:
        if self.round_over:
            raise ValueError("Raund tugagan.")
        self.current_player.stood = True
        self._advance()

    def play_bots(self) -> list[str]:
        messages = []
        while not self.round_over and not self.current_player.is_human:
            player = self.current_player
            score = hand_score(player.cards)
            if not self.allow_exchanges:
                player.stood = True
                messages.append(f"{player.name} kartalarni ochdi ({score} ochko).")
                self._advance()
                continue
            if score >= 20 or player.exchanges >= MAX_EXCHANGES or not self.deck:
                player.stood = True
                messages.append(f"{player.name} yurishni tugatdi ({score} ochko).")
                self._advance()
                continue

            discard_index = self._bot_discard_index(player.cards)
            self.exchange(discard_index)
            messages.append(f"{player.name} bitta kartasini almashtirdi.")
        return messages

    @staticmethod
    def _bot_discard_index(cards: list[Card]) -> int:
        suit_counts = {suit: 0 for suit in SUITS}
        for card in cards:
            suit_counts[card.suit] += 1
        return min(
            range(len(cards)),
            key=lambda index: (suit_counts[cards[index].suit], cards[index].points),
        )

    def _advance(self) -> None:
        if all(player.stood for player in self.players):
            self.round_over = True
            return
        for step in range(1, len(self.players) + 1):
            next_index = (self.current_index + step) % len(self.players)
            if not self.players[next_index].stood:
                self.current_index = next_index
                return
