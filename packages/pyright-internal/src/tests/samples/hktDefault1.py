# This sample tests that subclassing a generic class whose type constructor parameter
# has a default does NOT cause the subclass to incorrectly inherit free TypeVars and
# become generic itself.

from typing import reveal_type

type Identity[T] = T

class Container[T]: ...

# Case 1: Base class with type constructor parameter defaulting to a type alias
class KVStore[WrapperT[T] = Identity[T]]:
    def get(self, key: str) -> WrapperT[str]: ...

# Subclass does not specify type arguments; should use default Identity and NOT become generic
class SyncKVStore(KVStore): ...

# SyncKVStore should be concrete type[SyncKVStore], not type[SyncKVStore[T@WrapperT]]
reveal_type(SyncKVStore, expected_text="type[SyncKVStore]")

# Using SyncKVStore as a type annotation should NOT require type arguments
def take_sync_store(store: SyncKVStore) -> None:
    reveal_type(store.get("key"), expected_text="str")

# Case 2: Base class with type constructor parameter defaulting to a generic class
class Base[F[T] = Container[T]]:
    def get(self) -> F[int]: ...

class Sub(Base): ...

reveal_type(Sub, expected_text="type[Sub]")

def take_sub(sub: Sub) -> None:
    reveal_type(sub.get(), expected_text="Container[int]")
