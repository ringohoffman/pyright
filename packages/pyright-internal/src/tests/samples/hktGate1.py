# This sample tests version and kind gating for type constructor
# parameter syntax. It is analyzed with Python 3.13, where the
# syntax is not yet available.


# This should generate an error because the syntax requires Python 3.16.
def func1[F[T]](x: F[int]) -> F[str]: ...


# This should generate an error because the syntax requires Python 3.16.
class ClassA[F[T]]:
    x: F[int]


# This should generate an error because the syntax requires Python 3.16.
type TA1[F[T]] = F[int]
