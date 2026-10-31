# This sample tests that inner type parameters are rejected on
# TypeVarTuple and ParamSpec type parameters.


# This should generate an error because a TypeVarTuple cannot have inner type parameters.
def func1[*Ts[T]](*args: *Ts) -> tuple[*Ts]: ...


# This should generate an error because a ParamSpec cannot have inner type parameters.
def func2[**P[T]](*args: P.args, **kwargs: P.kwargs) -> None: ...
