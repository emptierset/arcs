from pytest import raises

from arcsync.ambition import Ambition
from arcsync.color import Color
from arcsync.play import Lead
from tests.helpers.actioncard_shorthand import ADMIN
from tests.helpers.autostatic import Autostatic

# TODO(cleanup): For mypy, I don't know how to avoid casting things to mocks.

# misc: Mypy can't figure out that Autostatic makes `self` unnecessary, so we just turn off "misc".
# There aren't that many errors under that code, so it shouldn't cause significant false negatives.
#
# mypy: disable-error-code="misc"


class TestLead(metaclass=Autostatic):
    def test_zero_token_placed(color: Color) -> None:
        lead = Lead(color, ADMIN[3], Ambition.TYRANT)
        assert lead.zero_token_placed

    def test_zero_token_not_placed(color: Color) -> None:
        lead = Lead(color, ADMIN[3])
        assert not lead.zero_token_placed

    def test_declare_matching_ambition(color: Color) -> None:
        _ = Lead(color, ADMIN[2], Ambition.TYCOON)
        _ = Lead(color, ADMIN[3], Ambition.TYRANT)
        _ = Lead(color, ADMIN[4], Ambition.WARLORD)
        _ = Lead(color, ADMIN[5], Ambition.KEEPER)
        _ = Lead(color, ADMIN[6], Ambition.EMPATH)

    def test_declare_anything_with_7(color: Color) -> None:
        _ = Lead(color, ADMIN[7], Ambition.EDENGUARD)
        _ = Lead(color, ADMIN[7], Ambition.TYCOON)
        _ = Lead(color, ADMIN[7], Ambition.TYRANT)
        _ = Lead(color, ADMIN[7], Ambition.WARLORD)
        _ = Lead(color, ADMIN[7], Ambition.KEEPER)
        _ = Lead(color, ADMIN[7], Ambition.EMPATH)
        _ = Lead(color, ADMIN[7], Ambition.BLIGHTKIN)

    def test_cannot_declare_with_a_1(color: Color) -> None:
        with raises(ValueError, match="by leading a 1"):
            _ = Lead(color, ADMIN[1], Ambition.TYRANT)

    def test_cannot_declare_mismatched_ambition(color: Color) -> None:
        with raises(ValueError, match="you did not lead a 7 or a 3; you led a 2"):
            _ = Lead(color, ADMIN[2], Ambition.TYRANT)
