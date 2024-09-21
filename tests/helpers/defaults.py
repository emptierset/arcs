from collections.abc import Sequence

from arcsync.actioncard import ActionCard
from arcsync.color import Color
from arcsync.round import Lead, PassInitiative, Play, Surpass
from tests.helpers.actioncard_shorthand import ADMIN, AGGRE, CONST

multipip_card: ActionCard = ADMIN[3]
action_card: ActionCard = AGGRE[4]
other_action_card: ActionCard = CONST[5]

player1: Color = Color.RED
player2: Color = Color.WHITE
player3: Color = Color.BLUE
player4: Color = Color.YELLOW

color: Color = player3

turn_order: Sequence[Color] = [player1, player2, player3, player4]

lead: Lead = Lead(player1, action_card)
pass_initiative: PassInitiative = PassInitiative(player1)
surpass: Surpass = Surpass(player2, action_card)
play: Play = lead
