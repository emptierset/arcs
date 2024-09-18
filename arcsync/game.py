import random
import typing
from collections.abc import Sequence
from typing import Final, NewType

from arcsync.actioncard import ActionCardDeck, ActionCardDiscard
from arcsync.ambition import AmbitionManager
from arcsync.card import Deck
from arcsync.color import Color
from arcsync.court import Court
from arcsync.courtcard import CourtCard
from arcsync.event import InitiativeSeizedEvent
from arcsync.eventbus import EventBus
from arcsync.player import Player
from arcsync.reach import Reach

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

    court_deck: Final[Deck[CourtCard]]
    court: Final[Court]

    _event_bus: Final[EventBus]

    def __init__(self, players: Sequence[Player]) -> None:
        self._event_bus = EventBus()

        self.players = players
        self.initiative = random.choice(players).color
        self.chapter = Chapter(1)

        self.ambition_manager = AmbitionManager(self._event_bus)

        self.reach = Reach([])

        self.action_card_deck = ActionCardDeck(player_count=4)
        self.action_card_discard = ActionCardDiscard()

        self.court_deck = Deck[CourtCard]([])
        self.court = Court(num_slots=4)

    def _init_event_handlers(self) -> None:
        def handle_initiative_seized_event(e: InitiativeSeizedEvent) -> None:
            self.initiative = e.player


if __name__ == "__main__":
    pass
