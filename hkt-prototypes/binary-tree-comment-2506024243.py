# https://github.com/python/typing/issues/548#issuecomment-2506024243
#
# Use case from @samvv:
# Parameterizing a base tree class over a generic node constructor:
# `BinaryTree[T, Node[Val]: BinaryNode[Val]]` allows base algorithms (e.g. rotate_left)
# to operate on specialized node instances (AVLNode[T], RedBlackNode[T]) preserving
# subclass-specific attributes (height, color) without losing type precision.

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
    def __init__(self, value: T, height: int = 1) -> None:
        self.value = value
        self.left: AVLNode[T] | None = None
        self.right: AVLNode[T] | None = None
        self.height = height


class RedBlackNode[T]:
    def __init__(self, value: T, color: str = "red") -> None:
        self.value = value
        self.left: RedBlackNode[T] | None = None
        self.right: RedBlackNode[T] | None = None
        self.color = color


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


class AVLTree[T](BinaryTree[T, AVLNode]):
    def rebalance(self, node: AVLNode[T]) -> AVLNode[T]:
        if node.height > 1:
            rotated = self.rotate_left(node)
            rotated.height = node.height - 1
            return rotated
        return node


class RedBlackTree[T](BinaryTree[T, RedBlackNode]):
    def rebalance(self, node: RedBlackNode[T]) -> RedBlackNode[T]:
        if node.color == "red":
            rotated = self.rotate_left(node)
            rotated.color = "black"
            return rotated
        return node


# 1. Preserving concrete node types in tree operations
avl_tree = AVLTree[int](AVLNode(10, height=2))
reveal_type(avl_tree.get_root(), expected_text="AVLNode[int] | None")

rotated_avl = avl_tree.rotate_left(AVLNode(5, height=3))
reveal_type(rotated_avl, expected_text="AVLNode[int]")
assert rotated_avl.height == 3

# 2. Re-applying the node constructor over mapped element types
mapped_avl = avl_tree.map_values(str, AVLNode)
reveal_type(mapped_avl.root, expected_text="AVLNode[str] | None")

rb_tree = RedBlackTree[int](RedBlackNode(1, color="red"))
mapped_rb = rb_tree.map_values(lambda x: x > 0, RedBlackNode)
reveal_type(mapped_rb.root, expected_text="RedBlackNode[bool] | None")

# 3. Higher-kinded collection extraction
as_list = avl_tree.to_collection(list)
reveal_type(as_list, expected_text="list[int]")

as_set = avl_tree.to_collection(set)
reveal_type(as_set, expected_text="set[int]")
