import typing
from collections.abc import Sequence
from typing import Any, Callable
from unittest.mock import Mock

from pytest import fixture, raises
from pytest_mock import MockerFixture
from statemachine.exceptions import TransitionNotAllowed

from arcsync.actioncard import ActionCard
from arcsync.ambition import Ambition
from arcsync.color import Color
from arcsync.event import AmbitionDeclaredEvent, InitiativeGainedEvent
from arcsync.play import Copy, CouldNotFollow, Follow, Lead, PassInitiative, Pivot, Surpass
from arcsync.round import Round, Step
from tests.helpers import defaults, testcase
from tests.helpers.actioncard_shorthand import ADMIN, CONST, MOBIL
from tests.helpers.autostatic import Autostatic

# misc: Mypy can't figure out that Autostatic makes `self` unnecessary, so we just turn off "misc".
# There aren't that many errors under that code, so it shouldn't cause significant false negatives.
#
# I don't know how to avoid casting things to mocks, though...
#
# mypy: disable-error-code="misc"


@fixture
def r(mocker: MockerFixture, turn_order: Sequence[Color]) -> Round:
    _round = Round(turn_order)
    mocker.patch.object(_round._event_bus, "publish")
    return _round


@fixture
def r_lead_const2(r: Round, player1: Color) -> Round:
    r.begin_turn(Lead(player1, CONST[2]))
    r.end_prelude()
    r.end_pips()
    return r


@fixture
def r_complete(r: Round, player1: Color) -> Round:
    r.begin_turn(PassInitiative(player1))
    return r


class TestBeginTurn(metaclass=Autostatic):
    def test_begin_turn_advances_to_prelude(r: Round, lead: Lead) -> None:
        r.begin_turn(lead)
        assert r.step == Step.PRELUDE

    def test_pips_only_tracked_during_pips_step(
        r: Round, player1: Color, action_card: ActionCard
    ) -> None:
        r.begin_turn(Lead(player1, action_card))
        with raises(ValueError, match="pips_remaining only has meaning during"):
            r.pips_remaining

        r.end_prelude()

        assert r.pips_remaining == action_card.pips

        r.end_pips()
        with raises(ValueError, match="pips_remaining only has meaning during"):
            r.pips_remaining

    def test_cannot_begin_when_round_is_complete(r_complete: Round, lead: Lead) -> None:
        with raises(TransitionNotAllowed, match=r"Can't .* when in Complete"):
            r_complete.begin_turn(lead)

    def test_cannot_play_twice_consecutively(r: Round, lead: Lead) -> None:
        r.begin_turn(lead)
        with raises(TransitionNotAllowed, match=r"Can't .* when in Prelude"):
            r.begin_turn(lead)

    def test_cannot_begin_other_players_turn(
        r: Round, player2: Color, action_card: ActionCard
    ) -> None:
        with raises(ValueError, match=f"not {player2}'s turn"):
            r.begin_turn(Lead(player2, action_card))

    class TestLead(metaclass=Autostatic):
        def test_lead_card_play_is_set(r: Round, lead: Lead) -> None:
            with raises(ValueError):
                _ = r.lead_card_play
            r.begin_turn(lead)
            assert r.lead_card_play == lead

        def test_pips(r: Round, player1: Color, multipip_card: ActionCard) -> None:
            r.begin_turn(Lead(player1, multipip_card))
            r.end_prelude()
            assert r.pips_remaining == multipip_card.pips

        def test_declaration_is_published(r: Round, player1: Color) -> None:
            r.begin_turn(Lead(player1, ADMIN[5], Ambition.KEEPER))
            typing.cast(Mock, r._event_bus.publish).assert_called_once_with(
                AmbitionDeclaredEvent(player1, Ambition.KEEPER),
            )

        # TODO(base): Does this test actually test anything interesting now that we use
        # statemachine?
        # def test_cannot_lead_without_initiative(
        #    r_lead_const2: Round, player2: Color, action_card: ActionCard
        # ) -> None:
        #    with raises(ValueError, match=f"{player2} did not start with initiative"):
        #        r_lead_const2.begin_turn(Lead(player2, action_card))

    class TestPassInitiative(metaclass=Autostatic):
        def test_round_complete(r: Round, pass_initiative: PassInitiative) -> None:
            assert not r.complete
            r.begin_turn(pass_initiative)
            assert r.complete

        def test_initiative_change_is_published(
            r: Round, pass_initiative: PassInitiative, player2: Color
        ) -> None:
            r.begin_turn(pass_initiative)
            typing.cast(Mock, r._event_bus.publish).assert_called_once_with(
                InitiativeGainedEvent(player2),
            )

        # TODO(base): Does this test actually test anything interesting now that we use
        # statemachine?
        # def test_cannot_pass_without_initiative(r_lead_const2: Round, player2: Color) -> None:
        #    with raises(ValueError, match=f"{player2} did not start with initiative"):
        #        r_lead_const2.begin_turn(PassInitiative(player2))

    class TestCouldNotFollow(metaclass=Autostatic):
        def test_is_now_current_play(r_lead_const2: Round, player2: Color) -> None:
            could_not_follow = CouldNotFollow(player2)
            r_lead_const2.begin_turn(could_not_follow)
            assert r_lead_const2.current_play == could_not_follow

        def test_ends_turn(r_lead_const2: Round, player2: Color, player3: Color) -> None:
            assert r_lead_const2.current_player == player2
            r_lead_const2.begin_turn(CouldNotFollow(player2))
            assert r_lead_const2.current_player == player3

    class TestFollow(metaclass=Autostatic):
        def test_is_now_current_play(r_lead_const2: Round, player2: Color) -> None:
            copy = Copy(player2, ADMIN[3])
            r_lead_const2.begin_turn(copy)
            assert r_lead_const2.current_play == copy

        def test_no_seize(r_lead_const2: Round, player2: Color) -> None:
            r_lead_const2.begin_turn(Copy(player2, ADMIN[1]))
            typing.cast(Mock, r_lead_const2._event_bus.publish).assert_not_called()

        def test_normal_seize(r_lead_const2: Round, player2: Color) -> None:
            r_lead_const2.begin_turn(Copy(player2, ADMIN[1], seize_card=MOBIL[5]))
            typing.cast(Mock, r_lead_const2._event_bus.publish).assert_called_once_with(
                InitiativeGainedEvent(player2),
            )

        def test_7_seize(r_lead_const2: Round, player2: Color) -> None:
            # TODO(base): Once it's implemented.
            pass

        @testcase.parametrize(
            ["play", "want_pips"],
            [
                testcase.new(
                    "surpass_gets_full_pips",
                    play=Surpass(defaults.player2, CONST[3]),
                    want_pips=CONST[3].pips,
                ),
                testcase.new(
                    "copy_gets_one_pip",
                    play=Copy(defaults.player2, CONST[3]),
                    want_pips=1,
                ),
                testcase.new(
                    "pivot_gets_one_pip",
                    play=Pivot(defaults.player2, ADMIN[3]),
                    want_pips=1,
                ),
            ],
        )
        def test_pips(r_lead_const2: Round, play: Follow, want_pips: int) -> None:
            r_lead_const2.begin_turn(play)
            typing.cast(Callable[..., Any], r_lead_const2.end_prelude)()
            assert r_lead_const2.pips_remaining == want_pips

    class TestSurpass(metaclass=Autostatic):
        pass
        # TODO(base):

    class TestCopy(metaclass=Autostatic):
        pass
        # TODO(base):

    class TestPivot(metaclass=Autostatic):
        pass
        # TODO(base):


class TestRoundCompletion(metaclass=Autostatic):
    def test_only_complete_at_end(
        r: Round, player1: Color, player2: Color, player3: Color, player4: Color
    ) -> None:
        assert not r.complete
        r.begin_turn(Lead(player1, CONST[2]))
        assert not r.complete
        r.end_prelude()
        assert not r.complete
        r.end_pips()
        assert not r.complete
        r.begin_turn(Surpass(player2, CONST[3]))
        assert not r.complete
        r.end_prelude()
        assert not r.complete
        r.end_pips()
        assert not r.complete
        r.begin_turn(Surpass(player3, CONST[4]))
        assert not r.complete
        r.end_prelude()
        assert not r.complete
        r.end_pips()
        assert not r.complete
        r.begin_turn(Surpass(player4, CONST[5]))
        assert not r.complete
        r.end_prelude()
        assert not r.complete
        r.end_pips()
        assert r.complete
