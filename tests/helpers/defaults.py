from collections.abc import Sequence

from arcsync.actioncard import ActionCard
from arcsync.ambition import Ambition
from arcsync.color import Color
from arcsync.play import Lead, PassInitiative, Play, Surpass
from arcsync.resource import Resource
from tests.helpers.actioncard_shorthand import ADMIN, AGGRE, CONST

multipip_card: ActionCard = ADMIN[3]
action_card: ActionCard = AGGRE[4]
other_action_card: ActionCard = CONST[5]

player1: Color = Color.YELLOW
player2: Color = Color.BLUE
player3: Color = Color.WHITE
player4: Color = Color.RED

color: Color = player3

turn_order: Sequence[Color] = [player1, player2, player3, player4]

lead: Lead = Lead(player1, action_card)
pass_initiative: PassInitiative = PassInitiative(player1)
surpass: Surpass = Surpass(player2, action_card)
play: Play = lead

resource = Resource.PSIONIC
ambition = Ambition.EMPATH
