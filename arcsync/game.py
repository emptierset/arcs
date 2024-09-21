import random
import typing
from collections.abc import Sequence
from typing import Final, NewType

import arcsync.setupcard
from arcsync.actioncard import ActionCardDeck, ActionCardDiscard
from arcsync.ambition import AmbitionManager
from arcsync.color import Color
from arcsync.court import Court
from arcsync.event import InitiativeGainedEvent
from arcsync.eventbus import EventBus
from arcsync.player import Player
from arcsync.reach import Reach
from arcsync.setupcard import SetupCard

Chapter = NewType("Chapter", int)


@typing.final
class Game(object):
    players: Final[Sequence[Player]]
    initiative: Color
    chapter: Chapter

    ambition_manager: Final[AmbitionManager]

    reach: Final[Reach]

    action_card_deck: Final[ActionCardDeck]
    action_card_discard: Final[ActionCardDeck]

    court: Final[Court]

    _event_bus: Final[EventBus]

    def __init__(self) -> None:
        self._event_bus = EventBus()

        colors = [Color.RED, Color.BLUE, Color.WHITE, Color.YELLOW]
        random_turn_order = random.sample(colors, len(colors))
        self.players = [Player(color) for color in random_turn_order]
        self.initiative = self.players[0].color
        self.chapter = Chapter(1)

        self.ambition_manager = AmbitionManager(self._event_bus)

        setup_card: SetupCard = random.choice(arcsync.setupcard.four_player_setup_cards)
        self.reach = Reach(setup_card)

        self.action_card_deck = ActionCardDeck(player_count=4)
        self.action_card_discard = ActionCardDiscard()

        self.court = Court([], num_slots=4)

        # Initialize event handlers below this.

        def handle_initiative_gained_event(e: InitiativeGainedEvent) -> None:
            self.initiative = e.player

        self._event_bus.subscribe(InitiativeGainedEvent, handle_initiative_gained_event)


if __name__ == "__main__":
    g = Game()
