import random
from typing import Any, Callable

from pytest import fixture, raises

from arcsync.actioncard import ActionCard
from arcsync.ambition import Ambition
from arcsync.color import Color
from arcsync.game import Game
from arcsync.resource import Resource
from tests.helpers.actioncard_shorthand import ADMIN, AGGRE, CONST
from tests.helpers.autostatic import Autostatic

# misc: Mypy can't figure out that Autostatic makes `self` unnecessary, so we just turn off "misc".
# There aren't that many errors under that code, so it shouldn't cause significant false negatives.
#
# I don't know how to avoid casting things to mocks, though...
#
# mypy: disable-error-code="misc"

AnyFunc = Callable[..., Any]


def _lead(g: Game, player: Color, card: ActionCard, ambition: Ambition | None = None) -> None:
    g.lead(player, card, ambition=ambition)
    g.end_prelude()
    g.end_pips()


def _surpass(
    g: Game,
    player: Color,
    card: ActionCard,
    seize_card: ActionCard | None = None,
) -> None:
    g.surpass(player, card, seize_card=seize_card)
    g.end_prelude()
    g.end_pips()


def _copy(
    g: Game,
    player: Color,
    card: ActionCard,
    seize_card: ActionCard | None = None,
) -> None:
    g.copy(player, card, seize_card=seize_card)
    g.end_prelude()
    g.end_pips()


def _pivot(
    g: Game,
    player: Color,
    card: ActionCard,
    seize_card: ActionCard | None = None,
) -> None:
    g.pivot(player, card, seize_card=seize_card)
    g.end_prelude()
    g.end_pips()


@fixture
def g() -> Game:
    random.seed(a=2)  # maps to desired turn order
    game = Game(player_count=4)
    game.setup()
    return game


@fixture
def g_before_end(g: Game, player1: Color, player2: Color, player3: Color, player4: Color) -> Game:
    for _ in range(4):
        g.pass_initiative(player1)
        g.pass_initiative(player2)
        g.pass_initiative(player3)
        g.pass_initiative(player4)
    g.pass_initiative(player1)
    g.pass_initiative(player2)
    g.pass_initiative(player3)
    return g


def test_setup_sanity_checks(g: Game, player1: Color) -> None:
    assert len(g.action_card_deck) == 0
    assert len(g.action_card_discard) == 4

    for p in g.players.values():
        assert len(p.hand) == 6

    assert g.initiative == player1

    assert g.winner is None


def test_turn_order_changes_on_round_completion(
    g: Game, player1: Color, player2: Color, player3: Color, player4: Color
) -> None:
    assert g.turn_order == [player1, player2, player3, player4]

    _lead(g, player1, ADMIN[4])
    _surpass(g, player2, ADMIN[5])
    _pivot(g, player3, CONST[6])
    _copy(g, player4, ADMIN[7])

    assert g.turn_order == [player2, player3, player4, player1]


class TestCardPlay(metaclass=Autostatic):
    def test_cannot_lead_card_not_in_hand(
        g: Game,
        player1: Color,
    ) -> None:
        with raises(ValueError, match=f"not in {player1}'s hand"):
            _lead(g, player1, CONST[6])

    def test_cannot_surpass_with_card_not_in_hand(
        g: Game,
        player1: Color,
        player2: Color,
    ) -> None:
        _lead(g, player1, ADMIN[4])
        with raises(ValueError, match=f"not in {player2}'s hand"):
            _surpass(g, player2, ADMIN[6])

    def test_cannot_copy_with_card_not_in_hand(
        g: Game,
        player1: Color,
        player2: Color,
    ) -> None:
        _lead(g, player1, ADMIN[4])
        with raises(ValueError, match=f"not in {player2}'s hand"):
            _copy(g, player2, ADMIN[6])

    def test_cannot_pivot_with_card_not_in_hand(
        g: Game,
        player1: Color,
        player2: Color,
    ) -> None:
        _lead(g, player1, ADMIN[4])
        with raises(ValueError, match=f"not in {player2}'s hand"):
            _pivot(g, player2, AGGRE[1])


class TestAdvanceChapter(metaclass=Autostatic):
    def test_all_pass_consecutively_with_cards(
        g: Game,
        player1: Color,
        player2: Color,
        player3: Color,
        player4: Color,
    ) -> None:
        assert g.chapter == 1
        assert g.initiative == player1
        g.pass_initiative(player1)
        g.pass_initiative(player2)
        g.pass_initiative(player3)
        g.pass_initiative(player4)
        assert g.chapter == 2
        assert g.initiative == player1

    def test_all_run_out_of_cards(
        g: Game,
        player1: Color,
        player2: Color,
        player3: Color,
        player4: Color,
    ) -> None:
        for p in g.players.values():
            g.action_card_discard.add(p.hand[1:])
            p.hand = p.hand[:1]

        assert g.chapter == 1
        assert g.initiative == player1

        _lead(g, player1, ADMIN[4])
        _surpass(g, player2, ADMIN[5])
        _copy(g, player3, CONST[6])
        _copy(g, player4, ADMIN[7])

        assert g.chapter == 2
        assert g.initiative == player2


class TestWinner(metaclass=Autostatic):
    def test_most_power_wins(
        g_before_end: Game,
        player1: Color,
        player2: Color,
        player3: Color,
        player4: Color,
    ) -> None:
        g_before_end.players[player1].power = 6
        g_before_end.players[player2].power = 10
        g_before_end.players[player3].power = 9
        g_before_end.players[player4].power = 1
        g_before_end.pass_initiative(player4)
        assert g_before_end.winner == player2

    def test_initiative_breaks_tie(
        g_before_end: Game,
        player1: Color,
        player2: Color,
        player3: Color,
        player4: Color,
    ) -> None:
        g_before_end.players[player1].power = 6
        g_before_end.players[player2].power = 10
        g_before_end.players[player4].power = 10
        g_before_end.pass_initiative(player4)
        assert g_before_end.winner == player2


# TODO(cleanup): pytest output is a lot easier to debug if it is assigned to a local first.


class TestScoring(metaclass=Autostatic):
    class TestPowerGained(metaclass=Autostatic):
        def test_tie_for_first(
            g: Game,
            color: Color,
            resource: Resource,
            ambition: Ambition,
            player1: Color,
            player2: Color,
            player3: Color,
            player4: Color,
        ) -> None:
            g.ambition_manager.declare(color, ambition)
            g.players[player1].gain_resource(resource, slot_index=0)
            g.players[player2].gain_resource(resource, slot_index=0)
            g.players[player3].gain_resource(resource, slot_index=0)
            g.players[player4].gain_resource(resource, slot_index=0)
            g._score_ambitions()
            assert g.players[player1].power == g.ambition_manager.second_place_value(ambition)
            assert g.players[player2].power == g.ambition_manager.second_place_value(ambition)
            assert g.players[player3].power == g.ambition_manager.second_place_value(ambition)
            assert g.players[player4].power == g.ambition_manager.second_place_value(ambition)

        def test_tie_for_second(
            g: Game,
            color: Color,
            resource: Resource,
            ambition: Ambition,
            player1: Color,
            player2: Color,
            player3: Color,
            player4: Color,
        ) -> None:
            g.ambition_manager.declare(color, ambition)
            g.players[player1].gain_resource(resource, slot_index=0)
            g.players[player2].gain_resource(resource, slot_index=0)
            g.players[player2].gain_resource(resource, slot_index=1)
            g.players[player3].gain_resource(resource, slot_index=0)
            g.players[player4].gain_resource(resource, slot_index=0)
            g._score_ambitions()
            assert g.players[player1].power == 0
            assert g.players[player2].power == g.ambition_manager.first_place_value(ambition)
            assert g.players[player3].power == 0
            assert g.players[player4].power == 0

        def test_multiple_ambitions(
            g: Game,
            color: Color,
            player1: Color,
            player2: Color,
            player3: Color,
            player4: Color,
        ) -> None:
            g.ambition_manager.declare(color, Ambition.TYCOON)
            g.ambition_manager.declare(color, Ambition.KEEPER)
            g.players[player1].gain_resource(Resource.FUEL, slot_index=0)
            g.players[player1].gain_resource(Resource.MATERIAL, slot_index=1)
            g.players[player2].gain_resource(Resource.FUEL, slot_index=0)
            g.players[player3].gain_resource(Resource.RELIC, slot_index=0)
            g._score_ambitions()
            assert g.players[player1].power == g.ambition_manager.first_place_value(
                Ambition.TYCOON
            )
            assert g.players[player2].power == g.ambition_manager.second_place_value(
                Ambition.TYCOON
            )
            assert g.players[player3].power == g.ambition_manager.first_place_value(
                Ambition.KEEPER
            )
            assert g.players[player4].power == 0

    class TestRankPlayers(metaclass=Autostatic):
        def test_tie_for_first(
            g: Game,
            resource: Resource,
            ambition: Ambition,
            player1: Color,
            player2: Color,
            player3: Color,
            player4: Color,
        ) -> None:
            g.players[player1].gain_resource(resource, slot_index=0)
            g.players[player2].gain_resource(resource, slot_index=0)
            g.players[player3].gain_resource(resource, slot_index=0)
            g.players[player4].gain_resource(resource, slot_index=0)
            ranking = g._rank_players(ambition)
            assert ranking[player1] == 2
            assert ranking[player2] == 2
            assert ranking[player3] == 2
            assert ranking[player4] == 2

        def test_tie_for_second(
            g: Game,
            resource: Resource,
            ambition: Ambition,
            player1: Color,
            player2: Color,
            player3: Color,
            player4: Color,
        ) -> None:
            g.players[player1].gain_resource(resource, slot_index=0)
            g.players[player2].gain_resource(resource, slot_index=0)
            g.players[player2].gain_resource(resource, slot_index=1)
            g.players[player3].gain_resource(resource, slot_index=0)
            g.players[player4].gain_resource(resource, slot_index=0)
            ranking = g._rank_players(ambition)
            assert ranking[player1] == 3
            assert ranking[player2] == 1
            assert ranking[player3] == 3
            assert ranking[player4] == 3

        def test_no_ties(
            g: Game,
            resource: Resource,
            ambition: Ambition,
            player1: Color,
            player2: Color,
            player3: Color,
            player4: Color,
        ) -> None:
            g.players[player4].cities = 0
            g.players[player4].gain_resource(resource, slot_index=0)
            g.players[player4].gain_resource(resource, slot_index=1)
            g.players[player4].gain_resource(resource, slot_index=2)
            g.players[player4].gain_resource(resource, slot_index=3)

            g.players[player3].cities = 0
            g.players[player3].gain_resource(resource, slot_index=0)
            g.players[player3].gain_resource(resource, slot_index=1)
            g.players[player3].gain_resource(resource, slot_index=2)

            g.players[player2].gain_resource(resource, slot_index=0)
            g.players[player2].gain_resource(resource, slot_index=1)

            g.players[player1].gain_resource(resource, slot_index=0)

            ranking = g._rank_players(ambition)

            assert ranking[player1] == 4
            assert ranking[player2] == 3
            assert ranking[player3] == 2
            assert ranking[player4] == 1

        def test_player_with_nothing_is_culled(
            g: Game,
            resource: Resource,
            ambition: Ambition,
            player1: Color,
            player2: Color,
        ) -> None:
            g.players[player2].gain_resource(resource, slot_index=0)
            g.players[player2].gain_resource(resource, slot_index=1)

            ranking = g._rank_players(ambition)

            assert player1 not in ranking
            assert player2 in ranking
