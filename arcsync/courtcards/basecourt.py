from collections.abc import Sequence
from typing import Final

from arcsync.courtcard import GuildCard, Suit, VoxCard


class LoyalEngineers(GuildCard):
    def __init__(self) -> None:
        super().__init__("Loyal Engineers", "ARCS-BC01", Suit.MATERIAL, raid_cost=3)


class MiningInterest(GuildCard):
    def __init__(self) -> None:
        super().__init__("Mining Interest", "ARCS-BC02", Suit.MATERIAL, raid_cost=2)


class MaterialCartel(GuildCard):
    def __init__(self) -> None:
        super().__init__("Material Cartel", "ARCS-BC03", Suit.MATERIAL, raid_cost=2)


class AdminUnion(GuildCard):
    def __init__(self) -> None:
        super().__init__("Admin Union", "ARCS-BC04", Suit.MATERIAL, raid_cost=2)


class ConstructionUnion(GuildCard):
    def __init__(self) -> None:
        super().__init__("Construction Union", "ARCS-BC05", Suit.MATERIAL, raid_cost=2)


class FuelCartel(GuildCard):
    def __init__(self) -> None:
        super().__init__("Fuel Cartel", "ARCS-BC06", Suit.FUEL, raid_cost=2)


class LoyalPilots(GuildCard):
    def __init__(self) -> None:
        super().__init__("Loyal Pilots", "ARCS-BC07", Suit.FUEL, raid_cost=3)


class Gatekeepers(GuildCard):
    def __init__(self) -> None:
        super().__init__("Gate keepers", "ARCS-BC08", Suit.FUEL, raid_cost=2)


class ShippingInterest(GuildCard):
    def __init__(self) -> None:
        super().__init__("Shipping Interest", "ARCS-BC09", Suit.FUEL, raid_cost=2)


class SpacingUnion(GuildCard):
    def __init__(self) -> None:
        super().__init__("Spacing Union", "ARCS-BC10", Suit.FUEL, raid_cost=2)


class ArmsUnion(GuildCard):
    def __init__(self) -> None:
        super().__init__("Arms Union", "ARCS-BC11", Suit.WEAPON, raid_cost=2)


class PrisonWardens(GuildCard):
    def __init__(self) -> None:
        super().__init__("Prison Wardens", "ARCS-BC12", Suit.WEAPON, raid_cost=2)


class Skirmishers(GuildCard):
    def __init__(self) -> None:
        super().__init__("Skirmishers", "ARCS-BC13", Suit.WEAPON, raid_cost=2)


class CourtEnforcers(GuildCard):
    def __init__(self) -> None:
        super().__init__("Court Enforcers", "ARCS-BC14", Suit.WEAPON, raid_cost=2)


class LoyalMarines(GuildCard):
    def __init__(self) -> None:
        super().__init__("Loyal Marines", "ARCS-BC15", Suit.WEAPON, raid_cost=3)


class LatticeSpies(GuildCard):
    def __init__(self) -> None:
        super().__init__("Lattice Spies", "ARCS-BC16", Suit.PSIONIC, raid_cost=2)


class Farseers(GuildCard):
    def __init__(self) -> None:
        super().__init__("Farseers", "ARCS-BC17", Suit.PSIONIC, raid_cost=2)


class SecretOrder(GuildCard):
    def __init__(self) -> None:
        super().__init__("Secret Order", "ARCS-BC18", Suit.PSIONIC, raid_cost=2)


class LoyalEmpaths(GuildCard):
    def __init__(self) -> None:
        super().__init__("Loyal Empaths", "ARCS-BC19", Suit.PSIONIC, raid_cost=3)


class SilverTongues(GuildCard):
    def __init__(self) -> None:
        super().__init__("Silver-Tongues", "ARCS-BC20", Suit.PSIONIC, raid_cost=2)


class LoyalKeepers(GuildCard):
    def __init__(self) -> None:
        super().__init__("Loyal Keepers", "ARCS-BC21", Suit.PSIONIC, raid_cost=3)


class SwornGuardians(GuildCard):
    def __init__(self) -> None:
        super().__init__("Sworn Guardians", "ARCS-BC22", Suit.RELIC, raid_cost=1)


class ElderBroker(GuildCard):
    def __init__(self) -> None:
        super().__init__("Elder Broker", "ARCS-BC23", Suit.PSIONIC, raid_cost=2)


class RelicFence(GuildCard):
    def __init__(self) -> None:
        super().__init__("Relic Fence", "ARCS-BC24", Suit.PSIONIC, raid_cost=2)


class GalacticBards(GuildCard):
    def __init__(self) -> None:
        super().__init__("Galactic Bards", "ARCS-BC25", Suit.RELIC, raid_cost=1)


class MassUprising(VoxCard):
    def __init__(self) -> None:
        super().__init__("Mass Uprising", "ARCS-BC26")


class PopulistDemands(VoxCard):
    def __init__(self) -> None:
        super().__init__("Populist Demands", "ARCS-BC27")


class OutrageSpreads(VoxCard):
    def __init__(self) -> None:
        super().__init__("Outrage Spreads", "ARCS-BC28")


class SongOfFreedom(VoxCard):
    def __init__(self) -> None:
        super().__init__("Song of Freedom", "ARCS-BC29")


class GuildStruggle(VoxCard):
    def __init__(self) -> None:
        super().__init__("Guild Struggle", "ARCS-BC30")


class CallToAction(VoxCard):
    def __init__(self) -> None:
        super().__init__("Call to Action", "ARCS-BC31")


cards: Final[Sequence[GuildCard | VoxCard]] = [
    LoyalEngineers(),
    MiningInterest(),
    MaterialCartel(),
    AdminUnion(),
    ConstructionUnion(),
    FuelCartel(),
    LoyalPilots(),
    Gatekeepers(),
    ShippingInterest(),
    SpacingUnion(),
    ArmsUnion(),
    PrisonWardens(),
    Skirmishers(),
    CourtEnforcers(),
    LoyalMarines(),
    LatticeSpies(),
    Farseers(),
    SecretOrder(),
    LoyalEmpaths(),
    SilverTongues(),
    LoyalKeepers(),
    SwornGuardians(),
    ElderBroker(),
    RelicFence(),
    GalacticBards(),
    MassUprising(),
    PopulistDemands(),
    OutrageSpreads(),
    SongOfFreedom(),
    GuildStruggle(),
    CallToAction(),
]
