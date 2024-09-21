from collections.abc import Sequence

from pytest import fixture

from arcsync.actioncard import ActionCard
from arcsync.color import Color
from arcsync.round import Lead, PassInitiative, Play, Surpass
from tests.helpers import defaults


@fixture
def multipip_card() -> ActionCard:
    return defaults.multipip_card


@fixture
def action_card() -> ActionCard:
    return defaults.action_card


@fixture
def other_action_card() -> ActionCard:
    return defaults.other_action_card


@fixture
def color() -> Color:
    return defaults.color


@fixture
def player1() -> Color:
    return defaults.player1


@fixture
def player2() -> Color:
    return defaults.player2


@fixture
def player3() -> Color:
    return defaults.player3


@fixture
def player4() -> Color:
    return defaults.player4


@fixture
def turn_order() -> Sequence[Color]:
    return defaults.turn_order


@fixture
def play() -> Play:
    return defaults.play


@fixture
def lead() -> Lead:
    return defaults.lead


@fixture
def pass_initiative() -> PassInitiative:
    return defaults.pass_initiative


@fixture
def surpass() -> Surpass:
    return defaults.surpass
