import typing

from pytest import fixture, raises

import arcsync.courtcards.basecourt
from arcsync.color import Color
from arcsync.court import CardWithAgents, Court
from arcsync.courtcard import CourtCard
from tests.helpers.autostatic import Autostatic

# misc: Mypy can't figure out that Autostatic makes `self` unnecessary, so we just turn off "misc".
# There aren't that many errors under that code, so it shouldn't cause significant false negatives.
#
# I don't know how to avoid casting things to mocks, though...
#
# mypy: disable-error-code="misc"


@fixture
def c() -> Court:
    court = Court(arcsync.courtcards.basecourt.cards, num_slots=4, seed=2)
    return court


# TODO(cleanup): Is there some sort of t.Helper() thing, like in Go?
def _assert_slot_empty(c: Court, index: int) -> None:
    cwa, _ = c._get_slot(index)
    assert cwa is None


def _assert_slot_not_empty(c: Court, index: int) -> CardWithAgents:
    cwa, _ = c._get_slot(index)
    assert cwa is not None
    return cwa


def _assert_discard_from_initial_state(c: Court) -> CourtCard:
    cwa_in_slot = _assert_slot_not_empty(c, 0)
    assert len(c.discard_pile) == 0
    c.discard_card(0)
    assert c.discard_pile.top_card == cwa_in_slot.card
    return cwa_in_slot.card


def _assert_bury_from_initial_state(c: Court) -> CourtCard:
    cwa_in_slot = _assert_slot_not_empty(c, 0)
    deck_size_before = len(c.deck)
    c.bury_card(0)
    assert len(c.deck) == deck_size_before + 1
    assert c.deck.bottom_card == cwa_in_slot.card
    return cwa_in_slot.card


class TestRefillCourt(metaclass=Autostatic):
    def test_refill_one(c: Court) -> None:
        c.discard_card(0)
        _assert_slot_empty(c, 0)
        c.refill_court()
        _assert_slot_not_empty(c, 0)

    def test_refill_multiple(c: Court) -> None:
        c.discard_card(1)
        c.discard_card(3)
        _assert_slot_empty(c, 1)
        _assert_slot_empty(c, 3)
        c.refill_court()
        _assert_slot_not_empty(c, 1)
        _assert_slot_not_empty(c, 3)


class TestTakeCard(metaclass=Autostatic):
    def test_by_index(c: Court, court_slot0_card_name: str) -> None:
        got_cwa, got_agents = c.take_card(0)
        assert got_cwa.name == court_slot0_card_name
        assert not got_agents

    def test_by_name(c: Court, court_slot0_card_name: str) -> None:
        got_cwa, got_agents = c.take_card(court_slot0_card_name)
        assert got_cwa.name == court_slot0_card_name
        assert not got_agents

    def test_by_card(c: Court) -> None:
        key = c.card(0)
        got_cwa, got_agents = c.take_card(key)
        assert got_cwa == key
        assert not got_agents


class TestModifyAgentCount(metaclass=Autostatic):
    def test_positive(c: Court, color: Color) -> None:
        assert c.agents_on_card(0)[color] == 0
        c._modify_agent_count(color, 0, delta=5)
        assert c.agents_on_card(0)[color] == 5

    def test_negative(c: Court, color: Color) -> None:
        assert c.agents_on_card(0)[color] == 0
        c.add_agents(color, 0, num_agents=9)
        c._modify_agent_count(color, 0, delta=-7)
        assert c.agents_on_card(0)[color] == 2

    def test_remove_too_many_agents(c: Court, color: Color) -> None:
        with raises(ValueError, match=r"Cannot apply negative delt"):
            c._modify_agent_count(color, 0, delta=-7)


class TestAddAgents(metaclass=Autostatic):
    def test_add_negative_number(c: Court, color: Color) -> None:
        # TODO(cleanup): Make all match= strings raw strings.
        with raises(ValueError, match=r"negative"):
            c.add_agents(color, 0, num_agents=-4)

    def test_basic(c: Court, player1: Color, player2: Color) -> None:
        c.add_agents(player2, 0, num_agents=2)
        c.add_agents(player1, 0, num_agents=3)
        assert c.agents_on_card(0)[player1] == 3
        assert c.agents_on_card(0)[player2] == 2


class TestRemoveAgents(metaclass=Autostatic):
    def test_remove_negative_number(c: Court, color: Color) -> None:
        with raises(ValueError, match="negative"):
            c.remove_agents(color, 0, num_agents=-4)

    def test_basic(c: Court, player1: Color, player2: Color) -> None:
        c.add_agents(player1, 0, num_agents=5)
        c.add_agents(player2, 0, num_agents=3)
        c.remove_agents(player1, 0, num_agents=3)
        c.remove_agents(player2, 0, num_agents=2)
        assert c.agents_on_card(0)[player1] == 2
        assert c.agents_on_card(0)[player2] == 1


# TODO(cleanup): Verify that, in fail cases for mutative functions, the gamestate is not mutated.


class TestCardRecovery(metaclass=Autostatic):
    class TestUnbury(metaclass=Autostatic):
        def test_happy(c: Court) -> None:
            buried_card = _assert_bury_from_initial_state(c)
            c.unbury_to_empty_slot(0)
            cwa_in_slot = _assert_slot_not_empty(c, 0)
            assert buried_card == cwa_in_slot.card

        def test_slot_already_full(c: Court) -> None:
            with raises(ValueError, match=r"slot already containing"):
                c.unbury_to_empty_slot(0)

    class TestRecoverDiscarded(metaclass=Autostatic):
        def test_happy(c: Court) -> None:
            discarded_card = _assert_discard_from_initial_state(c)
            c.recover_discarded_card_to_empty_slot(discarded_card.name, 0)
            cwa_in_slot = _assert_slot_not_empty(c, 0)
            assert discarded_card == cwa_in_slot.card

        def test_slot_already_full(c: Court) -> None:
            discarded_card = _assert_discard_from_initial_state(c)
            c.refill_court()
            with raises(ValueError, match=r"slot already containing"):
                c.recover_discarded_card_to_empty_slot(discarded_card.name, 0)

    class TestDrawFromCardDeckByName(metaclass=Autostatic):
        def test_cannot_find_card(c: Court) -> None:
            with raises(ValueError, match=r"slot already containing"):
                c.recover_discarded_card_to_empty_slot("There ain't no card with this name", 0)


# TODO(cleanup): Assert that agents disappear on card removal.
class TestCardRemoval(metaclass=Autostatic):
    def test_remove(c: Court) -> None:
        _assert_slot_not_empty(c, 0)
        # It isn't import from _remove_card's POV that the card goes anywhere in particular, just
        # that it goes away. So, we can make up some BS callback that doesn't do anything useful.
        c._remove_card(0, lambda c: None)
        _assert_slot_empty(c, 0)

    def test_discard(c: Court) -> None:
        cwa = _assert_slot_not_empty(c, 0)
        # TODO(cleanup): Make whatever the truthy/falsy dunder method is for Deck return truthiness
        # of its internal deque.
        assert len(c.discard_pile) == 0
        c.discard_card(0)
        assert c.discard_pile.top_card == cwa.card

    def test_bury(c: Court) -> None:
        cwa = _assert_slot_not_empty(c, 0)
        # TODO(cleanup): Make whatever the truthy/falsy dunder method is for Deck return truthiness
        # of its internal deque.
        assert len(c.discard_pile) == 0
        c.bury_card(0)
        assert c.deck.bottom_card == cwa.card


class TestGetSlot(metaclass=Autostatic):
    def test_by_index(c: Court, court_slot0_card_name: str) -> None:
        got_cwa, got_agents = c._get_slot(0)
        assert got_cwa is not None
        assert got_cwa.card.name == court_slot0_card_name
        assert not got_agents

    def test_by_name(c: Court, court_slot0_card_name: str) -> None:
        got_cwa, got_agents = c._get_slot(court_slot0_card_name)
        assert got_cwa is not None
        assert got_cwa.card.name == court_slot0_card_name
        assert not got_agents

    def test_by_card(c: Court) -> None:
        key = c.card(0)
        got_cwa, got_agents = c._get_slot(key)
        assert got_cwa is not None
        assert got_cwa.card == key
        assert not got_agents


class TestGetSlotWithCard(metaclass=Autostatic):
    def test_not_found(c: Court) -> None:
        c.discard_card(0)
        with raises(ValueError, match=r"requires a card to be found"):
            _, _ = c._get_slot_with_card(0)


class TestFindSlotContaining(metaclass=Autostatic):
    def test_not_found(c: Court) -> None:
        c.discard_card(0)
        with raises(ValueError, match=r"not in court"):
            _, _ = c._find_slot_containing("Not a Real Card Name")


class TestSlotsContents(metaclass=Autostatic):
    def test_court_full(c: Court) -> None:
        # We know the court is full, so this doesn't return any `None`s.
        names = [typing.cast(CourtCard, card).name for card in c.slots_contents]
        assert names == ["Admin Union", "Elder Broker", "Secret Order", "Lattice Spies"]

    def test_court_some_missing(c: Court) -> None:
        c.discard_card(1)
        c.discard_card(2)
        names = [
            contents.name if isinstance(contents, CourtCard) else None
            for contents in c.slots_contents
        ]
        assert names == ["Admin Union", None, None, "Lattice Spies"]
