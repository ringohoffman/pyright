# https://github.com/python/typing/issues/548#issuecomment-2506024243
#
# Use case from @samvv:
# Generic tree algorithms where specialized trees (AVLTree, RedBlackTree) inherit from BinaryTree.
# Each tree variant requires its own specialized node structure:
#   - BinaryNode[T]: structural protocol defining what every node has (value: T, left, right)
#   - AVLNode[T]: specialized node with height: int
#   - RedBlackNode[T]: specialized node with color: str
#
# WHY THIS REQUIRES HKT (and why simple subtyping/generics fail):
# 1. Structural Protocol Conformance:
#    In standard Python, `N = TypeVar('N', bound=BinaryNode)` cannot be applied as `N[T]`.
#    If parameterized as `BinaryTree[T, N: BinaryNode[T]]`, `N` is fixed to `T`.
# 2. Functor / Mapping over trees:
#    Operations like `map_tree` or `tree.map_values(f: Callable[[T], U])` change the element
#    type from `T` to `U` while PRESERVING the exact node family constructor (`AVLNode[U]`).
#    Standard Python has NO way to express "re-apply the same node constructor to a new type U".
# 3. Dual-HKT Operations:
#    Extracting tree values into an arbitrary collection constructor `C[Elem]` (e.g. `list`, `set`),
#    giving `tree.to_collection(list) -> list[T]`.

from collections.abc import Callable
from typing import Protocol, reveal_type


# ==============================================================================
# 1. Structural Node Protocol
# ==============================================================================

class BinaryNode[T](Protocol):
    @property
    def value(self) -> T: ...
    @property
    def left(self) -> BinaryNode[T] | None: ...
    @property
    def right(self) -> BinaryNode[T] | None: ...


# ==============================================================================
# 2. Concrete Node Implementations (Unrelated classes implementing the protocol)
# ==============================================================================

class AVLNode[T]:
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


class RedBlackNode[T]:
    def __init__(self, value: T, color: str = "red") -> None:
        self._value = value
        self._left: RedBlackNode[T] | None = None
        self._right: RedBlackNode[T] | None = None
        self.color = color

    @property
    def value(self) -> T:
        return self._value

    @property
    def left(self) -> RedBlackNode[T] | None:
        return self._left

    @property
    def right(self) -> RedBlackNode[T] | None:
        return self._right


# ==============================================================================
# 3. Generic Tree using HKT: `Node[Val]: BinaryNode[Val]`
# ==============================================================================

class BinaryTree[T, Node[Val]: BinaryNode[Val]]:
    root: Node[T] | None

    def __init__(self, root: Node[T] | None = None) -> None:
        self.root = root

    def rotate_left(self, node: Node[T]) -> Node[T]:
        # Rotation logic returns the exact node type preserving subclass fields
        return node

    def get_root(self) -> Node[T] | None:
        return self.root

    # --- Full HKT Power: Functor mapping across element types ---
    # Changes element type T -> U while preserving the exact node constructor Node!
    def map_values[U](
        self,
        f: Callable[[T], U],
        node_ctor: Callable[[U], Node[U]],
    ) -> BinaryTree[U, Node]:
        new_root = node_ctor(f(self.root.value)) if self.root else None
        return BinaryTree[U, Node](new_root)

    # --- Dual HKT Power: Generic extraction to any collection constructor C ---
    def to_collection[C[Elem]](self, ctor: type[C[object]]) -> C[T]:
        raise NotImplementedError


# ==============================================================================
# 4. Specialized Trees Inheriting from BinaryTree
# ==============================================================================

class AVLTree[T](BinaryTree[T, AVLNode]):
    def rebalance(self, node: AVLNode[T]) -> AVLNode[T]:
        # AVLNode-specific fields like height are accessible directly:
        if node.height > 1:
            rotated = self.rotate_left(node)
            # rotate_left returns AVLNode[T], so height is still accessible:
            rotated.height = node.height - 1
            return rotated
        return node


class RedBlackTree[T](BinaryTree[T, RedBlackNode]):
    def rebalance(self, node: RedBlackNode[T]) -> RedBlackNode[T]:
        # RedBlackNode-specific fields like color are accessible directly:
        if node.color == "red":
            rotated = self.rotate_left(node)
            # rotate_left returns RedBlackNode[T], so color is still accessible:
            rotated.color = "black"
            return rotated
        return node


# ==============================================================================
# 5. Demonstrating Full HKT Power
# ==============================================================================

# --- Demonstration 1: Subclass rotation preserves concrete node fields ---
avl_tree = AVLTree[int](AVLNode(10, height=2))
reveal_type(avl_tree.get_root(), expected_text="AVLNode[int] | None")

rotated_avl = avl_tree.rotate_left(AVLNode(5, height=3))
reveal_type(rotated_avl, expected_text="AVLNode[int]")
assert rotated_avl.height == 3

# --- Demonstration 2: Functor mapping T (int) -> U (str) preserves node constructor ---
# Here `map_values` transforms BinaryTree[int, AVLNode] into BinaryTree[str, AVLNode]!
# The new tree's root is typed as AVLNode[str] | None, NOT base BinaryNode[str].
mapped_avl = avl_tree.map_values(str, AVLNode)
reveal_type(mapped_avl.root, expected_text="AVLNode[str] | None")

# --- Demonstration 3: Same functor mapping works for RedBlackTree ---
rb_tree = RedBlackTree[int](RedBlackNode(1, color="red"))
mapped_rb = rb_tree.map_values(lambda x: x > 0, RedBlackNode)
reveal_type(mapped_rb.root, expected_text="RedBlackNode[bool] | None")

# --- Demonstration 4: Higher-kinded collection extraction ---
# Extracts elements into arbitrary collection constructors (list, set)
as_list = avl_tree.to_collection(list)
reveal_type(as_list, expected_text="list[int]")

as_set = avl_tree.to_collection(set)
reveal_type(as_set, expected_text="set[int]")
