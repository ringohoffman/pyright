# Context: python/typing#548 comment 1347577379 (Gobot1234)
#
# Use case from gaming / trading systems:
# A `Trade` transaction exchanges items between two users (`OurUser` and `OtherUser`).
# The trade should accept any generic item constructor `ItemT` (such as `Item` or `SpecialItem`),
# but must enforce that items placed in `sending` belong to `OurUser` while items placed
# in `receiving` belong to `OtherUser`.
#
# Without HKT:
# In standard Python (PEP 484 / PEP 695):
# If `Trade` is parameterized by a concrete item type `Trade[ItemT]`, `ItemT` is fixed:
#     @dataclass
#     class Trade[ItemT: Item[BaseUser]]:
#         sending: Sequence[ItemT]
#         receiving: Sequence[ItemT]
# Both `sending` and `receiving` have the exact same item type `ItemT`.
# It is impossible to enforce that `sending` has `ItemT[OurUser]` and `receiving` has `ItemT[OtherUser]`
# while still keeping the class generic over the item subclass constructor `ItemT`!
# Swapping sending and receiving collections or passing items belonging to the wrong user
# is completely invisible to the type checker.
#
# With HKT:
# The class parameterizes over the unapplied item constructor `ItemT[O: BaseUser]: Item[O]`:
#     @dataclass
#     class Trade[ItemT[O: BaseUser]: Item[O]]:
#         sending: Sequence[ItemT[OurUser]]
#         receiving: Sequence[ItemT[OtherUser]]
# - `sending` is statically constrained to `ItemT[OurUser]`.
# - `receiving` is statically constrained to `ItemT[OtherUser]`.
# - The constructor identity `ItemT` is preserved (`Trade[Item]` or `Trade[SpecialItem]`).
# - Passing our items into `receiving` or other items into `sending` triggers a static type error.

from collections.abc import Sequence
from dataclasses import dataclass
from typing import reveal_type


class BaseUser:
    pass


class OurUser(BaseUser):
    pass


class OtherUser(BaseUser):
    pass


@dataclass
class Item[OwnerT: BaseUser]:
    id: int
    owner: OwnerT


@dataclass
class SpecialItem[OwnerT: BaseUser](Item[OwnerT]):
    rarity: str = "legendary"


@dataclass
class Trade[ItemT[O: BaseUser]: Item[O]]:
    sending: Sequence[ItemT[OurUser]]
    receiving: Sequence[ItemT[OtherUser]]


our_user = OurUser()
other_user = OtherUser()

our_items = [Item(1, our_user), Item(2, our_user)]
other_items = [Item(3, other_user), Item(4, other_user)]

# 1. Valid trade: Item constructor inferred cleanly
# sending -> Sequence[Item[OurUser]], receiving -> Sequence[Item[OtherUser]]
valid_trade = Trade(sending=our_items, receiving=other_items)
reveal_type(valid_trade, expected_text="Trade[Item[OwnerT@Item]]")

# 2. Subclass constructor preservation: SpecialItem constructor inferred
our_special = [SpecialItem(10, our_user)]
other_special = [SpecialItem(20, other_user)]

special_trade = Trade(sending=our_special, receiving=other_special)
reveal_type(special_trade, expected_text="Trade[SpecialItem[OwnerT@SpecialItem]]")

# 3. Runtime functional validation
assert valid_trade.sending == our_items
assert valid_trade.receiving == other_items
assert special_trade.sending == our_special
assert special_trade.receiving == other_special
