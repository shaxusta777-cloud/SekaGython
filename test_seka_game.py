import random
import unittest

from seka_game import Card, SekaGame, hand_score


class SekaRulesTests(unittest.TestCase):
    def test_score_adds_only_cards_of_the_same_suit(self):
        cards = [Card("A", "♠"), Card("K", "♠"), Card("10", "♥")]
        self.assertEqual(hand_score(cards), 21)

    def test_score_uses_highest_suit_total(self):
        cards = [Card("A", "♠"), Card("9", "♥"), Card("8", "♥")]
        self.assertEqual(hand_score(cards), 17)

    def test_round_deals_three_cards_and_starts_with_human(self):
        game = SekaGame(random.Random(1))
        game.new_round()
        self.assertEqual([len(player.cards) for player in game.players], [3, 3, 3, 3])
        self.assertEqual(len(game.deck), 24)
        self.assertTrue(game.current_player.is_human)

    def test_exchange_advances_turn_and_replaces_one_card(self):
        game = SekaGame(random.Random(2))
        game.new_round()
        old_cards = list(game.players[0].cards)
        game.exchange(1)
        self.assertEqual(len(game.players[0].cards), 3)
        self.assertEqual(game.players[0].exchanges, 1)
        self.assertEqual(len(game.deck), 23)
        self.assertNotEqual(game.players[0].cards[1], old_cards[1])
        self.assertEqual(game.current_player.name, "ILXOM")

    def test_bots_play_until_human_turn_returns(self):
        game = SekaGame(random.Random(3))
        game.new_round()
        game.exchange(0)
        game.play_bots()
        self.assertTrue(game.current_player.is_human or game.round_over)

    def test_bots_finish_round_after_human_stands(self):
        game = SekaGame(random.Random(4))
        game.new_round()
        game.stand()
        game.play_bots()
        self.assertTrue(game.round_over)
        self.assertIsNotNone(game.winner)

    def test_no_exchange_variant_rejects_card_exchange(self):
        game = SekaGame(random.Random(5), allow_exchanges=False)
        game.new_round()
        with self.assertRaisesRegex(ValueError, "almashtirish yo‘q"):
            game.exchange(0)

    def test_no_exchange_variant_finishes_after_human_stands(self):
        game = SekaGame(random.Random(6), allow_exchanges=False)
        game.new_round()
        game.stand()
        messages = game.play_bots()
        self.assertTrue(game.round_over)
        self.assertEqual(len(messages), 3)
        self.assertIsNotNone(game.winner)


if __name__ == "__main__":
    unittest.main()
