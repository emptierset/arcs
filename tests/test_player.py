from arcsync.ambition import Ambition
from arcsync.color import Color
from arcsync.player import Player
from arcsync.resource import Resource
from tests.helpers.autostatic import Autostatic

# misc: Mypy can't figure out that Autostatic makes `self` unnecessary, so we just turn off "misc".
# There aren't that many errors under that code, so it shouldn't cause significant false negatives.
#
# I don't know how to avoid casting things to mocks, though...
#
# mypy: disable-error-code="misc"


class TestCountForAmbition(metaclass=Autostatic):
    def test_empath(color: Color) -> None:
        p = Player(color)
        p.gain_resource(Resource.PSIONIC, slot_index=0)
        p.gain_resource(Resource.PSIONIC, slot_index=1)
        count = p.count_for_ambition(Ambition.EMPATH)
        assert count == 2
