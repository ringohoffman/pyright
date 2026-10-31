# This sample tests PEP 695 higher-kinded type constructor parameters on generic classes
# where the constructor type parameter is used inside class member type annotations (e.g., fields and methods).

from __future__ import annotations
from collections.abc import Callable
from typing import Protocol, reveal_type

class BinaryNode[T](Protocol):
    @property
    def value(self) -> T: ...
    @property
    def left(self) -> BinaryNode[T] | None: ...
    @property
    def right(self) -> BinaryNode[T] | None: ...

class AVLNode[T]:
    height: int

    def __init__(self, value: T, height: int = 1) -> None:
        self._value = value
        self._left: AVLNode[T] | None = None
        self._right: AVLNode[T] | None = None
        self.height = height

    @property
    def value(self) -> T:
        return self._value

    @property
    def left(self) -> AVLNode[T] | None:
        return self._left

    @property
    def right(self) -> AVLNode[T] | None:
        return self._right

class BinaryTree[T, Node[Val]: BinaryNode[Val]]:
    root: Node[T] | None

    def __init__(self, root: Node[T] | None = None) -> None:
        self.root = root

    def rotate_left(self, node: Node[T]) -> Node[T]:
        return node

    def get_root(self) -> Node[T] | None:
        return self.root

    def map_values[U](
        self,
        f: Callable[[T], U],
        node_ctor: Callable[[U], Node[U]],
    ) -> BinaryTree[U, Node]:
        new_root = node_ctor(f(self.root.value)) if self.root else None
        return BinaryTree[U, Node](new_root)

    def to_collection[C[Elem]](self, ctor: type[C[object]]) -> C[T]:
        raise NotImplementedError

tree: BinaryTree[int, AVLNode] = BinaryTree(AVLNode(10))
reveal_type(tree.get_root(), expected_text="AVLNode[int] | None")
reveal_type(tree.rotate_left(AVLNode(5)), expected_text="AVLNode[int]")

mapped_tree = tree.map_values(str, AVLNode)
reveal_type(mapped_tree.get_root(), expected_text="AVLNode[str] | None")

as_list = tree.to_collection(list)
reveal_type(as_list, expected_text="list[int]")
