from collections.abc import Sequence

import arcsync.courtcards.basecourt
from arcsync.actioncard import ActionCard
from arcsync.ambition import Ambition
from arcsync.color import Color
from arcsync.play import Lead, PassInitiative, Play, Surpass
from arcsync.resource import Resource
from tests.helpers.actioncard_shorthand import ADMIN, AGGRE, CONST

multipip_card: ActionCard = ADMIN[3]
action_card: ActionCard = AGGRE[4]
other_action_card: ActionCard = CONST[5]

player1: Color = Color.WHITE
player2: Color = Color.YELLOW
player3: Color = Color.BLUE
player4: Color = Color.RED

color: Color = player3

turn_order: Sequence[Color] = [player1, player2, player3, player4]

lead: Lead = Lead(player1, action_card)
pass_initiative: PassInitiative = PassInitiative(player1)
surpass: Surpass = Surpass(player2, action_card)
play: Play = lead

resource = Resource.PSIONIC
ambition = Ambition.EMPATH

court_slot0_card_name = arcsync.courtcards.basecourt.cards[3].name  # Admin Union
vox_card_in_court_name = arcsync.courtcards.basecourt.cards[27].name  # Outrage Spreads
guild_card_in_court_name = court_slot0_card_name
