# [Higher-Kinded TypeVars](https://github.com/python/typing/issues/548) (Issue #548)

- **State**: `open`
- **Author**: [@tek](https://github.com/tek)
- **Created**: `2018-03-30T22:56:19Z`
- **Updated**: `2026-06-19T19:06:11Z`
- **Total Comments**: `222`

## Original Issue Description

**Author**: @tek

aka type constructors, generic TypeVars

Has there already been discussion about those?
I do a lot of FP that results in impossible situations because of this. Consider an example:

```python
A = TypeVar('A')
B = TypeVar('B')
F = TypeVar('F')

class M(Generic[F[X], A]):
    def x(fa: F[A], f: Callable[[A], B]) -> F[B]:
        return map(f, fa)

M().x([1], str)
```

I haven't found a way to make this work, does anyone know a trick or is it impossible?
If not, consider the syntax as a proposal.
Reference implementations would be Haskell, Scala.
optimally, the HK's type param would be indexable as well, allowing for `F[X[X, X], X[X]]`

----

Summary of current status (by @smheidrich, 2024-02-08):

- @JelleZijlstra [has indicated interest](https://github.com/python/typing/issues/548#issuecomment-1193345123) in sponsoring a PEP, conditional on a prototype implementation in a major type checker and a well-specified draft PEP.
- Drafting the PEP takes place in @nekitdev's [fork](https://github.com/nekitdev/peps) of the `peps` repo. The [**stub PEP draft**](https://github.com/nekitdev/peps/blob/main/pep-9999.rst) so far contains a few examples of the proposed syntax.
- That same repo's [**GitHub Discussions forum**](https://github.com/nekitdev/peps/discussions) forum has been [designated](https://github.com/python/typing/issues/548#issuecomment-1193348994) as the place to discuss the PEP (and presumably the prototype implementation?). Some limited further discussions have taken place there.
  - If you want to be notified of new discussion threads, I think you have to set the whole repo as "watched" in GitHub?



---

## Comments

### Comment [377642510](https://github.com/python/typing/issues/548#issuecomment-377642510)

- **Author**: @ilevkivskyi
- **Date**: `2018-03-30T23:04:45Z`

I think this came up few times in other discussions, for example one use case is https://github.com/python/mypy/issues/4395. But TBH this is low priority, since such use cases are quite rare.


---

### Comment [377643203](https://github.com/python/typing/issues/548#issuecomment-377643203)

- **Author**: @tek
- **Date**: `2018-03-30T23:10:42Z`

damn, I searched very thoroughly but did not find this one! :smile: 
So, consider this my +1!


---

### Comment [377652438](https://github.com/python/typing/issues/548#issuecomment-377652438)

- **Author**: @gvanrossum
- **Date**: `2018-03-31T00:35:12Z`

Adding your +1 is all fine, but who's going to do the (probably pretty
complicated) implementation work?



---

### Comment [377652730](https://github.com/python/typing/issues/548#issuecomment-377652730)

- **Author**: @tek
- **Date**: `2018-03-31T00:38:18Z`

are you approving the feature?


---

### Comment [377664768](https://github.com/python/typing/issues/548#issuecomment-377664768)

- **Author**: @gvanrossum
- **Date**: `2018-03-31T04:20:45Z`

I am neither approving nor disapproving. Just observing that it may be a
lot of work for marginal benefits in most codebases.



---

### Comment [377677528](https://github.com/python/typing/issues/548#issuecomment-377677528)

- **Author**: @tek
- **Date**: `2018-03-31T08:46:16Z`

awfully pragmatic. Where's your sense of adventure? :smile: 
anyways, I'll work on it, though it's gonna take a while to get into the project.


---

### Comment [412718727](https://github.com/python/typing/issues/548#issuecomment-412718727)

- **Author**: @landonpoch
- **Date**: `2018-08-14T01:08:39Z`

Similar to https://github.com/Microsoft/TypeScript/issues/1213

Not sure if the discussion over there provides any useful insights to the effort over here.


---

### Comment [453101854](https://github.com/python/typing/issues/548#issuecomment-453101854)

- **Author**: @rcalsaverini
- **Date**: `2019-01-10T13:49:46Z`

Hi @tek. I'm also very interested in this, so I'd like to ask if you had any progress with this and volunteer to help if you want.


---

### Comment [453179820](https://github.com/python/typing/issues/548#issuecomment-453179820)

- **Author**: @tek
- **Date**: `2019-01-10T17:21:26Z`

@rcalsaverini sorry, I've been migrating my legacy code to haskell and am abandoning python altogether. but I wish you great success!


---

### Comment [453197172](https://github.com/python/typing/issues/548#issuecomment-453197172)

- **Author**: @rcalsaverini
- **Date**: `2019-01-10T18:12:41Z`

Oh, sad to hear but I see your point. Thanks.


---

### Comment [540830100](https://github.com/python/typing/issues/548#issuecomment-540830100)

- **Author**: @syastrov
- **Date**: `2019-10-10T22:48:45Z`

Just to add another use case (which I think relates to this issue):

Using Literal types along with overloading `__new__`, along with higher-kinded typevars could allow implementing a generic "nullable" ORM Field class, using a descriptor to provide access to the appropriate nullable-or-not field values. The descriptor wouldn't have to be reimplemented in subclasses.

It is one step closer to being possible due to the most recent mypy release's support for honoring the return type of `__new__` (https://github.com/python/mypy/issues/1020).

Note: this is basically a stripped-down version of Django's Field class:

```python
# in stub file

from typing import Generic, Optional, TypeVar, Union, overload, Type
from typing_extensions import Literal

_T = TypeVar("_T", bound="Field")
_GT = TypeVar("_GT")

class Field(Generic[_GT]):
    # on the line after the overload: error: Type variable "_T" used with arguments
    @overload
    def __new__(cls: Type[_T], null: Literal[False] = False, *args, **kwargs) -> _T[_GT]: ...
    @overload
    def __new__(cls: Type[_T], null: Literal[True], *args, **kwargs) -> _T[Optional[_GT]]: ...
    def __get__(self, instance, owner) -> _GT: ...

class CharField(Field[str]): ...
class IntegerField(Field[int]): ...
# etc...

# in code

class User:
  f1 = CharField(null=False)
  f2 = CharField(null=True)

reveal_type(User().f1) # Expected: str
reveal_type(User().f2) # Expected: Union[str, None]
```



---

### Comment [619580011](https://github.com/python/typing/issues/548#issuecomment-619580011)

- **Author**: @samuelcolvin
- **Date**: `2020-04-26T16:26:50Z`

I wonder if this is what I need or if there's currently a work around for my (slightly simpler) case?:

I'm building an async redis client with proper type hints. I have a "Commands" class with methods for all redis commands (`get`, `set`, `exists`, `strlen` ... and hundreds more). Normally each of those methods should return a future (actually coroutine) to the result, but in pipeline mode they should all return `None` - the commands are added to the pipeline to be executed later.

This is easy enough to implement in python, but not so easy to type hint correctly.

Basic example:

```py
class Redis:
    def execute(self, command) -> Coroutine[Any, Any, Union[None, str, int, float]]:
        return self.connection.execute(...)

    def get(self, *args) -> Coroutine[Any, Any, str]:
        ...
        return self.execute(command)

    def set(self, *args) -> Coroutine[Any, Any, None]:
        ...
        return self.execute(command)

    def exists(self, *args) -> Coroutine[Any, Any, bool]:
        ...
        return self.execute(command)

    # ... and many MANY more ...


class RedisPipeline(Redis):
    def execute(self, command) -> None:
        self.pipeline.append(command)
```

I tried numerous options to make `Coroutine[Any, Any, xxx]` generic, but nothing seems to work.

Is there any way around this with python 3.8 and latest mypy? If not a solution would be wonderful - as far as I can think, my only other route for proper types is a script which copy and pastes the entire class and changes the return types in code.


---

### Comment [619596147](https://github.com/python/typing/issues/548#issuecomment-619596147)

- **Author**: @gvanrossum
- **Date**: `2020-04-26T18:01:41Z`

@samuelcolvin I don't think this question belongs in this issue. The reason for the failure (knowing nothing about Redis but going purely by the code you posted) is that in order to make this work, the *base* class needs to switch to an `Optional` result, i.e.
```
    def execute(self, command) -> Optional[Coroutine[Any, Any, Union[None, str, int, float]]]:
```


---

### Comment [619603342](https://github.com/python/typing/issues/548#issuecomment-619603342)

- **Author**: @samuelcolvin
- **Date**: `2020-04-26T18:42:03Z`

I get that, but I need all the public methods to definitely return a coroutine. Otherwise, if it returned an optional coroutine, it would be extremely annoying to use.

What I'm trying to do is modify the return type of many methods on the sub-classes, including "higher kind" types which are parameterised.

Hence thinking it related to this issue.


---

### Comment [619605036](https://github.com/python/typing/issues/548#issuecomment-619605036)

- **Author**: @gvanrossum
- **Date**: `2020-04-26T18:52:43Z`

Honestly I have no idea what higher-kinded type vars are -- my eyes glaze over when I hear that kind of talk. :-)

I have one more suggestion, then you're on your own. Use a common base class that has an `Optional[Coroutine[...]]` return type and derive both the regular Redis class and the RedisPipeline class from it.


---

### Comment [619605422](https://github.com/python/typing/issues/548#issuecomment-619605422)

- **Author**: @samuelcolvin
- **Date**: `2020-04-26T18:55:44Z`

Okay, so the simple answer is that what I'm trying to do isn't possible with python types right now.

Thanks for helping - at least I can stop my search.


---

### Comment [619605716](https://github.com/python/typing/issues/548#issuecomment-619605716)

- **Author**: @gvanrossum
- **Date**: `2020-04-26T18:58:03Z`

I suspect that the reason is that it simply isn't type-safe, and you
couldn't do it (using subclassing) in any other typed language either.



---

### Comment [619609237](https://github.com/python/typing/issues/548#issuecomment-619609237)

- **Author**: @samuelcolvin
- **Date**: `2020-04-26T19:16:29Z`

humm, but the example above under "Basic example" I would argue IS type-safe.

All the methods which end `return self.execute(...)` return what `execute` returns - either a `Coroutine` or `None`.

Thus I don't see how this as any more "unsafe" than normal use of generics.


---

### Comment [621195693](https://github.com/python/typing/issues/548#issuecomment-621195693)

- **Author**: @jab
- **Date**: `2020-04-29T13:13:35Z`

@gvanrossum, I can relate!

I wonder if [bidict](https://bidict.readthedocs.io) provides a practical example of how this issue prevents expressing a type that you can actually imagine yourself needing.
```python
>>> element_by_atomicnum = bidict({0: "hydrogen", 1: "helium"})
>>> reveal_type(element_by_atomicnum)  # bidict[int, str]
# So far so good, but now consider the inverse:
>>> element_by_atomicnum.inverse
bidict({"hydrogen": 0, "helium": 1})
```
What we want is for mypy to know this:
```python
>>> reveal_type(element_by_atomicnum.inverse)  # bidict[str, int]
```
merely from a type hint that we could add to a super class. It would parameterize not just the key type and the value type, but also the self type. In other words, something like:
```python
KT = TypeVar('KT')
VT = TypeVar('VT')

class BidirectionalMapping(Mapping[KT, VT]):
    ...
    def inverse(self) -> $SELF_TYPE[VT, KT]:
        ...
```
where `$SELF_TYPE` would of course use some actually legal syntax that allowed composing the self type with the other parameterized types.


---

### Comment [621571821](https://github.com/python/typing/issues/548#issuecomment-621571821)

- **Author**: @gvanrossum
- **Date**: `2020-04-30T02:15:58Z`

Okay, I think that example is helpful. I recreated it somewhat simpler (skipping the inheritance from `Mapping` and the property decorators):
```python
from abc import abstractmethod
from typing import *

T = TypeVar('T')
KT = TypeVar('KT')
VT = TypeVar('VT')

class BidirectionalMapping(Generic[KT, VT]):
    @abstractmethod
    def inverse(self) -> BidirectionalMapping[VT, KT]:
        ...

class bidict(BidirectionalMapping[KT, VT]):
    def __init__(self, key: KT, val: VT):
        self.key = key
        self.val = val
    def inverse(self) -> bidict[VT, KT]:
        return bidict(self.val, self.key)

b = bidict(3, "abc")
reveal_type(b)  # bidict[int, str]
reveal_type(b.inverse())  # bidict[str, int]
```
This passes but IIUC you want the ABC to have a more powerful type. I guess here we might want to write it as
```py
    def inverse(self: T) -> T[VT, KT]:  # E: Type variable "T" used with arguments
```
Have I got that?


---

### Comment [621574435](https://github.com/python/typing/issues/548#issuecomment-621574435)

- **Author**: @jab
- **Date**: `2020-04-30T02:24:47Z`

Exactly! It should be possible to e.g. subclass bidict (without overriding inverse), and have mypy realize that calling inverse on the subclass gives an instance of the subclass (with the key and value types swapped as well).

This isn’t only hypothetically useful, it’d really be useful in practice for the various subclasses in the bidict library where this actually happens (frozenbidict, OrderedBidict, etc.).

Glad this example was helpful! Please let me know if there’s anything further I can do to help here, and (can’t help myself) thanks for creating Python, it’s such a joy to use.


---

### Comment [621580882](https://github.com/python/typing/issues/548#issuecomment-621580882)

- **Author**: @gvanrossum
- **Date**: `2020-04-30T02:48:42Z`

Ah, so the `@abstractmethod` is also a red herring.

And now I finally get the connection with the comment that started this issue.

But I still don't get the connection with @samuelcolvin's RedisPipeline class. :-(


---

### Comment [621686416](https://github.com/python/typing/issues/548#issuecomment-621686416)

- **Author**: @sobolevn
- **Date**: `2020-04-30T08:16:32Z`

I would also say that this example is really simple, common, but not supported:

```python
def create(klass: Type[T], value: K) -> T[K]:
     return klass(value)
```

We use quite a lot of similar constructs in [`dry-python/returns`](https://github.com/dry-python/returns).

As a workaround I am trying to build a plugin with emulated HKT, just like in some other languages where support of it is limited. Like:

- Swift and `bow`: https://bow-swift.io/docs/fp-concepts/higher-kinded-types/
- TypeScript and `fp-ts`: https://github.com/gcanti/fp-ts/blob/master/src/HKT.ts

Paper on "Lightweight higher-kinded polymorphism": https://www.cl.cam.ac.uk/~jdy22/papers/lightweight-higher-kinded-polymorphism.pdf

**TLDR**: So, instead of writing `T[K]` we can emulate this by using `HKT[T, K]` where `HKT` is a basic generic instance processed by a custom `mypy` plugin. I am working on this plugin for already some time now, but there's still nothing to show. You can track the progress here: https://pypi.org/project/kinds/ (part of dry-python libraries)


---

### Comment [621790339](https://github.com/python/typing/issues/548#issuecomment-621790339)

- **Author**: @samuelcolvin
- **Date**: `2020-04-30T12:04:08Z`

> But I still don't get the connection with @samuelcolvin's RedisPipeline class. :-(

Sorry if I wasn't clear. I'll try again to explain:

I have a class with many (~200) methods, they all return coroutines with different result types (`None`, `bytes`, `str`, `int` or `float`). I want a subclass with the same internal logic but where all those methods return `None` - I can do this in python, but not with type hints currently ([here's](https://github.com/samuelcolvin/async-redis/blob/1828a346453c9e95d9f7f3e771b92e97b1ebe5e0/async_redis/commands.py) the actual code if it helps)

So roughly I want:

```py
T = TypeVar('T', bytes, str, int, float, 'None')
Result = Coroutine[Any, Any, T]

class Foo:
    def method_1(self, *args) -> Result[str]:
        ...

    def method_2(self, *args) -> Result[None]:
        ...

    def method_3(self, *args) -> Result[bool]:
        ...

    ...
    ...

    def method_200(self, *args) -> Result[int]:
        ...

class Bar:

    def method_1(self, *args) -> None:
        ...

    def method_2(self, *args) -> None:
        ...

    def method_3(self, *args) -> None:
        ...

    ...
    ...

    def method_200(self, *args) -> None:
        ...
```

Except I don't want to have to redefine all the methods on `Bar`. Assuming I could create my own `AlwaysNone` type which even when parameterised told mypy the result would always be `None`

```py
class AlwaysNoneMeta(type):
    def __getitem__(self, item) -> None:
        return None

class AlwaysNone(metaclass=AlwaysNoneMeta):
    pass
```

I think the feature requested here could solve my problem.

In other words if mypy could understand

```py
def generate_cls(OuterType):
    class TheClass:
        def method_1(self, *args) -> OuterType[str]:
            ...
        ...
    
    return TheClass

Foo = generate_cls(Result)
Bar = Generate_cls(AlwaysNone)
```

I'd be in the money, but quite understandably it can't.

---

I've currently got a working solution where i generate a `.pyi` stub file with definitions for all these methods but changing the return type to `None` (see [here](https://github.com/samuelcolvin/async-redis/blob/master/tools/generate_stubs.py))  so I'm not in immediate need of this anymore.


---

### Comment [621836402](https://github.com/python/typing/issues/548#issuecomment-621836402)

- **Author**: @Kentzo
- **Date**: `2020-04-30T13:27:40Z`

It looks like you want completely different signatures whose likeness is limited to their names and arguments:

```python
async def do_work(redis_client: Redis):
    await redit_sclient.get(...)

do_work(RedisPipeline())  # user expects type checker to warn about misuse
```

It's understandable you're looking to reuse some common "template", but I fail to see what it has to do with higher-kinded types.


---

### Comment [624548663](https://github.com/python/typing/issues/548#issuecomment-624548663)

- **Author**: @samuelcolvin
- **Date**: `2020-05-06T09:47:58Z`

Hi @Kentzo, that's incorrect, these are not completely different signatures.


Please review the code [here](https://github.com/samuelcolvin/async-redis/blob/master/async_redis/commands.py); as you can see these are functions which may return an awaitable object, not coroutines. This approach and similar, while not necessarily obvious to beginners, is relatively common in libraries which make extensive use of asyncio and the standard library asyncio code.

If you're not sure how it works, feel free to submit an issue on that project and I'll endeavour to explain it to you.


---

### Comment [624554525](https://github.com/python/typing/issues/548#issuecomment-624554525)

- **Author**: @Kentzo
- **Date**: `2020-05-06T09:59:30Z`

In your initial example:

```python
class Redis:
    def execute(self, command) -> Coroutine[Any, Any, Union[None, str, int, float]]:
        ...

class RedisPipeline(Redis):
    def execute(self, command) -> None:
```

These are different signatures. Functions annotated to accept `Redis` as an argument would expect `execute` to return a coroutine.


---

### Comment [624562518](https://github.com/python/typing/issues/548#issuecomment-624562518)

- **Author**: @samuelcolvin
- **Date**: `2020-05-06T10:17:46Z`

This is off-topic, please create an issue on async-redis if you want to discuss this more.

In short, yes they're different signatures, but I think my explanation above gives enough detail on what I'm doing and why I think it relates to this issue.


---

### Comment [682918789](https://github.com/python/typing/issues/548#issuecomment-682918789)

- **Author**: @3noch
- **Date**: `2020-08-28T17:05:50Z`

+1 on this. It's hard to say the use cases are rare when it's not even possible to express... There may be countless use cases hiding behind duck typing that simply can't be checked by the type system and therefore certainly aren't recognized as such. Having a type safe generic "Mappable" class as shown in the OP would be really useful.


---

### Comment [682935523](https://github.com/python/typing/issues/548#issuecomment-682935523)

- **Author**: @gvanrossum
- **Date**: `2020-08-28T17:10:25Z`

> It's hard to say the use cases are rare when it's not even possible to express

That makes no sense. You can express the OP's example just fine in untyped Python, you just can't express the types correctly. So if there were "countless" real examples we would encounter frequent user requests for type system extensions to allow typing this correctly. I haven't seen a lot of those.

Do you have an actual (non-toy) example?


---

### Comment [682974062](https://github.com/python/typing/issues/548#issuecomment-682974062)

- **Author**: @sobolevn
- **Date**: `2020-08-28T17:35:15Z`

You actually can have Higher Kinded Types in Python with full `mypy` support.

Here's how `Mappable` looks like from OP:
- interface `Mappable` aka `Functor`: https://github.com/dry-python/returns/blob/master/returns/interfaces/mappable.py
- tests for it: https://github.com/dry-python/returns/blob/master/typesafety/test_interfaces/test_mappable/test_inheritance.yml 
- real type implementing this interface: https://github.com/dry-python/returns/blob/f144affb73da17f5efbcb244507632452df92d24/returns/result.py#L89



---

### Comment [682989203](https://github.com/python/typing/issues/548#issuecomment-682989203)

- **Author**: @3noch
- **Date**: `2020-08-28T17:50:26Z`

@sobolevn That's awesome! Thank you!

@gvanrossum Inexpressible in the type system is what I was referring to. My point was that writing this off as rare seems premature since Python's types system is not a *hard stop* on your ability to keep going. So it *might* be actually quite common and how would we know? Certainly you're right that it's not a common *request* though which is a good point and slightly different than mine. However, it's all moot now because it can be done! Awesome!


---

### Comment [683336963](https://github.com/python/typing/issues/548#issuecomment-683336963)

- **Author**: @BvB93
- **Date**: `2020-08-29T20:11:28Z`

> Do you have an actual (non-toy) example?

An example would be the [`dict.fromkeys(...)`](https://docs.python.org/3/library/stdtypes.html#dict.fromkeys) method, as the output type is variable with respect to both the `dict` (sub-)class as well as the key type (see https://github.com/python/typeshed/issues/3800). This example above can, admittedly, be more or less resolved by explicitly re-annotating aforementioned method in every single subclass.

Another less easily resolved example one would be the [`np.asanyarray(a, dtype=..., ...)`](https://numpy.org/doc/stable/reference/generated/numpy.asanyarray.html) function in numpy. Per the documentation: "Convert the input to an ndarray, but pass ndarray subclasses through.". 
What this means is that, similar to `dict.fromkeys(...)`, the output is variable with respect to both any passed `ndarray` subclasses (the `a` parameter) as well as the type of the embedded scalars (the `dtype` parameter).

Examples
---------
``` python
In [1]: import numpy as np

In [2]: class TestArray(np.ndarray):
   ...:     ...
   ...:

In [3]: array: TestArray = np.array([0, 1, 2]).view(TestArray)

In [4]: array  # array of integers
Out[4]: TestArray([0, 1, 2])

In [5]: np.asanyarray(array, dtype=float)  # array of floats
Out[5]: TestArray([0., 1., 2.])
```


---

### Comment [683341789](https://github.com/python/typing/issues/548#issuecomment-683341789)

- **Author**: @gvanrossum
- **Date**: `2020-08-29T21:04:30Z`

Thanks, that was helpful.



---

### Comment [693100157](https://github.com/python/typing/issues/548#issuecomment-693100157)

- **Author**: @NeilGirdhar
- **Date**: `2020-09-16T00:32:00Z`

Ran into this today:
```python
from typing import Any, Generic, Mapping, TypeVar


ProblemState = TypeVar('ProblemState')
Action = TypeVar('Action')


class Problem(Generic[ProblemState, Action]):
    pass


ProblemT = TypeVar('ProblemT', bound=Problem[ProblemState, Action])


class Solution(Generic[ProblemT, ProblemState, Action]):
    pass
```
I could have worked around it with an intersection operator:
```python
ProblemU = TypeVar('ProblemU', bound=Problem[Any, Any])

class Solution(Generic[ProblemU, ProblemState, Action]):
    ProblemT = Intersection[ProblemU, Problem[ProblemState, Action]]
```
Would intersection help in the general case without requiring as much effort?


---

### Comment [701207531](https://github.com/python/typing/issues/548#issuecomment-701207531)

- **Author**: @florensacc
- **Date**: `2020-09-30T07:16:36Z`

Just ran into this limitation when trying to type methods of a generic class that return an instance of the same generic class but with other arguments. This is actually very common for classes that can easily have some properties changed, like numpy arrays or torch tensors and their `device` (gpu or cpu) or `dtype` (`int`, `float`, ...):

```
DeviceTransferableT = TypeVar("DeviceTransferableT", bound="DeviceTransferable")

class DeviceTransferable(Generic[DeviceT]):

    def to_device(self: DeviceTransferableT, device: Type[DeviceT]) -> DeviceTransferableT[DeviceT]:   # error!
          ...  # some great implementation

class SomeOtherClass(DeviceTransferable):
    """Would prefer not to re-implement `to_device` in every inheriting class."""
```
Is there any other solution?


---

### Comment [701426830](https://github.com/python/typing/issues/548#issuecomment-701426830)

- **Author**: @gvanrossum
- **Date**: `2020-09-30T14:27:17Z`

@florensacc Can you expand the example so that I can actually run it by mypy? A few things are missing and I can’t guess what their definitions should be.


---

### Comment [701504878](https://github.com/python/typing/issues/548#issuecomment-701504878)

- **Author**: @florensacc
- **Date**: `2020-09-30T16:35:19Z`

Here's a full example, which throws two errors: `error: Type variable "DeviceTransferableT" used with arguments` and `Argument 1 to "f" has incompatible type "SomeOtherClass[Device0]"; expected "SomeOtherClass[Device1]"`.
```python
import attr
import abc
from typing import Type, TypeVar, Generic, ClassVar


class Device(abc.ABC):
    device_id: ClassVar[int]


class Device0(Device):
    device_id = 0


class Device1(Device):
    device_id = 1


DeviceT = TypeVar("DeviceT", bound=Device)
AnotherDeviceT = TypeVar("AnotherDeviceT", bound=Device)
DeviceTransferableT = TypeVar("DeviceTransferableT", bound="DeviceTransferable")


@attr.s()
class DeviceTransferable(Generic[DeviceT]):

    device: DeviceT = attr.ib()

    def to_device(self: DeviceTransferableT, device: Type[AnotherDeviceT]) -> DeviceTransferableT[AnotherDeviceT]:
        return attr.evolve(self, device=device)


@attr.s()
class SomeOtherClass(DeviceTransferable[DeviceT]):
    """Would prefer not to re-implement `to_device` in every inheriting class."""
    pass


C_in0 = SomeOtherClass(device=Device0())

C_in1 = C_in0.to_device(Device1)


def f(c: SomeOtherClass[Device1]) -> None:
    print(f"The device of c is {c.device}, but its type is still SomeOtherClass[Device0]!")


f(C_in1)
```


---

### Comment [701526019](https://github.com/python/typing/issues/548#issuecomment-701526019)

- **Author**: @gvanrossum
- **Date**: `2020-09-30T17:14:20Z`

Oh, @attr.s :-(

Can you do it without?


---

### Comment [701547644](https://github.com/python/typing/issues/548#issuecomment-701547644)

- **Author**: @florensacc
- **Date**: `2020-09-30T17:55:52Z`

sure, you can remove all attr.s stuff and use this class definition:
```python
class DeviceTransferable(Generic[DeviceT]):

    def __init__(self, device: DeviceT):
        self.device = device

    def to_device(self: DeviceTransferableT, device: Type[AnotherDeviceT]) -> DeviceTransferableT[AnotherDeviceT]:
        return type(self)(device=device)
```
without the "argument" to the `TypeVar` this code runs happily and prints my message:
`The device of c is <class '__main__.Device1'>, but its type is still SomeOtherClass[Device0]!`


---

### Comment [701579348](https://github.com/python/typing/issues/548#issuecomment-701579348)

- **Author**: @gvanrossum
- **Date**: `2020-09-30T18:54:34Z`

Okay, I get it. If/when we fix this we'll make sure to have a test like that. Thanks!


---

### Comment [719496694](https://github.com/python/typing/issues/548#issuecomment-719496694)

- **Author**: @sobolevn
- **Date**: `2020-10-30T11:22:50Z`

We have released a first prototype of Higher Kinded Types emulation for Python.

It is available for everyone to try! Quick demo: https://gist.github.com/sobolevn/7f8ffd885aec70e55dd47928a1fb3e61

Here's how a function's signature will look like:

```python
from returns.primitives.hkt import Kind1, kinded

_InstanceKind = TypeVar('_InstanceKind', bound='HasValue')

@kinded
def apply_function(
    instance: Kind1[_InstanceKind, _ValueType],
    callback: Callable[[_ValueType], _NewValueType],
) -> Kind1[_InstanceKind, _NewValueType]:
    ...
```


Source code: https://github.com/dry-python/returns
Docs: https://returns.readthedocs.io/en/latest/pages/hkt.html and https://sobolevn.me/2020/10/higher-kinded-types-in-python


---

### Comment [762314154](https://github.com/python/typing/issues/548#issuecomment-762314154)

- **Author**: @sebastian-philipp
- **Date**: `2021-01-18T15:18:45Z`

See https://github.com/ceph/ceph/pull/38953 for a real world use case


---

### Comment [811894377](https://github.com/python/typing/issues/548#issuecomment-811894377)

- **Author**: @benjamindkilleen
- **Date**: `2021-04-01T13:06:21Z`

Finally found this issue after running into `TypeError: 'TypeVar' object is not subscriptable` and searching around for the right way to do this. Turns out there isn't. Has there been any change in status for the implementation? The use-case might be limited for the annotations themselves, but if utilized in a couple core libraries, the end-user experience could be greatly improved by the resulting hints in IDEs.

I empathize with @tek, but unfortunately can't leave Python for the strongly-typed shores of Scala or Haskell, due to Python's ML ecosystem and relatively easy learning curve.


---

### Comment [843663432](https://github.com/python/typing/issues/548#issuecomment-843663432)

- **Author**: @Tinche
- **Date**: `2021-05-19T00:50:20Z`

Hm, I believe I've finally run into this. Here's my example, let me know if I'm misunderstanding something.

Let's say you're adding static types to a Mongo ODM/ORM-type framework. You define your model using a class.

```python3
@dataclass
class User:
    __collection__ = "users"  # This is the "table", or collection in Mongo. Class variable, not instance

    _id: ObjectId  # Every Mongo document has an ID, most often ObjectId, but can be maybe str or something else
    username: str  # A random property
```
Now you write a function to query for this model. We write a generic protocol for models, parametrizing by the ID type:
```python3
ID = TypeVar("ID")

class MongoModel(Protocol[ID])
    __collection__: str

    @property
    def _id(self) -> ID:
        ...
```

Our `User` class is thus a `MongoModel`. Now the actual querying function. We can query just passing in the ID.
```python3
C = TypeVar("C", bound=MongoModel)
def find_one(model_cls: Type[C], id: ???) -> C: ...
```
There's nothing to put instead of `???`, is there?

My first instinct was to try:
```python3
C = TypeVar("C", bound=MongoModel)
TID = TypeVar("TID")
def find_one(model_cls: Type[C[TID], id: TID) -> C: ...
```
But no dice, obviously.

Second approach: I hoped Mypy would realize `MongoModel` already references `ID` (since it's defined with it), so I can write this:

```
C = TypeVar("C", bound=MongoModel)
def find_one(model_cls: Type[C], id: ID) -> C: ...
```

But no, Mypy treats them as two separate type variables (in other words, I can pass in an int and it doesn't catch it).

And `C` cannot be changed to `TypeVar("C", bound=MongoModel[ID])` either.


---

### Comment [900337917](https://github.com/python/typing/issues/548#issuecomment-900337917)

- **Author**: @MischaPanch
- **Date**: `2021-08-17T14:16:27Z`

Just to extend the list of people encountering it, I also ran into this. My example is similar to the ones above in spirit but aggravated by extraction of the generic class at runtime, which is possible since python 3.8. I am not sure whether it is officially recommended but I really like this mechanism :). Unfortunately, using it will very often require subscriptable TypeVars, like in the sketch below.

For simplicity I slightly changed the real signature. In real use cases I load the registry from a file and not from prepared list, so polymorphism makes a bit more sense there.

```python

class SettingsRegistry(Generic[TSettings], ABC):
    @classmethod
    def from_serialized_settings(cls: Type[TSettingsRegistry], serialized_settings: List[str]) -> TSettingsRegistry[TSettings]:
         settings_class = get_args(cls.__orig_bases__[0])[0]
         deserialized_settings = [settings_class.deserialize(setting) for setting in serialized_settings]
         return cls(deserialized_settings)
```

This way I can avoid code duplication but typing `TSettingsRegistry[TSettings]` is currently disallowed, of course.


---

### Comment [919555518](https://github.com/python/typing/issues/548#issuecomment-919555518)

- **Author**: @vnmabus
- **Date**: `2021-09-14T22:25:05Z`

Just another use for this: use the new `TypeGuard` to check the types of a collection:
```python
T = TypeVar("T", bound=Collection)
V = TypeVar("V")

def all_elements_type(
    collection: T[object],
    element_type: Type[V],
) -> TypeGuard[T[V]]:
    return all(isinstance(t, element_type) for t in collection)
```
This is very useful and currently not possible AFAIK.



---

### Comment [970287830](https://github.com/python/typing/issues/548#issuecomment-970287830)

- **Author**: @harahu
- **Date**: `2021-11-16T13:43:50Z`

Another potential use case example for HKTs:

https://toolz.readthedocs.io/en/latest/_modules/toolz/dicttoolz.html#valmap

I've made my own typed version of it, like so:

```py
K = TypeVar("K")
V = TypeVar("V")
M = TypeVar("M")


def valmap(
    func: Callable[[V], M],
    d: Mapping[K, V],
    factory: Type[MutableMapping[K, M]] = dict,
) -> MutableMapping[K, M]:
    rv = factory()
    rv.update(zip(d.keys(), map(func, d.values())))
    return rv

```

but in order to preserve type information, I would much rather want to type it as:

```py
K = TypeVar("K")
V = TypeVar("V")
M = TypeVar("M")
F = TypeVar("F", bound=MutableMapping)


def valmap(
    func: Callable[[V], M],
    d: Mapping[K, V],
    factory: Type[F] = dict,
) -> F[K, M]:
    rv = factory()
    rv.update(zip(d.keys(), map(func, d.values())))
    return rv
```

@gvanrossum makes the point that this isn't a commonly requested feature. I think that is correct to some extent, although the level of activity in this thread is making me slightly reconsider. I think it isn't commonly requested because it is a fairly advanced technique. But, I think my example, as well as many other examples in this thread are showing that fundamental library code in fairly prevalent use would be able to benefit from HKT in the sense that annotations would more accurately describe actual behavior. Often times this library code is maintained by skilled programmers that could leverage HKT if available. This is a benefit that then trickles down to the wider python ecosystem, including users that have never heard of HKT, but might leverage type checkers. You don't need to be a wizard to enjoy more accurate lib function call return types.



---

### Comment [986955643](https://github.com/python/typing/issues/548#issuecomment-986955643)

- **Author**: @xkortex
- **Date**: `2021-12-06T16:47:19Z`

@harahu - That is an excellent example. I think you described the situation perfectly. I've been in the exact same spot of wanting to write a transformation over a map-like collection, and resorting to some zany nested type signatures, when really all I wanted to do was turn some `D[K, V]` into a `F[K, M]` based on some provided type `F` and a transform `func(v: V) -> M`. 

HKT is a fairly sophisticated tool that many folks do not even know to reach for, but when you are in a situation which benefits it, many doors are unlocked. HKTs often greatly simplify the type signature, like in the example above. It shows up most frequently when you want to "transmute" some object (typically a container type) into a target (container) type, but you want the internal types to be preserved. 

This pattern does not seem to show up frequently when writing application code. Most software engineers probably do not need to know about it if they don't want to. However, when writing library code for others to consume, the pattern shows up quite a lot. Probably because it's a fairly high level abstraction, and that kind of abstraction lends itself to reuse.

In my opinion, HKTs would push the envelop for maintainability and ergonomics for maintainers of libraries that embrace the static typing discipline. In the same vein, it would not add any cognitive overhead for those looking to implement libraries, nor those looking to start writing libraries with static types. If anything, I think it has the potential to *shorten* the learning curve for those with medium experience with type systems (such as myself). I have definitely gotten myself into some really convoluted type signatures trying to express the transformation I wanted. Desire to use HKTs seems to scale with familiarity with type systems and abstracting over generics.


---

### Comment [993593190](https://github.com/python/typing/issues/548#issuecomment-993593190)

- **Author**: @3noch
- **Date**: `2021-12-14T14:24:23Z`

> I think it has the potential to shorten the learning curve for those with medium experience with type systems (such as myself).

💯 When you have generics but not HKT, you end up having to twist yourself into knots trying to express what would otherwise be simple. HKT is merely generics that works everywhere instead of generics that only works in some places.


---

### Comment [1000492498](https://github.com/python/typing/issues/548#issuecomment-1000492498)

- **Author**: @Tishka17
- **Date**: `2021-12-23T19:37:51Z`

I am having two similar protocols:
```python
class A(Protocol):
   def foo(self)-> int:...
   def bar(self)-> bool:...

class AsyncA(Protocol):
   def foo(self)-> Awaitable[int]:...
   def bar(self)-> Awaitable[bool]:...
```

Then only difference is that in second case there are async functions. I would be glad to unite them using Generics. But of cause this does not work:

```python
AT = TypeVar("AT", Union, Awaitable)


class A(Protocol[AT]):
    def foo(self) -> AT[int]: ...
    def bar(self) -> AT[bool]: ...

```


---

### Comment [1003624963](https://github.com/python/typing/issues/548#issuecomment-1003624963)

- **Author**: @zzzeek
- **Date**: `2022-01-01T22:02:18Z`

hey folks, another ORM use case coming in here, this system is in fact what we would have used for sqlalchemy2-stubs had it existed to encapsulate our structure of ColumnElement[TypeEngine[_T]], but as it's not, SQLAlchemy 2.0's typing will likely do what the original sqlalchemy-stubs did which is consider it to be ColumnElement[_T].  this solves most of the practical problems at the expense of looking a little funny and breaking the hierarchy a bit.

references for me at:

https://github.com/python/typing/discussions/999  

https://github.com/sqlalchemy/sqlalchemy/issues/7519 


---

### Comment [1068008566](https://github.com/python/typing/issues/548#issuecomment-1068008566)

- **Author**: @jab
- **Date**: `2022-03-15T13:47:19Z`

I just found out about [the `Self` type](https://peps.python.org/pep-0673/) that was recently added to Python 3.11. Could that be extended to add support for higher-kinded types?
```python
import typing as t

KT = t.TypeVar('KT')
VT = t.TypeVar('VT')

class BidirectionalMapping(t.Mapping[KT, VT]):
    @property
    def inverse(self: t.Self[KT, VT]) -> t.Self[VT, KT]:
        ...
```
cc @JelleZijlstra @pradeep90 @Gobot1234 et al.


---

### Comment [1068078500](https://github.com/python/typing/issues/548#issuecomment-1068078500)

- **Author**: @mwchase
- **Date**: `2022-03-15T14:52:32Z`

Using parameters on Self is explicitly disallowed by the PEP, so that seems like a non-starter unless the justifications can be addressed.


---

### Comment [1068098796](https://github.com/python/typing/issues/548#issuecomment-1068098796)

- **Author**: @jab
- **Date**: `2022-03-15T15:09:09Z`

Thanks. If you're talking about the
> In such cases, we recommend using an explicit type for self

in the https://peps.python.org/pep-0673/#use-in-generic-classes section, this recommendation doesn't work for the use case here. Since no specific mention of higher-kinded types is mentioned in the PEP, perhaps this use case wasn't even in mind when the PEP was written?


---

### Comment [1068101292](https://github.com/python/typing/issues/548#issuecomment-1068101292)

- **Author**: @mwchase
- **Date**: `2022-03-15T15:11:03Z`

I meant
> Note that we reject using Self with type arguments, such as Self[int]. This is because it creates ambiguity about the type of the self parameter and introduces unnecessary complexity:


---

### Comment [1068101978](https://github.com/python/typing/issues/548#issuecomment-1068101978)

- **Author**: @Gobot1234
- **Date**: `2022-03-15T15:11:35Z`

> I just found out about [the `Self` type](https://peps.python.org/pep-0673/) that was recently added to Python 3.11. Could that be extended to add support for higher-kinded types?
> 
> ```python
> 
> import typing as t
> 
> 
> 
> KT = t.TypeVar('KT')
> 
> VT = t.TypeVar('VT')
> 
> 
> 
> class BidirectionalMapping(t.Mapping[KT, VT]):
> 
>     @property
> 
>     def inverse(self: t.Self[KT, VT]) -> t.Self[VT, KT]:
> 
>         ...
> 
> ```
> 
> cc @JelleZijlstra @pradeep90 @Gobot1234 et al.

Yes I would be in support of this, it was something I considered but as HKT wasn't/isn't a thing I didn't think it would be a good idea to include in the PEP


---

### Comment [1068234931](https://github.com/python/typing/issues/548#issuecomment-1068234931)

- **Author**: @pradeep90
- **Date**: `2022-03-15T17:06:32Z`

> I just found out about the Self type added recently added to Python 3.11.
Could that be extended to add support for higher-kinded types?

I'm strongly against this. We'd explicitly discussed such cases during the
PEP drafting and rejected it with:

> Note that we reject using Self with type arguments, such as Self[int].
This is because it creates ambiguity about the type of the self parameter
and introduces unnecessary complexity:
>
> -- https://peps.python.org/pep-0673/#use-in-generic-classes

The PEP also suggests using an explicit type for `self` in generic classes
where you want to do something with the generic type parameter:

> In such cases, we recommend using an explicit type for self:

class Container(Generic[T]):
    def foo(
        self: Container[T],
        other: Container[int],
        other2: Container[T]
    ) -> Container[str]: ...


In your case, it would look like:

class BidirectionalMapping(t.Mapping[KT, VT]):
    @property
    def inverse(self: BidirectionalMapping[KT, VT]) ->
BidirectionalMapping[VT, KT]:
        ...

def main() -> None:
    m: BidirectionalMapping[int, str]
    y = m.inverse
    reveal_type(y)  # => `BidirectionalMapping[str, int]`


On Tue, Mar 15, 2022 at 8:11 AM James Hilton-Balfe ***@***.***>
wrote:

> I just found out about the Self type <https://peps.python.org/pep-0673/>
> that was recently added to Python 3.11. Could that be extended to add
> support for higher-kinded types?
>
> import typing as t
>
>
> KT = t.TypeVar('KT')
> VT = t.TypeVar('VT')
>
>
> class BidirectionalMapping(t.Mapping[KT, VT]):
>
>     @property
>
>     def inverse(self: t.Self[KT, VT]) -> t.Self[VT, KT]:
>
>         ...
>
> cc @JelleZijlstra <https://github.com/JelleZijlstra> @pradeep90
> <https://github.com/pradeep90> @Gobot1234 <https://github.com/Gobot1234>
> et al.
>
> Yes I would be in support of this, it was something I considered but as
> HKT wasn't/isn't a thing I didn't think it would be a good idea to include
> in the PEP
>
> —
> Reply to this email directly, view it on GitHub
> <https://github.com/python/typing/issues/548#issuecomment-1068101978>, or
> unsubscribe
> <https://github.com/notifications/unsubscribe-auth/AAC6L67HMGL2U7IMJDPIDE3VACSDLANCNFSM4EYI34UQ>
> .
> Triage notifications on the go with GitHub Mobile for iOS
> <https://apps.apple.com/app/apple-store/id1477376905?ct=notification-email&mt=8&pt=524675>
> or Android
> <https://play.google.com/store/apps/details?id=com.github.android&referrer=utm_campaign%3Dnotification-email%26utm_medium%3Demail%26utm_source%3Dgithub>.
>
> You are receiving this because you were mentioned.Message ID:
> ***@***.***>
>


-- 
S Pradeep Kumar



---

### Comment [1068250930](https://github.com/python/typing/issues/548#issuecomment-1068250930)

- **Author**: @erictraut
- **Date**: `2022-03-15T17:23:46Z`

I agree with @pradeep90. I think this would create significant confusion and complexity. It would also deviate from the `Self` type in other languages.


---

### Comment [1068257265](https://github.com/python/typing/issues/548#issuecomment-1068257265)

- **Author**: @jab
- **Date**: `2022-03-15T17:30:33Z`

@pradeep90 writes:
> In your case, it would look like: ..

I think there might be a misunderstanding? I am [already doing what you proposed](https://github.com/jab/bidict/blob/62bc061bf67e6a48af4e95a89048632e4915e1ee/bidict/_abc.py#L37), and [it does not help with this issue](https://github.com/jab/bidict/blob/62bc061bf67e6a48af4e95a89048632e4915e1ee/bidict/_frozenbidict.py#L27-L31), as [I commented here previously](https://github.com/python/typing/issues/548#issuecomment-621195693).


---

### Comment [1068259110](https://github.com/python/typing/issues/548#issuecomment-1068259110)

- **Author**: @jab
- **Date**: `2022-03-15T17:32:21Z`

@erictraut writes:
> I agree with @pradeep90. I think this would create significant confusion and complexity. It would also deviate from the Self type in other languages.

Good to know, thank you. Do you have any ideas about how support for HKTs could be added in a way that would match other languages that already support them?


---

### Comment [1068269215](https://github.com/python/typing/issues/548#issuecomment-1068269215)

- **Author**: @pradeep90
- **Date**: `2022-03-15T17:41:59Z`

> @pradeep90 writes:
> 
> > In your case, it would look like: ..
> 
> I think there might be a misunderstanding? I am [already doing what you proposed](https://github.com/jab/bidict/blob/62bc061bf67e6a48af4e95a89048632e4915e1ee/bidict/_abc.py#L37), and [it does not help with this issue](https://github.com/jab/bidict/blob/62bc061bf67e6a48af4e95a89048632e4915e1ee/bidict/_frozenbidict.py#L27-L31), as [I commented here previously](https://github.com/python/typing/issues/548#issuecomment-621195693).

I hadn't read your earlier comment in the thread because I mistakenly assumed this was a fresh (typing-sig) thread.

The snippet I shared works in both Pyre and Mypy ([playground link](https://mypy-play.net/?mypy=latest&python=3.8&gist=4c180b825bea753074af1805379043ae)). The same goes for [your existing code](https://github.com/python/typing/issues/548), where the `self` is not annotated. 

If you're still having trouble, could you repro your case in a Mypy playground snippet?


---

### Comment [1068276820](https://github.com/python/typing/issues/548#issuecomment-1068276820)

- **Author**: @jab
- **Date**: `2022-03-15T17:48:42Z`

@pradeep90, please reread https://github.com/python/typing/issues/548#issuecomment-621195693. Your [playground link](https://mypy-play.net/?mypy=latest&python=3.8&gist=4c180b825bea753074af1805379043ae) does not exercise the functionality this is asking for. You haven't created a subclass of BidirectionalMapping. If you do, you will see that its inherited `inverse` undesirably returns a BidirectionalMapping, rather than an instance of the subclass.


---

### Comment [1068297441](https://github.com/python/typing/issues/548#issuecomment-1068297441)

- **Author**: @erictraut
- **Date**: `2022-03-15T18:06:44Z`

> Do you have any ideas about how support for HKTs could be added in a way that would match other languages that already support them?

I don't consider this an example of HKT. I think of `Self` as a type that is implicitly specialized with the type parameters of the class that encloses it. In your example, it's effectively bound to the type `BidirectionalMapping[KT, VT]`. Specializing it a second time therefore doesn't make sense, any more than it would make sense to re-specialize `list[int]`.


---

### Comment [1068313578](https://github.com/python/typing/issues/548#issuecomment-1068313578)

- **Author**: @jab
- **Date**: `2022-03-15T18:20:58Z`

What would you consider this, then, and should I open a separate issue for that once I know what to call it?


---

### Comment [1068315851](https://github.com/python/typing/issues/548#issuecomment-1068315851)

- **Author**: @pradeep90
- **Date**: `2022-03-15T18:23:00Z`

> You haven't created a subclass of BidirectionalMapping. If you do, you will see that its inherited `inverse` undesirably returns a BidirectionalMapping, rather than an instance of the subclass.

Guido's thoughtful [snippet](https://github.com/python/typing/issues/548#issuecomment-621571821) demonstrates what you were trying to get at and is the kind of repro I was asking for ([mypy playground](https://mypy-play.net/?mypy=latest&python=3.8&gist=e713b65264b61e98a4e603f141ad2be2), for any future readers trying to follow).

Yeah, this is one of the `self` cases where you'd need to add explicit stubs to the subclass methods, like you do in [`frozenbidict`](https://github.com/jab/bidict/blob/62bc061bf67e6a48af4e95a89048632e4915e1ee/bidict/_abc.py#L37). The exact same thing would occur for the generic `Container` example in the PEP: if we subclassed it, we would need to explicitly specify the subclass method's return type.

If we eventually get HKTs in the type system, that would have to be the solution here rather than co-opting the `Self` type. As @erictraut mentioned, `Self` is intended to be a simple replacement for a handwritten `TypeVar` and helps with almost all cases except the ones in generic classes where we need to tinker with the generic type parameters (as in the PEP's `Container` or your `BidirectionalMapping`).


---

### Comment [1068345349](https://github.com/python/typing/issues/548#issuecomment-1068345349)

- **Author**: @Gobot1234
- **Date**: `2022-03-15T18:54:16Z`

Maybe I'm missing something but if Self is meant to act like a shorthand for a bound TypeVar so surely the example which could be written as:
```py
SelfBidirectionalMapping = TypeVar("SelfBidirectionalMapping", bound=BidirectionalMapping[Any, Any])

class BidirectionalMapping(t.Mapping[KT, VT]):
    @property
    def inverse(self: SelfBidirectionalMapping[KT, VT]) -> SelfBidirectionalMapping[VT, KT]:
        ...


m: BidirectionalMapping[int, str]
y = m.inverse
reveal_type(y)  # => `BidirectionalMapping[str, int]`
```
Could be written using Self as shown in https://github.com/python/typing/issues/548#issuecomment-1068008566?


---

### Comment [1069694263](https://github.com/python/typing/issues/548#issuecomment-1069694263)

- **Author**: @jab
- **Date**: `2022-03-16T22:20:07Z`

Thanks @Gobot1234, but the `SelfBidirectionalMapping[KT, VT]` in that snippet (and similarly the `SelfBidirectionalMapping[VT, KT]`) cause `error: Type variable "SelfBidirectionalMapping" used with arguments`.

In any case, I don't think this is getting the job done.

Here's a more complete example based on your snippet, demonstrating that we do need HKTs (or some other not-yet-implemented feature) to make this use case work:

```python
from collections import UserDict
import typing as t


KT = t.TypeVar('KT')
VT = t.TypeVar('VT')

SelfBidirectionalMapping = t.TypeVar("SelfBidirectionalMapping", bound=BidirectionalMapping[t.Any, t.Any])


class BidirectionalMapping(t.Mapping[KT, VT]):
    @property
    def inverse(self: SelfBidirectionalMapping[KT, VT]) -> SelfBidirectionalMapping[VT, KT]:  # results in "error: Type variable "SelfBidirectionalMapping" used with arguments"
        ...


class bidict(UserDict[KT, VT], BidirectionalMapping[KT, VT]):
    pass


b = bidict({'answer': 42})
reveal_type(b)  # correct: bidict[str, int]
reveal_type(b.inverse)  # wrong: bidict[str, int]  (should be: bidict[int, str])
```

mypy-play link here: https://mypy-play.net/?mypy=latest&python=3.7&gist=5272ebc066abb4b6b32df0a336c78b00&flags=strict


---

### Comment [1069695949](https://github.com/python/typing/issues/548#issuecomment-1069695949)

- **Author**: @Gobot1234
- **Date**: `2022-03-16T22:22:30Z`

> Thanks @Gobot1234, but the `SelfBidirectionalMapping[KT, VT]` in that snippet (and similarly the `SelfBidirectionalMapping[VT, KT]`) cause `error: Type variable "SelfBidirectionalMapping" used with arguments`.
> 
> 
> 
> In any case, I don't think this is getting the job done.
> 
> 
> 
> Here's a more complete example based on your snippet:
> 
> 
> 
> ```python
> 
> from collections import UserDict
> 
> import typing as t
> 
> 
> 
> 
> 
> KT = t.TypeVar('KT')
> 
> VT = t.TypeVar('VT')
> 
> 
> 
> SelfBidirectionalMapping = t.TypeVar("SelfBidirectionalMapping", bound=BidirectionalMapping[t.Any, t.Any])
> 
> 
> 
> 
> 
> class BidirectionalMapping(t.Mapping[KT, VT]):
> 
>     @property
> 
>     def inverse(self: SelfBidirectionalMapping[KT, VT]) -> SelfBidirectionalMapping[VT, KT]:  # results in "error: Type variable "SelfBidirectionalMapping" used with arguments"
> 
>         ...
> 
> 
> 
> 
> 
> class bidict(UserDict[KT, VT], BidirectionalMapping[KT, VT]):
> 
>     pass
> 
> 
> 
> 
> 
> b = bidict({'answer': 42})
> 
> reveal_type(b)  # correct: bidict[str, int]
> 
> reveal_type(b.inverse)  # wrong: bidict[str, int]  (should be: bidict[int, str])
> 
> ```
> 
> 
> 
> [mypy-play link here](https://mypy-play.net/?mypy=latest&python=3.7&gist=e713b65264b61e98a4e603f141ad2be2&flags=strict)

This is meant to use HKT is it not? The error (currently) is to be expected


---

### Comment [1071002445](https://github.com/python/typing/issues/548#issuecomment-1071002445)

- **Author**: @mwchase
- **Date**: `2022-03-17T15:49:28Z`

Going way back, I think there's a potential workaround for the Awaitable-or-None case, but it requires code reorganization because of the lack of higher-kinded types. Something like
```
# Assume Command[T] is some kind of hacky parametric newtype or container
class Redis:
    def get(self, *args) -> Command[str]:
        ...
        return Command[str](command)

    def set(self, *args) -> Command[None]:
        ...
        return Command[None](command)

    def exists(self, *args) -> Command[bool]:
        ...
        return Command[bool](command)

    # ... and many MANY more ...

class ConnectionExecutor:
    def execute(self, command: Command[T]) -> Coroutine[Any, Any, T]:
        return self.connection.execute(...)

class PipelineExecutor:
    def execute(self, command: Command[T]) -> None:
        self.pipeline.append(command)
```
And then you can have an `executor` variable and a `redis` variable, and instead of `redis.set(*args) # type: ???`, you have `executor.execute(redis.set(*args))`, which knows what the return type is because we've got a sensible value from the `Redis` object's method, passed into the `executor`, which has a known type.

(I don't know if it makes sense to still have the `Redis` class in that case, or to just have a module with a bunch of top-level functions.)

(Anyway, note that this means that the wrapper methods explicitly can't wrap multiple calls or anything like that, but writing methods like that is already broken under the original code, so...)

Assuming it still makes sense for all of those classes to exist, then the HKT issue can be made to re-manifest by saying "I'd rather have the `Redis` and `Executor` classes combined into one."
I tried to sketch out what typing that would look like, and it got so messy that I'm sure I was overcomplicating it somehow, so I'm going to stop for now.


---

### Comment [1079552637](https://github.com/python/typing/issues/548#issuecomment-1079552637)

- **Author**: @SimpleArt
- **Date**: `2022-03-26T01:32:44Z`

I just recently came across this issue myself and realized that there could be an extremely simple fix using [intersection types](https://github.com/python/typing/issues/213) assuming they would work with type variables.

Example:

```python
from collections import UserList
from typing import List, TypeVar

T = TypeVar("T")
ListType = TypeVar("ListType", bound=List)

def append(L: ListType & List[T], x: T) -> ListType & List[T]:
    L.append(x)
    return L

L: UserList[int] = append(UserList[int](), 0)  # Should pass, as it is both UserList and List[int].
```

In this case, `ListType & List[T]` is the desired behavior for `ListType[T]`, the HKT desired in this thread.

This would however require type intersections to support generics i.e. `UserList[int] == UserList & List[int]`.


---

### Comment [1079568920](https://github.com/python/typing/issues/548#issuecomment-1079568920)

- **Author**: @joelberkeley
- **Date**: `2022-03-26T02:22:19Z`

@SimpleArt that's neat and I can imagine that would work in some cases, but I don't believe it solves the full problem. For example, unless I'm mistaken, you can't use it in functor*
```python
class Functor(ABC):
    def map(self: F[A], f : Callable[[A], B]) -> F[B]:
        ...
```
because the type variable `F` can't be applied to type variables `A` or `B` in the way `List` can in your example.

*someone tell me if I've got functor wrong - i'm not clear what it looks like in python


---

### Comment [1079569591](https://github.com/python/typing/issues/548#issuecomment-1079569591)

- **Author**: @SimpleArt
- **Date**: `2022-03-26T02:24:26Z`

@joelberkeley It would, I'm suggesting `F[A]` in your example be interpreted as `F & F.bound[A]`, where `F.bound` is the bound for your type variable e.g. `TypeVar("F", bound=List)`.

In this case it looks like `F` is the previously mentioned `Self` type. Fully written out, your example would be:

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar

A = TypeVar("A")
B = TypeVar("B")
Self = TypeVar("Self", bound="Functor")
T = TypeVar("T")


class Functor(ABC, Generic[T]):

    @abstractmethod
    def map(self: Self & Functor[A], f: Callable[[A], B]) -> Self & Functor[B]:
        ...
```

`Self` ensures `functorB = functorA.map(f)` makes `functorB` retains the same subclass as `functorA`.

`Functor[A] -> Functor[B]` ensures `functorB = functorA.map(f)` makes `functorB` retains the correct type variable instead of just `Any`.


---

### Comment [1079580197](https://github.com/python/typing/issues/548#issuecomment-1079580197)

- **Author**: @joelberkeley
- **Date**: `2022-03-26T03:05:45Z`

`F` doesn't have a bound in my code, but maybe let's wait for someone else to chime in because I'm not very confident in my definition of `Functor` (specifically, whether `Functor` should be generic in `F`, the "container type" if you will).

What I do believe, however, is that `Functor` isn't generic in `T` (the "element type" if you will) so you wouldn't be able to write `Functor[A]`. Indeed, I think it's core to the definition of `Functor` that it's _not_ generic in `T`


---

### Comment [1079602897](https://github.com/python/typing/issues/548#issuecomment-1079602897)

- **Author**: @SimpleArt
- **Date**: `2022-03-26T04:46:54Z`

@joelberkeley Perhaps we are misunderstanding each other. The `self` parameter must* have type `Functor` in your example, that's how Python methods work. That means `Functor` must be a subtype of `F[A]`, which according to what you inherited that won't be the case 

Perhaps what you really wanted was another separate argument for the `F[A]`? Or like I suggested, it is `Functor` which should be `Generic`? Or maybe you meant `Functor[F[A]]`?


---

### Comment [1079668261](https://github.com/python/typing/issues/548#issuecomment-1079668261)

- **Author**: @joelberkeley
- **Date**: `2022-03-26T11:39:56Z`

I think what's confusing me is that I'm trying to inherit Functor in its container type, rather than make instances of it (which is the more usual approach). In that case, `Functor` is like
```python
class Functor(ABC, Generic[F]):
    def map(self, f : Callable[[A], B], xs : F[A]) -> F[B]:
        ...

class ListFunctor(Functor[List]):
    def map(self, f : Callable[[A], B], xs : List[A]) -> List[B]:
        return [f(x) for x in xs]

strs : List[str] = ListFunctor().map(str, [1, 2])
```
Hopefully that clears up the confusion.


---

### Comment [1079714821](https://github.com/python/typing/issues/548#issuecomment-1079714821)

- **Author**: @SimpleArt
- **Date**: `2022-03-26T15:21:15Z`

@joelberkeley Then this is what it would look like with my suggestion:

```python
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Callable, Generic, List, TypeVar

T = TypeVar("T")


class Kind1(Generic[T]):
    """A generic with 1 parameter."""
    pass


A = TypeVar("A")
B = TypeVar("B")
F = TypeVar("F", bound=Kind1)


class Functor(ABC, Generic[F]):

    @abstractmethod
    def map(self: Functor[F], f: Callable[[A], B], xs: F & Kind1[A]) -> F & Kind1[B]:
        ...
```

This ensures the following types should be preserved:

```python
def map(self: Functor[F], f: Callable, xs: F) -> F:

def map(self: Functor, f: Callable[[A], B], xs: Kind1[A]) -> Kind1[B]:
```


---

### Comment [1079724618](https://github.com/python/typing/issues/548#issuecomment-1079724618)

- **Author**: @joelberkeley
- **Date**: `2022-03-26T16:12:22Z`

I believe that by bounding `F` on `Kind1`, you're implicitly recreating the `List` example. For example, you can't do this with types you don't own, which don't subclass `Kind1`, including stdlib types. That _might_ be resolvable with a `Protocol` but you'll have other problems if you try to do that such as `Protocol`s requiring covariant type parameters. I don't believe it's appropriate to require covariance in a general functor.


---

### Comment [1131695643](https://github.com/python/typing/issues/548#issuecomment-1131695643)

- **Author**: @SimpleArt
- **Date**: `2022-05-19T13:34:28Z`

Interestingly, some linters such as `mypy` already treat `self` as an intersection of types. Here's a minimal example:

```python
from typing import Generic, TypeVar

Self = TypeVar("Self", bound="Parent")
T1 = TypeVar("T1")
T2 = TypeVar("T2")


class Parent(Generic[T1]):  # Binds `self: Parent[T1]` to methods implicitly.

    def add(self: Self, x: T1) -> Self:  # Binds `self: Self` tightly to subclasses.
        ...


class Child(Parent[T1], Generic[T1, T2]):
    ...


x = Child[int, str]()  # Child[int, str]
y = x.add(0)           # Passes, and `Child[int, str]` still.
z = x.add("abc")       # Fails, incompatible `A[int]` with `x: str`.
```

In this example, when doing `x.add`, `self` is implicitly bound as `Parent[int]` from the `Parent` class itself. It is also simultaneously bound as `Child[int, str]` via `Self`. In this way, we have two types being bound to `self` simultaneously.


---

### Comment [1193014095](https://github.com/python/typing/issues/548#issuecomment-1193014095)

- **Author**: @nekitdev
- **Date**: `2022-07-23T00:05:15Z`

I'm currently writing a PEP to propose HKTs with the `args` argument to the `TypeVar`. Any suggestions are welcomed!

Here's how a functor would look like:
```python
from typing import Callable, Protocol, TypeVar

F = TypeVar("F", bound="Functor[T]", args=1)

T = TypeVar("T", covariant=True)
U = TypeVar("U")


class Functor(Protocol[T]):
    def map(self: F[T], function: Callable[[T], U]) -> F[U]:
        ...
```


---

### Comment [1193015363](https://github.com/python/typing/issues/548#issuecomment-1193015363)

- **Author**: @nekitdev
- **Date**: `2022-07-23T00:09:41Z`

Following the `bidict` example, one could do:

```python
from collections import UserDict
from typing import Mapping, TypeVar

BM = TypeVar("BM", bound="BidirectionalMapping[K, V]", args=2)

K = TypeVar("K")
V = TypeVar("V")


class BidirectionalMapping(Mapping[K, V]):
    @property
    def inverse(self: BM[K, V]) -> BM[V, K]:
        ...


class bidict(UserDict[K, V], BidirectionalMapping[K, V]):
    ...


bd = bidict(value=42)

reveal_type(bd)  # bidict[str, int]

reveal_type(bd.inverse)  # bidict[int, str]
```


---

### Comment [1193016458](https://github.com/python/typing/issues/548#issuecomment-1193016458)

- **Author**: @nekitdev
- **Date**: `2022-07-23T00:13:42Z`

The `create` example mentioned by @sobolevn is a bit more difficult to express, though, since `T` is not bound to anything, therefore referring to its type constructor is not exactly trivial.


---

### Comment [1193017510](https://github.com/python/typing/issues/548#issuecomment-1193017510)

- **Author**: @nekitdev
- **Date**: `2022-07-23T00:16:59Z`

In general, any code that needs to be generic over types *and* type constructors needs *HKTs* in one way or another.

As the simplest example, the wrapping type:

```python
from typing import Callable, Generic, TypeVar

from attrs import frozen

W = TypeVar("W", bound="Wrap[T]", args=1)

T = TypeVar("T", covariant=True)
U = TypeVar("U")


@frozen()
class Wrap(Generic[T]):
    value: T

    def map(self: W[T], function: Callable[[T], U]) -> W[U]:
        return type(self)(function(self.value))
```


---

### Comment [1193017802](https://github.com/python/typing/issues/548#issuecomment-1193017802)

- **Author**: @nekitdev
- **Date**: `2022-07-23T00:17:56Z`

I'm pretty sure it's possible to run into issues related to how `__new__` is handled by type checkers, though, which might add onto the resulting complexity.


---

### Comment [1193031614](https://github.com/python/typing/issues/548#issuecomment-1193031614)

- **Author**: @erictraut
- **Date**: `2022-07-23T01:25:10Z`

It's not clear to me how this would compose with [PEP 695](https://peps.python.org/pep-0695/) if both were to be accepted. In particular, if the notion of defining TypeVars as global variables were deprecated, how would your proposal work? You will need to consider the scoping rules carefully.

It may be instructive to look at other languages that support HKTs. You'll notice that I did a survey of type parameter syntax for other languages as part of PEP 695 (see Appendix A). I think it would be useful to do a similar survey of other languages that support HKTs. To my knowledge, very few of them do. It would be interesting to understand why that's the case — and why you think this added level of complexity is justified in the Python type system when most languages have not gone this route. I've seen a few examples of where it might be useful, but they strike me as edge cases. I'd want to see evidence that such a feature would be useful to more than just a handful of users because it will not be easy to implement such a feature within the various Python type checkers.


---

### Comment [1193035079](https://github.com/python/typing/issues/548#issuecomment-1193035079)

- **Author**: @nekitdev
- **Date**: `2022-07-23T01:47:24Z`

Indeed, [PEP 695](https://peps.python.org/pep-0695) does make this feature much more complex to implement.


---

### Comment [1193113580](https://github.com/python/typing/issues/548#issuecomment-1193113580)

- **Author**: @joelberkeley
- **Date**: `2022-07-23T11:57:02Z`

@nekitdev given the similarity with scala's syntax in that PEP, you may find scala's syntax for higher-kinded types useful


---

### Comment [1193146075](https://github.com/python/typing/issues/548#issuecomment-1193146075)

- **Author**: @nekitdev
- **Date**: `2022-07-23T15:52:59Z`

IMO Scala's HKT syntax fits well with PEP 695, though, as Eric has mentioned, HKTs are rather complex to implement type-checker-wise.


---

### Comment [1193164312](https://github.com/python/typing/issues/548#issuecomment-1193164312)

- **Author**: @nekitdev
- **Date**: `2022-07-23T17:58:26Z`

Then the monad would look something like this:

```python
from typing import Callable, Protocol


class Functor[F[_]](Protocol):
    def map[T, U](self: F[T], function: Callable[[T], U]) -> F[U]:
        ...
```

@erictraut

EDIT: renamed to `Functor[T]`


---

### Comment [1193172389](https://github.com/python/typing/issues/548#issuecomment-1193172389)

- **Author**: @erictraut
- **Date**: `2022-07-23T18:54:37Z`

That syntax approach looks good to me. A variation that may be worth considering is to use `...` rather than `_`.


---

### Comment [1193175464](https://github.com/python/typing/issues/548#issuecomment-1193175464)

- **Author**: @nekitdev
- **Date**: `2022-07-23T19:17:18Z`

The `_` syntax is a bit more extensive than `...`; for example, `T[_, _]` is a HKT with two generic types.
This essentially would allow an arbitrary amount of generic types in HKTs.


---

### Comment [1193175964](https://github.com/python/typing/issues/548#issuecomment-1193175964)

- **Author**: @nekitdev
- **Date**: `2022-07-23T19:20:45Z`

I'm not fully sure how *implementing* the aforementioned `Functor` would look like. Open for discussion here, I guess.



---

### Comment [1193177501](https://github.com/python/typing/issues/548#issuecomment-1193177501)

- **Author**: @erictraut
- **Date**: `2022-07-23T19:32:52Z`

I was suggesting `T[..., ...]` for an HKT with two generic types. The character sequence `...` is already a defined token in Python that generally means "this is a stand-in for something that will be supplied elsewhere". For example, consider how it's used in a `Callable` type annotation or a `ParamSpec` specialization.

By contrast, the character `_` is not a dedicated token but an identifier, and it typically means "I don't care about the value of this identifier". PEP 634 did extend `_` to mean a wildcard pattern, so maybe it's OK to extend its meaning for this use case as well, but `...` strikes me as a closer fit in terms of established semantics.


---

### Comment [1193182391](https://github.com/python/typing/issues/548#issuecomment-1193182391)

- **Author**: @nekitdev
- **Date**: `2022-07-23T20:11:34Z`

Alright, I agree that `...` might be nicer (and cuter, for that matter). Back to implementing `Functor`, though:
```python
from attrs import frozen

@frozen()
class Option[O[...]](Functor[T]):
    value: Optional[T]

    def map[U](self: O[T], function: Callable[[T], U]) -> O[U]:
        value = self.value

        if value is None:
            return self

        return type(self)(function(value))  # preserve types, allowing to inherit from `Option[T]`
```

I feel like this should make sense here.


---

### Comment [1193186922](https://github.com/python/typing/issues/548#issuecomment-1193186922)

- **Author**: @joelberkeley
- **Date**: `2022-07-23T20:51:55Z`

That's an interesting problem: Scala and Haskell don't have subclassing of concrete classes. Do any languages have that and higher-kinded types? What about higher-kinded types and covariance? Maybe it's no different to interface inheritance with HKTs

BTW I don't think you'd parametrize over `O[...]` in `Option`. There would be a number of problems with that, e.g. how would you type hint it (`Option[Option[Option ad infinitum], int]`)? You might drop `O[...]` in that line and use [`Self`](https://peps.python.org/pep-0673/) but then given that might you use `Self` in `Functor`? How does `Self` fit into all this?

**also are PEP details on topic for this thread?** I don't want to spam people


---

### Comment [1193187227](https://github.com/python/typing/issues/548#issuecomment-1193187227)

- **Author**: @nekitdev
- **Date**: `2022-07-23T20:54:18Z`

On that idea, we could throw things away all together and allow parametrizing `Self` instead.


---

### Comment [1193187528](https://github.com/python/typing/issues/548#issuecomment-1193187528)

- **Author**: @nekitdev
- **Date**: `2022-07-23T20:57:09Z`

For instance, the Functor would be as follows:

```python
class Functor[T](Protocol):
    def map[U](self, function: Callable[[T], U]) -> Self[U]:
        ...


@frozen()
class Option(Functor[T]):
    value: Optional[T] = None

    def map[U](self, function: Callable[[T], U]) -> Self[U]:
        value = self.value

        if value is None:
            return self

        return type(self)(value)
```


---

### Comment [1193187685](https://github.com/python/typing/issues/548#issuecomment-1193187685)

- **Author**: @Gobot1234
- **Date**: `2022-07-23T20:58:37Z`

I think being able to parameterise Self only solves  part of the problem, it would still leave functions like all untypeable 


---

### Comment [1193187803](https://github.com/python/typing/issues/548#issuecomment-1193187803)

- **Author**: @nekitdev
- **Date**: `2022-07-23T20:59:56Z`

Could you by any chance give an example?


---

### Comment [1193189442](https://github.com/python/typing/issues/548#issuecomment-1193189442)

- **Author**: @joelberkeley
- **Date**: `2022-07-23T21:14:31Z`

Anywhere `Self` isn't defined, like a free function
```python
def map[F[...]: Functor, A, B](x: F[A], f: Callable[[A], B]) -> F[B]:
    return x.map(f)
```


---

### Comment [1193189542](https://github.com/python/typing/issues/548#issuecomment-1193189542)

- **Author**: @Gobot1234
- **Date**: `2022-07-23T21:15:35Z`

So I was thinking this would be useful to rewrite all to look like
```py
class AlwaysFalsey(Protocol):
    def __bool__(self) -> Literal[False]: ...

I = TypeVar("I", bound=Iterable[T])
def all(x: I[T | AlwaysFalsey]) -> TypeGuard[I[T]]: ...
```
I think there are more examples where having this in functions is useful, so if you were going to go the effort of allowing Self to be subscripted (which in most type checkers is equivalent to a bound TypeVar) I don't see the point in not adding this.


---

### Comment [1193189772](https://github.com/python/typing/issues/548#issuecomment-1193189772)

- **Author**: @nekitdev
- **Date**: `2022-07-23T21:17:31Z`

Hm, indeed, if we want to bring the full power of HKTs, we can't limit it so these examples won't work.


---

### Comment [1193192920](https://github.com/python/typing/issues/548#issuecomment-1193192920)

- **Author**: @nekitdev
- **Date**: `2022-07-23T21:46:46Z`

The ultimate solution I can think of is parametrizing bounded `TypeVar`s, even though it doesn't exactly go nicely with [PEP 695](https://peps.python.org/pep-0695)'s attitude.


---

### Comment [1193287380](https://github.com/python/typing/issues/548#issuecomment-1193287380)

- **Author**: @nekitdev
- **Date**: `2022-07-24T10:14:32Z`

So the syntax would be something like

```python
type Unary[T, U] = Callable[[T], U]


def map_magical[I: Iterable[T], T, U](function: Unary[T, U], iterable: I[T]) -> I[U]:
    return type(iterable)(map(function, iterable))


# NOTE: type checkers would need to verify that
# type(instance)(...) gives an actual new instance

array = map_magical(str, [1, 2, 3])  # inferred `list[str]`
```

@erictraut what do you think?


---

### Comment [1193311903](https://github.com/python/typing/issues/548#issuecomment-1193311903)

- **Author**: @johnynek
- **Date**: `2022-07-24T12:47:49Z`

> That's an interesting problem: Scala and Haskell don't have subclassing of concrete classes. Do any languages have that and higher-kinded types? What about higher-kinded types and covariance? Maybe it's no different to interface inheritance with HKTs

Just a note: Scala *does* permit subclasses of concrete classes.


---

### Comment [1193340975](https://github.com/python/typing/issues/548#issuecomment-1193340975)

- **Author**: @erictraut
- **Date**: `2022-07-24T15:31:56Z`

That syntax looks reasonable. The approach wouldn't work with the current (prototype) implementation of PEP 695 because the compiler constructs the TypeVars for a generic class, function or type alias prior to evaluating any expressions that use those TypeVars. In your example, the upper bound expression for TypeVar `I` references TypeVar `T`, which hasn't yet been allocated. If we wanted to support this, the compiler would need to allocate all of the TypeVars prior to evaluating their upper bound expression, then bind the objects to their corresponding names, and then evaluate their bound expressions and "inject" the result into the pre-constructed TypeVar objects. A bit messy, but doable.


---

### Comment [1193341638](https://github.com/python/typing/issues/548#issuecomment-1193341638)

- **Author**: @nekitdev
- **Date**: `2022-07-24T15:34:49Z`

I see, if we want to keep the allocation simpler, perhaps the following order could be required: 

```python
[T, I[T], U]
```

(still, this will probably introduce some additional things needed for the compiler to do)

Allocating all of them is also an option, which imo is a bit closer to several-step compilers, in some sense.

By the way, would this feature need its own PEP or could 695 introduce it as well?


---

### Comment [1193343975](https://github.com/python/typing/issues/548#issuecomment-1193343975)

- **Author**: @erictraut
- **Date**: `2022-07-24T15:44:22Z`

HKT support would definitely require its own PEP. It shouldn't be tied to PEP 695 other than to make sure that the two compose and there's a plan for how they work together if both are accepted. HKT support will require significant spec'ing, refining, socializing, and prototyping.


---

### Comment [1193344598](https://github.com/python/typing/issues/548#issuecomment-1193344598)

- **Author**: @nekitdev
- **Date**: `2022-07-24T15:47:42Z`

I'm open to work on such a PEP, but it definitely needs lots of discussions on its specification and implementation. Honestly, 696 seems like a nice number for it, either way! :)



---

### Comment [1193344860](https://github.com/python/typing/issues/548#issuecomment-1193344860)

- **Author**: @Gobot1234
- **Date**: `2022-07-24T15:49:06Z`

> I'm open to work on such a PEP, but it definitely needs lots of discussions on its specification and implementation. Honestly, 696 seems like a nice number for it, either way! :)
> 

696 is already taken by yours truly 😉 


---

### Comment [1193345123](https://github.com/python/typing/issues/548#issuecomment-1193345123)

- **Author**: @JelleZijlstra
- **Date**: `2022-07-24T15:50:24Z`

Right, 696 is going to be typevar defaults. I may be willing to sponsor a PEP for HKT, but given the complexity of the feature I'd like to see a prototype in a major type checker first, as well as a well-specified draft PEP.


---

### Comment [1193345790](https://github.com/python/typing/issues/548#issuecomment-1193345790)

- **Author**: @nekitdev
- **Date**: `2022-07-24T15:53:39Z`

Alright, I'm going to work on the PEP along with the implementation in [mypy](https://github.com/python/mypy) (though contributors are definitely welcome, haha) type checker.


---

### Comment [1193346153](https://github.com/python/typing/issues/548#issuecomment-1193346153)

- **Author**: @AlexWaygood
- **Date**: `2022-07-24T15:55:23Z`

I'd be happy to help co-write or proofread a HKT PEP. It's a feature I'm quite interested in.

I agree with the other voices in this thread, however, that this would be a significant new feature with a high degree of complexity, that we'd need to take a large degree of care over.


---

### Comment [1193348994](https://github.com/python/typing/issues/548#issuecomment-1193348994)

- **Author**: @nekitdev
- **Date**: `2022-07-24T16:09:11Z`

Okay, I'm going to fork [peps](https://github.com/python/peps) repository and add anyone willing to participate as contributors. For discussions, we can either use GitHub Discussions or, alternatively, one can contact me on Discord at `nekitdev#3556` ([link](https://nekit.dev/discord) to my server in case my name changes).


---

### Comment [1194129519](https://github.com/python/typing/issues/548#issuecomment-1194129519)

- **Author**: @jab
- **Date**: `2022-07-25T14:32:24Z`

Thank you @nekitdev, @AlexWaygood, @JelleZijlstra, @erictraut, et al., this is exciting progress! If the bidict example should make it into the PEP as one of the motivating examples and there's anything I can do to help with that, please don't hesitate to let me know. And likewise let me know if there's anything I can do to help with testing any mypy or pyright reference implementations of this against a version of bidict that makes use of the new feature.


---

### Comment [1341891543](https://github.com/python/typing/issues/548#issuecomment-1341891543)

- **Author**: @mscuthbert
- **Date**: `2022-12-08T02:25:58Z`

It looks like the work on the [new PEP](https://github.com/python/peps/compare/main...nekitdev:peps:main) has gotten a little stalled?  

Just to give yet another example, [music21](https://github.com/cuthbertLab/music21)--the most used library for processing musical scores--has both a number (n) of different ways of iterating across musical scores (parts first, position first, etc.) all of which are subclasses of the main StreamIterator class and use the same iter method, and then a number (m) of different ways of filtering which objects are returned (notes only, metadata only, custom classes, etc.) almost all of which all subclasses of the same StreamFilter class and use the same filter function.  As I've been working to extensively type the library, it means that I've had to go from 2 methods that work well together to min(m, n) functions to get the correct typing.  (To make matters worse, there are 3 `@overload` versions of each method).  The lack of HKT is preventing me from wanting to implement new iteration and filtering methods in the next version.  It would be great to get something like the `args=1` syntax working together with the PEP695 proposals.  Happy to help with the writing, though most implementation details might be beyond my understanding of the corner-cases of Functor world.


---

### Comment [1344588738](https://github.com/python/typing/issues/548#issuecomment-1344588738)

- **Author**: @nekitdev
- **Date**: `2022-12-09T17:47:34Z`

The new PEP was indeed stalled for a while. I'll try to work on it more in the future, though I'm quite busy with my university atm. Thanks for providing another example, though! Will definitely consider adding it to the PEP.


---

### Comment [1345258154](https://github.com/python/typing/issues/548#issuecomment-1345258154)

- **Author**: @nekitdev
- **Date**: `2022-12-10T12:49:48Z`

So, just to be sure, below is what syntax I'm currently planning.

In classes (and their methods), *without* PEP 695:

```python
from typing import Callable, Generic, TypeVar

from attrs import frozen

T = TypeVar("T", covariant=True)
U = TypeVar("U")


@frozen()
class Option(Generic[T]):
    value: T

    def map(self: Self[T], function: Callable[[T], U]) -> Self[U]:
        return type(self)(function(self.value))
```

In functions, *without* PEP 695:

```python
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
U = TypeVar("U")

I = TypeVar("I", bound=Iterable[T], args=1)


def map_iterable(function: Callable[[T], U], iterable: I[T]) -> I[U]:
    return type(iterable)(map(function, iterable))
```

In classes (and their methods), *with* PEP 695:

```python
from attrs import frozen

type Unary[T, U] = Callable[[T], U]  # extra funky!

@frozen()
class Option[T]:
    value: T

    def map[U](self: Self[T], function: Unary[T, U]) -> Self[U]:
        return type(self)(function(self.value))
```

In functions, *with* PEP 695:

```python
type Unary[T, U] = Callable[[T], U]


def map_iterable[I: Iterable[T], T, U](function: Unary[T, U], iterable: I[T]) -> I[U]:
    return type(iterable)(map(function, iterable))
```

[PEP 695](https://peps.python.org/pep-0695) authors may need to consider implementing functionality
that would count the number of type arguments (`args`) based on the definition, for instance:

| `type`           | `args` |
|------------------|--------|
| `Iterable[T]`    | `1`    |
| `Dict[Q, T]`     | `2`    |
| `Tuple[T, U, V]` | `3`    |

It is worth noting that that definitions like `Dict[Q]` should be rejected by type checkers because of missing arguments.

Also there should be a change in how type checkers treat generics in expressions like `type(item)(...)`.


---

### Comment [1345455410](https://github.com/python/typing/issues/548#issuecomment-1345455410)

- **Author**: @mscuthbert
- **Date**: `2022-12-11T04:36:49Z`

What is "Unary" signifying in this case? and is `attrs` necessary to explain the example (for those of us who don't use it, it seems to obfuscate rather than explain. -- does "classes with PEP 695" work just as well if written as:

```python
@dataclass
class Option[T]:
    value: T

    def map[U](self: Self[T], function: Callable[[T], U]) -> Self[U]:
        return type(self)(function(self.value))
```

I like this, but I can see the objection that Self already implies "Option[T]" so "Self[T]" looks like "Option[T][T]" what about considering something like this if objections are raised:

```python
@dataclass
class Option[T]:
    value: T

    def map[U](self: Self, function: Callable[[T], U]) -> HigherKind[Self][U]:  # or HigherKind[Self, [U]]
        return type(self)(function(self.value))
```

other terms could be NonGeneric[Self][U] (if the first syntax is allowed) or ChangedGeneric[Self, [U]] (for the second).   I sort of feel that the process of stripping and replacing the GenericType should be explicit.


---

### Comment [1345552370](https://github.com/python/typing/issues/548#issuecomment-1345552370)

- **Author**: @joelberkeley
- **Date**: `2022-12-11T13:17:11Z`

I agree about using `attrs`. Would much prefer keeping to the stdlib.

Can I also suggest avoiding calling classes (such as `type(self)(...)`) in the examples because I'm almost certain that's a very significant hole in Python's type system that could cause confusion when defining the PEP?

I'm interested in helping with the PEP but need to see how much time I have


---

### Comment [1347406592](https://github.com/python/typing/issues/548#issuecomment-1347406592)

- **Author**: @nekitdev
- **Date**: `2022-12-12T22:06:31Z`

I agree with skipping the `attrs` usage in favor of the standard library. I'm simply too used to the library :p
As for the `type(self)(...)`, it's arguably the reason the PEP exists — to note that we want to be generic over type constructors.


---

### Comment [1347557116](https://github.com/python/typing/issues/548#issuecomment-1347557116)

- **Author**: @joelberkeley
- **Date**: `2022-12-13T00:11:15Z`

> As for the `type(self)(...)`, it's arguably the reason the PEP exists

I don't follow. The signature of `type(self)(...)` is defined by the `__init__` method, which can be essentially anything. The "type contructor"-ness is the application of the class as a type-level thing to types e.g. `type -> type` or `Foo[int]`, rather than the application of the class as an object constructor `int -> Foo` or `Foo(1)`, or indeed `int -> bool -> str -> Foo` and `Foo(0, True, "")`.

The hole I'm referring to is (and I may get this example wrong first time as I'll try to use your example rather than how i'm used to presenting it)
```python
@dataclass
class Foo(Option[T]):
    bar: int
```
which in python typing is valid, but `map` but will `TypeError` due to an incorrect number of arguments. Where would the type checker raise an error there? My guess is it has to be at `type(self)(...)` because who knows what signature `type(self)` will have once subclassed.


---

### Comment [1347577379](https://github.com/python/typing/issues/548#issuecomment-1347577379)

- **Author**: @Gobot1234
- **Date**: `2022-12-13T00:34:56Z`

I'd like to share one of my use cases for HKT which I don't think has really been considered
```py
@dataclass
class Item[OwnerT: BaseUser]: 
    id: int
    owner: OwnerT

@dataclass
class Trade[ItemT: Item, OwnerT: BaseUser]:
    sending: Sequence[ItemT]  # from our inventory
    receiving: Sequence[ItemT]  # from their inventory
```
Item's are in a user's inventory and you can't send trades for items that are in another user's inventory. A common error that I see could be solved with HKT is swapping around the sending and receiving arguments and HKT could enforce at type checking time that you don't have this issue. The code would look something like
```py
@dataclass
class Trade[ItemT: Item, OwnerT: BaseUser]:
    sending: Sequence[ItemT[OurUser]]
    receiving: Sequence[ItemT[OtherUser]]
```
then using it
```py
bad_trade = Trade(receiving=our_inventory.items)  # error: list[Item[OurUser]] cannot be assigned to list[Item[OtherUser]]
```

> [PEP 695](https://peps.python.org/pep-0695) authors may need to consider implementing functionality that would count the number of type arguments (`args`) based on the definition, for instance:
> 
> `type`	`args`
> `Iterable[T]`	`1`
> `Dict[Q, T]`	`2`
> `Tuple[T, U, V]`	`3`
> It is worth noting that that definitions like `Dict[Q]` should be rejected by type checkers because of missing arguments.

Just chiming in here, I think this is a bad idea (for now) for multiple reasons. 
1. it would increase the complexity of an already very complex PEP.
2. PEP 696 would make Dict[Q] a valid subscription at runtime and it'd be perfectly valid at type checking time unless you enabled some form of missing type parameter check (which is normally gated behind strict mode).

Other than that I really like the syntax and can't wait for this to be implemented, keep up the good work :)





---

### Comment [1353709464](https://github.com/python/typing/issues/548#issuecomment-1353709464)

- **Author**: @schuelermine
- **Date**: `2022-12-15T21:08:14Z`

I would find this proposal very useful.


---

### Comment [1354254493](https://github.com/python/typing/issues/548#issuecomment-1354254493)

- **Author**: @parched
- **Date**: `2022-12-16T05:48:32Z`

The original comment mentions Scala and Haskell reference implementations, but what I really want is just generic bounds like even the mainstream Java
```java
public class A<T> {
	public T t;
};

public class B<R extends A<?>> {
	public R r;
};
```
and C# have
```csharp
public class A<T> {
	public T t;
};

public class B<R, S> where R : A<S> {
	public R r;
};
```




---

### Comment [1354451535](https://github.com/python/typing/issues/548#issuecomment-1354451535)

- **Author**: @joelberkeley
- **Date**: `2022-12-16T09:28:50Z`

I agree that would be useful, but I don't believe it's higher-kinded types. There are no typevars that take another typevar there. Your example is rather a limitation on how python does typevar bounds. It's similar to [this SO post of mine](https://stackoverflow.com/q/57590086/5986907).

What might be confusing here is that the title says "Higher-Kinded TypeVars", but the description says "aka type constructors, generic TypeVars". I don't think this is technically correct. Higher kinded types aren't the same as type constructors. Python already has type constructors e.g. `list`, a `type -> type`. A higher-kinded type is a type that abstracts over a type constructor. We'll need to be clear about this in the PEP


---

### Comment [1355608326](https://github.com/python/typing/issues/548#issuecomment-1355608326)

- **Author**: @parched
- **Date**: `2022-12-16T21:06:26Z`

Ok, would it be worth having a separate PEP just for generic bounds? It looks like most of the Mypy issues that link here are actually just asking for generic bounds not HKT. [This one also](https://github.com/python/typing/issues/1311). I wonder how many of the 👍 on this issue are just for generic bounds.


---

### Comment [1355830636](https://github.com/python/typing/issues/548#issuecomment-1355830636)

- **Author**: @schuelermine
- **Date**: `2022-12-16T23:41:20Z`

You linked my issue, so I’d like to chime in again: I believe my issue is a different thing than this issue, as stated by @joelberkeley. I also voiced my approval of this issue before. I want to make clear that this was not mistaken, I want both to be implemented.


---

### Comment [1502079936](https://github.com/python/typing/issues/548#issuecomment-1502079936)

- **Author**: @qexat
- **Date**: `2023-04-10T17:17:20Z`

It's been more than 5 years since this issue was opened. What is its current state? I'm very interested, because I've faced more than one situation where HKTs were required to properly annotate the code I've written. Thank you in advance to anyone who will enlighten me.


---

### Comment [1502472890](https://github.com/python/typing/issues/548#issuecomment-1502472890)

- **Author**: @Gobot1234
- **Date**: `2023-04-10T23:38:11Z`

> It's been more than 5 years since this issue was opened. What is its current state? I'm very interested, because I've faced more than one situation where HKTs were required to properly annotate the code I've written. Thank you in advance to anyone who will enlighten me.

If you want to help, you might be able to contribute to https://github.com/nekitdev/peps


---

### Comment [1505361914](https://github.com/python/typing/issues/548#issuecomment-1505361914)

- **Author**: @mscuthbert
- **Date**: `2023-04-12T14:17:40Z`

> If you want to help, you might be able to contribute to https://github.com/nekitdev/peps

Specifically the file there is pep-9999.rst



---

### Comment [1732369751](https://github.com/python/typing/issues/548#issuecomment-1732369751)

- **Author**: @Asaurus1
- **Date**: `2023-09-23T17:24:22Z`

> Ok, would it be worth having a separate PEP just for generic bounds? It looks like most of the Mypy issues that link here are actually just asking for generic bounds not HKT. [This one also](https://github.com/python/typing/issues/1311). I wonder how many of the 👍 on this issue are just for generic bounds.

+1 here for generic bounds. I am running into issues with a project right now that would be easily solved with them.


---

### Comment [1813823497](https://github.com/python/typing/issues/548#issuecomment-1813823497)

- **Author**: @vnmabus
- **Date**: `2023-11-16T05:42:48Z`

I just wanted to say that until this is fixed, it would be impossible to type any library that makes use of the [array API standard](https://data-apis.org/array-api/) and has functions that are generic not only on the array type, but also on the dtype or shape parameters. E.g.:

```python
def astype[A: ArrayProtocol, D: DTypeProtocol](array: A[Any], dtype: D) -> A[D]:
    ...
```
What I try to say is that this is not a marginal use case, and will likely become more ubiquitous as more array-related libraries start following the standard.




---

### Comment [1863626617](https://github.com/python/typing/issues/548#issuecomment-1863626617)

- **Author**: @smheidrich
- **Date**: `2023-12-19T23:49:04Z`

I don't know if everyone saw, but generic TypeVar bounds have a(nother?) dedicated issue at #1226 and have also been implemented in Mypy fork [basedmypy](https://github.com/KotlinIsland/basedmypy). Maybe some of the people who only need generic TypeVar bounds and not the full power of HKTs¹ want to get involved there.

¹ Roughly, as far as I understand it: When you only want to annotate some things as `T[U]` while referring to `U` by itself elsewhere in the same signature, but _don't_ need to have a different parametrization `T[W]` in it as well (`T`, `U` and `W` all being TypeVars and `T` having a generic bound).


---

### Comment [1865430716](https://github.com/python/typing/issues/548#issuecomment-1865430716)

- **Author**: @rianhunter
- **Date**: `2023-12-21T03:39:51Z`

+1 for this feature. I can do this easily in C++ or Haskell:

```Python

A = TypeVar('A')
class Baz(Protocol[A]):
  pass

B = TypeVar('B', bound=Baz[A]) # <- throws unbound typevar error here

class Foo[B]:
  def bar(self) -> B:
    ...
```

If there is another way to do this that's currently supported that would be great.


---

### Comment [1885852394](https://github.com/python/typing/issues/548#issuecomment-1885852394)

- **Author**: @omer54463
- **Date**: `2024-01-10T22:36:07Z`

According to PEP-695, which proposed the new (3.12) generics API:

> The specified constrained types must be concrete. An attempt to use a generic type should be flagged as an error by a type checker. This is consistent with the existing rules enforced by type checkers for a TypeVar constructor call.

Any idea why? Generic bound types seem absolutely logical (I even assumed it was possible before trying it and getting disappointed).
The reason it isn't supported yet might be relevant here.


---

### Comment [1885928288](https://github.com/python/typing/issues/548#issuecomment-1885928288)

- **Author**: @erictraut
- **Date**: `2024-01-10T23:38:16Z`

> Any idea why?

PEP 695 was intended to provide a new syntax for existing mainstream typing features. The PEP was already quite large and involved (with nearly a year of planning that went into it). It didn't make sense to introduce new orthogonal features as part of the PEP.

Almost all modern languages support generics, but very few support higher-kinded types. HKTs are an advanced (and somewhat esoteric) capability that can be useful in certain situations, but they add significant complexity to the type system.


---

### Comment [1886789287](https://github.com/python/typing/issues/548#issuecomment-1886789287)

- **Author**: @omer54463
- **Date**: `2024-01-11T10:17:11Z`

> Almost all modern languages support generics, but very few support higher-kinded types.

Correct me if I'm wrong, but the example by @rianhunter should be easily achievable in most languages that support generics.
Is it a simple, specific case of HKT? Because according to references to this issue from other issues, that's most of the demand.


---

### Comment [1887884856](https://github.com/python/typing/issues/548#issuecomment-1887884856)

- **Author**: @antonagestam
- **Date**: `2024-01-11T20:07:40Z`

@omer54463 I don't know what would be specific about it, but it's also hard to tell what the expectations are. If the expectation is for the return type of Foo.bar to somehow vary over A, it's not clear to me with the syntax given how it's expected to vary. In my opinion it's an incomplete example because it doesn't show what the expectations are on usage of these classes.

Perhaps it would be useful to instead provide an actual working piece of C++ to show the capability you mean to compare with?


---

### Comment [1890588872](https://github.com/python/typing/issues/548#issuecomment-1890588872)

- **Author**: @omer54463
- **Date**: `2024-01-13T16:42:33Z`

@antonagestam Sure!

Here is a simple C++ program to demonstrate the issue:

```c++
#include <concepts>

template <typename I, typename T>
concept Interface = requires(I interface) {
  { interface.interface_method() } -> std::same_as<T>;
};

template <typename T, Interface<T> I> class Container {
public:
  Container(I interface) : interface(interface) {}
  I &get() { return this->interface; }

private:
  I interface;
};

class Concrete {
public:
  Concrete() {}
  int interface_method() { return 0; }
  int non_interface_method() { return 0; }
};

int main(void) {
  auto container = Container<int, Concrete>(Concrete());
  container.get().interface_method();
  container.get().non_interface_method(); // Works!
  return 0;
}
```

The call to `non_interface_method` works because we don't just have `T = int` - we have `I = Counter<int>` too.
This way, the member's type, `Counter<int>`, is fully known.
This isn't possible in python:

```python
from typing import Generic, Protocol, TypeVar

T = TypeVar("T")

class Interface(Protocol[T]):
    def interface_method() -> T:
        raise NotImplementedError

T = TypeVar("T")

class Container(Generic[T]):
    interface: Interface[T]

    def __init__(self, interface: Interface[T]) -> None:
        self.interface = interface

    def get(self) -> Interface[T]:
        return self.interface

class Concrete:
    def interface_method() -> int:
        return 0

    def non_interface_method() -> int:
        return 0

def main() -> None:
    container = Container(Concrete())
    container.get().interface_method()
    container.get().non_interface_method()   # Unrecognized!

if __name__ == "__main__":
    main()
```

`container.get()` returns `Interface[int]`, and not the specific type that implements `Interface[int]`, so we don't have any methods except for the interface.
It should be possible if we allow something like this:

```python
...
T = TypeVar("T")
I = TypeVar("I", bound=Interface[T])

class Container(Generic[T, I[T]]):
    interface: I[T]
...
```



---

### Comment [1890593417](https://github.com/python/typing/issues/548#issuecomment-1890593417)

- **Author**: @omer54463
- **Date**: `2024-01-13T17:01:29Z`

In addition, even `Typevar("I", bound=Interface[int])` is unallowed!
This is a very weird restriction - there is nothing generic about `Interface[int]` - all of the parameters are resolved.


---

### Comment [1890792730](https://github.com/python/typing/issues/548#issuecomment-1890792730)

- **Author**: @antonagestam
- **Date**: `2024-01-13T23:24:26Z`

@omer54463 With some minor changes this code passes mypy: https://mypy-play.net/?mypy=latest&python=3.12&gist=e88f88086056aa61c8d8d2c3c0678d8a. Note that it respects the specialization in the TypeVar.




---

### Comment [1890802196](https://github.com/python/typing/issues/548#issuecomment-1890802196)

- **Author**: @omer54463
- **Date**: `2024-01-14T00:12:06Z`

@antonagestam Woah, it seems my second comment is incorrect. I had no idea.
I saw your comment and literally got out of bed to check it out.

Unfortunately, `TypeVar("I", bound=Interface[T])` or any similar trick I could think of still doesn't work.
For example:

```python
from typing import Generic, Protocol, TypeVar

T = TypeVar("T", covariant=True)


class Interface(Protocol[T]):
    def interface_method(self) -> T:
        raise NotImplementedError


I = TypeVar("I", bound=Interface[T])  # error: Type variable "example.T" is unbound


class Container(Generic[T, I]):
    interface: I

    def __init__(self, interface: I) -> None:
        self.interface = interface

    def get(self) -> I:
        return self.interface

    def interface_method(self) -> T:
        return self.interface.interface_method()


class Concrete:
    def interface_method(self) -> int:
        return 0


def main() -> None:
    # Works great! Everyone's happy!
    container_1 = Container[int, Concrete](Concrete())
    container_1.interface_method()  # -> int
    container_1.get().interface_method()  # -> int

    # WTF! T and I have nothing to do with eachother!
    container_2 = Container[str, Concrete](Concrete())
    container_2.interface_method()  # -> str
    container_2.get().interface_method()  # -> int


if __name__ == "__main__":
    main()
```

Is there any complicated reason for it to not be supported? Any HKT rabbit hole we must end up going down to solve all edge cases?


---

### Comment [1891554034](https://github.com/python/typing/issues/548#issuecomment-1891554034)

- **Author**: @sebastian-philipp
- **Date**: `2024-01-15T08:29:07Z`

@rianhunter , I think, we're close already: https://mypy-play.net/?mypy=latest&python=3.12&gist=e88f88086056aa61c8d8d2c3c0678d8a



---

### Comment [1892609221](https://github.com/python/typing/issues/548#issuecomment-1892609221)

- **Author**: @rianhunter
- **Date**: `2024-01-15T18:15:57Z`

> @rianhunter , I think, we're close already: https://mypy-play.net/?mypy=latest&python=3.12&gist=e88f88086056aa61c8d8d2c3c0678d8a

No, you can bind `Protocol[concrete_type]` to a type var but not `Protocol[type_var]`


---

### Comment [1892647812](https://github.com/python/typing/issues/548#issuecomment-1892647812)

- **Author**: @jorenham
- **Date**: `2024-01-15T18:55:04Z`

Like @sobolevn mentioned almost 4 years ago, the closest you can get to a solution, is by using the approach that's used in `python-returns`:

Their approach to e.g.

```python
from typing import TypeVar
from returns.interfaces.container import Container1

T = TypeVar('T', bound=Container1)

def all_to_str(arg: T[int]) -> T[str]:
    ...
```

is to wrap everythin in "containers" (i.e. monads, but don't say that out loud, monads must remain esoteric for some reason):

```python
>>> from returns.primitives.hkt import Kind1, kinded
>>> from returns.interfaces.container import ContainerN
>>> from typing import TypeVar

>>> T = TypeVar('T', bound=ContainerN)

>>> @kinded
... def to_str(container: Kind1[T, int]) -> Kind1[T, str]:
...     return container.map(str)
```

However, this requires a mypy plugin to work, so it almost surely will not work with e.g. pyright.

See https://returns.readthedocs.io/en/latest/pages/hkt.html for more info.


---

### Comment [1893241045](https://github.com/python/typing/issues/548#issuecomment-1893241045)

- **Author**: @omer54463
- **Date**: `2024-01-16T08:07:00Z`

> Like @sobolevn mentioned almost 4 years ago, the closest you can get to a solution, is by using the approach that's used in `python-returns`:

It would work. It's also pretty ugly and counterintuitive. I really don't want to introduce returns into an existing company's codebase out of fear of the termination of my employment.

I'm suggesting making the syntax I mentioned a supported feature - is this not an appropriate place for that?



---

### Comment [1893798566](https://github.com/python/typing/issues/548#issuecomment-1893798566)

- **Author**: @jorenham
- **Date**: `2024-01-16T14:00:21Z`

@omer54463 Perhaps I wasn't clear about this, but I meant to show that the currently best "solution" to HKT will probably require significant changes to your codebase, requires you to use mypy and a third-party mypy-plugin, and results in verbose and difficult to read code. 

The syntax you mentioned earlier uses `typing.TypeVar`, instead of the new [PEP 695](https://peps.python.org/pep-0695/) syntax.

I guess that the desireable HKT syntax would look like either

```python
from returns.interfaces.container import Container1

# explicit notation
def all_to_str[T[V]: Container1[V]](arg: T[int]) -> T[str]:
    ...

# implicit notation
def all_to_str[T: Container1](arg: T[int]) -> T[str]:
    ...
```

or some combination of the two.


---

### Comment [1897962303](https://github.com/python/typing/issues/548#issuecomment-1897962303)

- **Author**: @omer54463
- **Date**: `2024-01-18T07:47:24Z`

@jorenham I roughly agree about the syntax.
However, there is still a distinction I want to make:

Your intentions seem to be to simulate something like this:

```python
T = TypeVar("T")
V = TypeVar("V")

def f(value: T[V]):
    ...
```

This makes no sense to me.
T can be any type, not all types receive type arguments.
I am not saying this could not be checked and supported, but it's a much bigger feature.

However, look at this.

```python
T = TypeVar("T")

class MyProtocol(Protocol[T]):
    ...

P = TypeVar("P", bound=MyProtocol)

def f(value: P[T]):
    ...
```

It's trivial that P gets a generic parameter. It's not because we dictate that when using P, but because the bound type has to be generic.

Is P technically an HKT? I'm pretty sure it is. But it's a much simpler case.


---

### Comment [1898255372](https://github.com/python/typing/issues/548#issuecomment-1898255372)

- **Author**: @jorenham
- **Date**: `2024-01-18T10:58:24Z`

@omer54463 I don't know what you mean with the first example. It makes me suspect that you don't understand PEP 695, so let me "backport" my previous example into the pre- PEP 695 era:

```python
from typing import TypeVar
from returns.interfaces.container import Container1


V = TypeVar("V", covariant=True)

# implicit notation
T = TypeVar("T", bound=Container1)
# explicit notation
T = TypeVar("T", bound=Container1[V], params=[V])


def all_to_str(arg: T[int]) -> T[str]: ...
```

The explicit `TypeVar` syntax here, is just an illustrative example I came up with from the top of my head.

---

In your last example, `P` denotes the parameter that is bound to *some kind of higher type*, so I'd consider its use in `f: P[T] -> ?` as HKT.


---

### Comment [1898377873](https://github.com/python/typing/issues/548#issuecomment-1898377873)

- **Author**: @jorenham
- **Date**: `2024-01-18T12:20:57Z`

A slightly more involved, realistic example of what HKT could look like in Python:

```python
from collections.abc import Awaitable, Callable


type Maps1[V, R] = Callable[[V], R]

def map_async[V, R, T: Awaitable](fn: Maps1[V, R], aval: T[V]) -> T[R]: ...

# for example:
# map_async(str, asyncio.Task[int]) -> asyncio.Task[str]
```

This example made me realise that the "explicit notation" from [my earlier post](https://github.com/python/typing/issues/548#issuecomment-1893798566) isn't going to work.
I can think of two "explicit notations":

- `map_async[R, T: Awaitable[V]](fn: Maps1[V, R], aval: T[V]): T[R]` - `V` occurs in both `fn` and `aval`, but is bound to `V@Awaitable`
- `map_async[V, R, T: Awaitable[V]](fn: Maps1[V, R], aval: T[V]): T[R]` - `V` is bound to `V@Awaitable` and to itself, implying equivalence of `T[V]` and `T[R]`, but `V` and `R` need not be equivalent

Both cases are self-contractictory, making my earlier proposal for an "explicit notation" a bad idea.

This leaves the "implicit notation", i.e. which I used in this post's example (i.e. `map_async[V, R, T: Awaitable](fn: Maps1[V, R], aval: T[V]) -> T[R]`). 
As far as I can tell, it doesn't have any of the problems that the explicit variant has.
Additionally, it has the benefit that there is only one obvious to do it (and coincidentally, I'm dutch).



---

### Comment [1900638172](https://github.com/python/typing/issues/548#issuecomment-1900638172)

- **Author**: @omer54463
- **Date**: `2024-01-19T15:34:03Z`

We can support an explicit syntax similar to the ones you mentioned without contradictions.

1. If we have `[X, Y, T: Awaitable]`, we can use `T[X]`, `T[Y]`, and so on. Let's call this "implicit".
2. If we have `[X, T: Awaitable[X]]` we can use `T`, but `T[X]` makes no sense anymore. Let's call this "explicit".

The signature  of the function you gave would then be either:

1. `def map_async[V, R, A: Awaitable](fn: Maps1[V, R], aval: A[V]) -> A[R]: ...` - implicit, same Awaitable.
2. `def map_async[V, R, AV: Awaitable, AR: Awaitable](fn: Maps1[V, R], aval: AV[V]) -> AR[R]: ...` - implicit, different Awaitable.
3. `def map_async[V, R, AV: Awaitable[V], AR: Awaitable[R]](fn: Maps1[V, R], aval: AV) -> AR: ...` - explicit, different Awaitable.

Though I am not sure "explicit" is the right term here.


---

### Comment [1900965663](https://github.com/python/typing/issues/548#issuecomment-1900965663)

- **Author**: @jorenham
- **Date**: `2024-01-19T19:11:27Z`

@omer54463 Your 2nd and 3rd signature specifications with 4 type parameters are invalid.
To see why, consider the `map_async(str, asyncio.Task[int])` example:

- `Maps1[V, R]` matches `str: Any -> str`
  - `V` binds to `Any`
  - `R` binds to `str`
- `AV[V]` binds to `asyncio.Task[V]`
  - `V` binds to `int`, because and `int <: Any`
- `AR[R]` is narrowed to `AR[str]`
- `AR` cannout be bound

So a type checker has no way of inferring the type of `AR`, unless you consider `Awaitable` to be its default, in which case it will always return an `Awaitable[R]`, which defeats the purpose of HKT in this example.


---

### Comment [1935140071](https://github.com/python/typing/issues/548#issuecomment-1935140071)

- **Author**: @smheidrich
- **Date**: `2024-02-09T00:26:03Z`

The important points about the status of this feature and how to contribute have scrolled out of GitHub's very limited window of comments visible on page load by now, which makes them hard for newcomers to this issue to find. So here is a summary again:

- @JelleZijlstra [has indicated interest](https://github.com/python/typing/issues/548#issuecomment-1193345123) in sponsoring a PEP, conditional on a prototype implementation in a major type checker and a well-specified draft PEP.
- Drafting the PEP takes place in @nekitdev's [fork](https://github.com/nekitdev/peps) of the `peps` repo. The [**stub PEP draft**](https://github.com/nekitdev/peps/blob/main/pep-9999.rst) so far contains a few examples of the proposed syntax.
- That same repo's [**GitHub Discussions forum**](https://github.com/nekitdev/peps/discussions) forum has been [designated](https://github.com/python/typing/issues/548#issuecomment-1193348994) as the place to discuss the PEP (and presumably the prototype implementation?). Some limited further discussions have taken place there.
  - If you want to be notified of new discussion threads, I think you have to set the whole repo as "watched" in GitHub?

Maybe @tek or someone else who is allowed to edit it can put this in the original issue so new arrivals find it quickly?


---

### Comment [1935146772](https://github.com/python/typing/issues/548#issuecomment-1935146772)

- **Author**: @JelleZijlstra
- **Date**: `2024-02-09T00:34:19Z`

Good point, I'll put this summary in the top post.


---

### Comment [1979627037](https://github.com/python/typing/issues/548#issuecomment-1979627037)

- **Author**: @Badg
- **Date**: `2024-03-05T21:00:00Z`

> * Drafting the PEP takes place in @nekitdev's [fork](https://github.com/nekitdev/peps) of the `peps` repo. The [**stub PEP draft**](https://github.com/nekitdev/peps/blob/main/pep-9999.rst) so far contains a few examples of the proposed syntax.

I wanted to post this on the linked PEP draft, but I'm getting a 404. Did it maybe move? (cc: @nekitdev)

-----

At any rate, I'm pretty sure I have another use case. I'm currently writing an asset management system that supports the idea of presentation variants, and each presentation variant has a metadata dict. However, the exact format of the metadata dict is determined by the kind of one of the arguments to its constructor. More specifically, I've implemented multiple asset builder classes, which all inherit from a base ``Builder``, and may then themselves be subclassed further. Each of the ``Builder`` subclasses define their own required metadata keys, but the ``PresentationVariantInfo`` is generic with respect to the actual ``Builder`` subclass. Simplifying a lot, it looks something like this:

```python
class StaticNoopBuilderMetadata(TypedDict):
    static_renders: dict[ContentVariantInfo, str]


class StaticNoopBuilder[MD: StaticNoopBuilderMetadata](Builder):

    def build(self, metadata: MD) -> bytes:
        ...


@dataclass
class PresentationVariantInfo[B: Builder]:
    builder: B
    metadata: dict
```

However, what I really want is something like this:

```python
@dataclass
class PresentationVariantInfo[B: Builder]:
    builder: B
    metadata: B.MD
```

Where the type of the metadata can reference the kind of the nested generic B.

-----

Unnecessary details:

Actually, in my case, I actually need **both** HKT and an intersection type (cross ref [here](https://github.com/CarliJoy/intersection_examples/issues/40), though this is a different example I didn't include there). In reality, the AMS supports both a build step (always static for any given asset version, for example, reading a template file into memory) and a render step (actually rendering out the asset, for example, rendering a jinja template). Because both the builder **and** the renderer specify metadata keys, I really need the intersection of both of their typed dicts. So in that case it would look something like this:

```python
class Builder[MD]:
    ...


class Renderer[MD]:
    ...


class PresentationVariantInfo[B: Builder, R: Renderer]:
    builder: B
    renderer: R
    # The intersection of the MD type argument for both the builder and the
    # renderer
    metadata: B.MD & R.MD
```


---

### Comment [1979629811](https://github.com/python/typing/issues/548#issuecomment-1979629811)

- **Author**: @nekitdev
- **Date**: `2024-03-05T21:02:05Z`

Hey! Yeah, sorry, I messed up sync with the upstream so had to reclone. I'll push the draft shortly.
Edit: [here](https://github.com/nekitdev/peps/blob/main/peps/pep-9999.rst) is the updated link.


---

### Comment [1979684275](https://github.com/python/typing/issues/548#issuecomment-1979684275)

- **Author**: @Badg
- **Date**: `2024-03-05T21:41:35Z`

Awesome, thanks!

To be completely honest, theoretical typing discussions are... a bit too abstract for me at times. So I'm not 100% sure that my use case above is actually and example of HKT. But if it is, feel free to use it!


---

### Comment [2073989611](https://github.com/python/typing/issues/548#issuecomment-2073989611)

- **Author**: @purepani
- **Date**: `2024-04-24T04:12:27Z`

I think libraries like einops would also benefit greatly from this. It would be pretty useful to be able to get shape information both into and out of any sort of array manipulation function. 


---

### Comment [2332982180](https://github.com/python/typing/issues/548#issuecomment-2332982180)

- **Author**: @finite-state-machine
- **Date**: `2024-09-06T01:01:18Z`

I'm not sure if further motivating examples are useful, but here's a simple function, not involved in type checking, that I don't believe can be described today:

```python
# sketch -- not carefully checked

T = TypeVar('T')
C = TypeVar('C', bound='Collection[T]')

def filter_and_count_dups(c: C[T]) -> Tuple[C[T], Counter[T]]:
    '''copy any 'Collection' w/o duplicates, counting what's omitted

    Args:
        c: any collection of elements
    Returns:
        (c_wo_dups, dup_counts), where...
        c_wo_dups: a copy of 'c', with the 2nd and subsequent
            appearances of any given element omitted
        dup_counts: counts removed duplicates
    '''
    seen: Set[T] = set()
    ret_list: List[T] = []
    ret_counter = Counter[T]()
    for elem in c:
        if elem in seen:
            ret_counter[elem] += 1
        else:
            ret_list.append(elem)
            seen.add(elem)

    ret_wo_dups = type(c)(ret_list)
    return (ret_wo_dups, ret_counter)


r1 = filter_and_count_dups((1, 2, 4, 3, 4, 4, 2, 1))
reveal_type(r1) # ≈ Tuple[Tuple[int, ...], Counter[int]]
print(repr(r1)) # ≈ ((1, 2, 4, 3), Counter({4: 2, 2: 1, 1: 1}))

r2 = filter_and_count_dups(list('alphabet'))
reveal_type(r2) # ≈ Tuple[List[str], Counter[str]]
print(repr(r2)) # ≈ (['a', 'l', 'p', 'h', 'b', 'e', 't'], Counter({'a': 1}))
```



---

### Comment [2350956086](https://github.com/python/typing/issues/548#issuecomment-2350956086)

- **Author**: @nerodono
- **Date**: `2024-09-14T11:16:14Z`

One more use case, consider the following code:
```python
class Handler[I, O](Protocol):
    def __call__(self, input: I, /) -> O: ...

class Modify(Protocol):
    def modify[O](self, f: Callable[[Self], O], /) -> O: ...

# Mixing styles since idk how to properly express it in 695
M = TypeVar("M", bound="Modify")

class Ext[Inner]:
    inner: Inner

    def modify[O](self: Ext[M], f: Callable[[M], O], /) -> Ext[O]:
        return Ext(f(self.inner))
```

I can extend `Ext`, with something like:
```python
class MyExt[Inner](Ext[Inner]):
    def another_method(self) -> MyExt[SomeOtherType]:
        return self.modify(xxx)
```

However, since `Ext.modify` is defined to return `Ext[Inner]`, not `MyExt[Inner]`, my type will be erased and I'll lose all extended methods. To fix this, `Ext.modify` needs to be defined like that:
```python
class Ext[Inner]:
    def modify[O](self: Self[M], f: Callable[[M], O]) -> Self[O]:
        return type(self)(self.inner.modify(f))
```

I have encountered that limitation when writing syntactic sugar for my library for handlers. `Handler`s can be combined, and handlers can be specialized, like this:
```python
class Predicate[I](Handler[I, bool], Protocol):
    ...
```

Here, we specialize `Predicate` as `Handler` which returns boolean value, for this specialized version we could add some methods in `Ext`:
```python
class PredicateExt[P](Ext[P]):
    def and_[I](self: PredicateExt[Predicate[I]], rhs: Predicate[I]) -> PredicateExt[Predicate[I]]:
        return self.modify(lambda lhs: And(lhs, rhs))
```

... but there's no way to do that without triggering type-checker, unless we had HKTs



---

### Comment [2357252461](https://github.com/python/typing/issues/548#issuecomment-2357252461)

- **Author**: @jorenham
- **Date**: `2024-09-18T00:29:33Z`

I'm starting to think that by simply making `types.GenericAlias` generic, we can get HKT "for free".

With this, we could write some HKT function `f: (T[int]) -> T[str]` with `T: Sequence` as:

```python
from collections.abc import Sequence
from types import GenericAlias

def f[T: Sequence](x: GenericAlias[T, int], /) -> GenericAlias[T, str]: ...
```

<sub>*Note that type-checkers might complain about the missing type argument in `T: Sequence`, which I omitted for the sake of clarity*</sub>


---

So to be a little bit more specific, the generic `GenericAlias` could look something like 

```python
class GenericAlias[T, *Ps]:
    @property
    def __origin__(self) -> type[T]: ...
    @property
    def __args__(self) -> tuple[*Ps]: ...
    ...  # etc
```

<sub>*Note that because a variadic type-parameter like `*Ps` cannot be covariant (at the time of writing), this might not work out-of-the-box for all HKT use-cases.*</sub>

Through the `__class_getitem__` method of generic classes, you'd then have e.g. `Spam.__class_getitem__(T) -> GenericAlias[Spam, T]`, which is equivalent to `Spam[T]`.

---

But there's one big problem with this approach:

```python
>>> type(list[str])
<class 'types.GenericAlias'>
>>> class Spam[T]: ...
... 
>>> type(Spam[str])
<class 'typing._GenericAlias'>
```

There are two generic aliases!
... but this is probably not the right place to be discussing this, so I'll keep my rant short :)


---

### Comment [2464655082](https://github.com/python/typing/issues/548#issuecomment-2464655082)

- **Author**: @joaoe
- **Date**: `2024-11-08T12:35:41Z`

Hi.
I see many people with somewhat complex examples which are hard to read.
Some of the proposed syntaxes I see are convoluted and hard to work, and will require constantly peeking at the documentation and copy-paste the same code snippets repeatedly.

Here's the code example I have from my project

```
T_num = TypeVar("T_num", float, int, str)
T_seq = TypeVar("T_seq", list, tuple)

def my_fn(seq: T_seq[T_num]) -> T_seq[T_num]: ....
```
This obviously does not work. mypy requires `list, tuple` to be parametrized in the `T_seq` declaration, and mypy does not recognize `T_seq` as being a generic.

I'd suggest the syntax for the feature to be something as simple as
```
T_seq = TypeVar[T_num]("T_seq", list[T_num], tuple[T_num])
```

Cheers.





---

### Comment [2464696425](https://github.com/python/typing/issues/548#issuecomment-2464696425)

- **Author**: @jorenham
- **Date**: `2024-11-08T12:59:13Z`

> I see many people with somewhat complex examples which are hard to read.
> Some of the proposed syntaxes I see are convoluted and hard to work, and will require constantly peeking at the documentation and copy-paste the same code snippets repeatedly.

Can you be more specific?

> I'd suggest the syntax for the feature to be something as simple as
> 
> ```
> T_seq = TypeVar[T_num]("T_seq", list[T_num], tuple[T_num])
> ```

Since Python 3.12 the new PEP 695 generic syntax is preferred over `TypeVar`




---

### Comment [2506024243](https://github.com/python/typing/issues/548#issuecomment-2506024243)

- **Author**: @samvv
- **Date**: `2024-11-28T12:37:47Z`

Someone pointed me to this issue. I just crashed hard onto this one today. I am writing generic tree algorithms. I have: `IntervalTree` inherits from `AVLTree` inherits from `BinaryTree`. What I want:

```py
T = TypeVar('T')

# What every node should have in common
class BinaryNode(Protocol[T]): ...

# Represents the actual node that is used by e.g. AVLTree
N = TypeVar('N', bound=BinaryNode)

# Parameterized on the actual node that is used and the value of it
class BinaryTree(Generic[N[T], T]):
   def rotate_left(self, node: N[T]) -> None: ...
   def add(self, value: T) -> None: ...
```

However, `N[T]` isn't valid in MyPy. No matter what I try (I even tried to just use plain functions), I can't seem to eliminate the 'higher kindness' of this structure. There is no way to extract `T` out of `N`.

If anyone knows workarounds for this pattern I'd be happy to learn them.


---

### Comment [2506182795](https://github.com/python/typing/issues/548#issuecomment-2506182795)

- **Author**: @Matt-Ord
- **Date**: `2024-11-28T13:54:46Z`

> Someone pointed me to this issue. I just crashed hard onto this one today. I am writing generic tree algorithms. I have: `IntervalTree` inherits from `AVLTree` inherits from `BinaryTree`. What I want:
> 
> ```python
> T = TypeVar('T')
> 
> # What every node should have in common
> class BinaryNode(Protocol[T]): ...
> 
> # Represents the actual node that is used by e.g. AVLTree
> N = TypeVar('N', bound=BinaryNode)
> 
> # Parameterized on the actual node that is used and the value of it
> class BinaryTree(Generic[N[T], T]):
>    def rotate_left(self, node: N[T]) -> None: ...
>    def add(self, value: T) -> None: ...
> ```
> 
> However, `N[T]` isn't valid in MyPy. No matter what I try (I even tried to just use plain functions), I can't seem to eliminate the 'higher kindness' of this structure. There is no way to extract `T` out of `N`.
> 
> If anyone knows workarounds for this pattern I'd be happy to learn them.

I've been able to work around this issue using default type parameters in python 3.13. The idea is to have both a node and a T param like so

```python


# What every node should have in common
class BinaryNode[T]: ...



# Parameterized on the actual node that is used and the value of it
class BinaryTree[T, N: BinaryNode[Any] = BinaryNode[T]]:
   def rotate_left[_T, _N: BinaryNode[Any] = BinaryNode[_T]](self:BinaryTree[_T, _N], node: _N) -> None: ...
   def add(self, value: T) -> None: ...
```
Note that this is subtlety broken, as the bound on BinaryNode[T] is
not necessarily upheld, but it seems to work ok in practise

For a working example (applied to a similar array type):
https://github.com/Matt-Ord/slate/blob/main/slate/array/_array.py




---

### Comment [2515460255](https://github.com/python/typing/issues/548#issuecomment-2515460255)

- **Author**: @thomas-mckay
- **Date**: `2024-12-03T20:13:39Z`

I think I may have a case that might be related to this:
```python
class Language(Enum):
    ...

LanguageT = TypeVar('LanguageT', bound=Language)


class Params(Generic[LanguageT]):
    target_language: LanguageT

ParamsT = TypeVar('ParamsT', bound=Params)


class Tasks(Generic[LanguageT, ParamsT]):  # I'd like it to be Generic[LanguageT, ParamsT[LanguageT]]
    source_language: LanguageT
    params: list[ParamsT]  # I'd like it to be list[ParamsT[LanguageT]]
```

I then have several providers which all have their own `Language` Enum class (because each provider supports a different set of languages). Each provider also has their own params classes.

```python
class ProviderALanguage(Language):
    ...

class ProviderAParams(Params[ProviderALanguage]):
    ...


class ProviderBLanguage(Language):
    ...

class ProviderBParams(Params[ProviderBLanguage]):
    ...

```
Ideally I'd need the type-checker to catch bad cases of inheritance as well as  wrongful usage:

```python
class ProviderATasks(Tasks[ProviderALanguage, ProviderBParams]):
     ...


tasks = Tasks[ProviderALanguage, ProviderBParams](...)
```

Currently I don't see a way to do this, but I think this proposed feature would help. It's also possible I can't see the obvious, as I've been looking at this so long...


---

### Comment [2515587119](https://github.com/python/typing/issues/548#issuecomment-2515587119)

- **Author**: @jorenham
- **Date**: `2024-12-03T21:28:44Z`

> I think I may have a case that might be related to this:
> 
> ```python
> class Language(Enum):
>     ...
> 
> LanguageT = TypeVar('LanguageT', bound=Language)
> 
> 
> class Params(Generic[LanguageT]):
>     target_language: LanguageT
> 
> ParamsT = TypeVar('ParamsT', bound=Params)
> 
> 
> class Tasks(Generic[LanguageT, ParamsT]):  # I'd like it to be Generic[LanguageT, ParamsT[LanguageT]]
>     source_language: LanguageT
>     params: list[ParamsT]  # I'd like it to be list[ParamsT[LanguageT]]
> ```

The best you could currently do is (using Python 3.12 syntax, but this is also possible with `TypeVar`):

```pyi
class Language(Enum): ...

class Params[LanguageT: Language]:
    target_language: LanguageT

class Tasks[LanguageT: Language]:
    source_language: LanguageT
    params: list[Params[LanguageT]]
```

---

edit:

alternatively, you could also parametrize the entire params list like

```pyi
class Language(Enum): ...

class Params[LanguageT: Language]:
    target_language: LanguageT

class Tasks2[LanguageT: Language, ParamsListT: list[Params[Language]]]:
    source_language: LanguageT
    params: ParamsListT
```

this `Tasks2` is strictly more general than the `Tasks` in my earlier example, which you could "get back" by doing something like

```pyi
type Tasks[LanguageT: Language] = Tasks[LanguageT, list[Params[LanguageT]]]
```




---

### Comment [2517146007](https://github.com/python/typing/issues/548#issuecomment-2517146007)

- **Author**: @thomas-mckay
- **Date**: `2024-12-04T12:00:24Z`

> 
> The best you could currently do is (using Python 3.12 syntax, but this is also possible with `TypeVar`):
> 
> ```python
> class Language(Enum): ...
> 
> class Params[LanguageT: Language]:
>     target_language: LanguageT
> 
> class Tasks[LanguageT: Language]:
>     source_language: LanguageT
>     params: list[Params[LanguageT]]
> ```

I thought of that, but it doesn't work for me as I really need `Tasks` to be a `Generic` of `ParamsT`. I'm using Generics in the context of Pydantic and basically every single class in my code snippets, save for `Language`, is a `pydantic.BaseModel`. I left it out of the example out of simplicity but maybe I shouldn't have. Even without the Pydantic constraint, I lose code-completion on `Tasks.params[0]` (each implementation has their own attributes).

> edit:
> 
> alternatively, you could also parametrize the entire params list like
> 
> ```python
> class Language(Enum): ...
> 
> class Params[LanguageT: Language]:
>     target_language: LanguageT
> 
> class Tasks2[LanguageT: Language, ParamsListT: list[Params[Language]]]:
>     source_language: LanguageT
>     params: ParamsListT
> ```
>
> this `Tasks2` is strictly more general than the `Tasks` in my earlier example, which you could "get back" by doing something like
> ```python
> type Tasks[LanguageT: Language] = Tasks[LanguageT, list[Params[LanguageT]]]
> ```

This feels like a more convoluted way of writing the first example (maybe I'm wrong, though). The type-checker (and the code completion tools) still assume `Tasks.params[0]` is strictly `Params`. And I get the same problem with pydantic.

```python
t = Tasks[LangAImpl]()
t.params.append(ParamsAImpl())
t.params[0].  # any ParamsAImpl-specific attributes are not shown by code-completion tools
```

Thanks for trying to help. I'm trying to have it all, I know. I should have been more clear in that I can't get rid of the `ParamsT` generic-ity at the `Tasks` level and I'm trying to enforce a rule on the parametrization of `ParamsT` at the `Tasks` level (which is why I thought this proposed feature might be the solution). Otherwise, your examples would all work.


---

### Comment [2517306881](https://github.com/python/typing/issues/548#issuecomment-2517306881)

- **Author**: @jorenham
- **Date**: `2024-12-04T13:10:54Z`

> This feels like a more convoluted way of writing the first example (maybe I'm wrong, though). The type-checker (and the code completion tools) still assume `Tasks.params[0]` is strictly `Params`. And I get the same problem with pydantic.

Exactly; I'm not trying to say that it's a solution, but that without HKT, it's the best we can currently do 🤷🏻 


---

### Comment [2517513566](https://github.com/python/typing/issues/548#issuecomment-2517513566)

- **Author**: @joaoe
- **Date**: `2024-12-04T14:07:08Z`

> Since Python 3.12 the new PEP 695 generic syntax is preferred over TypeVar

Ok then, here's some extra syntax.

```python
def my_fn[T_elm: (int, float, str), T_seq: list[T_elm] | tuple[T_elm]](
    seq: T_seq[T_elm],
) -> T_seq[T_elm]:
    return seq
```
which nowadays fails
```
error: Name "T_elm" is not defined  [name-defined]
error: Type variable "T_seq" used with arguments  [valid-type]
error: Type variable "T_seq" used with arguments  [valid-type]
```
But this syntax is actually covered in [PEP 695](https://peps.python.org/pep-0695/)
```python
# The following generates no compiler error, but a type checker
# should generate an error because an upper bound type must be concrete,
# and ``Sequence[S]`` is generic. Future extensions to the type system may
# eliminate this limitation.
class ClassA[S, T: Sequence[S]]: ...

# The following generates no compiler error, because the bound for ``S``
# is lazily evaluated. However, type checkers should generate an error.
class ClassB[S: Sequence[T], T]: ...
```
So it's syntax that has been suggested but not yet supported or precised.

Or we could allow the syntax I showed above, where TypeVar can be subscripted like a generic.
```python
T_elm = TypeVar("T_elm", float, int, str)
T_seq = TypeVar[T_elm]("T_seq", list[T_elm], tuple[T_elm])
```





---

### Comment [2517560250](https://github.com/python/typing/issues/548#issuecomment-2517560250)

- **Author**: @jorenham
- **Date**: `2024-12-04T14:15:16Z`

> > Since Python 3.12 the new PEP 695 generic syntax is preferred over TypeVar
> 
> Ok then, here's some extra syntax.
> 
> ```python
> def my_fn[T_elm: (int, float, str), T_seq: list[T_elm] | tuple[T_elm]](
>     seq: T_seq[T_elm],
> ) -> T_seq[T_elm]:
>     return seq
> ```
> 
> which nowadays fails
> 
> ```
> error: Name "T_elm" is not defined  [name-defined]
> error: Type variable "T_seq" used with arguments  [valid-type]
> error: Type variable "T_seq" used with arguments  [valid-type]
> ```
> 
> But this syntax is actually covered in [PEP 695](https://peps.python.org/pep-0695/)
> 
> ```python
> # The following generates no compiler error, but a type checker
> # should generate an error because an upper bound type must be concrete,
> # and ``Sequence[S]`` is generic. Future extensions to the type system may
> # eliminate this limitation.
> class ClassA[S, T: Sequence[S]]: ...
> 
> # The following generates no compiler error, because the bound for ``S``
> # is lazily evaluated. However, type checkers should generate an error.
> class ClassB[S: Sequence[T], T]: ...
> ```
> 
> So it's syntax that has been suggested but not yet supported or precised.

I like this 👍🏻 

> Or we could allow the syntax I showed above, where TypeVar can be subscripted like a generic.
> 
> ```python
> T_elm = TypeVar("T_elm", float, int, str)
> T_seq = TypeVar[T_elm]("T_seq", list[T_elm], tuple[T_elm])
> ```

This is confusing when doing "meta-typing" of `TypeVar`, where you'd annotate `TypeVar("T", bound=A)` as e.g. `T: TypeVar[A]`. Even though this is all hypothetical, implementing such "meta-typing" in e.g. typeshed could potentially solve many open issues, one of them being Higher Kinded Typing itself, as I explained in https://github.com/python/typing/issues/548#issuecomment-2357252461


---

### Comment [2582744873](https://github.com/python/typing/issues/548#issuecomment-2582744873)

- **Author**: @vtgn
- **Date**: `2025-01-10T13:44:31Z`

Very useful feature, for a lot of cases!
I don't understand why Python couldn't do this, when Java, C#, and Javascript already do...
Yes we can apply workarounds (ex. checks in the constructor), but this is ugly because we need to give as args the classes used as the generic types.


---

### Comment [2582764209](https://github.com/python/typing/issues/548#issuecomment-2582764209)

- **Author**: @jorenham
- **Date**: `2025-01-10T13:54:44Z`

> Yes we can apply workarounds (ex. checks in the constructor), but this is ugly because we need to give as args the classes used as the generic types.

There are many cases where there are no complete workarounds.


---

### Comment [2582765820](https://github.com/python/typing/issues/548#issuecomment-2582765820)

- **Author**: @Pleket
- **Date**: `2025-01-10T13:55:39Z`

> Very useful feature, for a lot of cases! I don't understand why Python couldn't do this, when Java, C#, and Javascript already do... Yes we can apply workarounds (ex. checks in the constructor), but this is ugly because we need to give as args the classes used as the generic types.

From what I understood, generic typing has slowly been introduced but not yet implemented at the higher-kindedness level due to the aim of keeping Python updates and source code rather simple. The required type inference to support generic types at this level has a couple of edge cases (or simply cases, since they are not rare) that would be untypable. An example (in OCaml) given by the author of Lightweight Higher Kinded Polymorphism can be found here: https://discuss.ocaml.org/t/higher-kinded-polymorphism/2192/5

There are a couple of solutions to this problem that mostly involve restricting the freedom in typing (Haskell has a newtype keyword that is reserved solely for potential higher-kinded polymorphism, and doesn't allow any aliases), but again, complicated. 

However, since I am now replying anyway, I would love to know if there is any recent progress toward expanding generic types in Python? It is hard to find any concrete attempts that are more recent than a couple of years. 


---

### Comment [2582779175](https://github.com/python/typing/issues/548#issuecomment-2582779175)

- **Author**: @jorenham
- **Date**: `2025-01-10T14:02:31Z`

> From what I understood, it has slowly been introduced but not yet implemented due to the aim of keeping Python updates and source code rather simple.

To avoid any confusion; I assume you're talking about other languages here? Python does not support HKT (not even a little bit).


---

### Comment [2582807911](https://github.com/python/typing/issues/548#issuecomment-2582807911)

- **Author**: @Pleket
- **Date**: `2025-01-10T14:14:18Z`

> > From what I understood, it has slowly been introduced but not yet implemented due to the aim of keeping Python updates and source code rather simple.
> 
> To avoid any confusion; I assume you're talking about other languages here? Python does not support HKT (not even a little bit).

I was talking about generic types, where HKTs are a type of genericness at a higher abstraction level. 


---

### Comment [2657261374](https://github.com/python/typing/issues/548#issuecomment-2657261374)

- **Author**: @Pleket
- **Date**: `2025-02-13T17:17:16Z`

> > Since Python 3.12 the new PEP 695 generic syntax is preferred over TypeVar
> 
> Ok then, here's some extra syntax.
> 
> def my_fn[T_elm: (int, float, str), T_seq: list[T_elm] | tuple[T_elm]](
>     seq: T_seq[T_elm],
> ) -> T_seq[T_elm]:
>     return seq
> which nowadays fails
> 
> ```
> error: Name "T_elm" is not defined  [name-defined]
> error: Type variable "T_seq" used with arguments  [valid-type]
> error: Type variable "T_seq" used with arguments  [valid-type]
> ```
> 
> But this syntax is actually covered in [PEP 695](https://peps.python.org/pep-0695/)
> 
> # The following generates no compiler error, but a type checker
> # should generate an error because an upper bound type must be concrete,
> # and ``Sequence[S]`` is generic. Future extensions to the type system may
> # eliminate this limitation.
> class ClassA[S, T: Sequence[S]]: ...
> 
> # The following generates no compiler error, because the bound for ``S``
> # is lazily evaluated. However, type checkers should generate an error.
> class ClassB[S: Sequence[T], T]: ...
> So it's syntax that has been suggested but not yet supported or precised.
> 
> Or we could allow the syntax I showed above, where TypeVar can be subscripted like a generic.
> 
> T_elm = TypeVar("T_elm", float, int, str)
> T_seq = TypeVar[T_elm]("T_seq", list[T_elm], tuple[T_elm])

I have recently been trying to recreate [Sobolevn's posts on emulating HKTs](https://sobolevn.me/2020/10/higher-kinded-types-in-python) and I have noticed that the new syntax is more limiting than the TypeVar syntax. Some things result in errors that would not even see the light of day with TypeVars, and vice versa. Most importantly, the missing attribute 'with_value' described in the [blog post](https://sobolevn.me/2020/10/higher-kinded-types-in-python) doesn't even get picked up with the new syntax, where it seems that something like 
```py
class HasValue[_ValueType]:
    ...

def apply_function[_ValueType, _NewValueType, _InstanceKind: 'HasValue'](
    instance: Kind[_InstanceKind, _NewValueType],
    callback: Callable[[_ValueType], _NewValueType],
) -> Kind[_InstanceKind, _NewValueType]: 
    ...
```
is not equivalent to 
```py
_ValueType = TypeVar('_ValueType')
_NewValueType = TypeVar('_NewValueType')
_InstanceKind = TypeVar('_InstanceKind', bound='HasValue')

class HasValue(Generic[_ValueType]):
    ...

def apply_function(
    instance: Kind[_InstanceKind, _ValueType],
    callback: Callable[[_ValueType], _NewValueType],
) -> Kind[_InstanceKind, _NewValueType]:
    ...
```

and similarly, I cannot find a way to express 
```py
_ValueType = TypeVar('_ValueType')

class Box(Generic[_ValueType], HasValue[_ValueType]):
    ...
```
in the new syntax besides an attempt like 
```py
class Box[_ValueType: HasValue[_ValueType]]
```
which is not allowed since '_ValueType is undefined' or 
```py
class Box[_ValueType: HasValue]:
```
which is also not allowed because HasValue has no input. 

Of course, these are examples involving HKTs that should not work in practice (without any 'hacks') anyway, but the fact that I get different errors with some important errors not even overlapping make it clear to me that they are by no means synonyms. Am I missing something? Or, should I stick to the old syntax after all? 


---

### Comment [2657415068](https://github.com/python/typing/issues/548#issuecomment-2657415068)

- **Author**: @erictraut
- **Date**: `2025-02-13T18:28:05Z`

I'm having a hard time following your post above because of formatting issues (perhaps you can edit it to fix that?).

The new syntax supports all of the functionality of the old syntax with the exception of explicitly-defined variance. I can't tell from your examples above whether variance is at play here. 

For example, the equivalent of
```python
_ValueType = TypeVar("_ValueType")
class Box(Generic[_ValueType], HasValue[_ValueType]): ...
```

is this:

```python
class Box[V](HasValue[V]): ...
```

The other examples above are not self-contained, which make them difficult to diagnose. If you'd like to provide some self-contained code samples that demonstrate an apparent difference in behavior between the old and new syntax, I'd be happy to take a look and offer suggestions.


---

### Comment [2657436254](https://github.com/python/typing/issues/548#issuecomment-2657436254)

- **Author**: @Pleket
- **Date**: `2025-02-13T18:38:48Z`

> I'm having a hard time following your post above because of formatting issues (perhaps you can edit it to fix that?).
> 
> The new syntax supports all of the functionality of the old syntax with the exception of explicitly-defined variance. I can't tell from your examples above whether variance is at play here.
> 
> For example, the equivalent of
> 
> _ValueType = TypeVar("_ValueType")
> class Box(Generic[_ValueType], HasValue[_ValueType]): ...
> is this:
> 
> class Box[V](HasValue[V]): ...
> The other examples above are not self-contained, which make them difficult to diagnose. If you'd like to provide some self-contained code samples that demonstrate an apparent difference in behavior between the old and new syntax, I'd be happy to take a look and offer suggestions.

You're right, I must've misunderstood the documentation. The bounds in documentation seemed limited to 
```py
class Box[V: SomeBound]
```
which was more problematic when SomeBound expects an input. 


---

### Comment [3019077864](https://github.com/python/typing/issues/548#issuecomment-3019077864)

- **Author**: @RobinSobczyk
- **Date**: `2025-06-30T13:04:35Z`

I don't know how well it's related, but I think HKT could be useful in a lot of situations to limit verbose. Mainly, I think it could be useful as well to introduce a `@lift` decorator along HKT to avoid redundant class definitions/verbose code that can just be resumed in lifting functions/class methods over a functor.

### Simplifying typing

I'm thinking mainly of the cases like
```Python
@overload
def fun1(inp : Functor_1[int]) -> Functor_1[str]:...
@overload
def fun1(inp : Functor_2[int]) -> Functor_2[str]:...
# [...]
@overload
def fun1(inp : Functor_n[int]) -> Functor_n[str]:...

def fun1(inp : int | Functor_1[int] | [...] | Functor_n[int]) -> str | Functor_1[str] | [...] | Functor_n[str]:
    ...
```
with most common cases being tuple/lists/arrays (and just iterables in fact).
This could be solved with a syntax like :
```Python
@lift [F : (Functor_1, [...], Functor_n)]
def fun1(inp : F[int]) -> F[str]: ...
```
with base typing being when `F` is identity mathematically speaking (i.e. no F), and this case should always be included.

This extends as well to classes, which can't really be overloaded :
```Python
class Converter:
    def __init__(self, data):
        self.data = data

    def convert(self):
        return fun1(self.data)

class IntConverter:
    def __init__(self, data : int): ...
    def convert(self) -> str : ...

class F1Converter:
    def __init__(self, data : Functor_1[int]): ...
    def convert(self) -> Functor_1[str] : ...

# [...]

class FnConverter:
    def __init__(self, data : Functor_n[int]): ...
    def convert(self) -> Functor_n[str] : ...
```
This could be summed up into
```Python
@lift [F : (Functor_1, [...], Functor_n)]
class Converter[F[int]]:
    def __init__(self, data : F[int]):
        self.data = data

    def convert(self) -> F[str]:
        return fun1(self.data)
```
### Simplifying code

Other use of a `@lift` decorator could be to cut code length for obvious lifts, instead of having something like
```Python
@lift [F : (Functor_1, [...], Functor_n)]
def fun1(inp : F[int]) -> F[str]:
    if isinstance(inp, int):
        return str(inp)
    elif isinstance(inp, Functor_1):
        ... # some code to lift over Functor_1 structure
    # [...]
    elif isinstance(inp, Functor_n):
        ... # some code to lift over Functor_1 structure
    else:
        raise TypeError
```
we could have
```Python
class Functor_1[T]:
    def __lift__(self, f : Callable[[T], V]) -> Functor_1[V]:
        ... # code to lift naturally over Functor_1 structure
[...]
class Functor_n[T]:
    def __lift__(self, f : Callable[[T], V]) -> Functor_n[V]:
        ... # code to lift naturally over Functor_n structure

@lift [F : (Functor_1, [...], Functor_n)]
def fun1(inp : F[int]) -> F[str]:
    return str(inp)
```
A foreseeable edge case is how to determine which parameter should be used for lifting in e.g. `list[tuple[int, int]]`, `list[tuple[int,...]]` etc (or dicts as they might have several arguments)
To me, it is clear that all the values of the functor variable `F` should have the same arity, and we could be explicit on how to lift :
```Python
@lift [F[T] : (list[T], tuple[T,int], list[tuple[T,int]])]
def fun1(inp : F[int]) -> F[str]:...

# lifting over two arguments
@lift [F[X,Y] : (dict[X,Y], frozendict[X,Y], tuple[X,Y])]
def fun2(inp : F[int, _], inp2 : F[_, str]) -> F[str, int] : ...

# lifting over first argument of some functors
@lift [F[X] : (dict[X,_], tuple[X, _])]
def fun3(inp : F[int]) -> F[str]:...

# different behavior from before, _ should not catch ... in tuple
@lift [F[X] : tuple[X, ...]]
def fun4(inp : F[int]) -> F[str]:...

# same as before, implicit
@lift [F : tuple]
def fun4_alike(inp : F[int]) -> F[str]:...
```
However, this disallows to have matching types expressions in the same lift (like `tuple[T,int]` and `tuple[int, T]` or even `tuple[T,...]` as `tuple[T, int]` is a subtype of `tuple[T, ...]` when `T` is int, but they should lead to different lifting patterns), as type expressions that could be confused would lead to an arbitrary choice over the lifting method. This also leads to questioning how to decide which lift method to use in cases of upper bounds :
```Python
class Graph[T]:
    def __lift__(self, f : Callable[[T], Y]) -> Graph[Y]:
        nodes = {f(node) for node in self.nodes}
        edges = {(f(x), f(y)) for (x,y) in self.edges}
        return Graph(nodes, edges)

@lift [F : Iterable]
def fun1(inp : F[int]) -> F[str]: ...
```
Here, `Graph` could easily be an iterable (natural iteration over nodes), but using the iterable natural lifting method wouldn't keep the graph structure. So, it is quite clear that the most specific lifting method should be used (and for inheritance, Python's order of inheritance is sufficient to handle).

### Specializing some cases

Last point I might highlight about lifting is how to implement specific cases along lifting. The easy answer is to do something like
```Python
@lift [F : Iterable]
def fun1(inp : F[int] | str) -> F[str] | None:
    if isinstance(inp, str):
        return None
    else:
        return str(inp)
```
However, we can see here that we lack type dependency, and we are just back to overloading our functions if we want a precise type hint :
```Python
@overload
@lift [F : Iterable]
def fun1(inp : F[int]) -> F[str]:...
@overload
def fun1(inp : str) -> None:...
@lift [F : Iterable]
def fun1(inp : F[int] | str) -> F[str] | None:
    if isinstance(inp, str):
        return None
    else:
        return str(inp)
```
It would honestly be really nice to have all that already. But HKT might allow even more concision

### To the bottom of overloading

The last nice thing that could be brought to Python by HKT is just type dependency, to avoid lengthy overloadings. It is just about being able to have [TypeMappings](https://github.com/python/typing/issues/1273) (except such mappings wouldn't have the naturality required for lifting, they would just be here for typing). It could obviously be handy to have something that would be like :
```Python
M : TypeMapping = {
    int : str,
    str : int,
    float : int,
    tuple : None,
}

def fun1(inp : T in M) -> M[T]: ...

class MyClass[T in M]:
    def __init__(self, value : T):
        self.value = value

    def mymethod(self) -> M[T]:
        return fun1(self.value)
```
but it would also allow us to reduce our other example :
```Python
M : TypeMapping[F : Iterable] = {
    F[int] : F[str],
    str : None,
}

@lift [F : Iterable]
def fun1(inp : F[T] in M) -> M[F[T]]:
    if isinstance(inp, str):
        return None
    else:
        return str(inp)
```
Which is completely sound, because the identity functor is always a possibility. Hence, `Id[str]` is a possible value equaling to `str` which is in `M`.
Even better, we can have the other way around with F and M just by moving M in the bracket :
```Python
M : TypeMapping = {
    int : str,
    str : int,
}

@lift [F : Iterable]
def fun1(inp : F[T in M]) -> F[M[T]]:
    if isinstance(inp, str):
        return len(str)
    else:
        return str(inp)
```
which allows us to lift once for multiple type dependencies.

### What use for overloading then ?

`@overload` could still be useful to specify functions that have different behaviors with different number of arguments. I know one could have the idea to use tuple of types in TypeMappings, but I think gathering all those types in one tuple at function definition would lead to messy code due to variable length of the tuple. Specifically, having something like this would be impractical :
```Python
M : TypeMapping = ...

def fun1[(Type1, Type2, Type3) in M](inp1 : Type1, inp2 : Type2 = default2, arg3 : Type3 = default3) -> M[(Type1, Type2, Type3):...
```
In fact, I can't come up with any practical syntax for such cases except for this very generic case :
```Python
def fun2(*args : *TypeTuple) -> M[TypeTuple]: ...
```
So I think it's better to stick to things like
```Python
@overload
def fun1(inp1 : Type1) -> ReturnType1 : ...
@overload
def fun1(inp1 : Type1, inp2 : Type2) -> ReturnType2 : ...
@overload
def fun1(inp1 : Type1, inp2 : Type2, arg3 : Type3) -> ReturnType3 : ...
@overload
def fun1(inp1 : Type1, inp3 : Type3) -> ReturnType4 : ... # not sure it is possible nor how to type it but we never know

def fun1(inp1 : Type1, inp2 : Type2 = default2, arg3 : Type3 = default3) -> ReturnType1 | ReturnType2 | ReturnType3 | ReturnType4:
    ...
```

I would be really happy to bring such things to python, if I can help anyhow let me know !


---

### Comment [3761116326](https://github.com/python/typing/issues/548#issuecomment-3761116326)

- **Author**: @RomanValov
- **Date**: `2026-01-16T17:40:50Z`

Posted one more use case for type variables bound by another type variable (but not generic actually) in the relevant [thread](https://github.com/python/typing/issues/1226#issuecomment-3761101019).


---

### Comment [3784037539](https://github.com/python/typing/issues/548#issuecomment-3784037539)

- **Author**: @flying-sheep
- **Date**: `2026-01-22T12:04:07Z`

We really need this to even stand a chance to correctly type our stuff. I’m reaching for this feature in half of my projects.

Here are three examples from three projects from the top of my mind.

1. ```py
   type AnyIndex = slice[None, None, None] | tuple[int, int]

   class Ref[IndexT: AnyIndex]:
       idx: IndexT

   @dataclass
   class Accessor[RefT: Ref]:
       ref_cls: type[RefT]  # RefT being higher-kinded
       def __call__[IndexT: AnyIndex](self) -> RefT[IndexT]: ...

   A_DEFAULT = Accessor(Ref)
   ```
2. ```py
   class ArrayKind[OuterT: MemArray | DiskArray[InnerT], InnerT: MemArray | None = None]: ...
   KINDS = [ArrayKind[np.ndarray], ArrayKind[DaskArray, np.ndarray], ...]
   ```
3. ```py
   class SparseMat[DataScalarT: np.number, IdxScalarT: np.integer, ArrayT: (npt.NDArray, cupy.ndarray)]:
       index: ArrayT[IdxScalarT]
       indptr: ArrayT[IdxScalarT]
       data: ArrayT[DataScalarT]
   ```


---

### Comment [4128237155](https://github.com/python/typing/issues/548#issuecomment-4128237155)

- **Author**: @jnsplt
- **Date**: `2026-03-25T17:02:20Z`

To provide yet another real-world example: We have to extend the agent framework [pydantic-ai](https://ai.pydantic.dev/) for our project. `pydantic-ai`s `Agent[DepsT, OutputDataT]` is generic over a deps type. We subclass the `Agent` class and want a method that accepts *both* deps and a chat object, where both must agree on the same state type `S`. However, `S` is "inside" the already-bound class-level type parameter `DepsT`.

```python
from typing import TypeVar
from pydantic import BaseModel

# --- library types (simplified) ---

type StateVars = BaseModel | None

class Deps[S: StateVars]:
    """Agent dependencies carrying typed state. Must be subclass-able"""
    def __init__(self, state: S = None) -> None:
        self.state = state

class ChatNode[S: StateVars]:
    """A node in a conversation, carrying a snapshot of the state."""
    def __init__(self, content: str, state: S = None) -> None:
        self.content = content
        self.state = state

class Chat[S: StateVars]:
    """A conversation whose nodes all share the same state type."""
    def __init__(self) -> None:
        self.nodes: list[ChatNode[S]] = []

# Upstream base class (defined in pydantic-ai) without OutputDataT for simplification:
class Agent[DepsT]:
    """Third-party agent base class, generic over deps."""
    ...

# --- Our subclass ---

class MyAgent[DepsT: Deps[StateVars] | None](Agent[DepsT]):
    def run_chat(
        self,
        chat: Chat[StateVars],  # would like to type Chat[S] but S is trapped inside DepsT; e.g. Chat[SomeState]
        deps: DepsT | None = None,  # e.g. Deps[SomeState] or OtherDeps[SomeState]
    ) -> None:
        """Run the agent on a chat, snapshotting state into new nodes."""
        ...
```

The problem: `DepsT` is `Deps[S]` for some `S`, and `Chat` is `Chat[S]` for the *same* `S`, but there's no way to tell the type checker to extract `S` from `DepsT` and use it to constrain `chat`. We now just use `Chat[StateVars]` (the full union) and add a runtime consistency check - but it would be so much more fun to have HKTs to solve this, for example like this:

```python
class MyAgent[DepsKind[...]: BaseDeps, StateVarsT: StateVars](
    Agent[DepsKind[StateVarsT]]
):
    async def run_chat(
        self,
        chat: Chat[StateVarsT],
        deps: DepsKind[StateVarsT] | None = None,
        ...
    ): ...
```


---

### Comment [4252344175](https://github.com/python/typing/issues/548#issuecomment-4252344175)

- **Author**: @flying-sheep
- **Date**: `2026-04-15T13:10:32Z`

@ilevkivskyi I don’t think your initial assessment is accurate:

> TBH this is low priority, since such use cases are quite rare.

I think at least of the last 5 projects I contributed to, 5 of them would use this if it was available, now they have less accurate typing as a result. A recent package we started has 3 files, 2 of them need this.


---

### Comment [4252750255](https://github.com/python/typing/issues/548#issuecomment-4252750255)

- **Author**: @bartfeenstra
- **Date**: `2026-04-15T14:07:06Z`

We've all come a long way since then, and that post was written in the early days of Python typing, at the time of Python 3.6. We didn't even have generics until 3.7 came out half a year after the quoted comment 😮 😄  


---

### Comment [4253252335](https://github.com/python/typing/issues/548#issuecomment-4253252335)

- **Author**: @JelleZijlstra
- **Date**: `2026-04-15T15:14:51Z`

It's not particularly productive to nitpick comments made almost a decade ago.

If you want this feature to happen, the path is to write a PEP with a clear specification, get type checkers to implement it, and shepherd the PEP to completion.

> We didn't even have generics until 3.7

For what it's worth this is not accurate, generics have existed since the genesis of typing in 3.5. 3.7 improved their internal representation though.


---

### Comment [4253516183](https://github.com/python/typing/issues/548#issuecomment-4253516183)

- **Author**: @bartfeenstra
- **Date**: `2026-04-15T15:53:54Z`

I meant to illustrate just how far Python has come since this thread was started, and that the landscape looks much different now; HKTs are on many more different people's radars than they were back in 2018. Also, we've all changed our minds a few times since 2018 ❤️ 


---

### Comment [4253622094](https://github.com/python/typing/issues/548#issuecomment-4253622094)

- **Author**: @flying-sheep
- **Date**: `2026-04-15T16:09:14Z`

> If you want this feature to happen, the path is to write a PEP with a clear specification

@nekitdev started a draft here https://github.com/nekitdev/peps/blob/d899c018477fd2ca6afcf7ceb41678a896ed0598/peps/pep-9999.rst

Happy to help. @nekitdev you wanna keep being the primary author or should someone else take over?


---

### Comment [4254129241](https://github.com/python/typing/issues/548#issuecomment-4254129241)

- **Author**: @x42005e1f
- **Date**: `2026-04-15T17:30:06Z`

Well, since the discussion has resumed, I would like to show my use case, which is somewhat similar to [the 2020 example with the `returns` library](https://github.com/python/typing/issues/548#issuecomment-719496694). I have a function that copies other functions, annotated as follows:

```python
_T = TypeVar("_T")
_P = ParamSpec("_P")

@overload
def copies(
    original: Callable[_P, _T],
    replaced: MissingType = MISSING,
    /,
) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]: ...
@overload
def copies(
    original: Callable[_P, _T],
    replaced: Callable[_P, _T],
    /,
) -> Callable[_P, _T]: ...
```

And used, for example, as follows:

```python
def f() -> int:
    """Some docstring."""
    return 42

@copies(f)  # `g.__code__` will be `f.__code__`
def g() -> int:
    """Another docstring."""
    return f()
```

It creates a new copy of function `f()` and makes it look like function `g()` (and `copies(f)(g)` is equivalent to `copies(f, g)`; `copies(f, f)` forces the copying of function `f()`).

The problem here is that I have to ignore the type of the function being copied. The returned object is always "some callable object". Because there are no higher-kinded TypeVars, I have to sacrifice type preservation in favor of ensuring that both functions (`f()` and `g()`) have the same signature. Therefore, for example, if I pass an object that is compatible with the following protocol:

```python
class ScopedCallable(Protocol):
    def __call__(self, /, *args: Any, **kwargs: Any) -> Any: ...
    @property
    def scope(self, /) -> ScopeType: ...
```

then I will not be able to access the `scope` attribute of the copy, even though my `copies()` copies the `__dict__` contents. And I will have to use `typing.cast()` to cast it to the original type.

Notably, I am not sure if it is possible to achieve the behavior I want even with the `returns` library.


---

### Comment [4255080425](https://github.com/python/typing/issues/548#issuecomment-4255080425)

- **Author**: @Pleket
- **Date**: `2026-04-15T20:01:57Z`

> It's not particularly productive to nitpick comments made almost a decade ago.
> 
> If you want this feature to happen, the path is to write a PEP with a clear specification, get type checkers to implement it, and shepherd the PEP to completion.
> 
> > We didn't even have generics until 3.7
> 
> For what it's worth this is not accurate, generics have existed since the genesis of typing in 3.5. 3.7 improved their internal representation though.

"The path is to write a PEP with a clear specification"
This has been done before. A user generally called "sobolevn" has made PEPs, created the returns Python library, and has been working on MyPy. [I highly recommend his blog.](https://sobolevn.me/) But even there, and the related Returns Python library, it is clear that he could only achieve such higher-kinded types by restricting the Python environment. 

I have worked on figuring out type checking in Python myself as well, by pretty much trying to hardcode it and leaving out many of Python's funny extras that kind of behave differently than you would expect... with little success. The reason it has not been implemented as a part of Python is that it is incredibly complex. Type checking is a kind of math that favors assumptions about procedural descriptions (so, code) that are pretty much what Python is not. I personally see it as something that requires a very strong link between procedures and (immutable) types, and in Python, that link is still quite weak. Most modern Python code still doesn't really use typing beyond basic parameter types. 

If you do end up trying to work this out, you should really work out some examples of what the type system should do to maintain higher-kinded typevars. Like in previous PEPs, you will find that implementing it is a complete package of typing requirements that should be carefully incorporated before it can be supported without major side effects. Think about laziness and typing lambda functions in general, type reductions (which are pretty much only implemented in open-source typing projects like MyPy and, more notably, PyRight, so your implementation would probably require one of the two), consequences of dynamic typing in a higher-kinded typevar, the order of type reduction (which ties in with laziness), etc. There is a lot to explore that is not quite visible from the surface. 


---

### Comment [4263465677](https://github.com/python/typing/issues/548#issuecomment-4263465677)

- **Author**: @RobinSobczyk
- **Date**: `2026-04-16T21:15:35Z`

I've started drafting something, I need a bit more time to release my PEP draft as I need to figure out the proper syntax and semantic first, then provide some new grammar for Python and finally have an implementation that works along with MyPy. I've noted every example up to this point in the thread and will include them, either to agree or disagree (always while providing reasons for it). I'm sorry if it takes a bit of time, I didn't announce anything because I have no ETA (and won't provide any). I've been working on it for some weeks and dealing with several problems as well (e.g. higher order unification is undecidable, which would have been a good intuitive solution if it worked). I still have a bunch of todos that I want to solve myself before releasing (I want to provide something that is consistent before getting any feedback, so the feedback don't focus on missing points at first), but eventually it will come (don't hesitate to ping me for updates in 2~3 months if there's no news).


---

### Comment [4270045356](https://github.com/python/typing/issues/548#issuecomment-4270045356)

- **Author**: @AshrithSagar
- **Date**: `2026-04-17T17:33:33Z`

Just wanted to chime in — I've also been working on a draft + experimental prototype for HKTs over the past few weeks.
You can find it here: https://github.com/AshrithSagar/pyHKTs
I am very interested in seeing this feature happen, so I'm trying to write a clear specification, as Jelle suggested.

It's **not complete at all** (everything is very rough, mypy/pyright patches are early-stage, and the design is still evolving), so I'm not trying to rush anything.
I mainly wanted to make it public here so that:
- People interested in HKTs can see an alternative approach (I'm currently exploring a `KindVar` primitive, instead of extending `TypeVar` with `args=`).
- There is some working code and examples available for discussion.
- I can get early feedback before going too deep in any particular direction.

My current examples focus on `fmap` and `Functor`.
I'm planning to expand it with more use cases from this thread (`bidict` and others).

Regardless of whatever I'm trying out in my repo, I'm happy to collaborate, compare approaches, or help in any way that’s useful. No pressure or ETA from my side either.
Looking forward to any constructive feedback!



---

### Comment [4278175490](https://github.com/python/typing/issues/548#issuecomment-4278175490)

- **Author**: @AshrithSagar
- **Date**: `2026-04-20T05:47:53Z`

I'm sure @sobolevn [is familiar with this](https://sobolevn.me/2021/12/paramspec-guide), but just to keep a reference in this issue, I believe the best we can do currently for the factory/constructor pattern mentioned by @sobolevn [here](https://github.com/python/typing/issues/548#issuecomment-621686416), is:

```python
from typing import Callable

def create[**P, R](klass: Callable[P, R], *args: P.args, **kwargs: P.kwargs) -> R:
    return klass(*args, **kwargs)
```

| Expression                | mypy           | pyright                 | pyrefly         | ty              | zuban       |
| ------------------------- | -------------- | ----------------------- | --------------- | --------------- | ----------- |
| `create(list, (1,))`      | `list[int]`    | `list[Literal[1]]`      | `list[Unknown]` | `list[_T@list]` | `list[Any]` |
| `create(list[int], (1,))` | `list[int]`    | `list[int]`             | `list[int]`     | `list[int]`     | `list[int]` |
| `create(list, (1, "2"))`  | `list[object]` | `list[Literal[1, '2']]` | `list[Unknown]` | `list[_T@list]` | `list[Any]` |

<details><summary>Code:</summary>
<p>

```python
from typing import reveal_type

c1 = create(list, (1,))
print(c1, type(c1))  # [1] <class 'list'>
reveal_type(c1)
# mypy :: Revealed type is "list[int]"
# pyright :: Type of "c1" is "list[Literal[1]]"
# pyrefly :: revealed type: list[Unknown]
# ty :: Revealed type: `list[_T@list]`
# zuban :: Revealed type is "builtins.list[Any]"

c2 = create(list[int], (1,))
print(c2, type(c2))  # [1] <class 'list'>
reveal_type(c2)
# mypy :: Revealed type is "list[int]"
# pyright :: Type of "c2" is "list[int]"
# pyrefly :: revealed type: list[int]
# ty :: Revealed type: `list[int]`
# zuban :: Revealed type is "builtins.list[builtins.int]"

c3 = create(list, (1, "2"))
print(c3, type(c3))  # [1, '2'] <class 'list'>
reveal_type(c3)
# mypy :: Revealed type is "list[object]"
# pyright :: Type of "c3" is "list[Literal[1, '2']]"
# pyrefly :: revealed type: list[Unknown]
# ty :: Revealed type: `list[_T@list]`
# zuban :: Revealed type is "builtins.list[Any]"
```

</p>
</details>

<details><summary>Tested with:</summary>
<p>

- Python 3.14.3
- mypy 1.20.1
- pyright 1.1.408
- pyrefly 0.61.1
- ty 0.0.31
- zuban 0.7.0

</p>
</details>



---

### Comment [4292415332](https://github.com/python/typing/issues/548#issuecomment-4292415332)

- **Author**: @jab
- **Date**: `2026-04-21T23:07:53Z`

@AshrithSagar writes:

> Just wanted to chime in — I've also been working on a draft + experimental prototype for HKTs over the past few weeks.
> ...
> My current examples focus on `fmap` and `Functor`. I'm planning to expand it with more use cases from this thread (`bidict` and others).

I'm the author/maintainer of bidict, and just wanted to say thanks for keeping bidict in mind with your work on this! Let me know if there's anything I can do once you're ready to test with bidict. Happy to consider any changes to the code that could make things easier.


---

### Comment [4364020039](https://github.com/python/typing/issues/548#issuecomment-4364020039)

- **Author**: @RobinSobczyk
- **Date**: `2026-05-02T14:24:21Z`

I'm nearing the end of the specification in my PEP (I still need to do the toy implementation after before sharing), and I'm stumbling upon a problem :
what do people think about the fact that `T != *tuple[T]` ?

In particular, `tuple[int] == tuple[*tuple[int]]` evaluates to False, although it is equivalent per [PEP 646](https://peps.python.org/pep-0646/#unpacking-concrete-tuple-types)

In particular, this prevents me from defining an Identity functor, because :
- `Id[T]` should be equal to `T` because this is the concept of identity
- `Id[*tuple[T1, T2]]` is different from `Id[tuple[T1, T2]]` per injectivity of `Id` (indeed, `tuple[T1, T2]` is different from `*tuple[T1, T2]`)
- `Id[*tuple[T]]` sounds like it should resolve to `T` or `Id[T]`, hence the wanted equality I'm asking people about


---

### Comment [4364075806](https://github.com/python/typing/issues/548#issuecomment-4364075806)

- **Author**: @JelleZijlstra
- **Date**: `2026-05-02T14:55:48Z`

Many types that are equivalent (in the formal sense) are not represented identically at runtime. I don't think that is a problem.


---

### Comment [4364160860](https://github.com/python/typing/issues/548#issuecomment-4364160860)

- **Author**: @ilevkivskyi
- **Date**: `2026-05-02T15:42:46Z`

FWIW I got more interested in this recently, so _maybe_ I will write some prototype implementation (in mypy) later this year. Couple comments:
1. I don't think we should support arbitrary HKT, I think we should only support "2nd kind" types, i.e. types without nested parentheses in their kind: e.g. `(* -> *) -> *` is OK, but `((* -> *) -> *) -> *` is not OK. This will simplify implementation significantly while covering 90%+ of use cases.
2. Variance got little discussion so far, while it is important in a type system with subtyping. Any potential syntax should account for that. One potential option I see is something like this:
```python
class Example[F: _[+_, _, -_]]: ...  # arbitrary type constructor that is covariant in first argument, invariant in second, and contravariant in third.
class Another[G: Sequence[_]]: ... # G is an invariant "Sequence-like" constructor, e.g. a list.
```


---

### Comment [4364195246](https://github.com/python/typing/issues/548#issuecomment-4364195246)

- **Author**: @jorenham
- **Date**: `2026-05-02T16:02:21Z`

> 1. I don't think we should support arbitrary HKT, I think we should only support "2nd kind" types, i.e. types without nested parentheses in their kind: e.g. `(* -> *) -> *` is OK, but `((* -> *) -> *) -> *` is not OK. This will simplify

I fully agree. If I remember correctly, type systems with >2nd order kinding are undecidable, so let's not open that can of worms.

---

> 2. Variance got little discussion so far, while it is important in a type system with subtyping. Any potential syntax should account for that. One potential option I see is something like this:
> 
> ```
> class Example[F: _[+_, _, -_]]: ...  # arbitrary type constructor that is covariant in first argument, invariant in second, and contravariant in third.
> class Another[G: Sequence[_]]: ... # G is an invariant "Sequence-like" constructor, e.g. a list.
> ```

Very good point. Perhaps we should even make polarity explicit, instead of implicit in case of invariance, i.e.e.g.: `class Example[F: _[+_, ~_, -_]]: ...`.



---

### Comment [4364951103](https://github.com/python/typing/issues/548#issuecomment-4364951103)

- **Author**: @mscuthbert
- **Date**: `2026-05-02T23:32:53Z`

As someone who used to have every Perl `@($$$&)` symbol memorized, can we please use words instead of making up new symbols for these covariants etc.:

`class Example[F: Constructor[Covariant, Invariant, Contravariant]]: ...`

In typing system that requires `List[str]` and not `str[]`, I think that special punctuation should be reserved for common and oft-used features.


---

### Comment [4364966307](https://github.com/python/typing/issues/548#issuecomment-4364966307)

- **Author**: @ilevkivskyi
- **Date**: `2026-05-02T23:43:35Z`

Was going to mention Perl myself after seeing `Example[F: _[+_, ~_, -_]]`, LOL. But IMO `Example[F: Constructor[Covariant, Invariant, Contravariant]]` is a bit too much as well. Anyway, I don't have strong opinion on the exact syntax (as soon as it satisfies my two comments above). This is something that should be decided by the community.

Another possible idea:
```python
class Example[F: _[Cov, Inv, Contra]]: ...
class Another[G: Sequence[Inv]]: ...
```


---

### Comment [4365700639](https://github.com/python/typing/issues/548#issuecomment-4365700639)

- **Author**: @RobinSobczyk
- **Date**: `2026-05-03T07:57:47Z`

I think that variance really gets more complicated than that. For now, I don't see any easy way to specify dependent variances like
```Python
class Applicator[ConstructorType[_], SomeType]:
    # behaves like ConstructorType[SomeType]
    ...
```
in this example, the variance of `Applicator` in `SomeType` depends on the variance of `ConstructorType` in its argument, which may be whatever in the general case (e.g. constructor can be `Lambda X : Callable[[X], ReturnType]` for contra, `Lambda X : Callable[[ArgType], X]` for co, `Lambda X : Callable[[X], X]` for inv and even `Lambda X : Callable[[ArgType], ReturnType]` for bivariance)


---

### Comment [4365909774](https://github.com/python/typing/issues/548#issuecomment-4365909774)

- **Author**: @jorenham
- **Date**: `2026-05-03T10:03:27Z`

Kotlin uses the keywords `out` and `in` to declare covariance and contravariance, respectively. Borrowing that idea, it could look something like `class Egg[F: _[Out, InOut, In]]: ...` in Python, which might be a bit more natural and easier to read than using the jargon-y {co/contra/in}variance terms directly.


---

### Comment [4459739698](https://github.com/python/typing/issues/548#issuecomment-4459739698)

- **Author**: @RobinSobczyk
- **Date**: `2026-05-15T12:26:58Z`

I stumbled upon some limits and would like some feedback about :
1. should assignment of value of type `Never`  be flagged as an error by type checkers ? To me, the assignment operator takes a variable and a value, and passing it a value of type `Never` is inherently an error. However, this also conflicts with `Never` being a bottom type, as it means whenever we assign a value of a specific type (say `int`), we could theoretically fall into the sub-type of `Never`. On the other hand, `Never` being a bottomtype is also a nice thing as it also means for typing that any function might fail. However, I feel like type checker/type system signaling that a function might fail is less a priority to users than assigning `Never` values that cannot exist. I've never seen anyone write `def some_fun(*args : *ArgTypes) -> ReturnType | Never:` to explicit that a function might fail, and it's implicitly admitted that any function might indeed fail.
Maybe separating `Never` and `NoReturn` would make sense to fix this situation, I don't really know, and I'm looking for the consensual feeling here.

2. It's about TypeVar substitution. I feel like there's a huge problem there. In particular, I tried keeping this feature alive, and it lead me to basically conceptualizing "type expressions" which are just higher order kinds, and to me, this is misleading, and should probably be introduced with lambda-like syntax to explicitly declare what might be substituted, how, and in which order. But before proposing to do so, I wonder how common is TypeVar substitution in codebases. Any input is welcome.

3. Tied to substitution but also typing in general, consider this code :
```Python
import asyncio

def context[*Ts, *Us](arg1 : tuple[*Ts], arg2 : tuple[*Us]) -> None:
    a: tuple[*Ts] | None = None
    b: tuple[*Us] | None = None
    
    a_ready = asyncio.Event()
    b_ready = asyncio.Event()
    
    async def fun1(*args : *Ts):
        nonlocal a
        a = args
        a_ready.set()
        await b_ready.wait()
        if b is None:
            raise RuntimeError
        return b
    
    async def fun2(*args : *Us):
        nonlocal b
        b = args
        b_ready.set()
        await a_ready.wait()
        if a is None:
            raise RuntimeError
        return a
    
    reveal_type(fun1)
```
I used async to explain in which kind of case it could be useful, but doing it without is possible as well. Still, anyone with a bit of type intuition would want to say "oh yes, `fun1` is of type `Callable[[*Ts], tuple[*Us]]`", which is quite non ambiguous to read. However, this comes in conflict with the impossibility to have several TypeVarTuple in one "type expression". The obvious runtime problem comes when one try to substitute in this expression. Is there anything I should be aware about this situation ? I have my personal feelings about that, but I'm asking about community insights.


---

### Comment [4459884119](https://github.com/python/typing/issues/548#issuecomment-4459884119)

- **Author**: @Pleket
- **Date**: `2026-05-15T12:48:30Z`

> 1. should assignment of value of type `Never`  be flagged as an error by type checkers ? To me, the assignment operator takes a variable and a value, and passing it a value of type `Never` is inherently an error. However, this also conflicts with `Never` being a bottom type, as it means whenever we assign a value of a specific type (say `int`), we could theoretically fall into the sub-type of `Never`. On the other hand, `Never` being a bottomtype is also a nice thing as it also means for typing that any function might fail. However, I feel like type checker/type system signaling that a function might fail is less a priority to users than assigning `Never` values that cannot exist. I've never seen anyone write `def some_fun(*args : *ArgTypes) -> ReturnType | Never:` to explicit that a function might fail, and it's implicitly admitted that any function might indeed fail.

This is the basis of why this implementation is so hard to do within Python. This is fully dependent on how lazy your evaluation is. Python is eager, so if we keep it 'Pythonic', that assignment would fail. But these inductive/recursive types should be inherently lazy (so essentially tell the evaluation to stop expanding it at each crossroads), meaning that a Never type should be as well. That would mean that type Never only really fails if evaluated. Essentially, unless there is a conflict of unification, if you write a function that always returns a type Never, that is fine type-wise. 

> 2. It's about TypeVar substitution. I feel like there's a huge problem there. In particular, I tried keeping this feature alive, and it lead me to basically conceptualizing "type expressions" which are just higher order kinds, and to me, this is misleading, and should probably be introduced with lambda-like syntax to explicitly declare what might be substituted, how, and in which order. But before proposing to do so, I wonder how common is TypeVar substitution in codebases. Any input is welcome.

Actual TypeVar substitution in codebases is a bit odd to me, because type substitution is something that normally happens in the background. However, given the complications of Python for this implementation, any help with typing from the user is very welcome; TypeVar substitution for defining type expressions is very common in languages with more sophisticated type systems. You might not see it often right now because it is not really possible, but if higher order types would have an actual equivalent (I cannot quickly think of an example, but there are many types right now that you can only really 'create' by writing a function and adding TypeVars to the parameters and return type) it would without a doubt be adopted in most Python codebases as well. In fact, I think you cannot implement this without conceptualizing type expressions the way you described, because what is the use of types to the user (and therefore, why would they go through the trouble of using them) if they cannot be seen? 


---

### Comment [4467756659](https://github.com/python/typing/issues/548#issuecomment-4467756659)

- **Author**: @ilevkivskyi
- **Date**: `2026-05-16T18:32:07Z`

As I have been thinking more about this, I realized it would be helpful to get a collection of examples distilled from real code where people believe HKTs will be useful. Importantly, examples should include expected type-checker behavior at various call sites, not just the definitions (this is because type inference will be the trickiest part).

This thread is already really long, and many examples/issues mentioned here are unrelated. Do we have a volunteer to create a dedicated repo and gather such examples (say one example per file)? If yes, as I mentioned, I am not really worried about the syntax, I want to better understand the desired _semantics_, so feel free to use an arbitrary syntax in the examples.


---

### Comment [4467840256](https://github.com/python/typing/issues/548#issuecomment-4467840256)

- **Author**: @jorenham
- **Date**: `2026-05-16T19:06:38Z`

> Do we have a volunteer to create a dedicated repo and gather such examples (say one example per file)?

Sure, I could do that. I'll post it here once I've got it up and running in a couple of days or so.


---

### Comment [4467903652](https://github.com/python/typing/issues/548#issuecomment-4467903652)

- **Author**: @RobinSobczyk
- **Date**: `2026-05-16T19:35:30Z`

For now, I only have a notebook with the examples from this thread, one per cell. It's rather hard to provide examples from real code I'd say, because e.g. numpy and other might benefit from this as well, but without insights from actual maintainers, it might be hard to know how and why. Maybe doing a round to ask the most common python packages might be insightful.


---

### Comment [4473636506](https://github.com/python/typing/issues/548#issuecomment-4473636506)

- **Author**: @jab
- **Date**: `2026-05-18T02:07:41Z`

@jorenham, thanks for offering to compile the repo with examples. As the author/maintainer of [bidict](https://github.com/jab/bidict), it'd be great to see that example included. Since it's buried now, [here's a link](https://github.com/python/typing/issues/548#issuecomment-621195693) to where I explained the use case upthread. Here is an updated [mypy play](https://mypy-play.net/?mypy=latest&python=3.14&gist=5272ebc066abb4b6b32df0a336c78b00&flags=strict) showing the type system's current limitations. Hope this helps.


---

### Comment [4482628476](https://github.com/python/typing/issues/548#issuecomment-4482628476)

- **Author**: @jorenham
- **Date**: `2026-05-18T21:59:15Z`

I've created the repo and added a couple of examples: https://github.com/jorenham/hkt-survey

If you have a good example (that's not too similar to any of the current ones), feel free to open a PR.


---

### Comment [4482775567](https://github.com/python/typing/issues/548#issuecomment-4482775567)

- **Author**: @AlexWaygood
- **Date**: `2026-05-18T22:27:12Z`

I think we came across another typeshed use case the other day in https://github.com/python/typeshed/pull/15724#discussion_r3211374603: it seems it's not possible to accurately type `builtins.frozendict.__new__` without HKTs


---

### Comment [4482887959](https://github.com/python/typing/issues/548#issuecomment-4482887959)

- **Author**: @ilevkivskyi
- **Date**: `2026-05-18T22:42:18Z`

@jorenham Thanks! We can discuss details in the repo. Two large-scale comments/questions:
* Another important thing that will be helpful is function/method bodies in the examples (at least in some). For example, is there an implementation of `map_async()` that type-checkers are expected to be able to type-check?
* I see there is a bunch of NumPy/SciPy related examples that seem to be already expressible with self-types, are those correct? For example, this already works (tried in mypy):
```python
from typing import Self, overload

import numpy as np

class _spbase[ScalarT]:
    @overload
    def __getitem__(self, key: int, /) -> Self: ...
    @overload
    def __getitem__(self, key: tuple[int, int], /) -> ScalarT: ...


class dok_matrix[ScalarT](_spbase[ScalarT]): ...

m: dok_matrix[np.float64]

reveal_type(m[2])  # dok_matrix[np.float64]
reveal_type(m[2, 3])  # np.float64
``` 


---

### Comment [4486539169](https://github.com/python/typing/issues/548#issuecomment-4486539169)

- **Author**: @jorenham
- **Date**: `2026-05-19T09:49:51Z`

Those are good points @ilevkivskyi. I'll address those soon (https://github.com/jorenham/hkt-survey/issues/3, https://github.com/jorenham/hkt-survey/issues/5)

On that note; I also opened issues for adding some of the other examples in this thread (https://github.com/jorenham/hkt-survey/issues). If anyone feels like helping out, those could be a good starting point. Opening issues or PRs for other examples would of course also help a lot.

**update**: I've addressed the points: The `map_async` example has been removed (and https://github.com/jorenham/hkt-survey/pull/16), and I've opened PRs that replace the NumPy and SciPy examples with new ones (https://github.com/jorenham/hkt-survey/pull/10, https://github.com/jorenham/hkt-survey/pull/11 ; currently open; reviews are welcome).


---

### Comment [4506417692](https://github.com/python/typing/issues/548#issuecomment-4506417692)

- **Author**: @Trimatix
- **Date**: `2026-05-21T08:51:13Z`

Regrettably I do not have the time to commit to helping this project, but I wanted to express my gratitude and excitement for the attention that this issue is getting. HKTs have been the answer to many issues in my personal projects over the years, particularly concerning container types. Many thanks.


---

### Comment [4526032478](https://github.com/python/typing/issues/548#issuecomment-4526032478)

- **Author**: @jorenham
- **Date**: `2026-05-23T17:09:53Z`

> I think we came across another typeshed use case the other day in [python/typeshed#15724 (comment)](https://github.com/python/typeshed/pull/15724#discussion_r3211374603): it seems it's not possible to accurately type `builtins.frozendict.__new__` without HKTs

Maybe generic upper type parameter bounds would suffice here 🤔 

```py
@overload
def __new__[KT=Any, VT=Any, SelfT: frozendict[KT, VT] = frozendict[Any, Any]](  # kinda sketchy
	cls: type[SelfT],
	/,
) -> SelfT: ...
@overload
def __new__[VT, SelfT: frozendict[str, VT]](
	cls: type[SelfT],
	/,
	**kwargs: VT,
) -> SelfT: ...
@overload
def __new__[KT, VT, SelfT: frozendict[KT, VT]](
    cls: type[SelfT],
	map: SupportsKeysAndGetItem[KT, VT],
	/,
) -> SelfT: ...
@overload
def __new__[VT, SelfT: frozendict[str, VT]](
    cls: type[SelfT],
    map: SupportsKeysAndGetItem[str, VT],
	/,
	**kwargs: VT,
) -> SelfT: ...
@overload
def __new__[KT, VT, SelfT: frozendict[KT, VT](
    cls: type[SelfT],
    iterable: Iterable[tuple[KT, VT]],
    /,
) -> SelfT: ...
@overload
def __new__[VT, SelfT: frozendict[str, VT]](
    cls: type[SelfT],
    iterable: Iterable[tuple[str, VT]],
    /,
    **kwargs: VT,
) -> SelfT: ...
```


---

### Comment [4563089142](https://github.com/python/typing/issues/548#issuecomment-4563089142)

- **Author**: @RobinSobczyk
- **Date**: `2026-05-28T10:24:42Z`

Is there a practical difference between `Callable[..., ReturnType]` and `Callable[[*tuple[Any, ...]], ReturnType]` ?
I understand the philosophical difference that in the first one it is explicitly stated that the argument signature is not specified, but to me saying "it's not specified" sounds to have the same consequences as saying "it might be any number of `Any`" (or even `object` if we want to avoid gradual).


---

### Comment [4563170607](https://github.com/python/typing/issues/548#issuecomment-4563170607)

- **Author**: @jorenham
- **Date**: `2026-05-28T10:34:06Z`

> Is there a practical difference between `Callable[..., ReturnType]` and `Callable[[*tuple[Any, ...]], ReturnType]` ?

`...` effectively means `*args: Any, **kwargs: Any`
`[*tuple[Any, ...]]` effectively means `*args: Any` (so it only accepts positional arguments)


---

### Comment [4563346305](https://github.com/python/typing/issues/548#issuecomment-4563346305)

- **Author**: @RobinSobczyk
- **Date**: `2026-05-28T10:59:47Z`

> so it only accepts positional arguments

Are you saying that any function that is like `def fun(arg1, arg2, *, kwarg1, kwarg2):` should be type-hinted through the help of a TypedDict to capture kwarg types ? I mean, it does not sound stupid at all, but I'm really curious if people actually do it, as it is a burden to create a new TypedDict every time.

EDIT : Adding details

The doc of [`Callable`](https://docs.python.org/3/library/typing.html#annotating-callable-objects) states that Callable "cannot express complex signatures such as functions that take a variadic number of arguments", which sounds false thanks to variadic tuple unpacking. In fact, this doc seems outdated.

Also, the doc of [`Unpack`](https://docs.python.org/3/library/typing.html#typing.Unpack) clearly talks about unpacking TypedDict, without mentionning its use in Callable. Typecheckers seem to handle that correctly though.

I think, there is just a blank in terms of the semantic of Callable. My pythonic point of view is that people probably don't expect to have to use TypedDict every time they want to specify kw-only args, as it was seemingly never defined nor enforced. I didn't play long enough with typecheckers to see how they react to this, but to me, it sounds that *right now*, the classic python user might think that `Callable[[*tuple[Any, ...]], ReturnType]` encompass kw-only args as well. It can be changed, obviously, but should it ?

Small code for tests : https://mypy-play.net/?mypy=latest&python=3.14&gist=5229bbb0567246d99b6627979c546964

On another note, `**kwargs` also capture only **excess** keyword arguments, meaning that a function like `def fun(arg1, *, kwarg1, **other_kwargs):` is a potential pain to type.

I highly fear that having TypedDict to work properly implies having [type intersection](https://github.com/python/typing/issues/213), which in itself already sounds painful. This is according to [TypedDict multiple inheritance](https://typing.python.org/en/latest/spec/typeddict.html#multiple-inheritance), which clearly expose multiple inheritance as the way to extend TypedDict in the way kwargs behaves. Shame it does not specify how multiple inheritance works with openness, extraitems etc, specifically when it's conflicting. Might be an opportunity to define those behaviors as well.


---

### Comment [4564704949](https://github.com/python/typing/issues/548#issuecomment-4564704949)

- **Author**: @JelleZijlstra
- **Date**: `2026-05-28T13:55:11Z`

(Not sure why we're talking about Callable semantics here or what it has to do with higher-kinded types.)

Yes, Callable as currently specified can only be used to spell callables with positional-only parameters. As of PEP-692, Unpack can be used in function signatures to unpack a TypedDict to a series of kwargs, but that PEP didn't add it to Callable. There are two pending PEPs that expand this: PEP-821 adds support for Unpack[TypedDict] in Callable, and PEP-827 adds a lot of features including more expressive callable types.


---

### Comment [4564919156](https://github.com/python/typing/issues/548#issuecomment-4564919156)

- **Author**: @RobinSobczyk
- **Date**: `2026-05-28T14:16:15Z`

> Not sure why we're talking about Callable semantics here or what it has to do with higher-kinded types

Well, the easy question is, what is the kind of `Callable` ? This is how I started going down this rabbit hole. This is tightly tied to `ParamSpec` not being a type either. So in my proposition so far, I decided to introduce :
- Types
- PackedDomains (the first argument of `Callable`, so `Callable :: PackedDomain -> Type -> Type`, but also the kind of `ParamSpec`)
- Domains (basically, for `Unpack`, which is of kind `Type -> Domain`)
and domains can furthermore be decomposed into positional domains, keyword domains, and have specific interactions with variadics.

> [PEP-821](https://peps.python.org/821) adds support for Unpack[TypedDict] in Callable, and [PEP-827](https://peps.python.org/827) adds a lot of features including more expressive callable types.

Thanks a lot for that, looking into it right now !


---

### Comment [4565694265](https://github.com/python/typing/issues/548#issuecomment-4565694265)

- **Author**: @RobinSobczyk
- **Date**: `2026-05-28T15:32:50Z`

This also leads me to question the meaning of expressions like `Concatenate[..., P]`. More precisely, `Concatenate` seems to currently accept any number of Ellipsis and ParamSpecs, without any specified semantic. Am I missing an information there, or is it the currently desired behavior ?
More specifically, from what I understand, `Concatenate` should be kinded as `...[Type] -> PackedDomain -> PackedDomain` (with `...[K]` representing a variadic number of elements of kind `K`), and this should forbid those previously questionned uses.


---

### Comment [4754092184](https://github.com/python/typing/issues/548#issuecomment-4754092184)

- **Author**: @RobinSobczyk
- **Date**: `2026-06-19T19:06:11Z`

Just a quick progress report, I'm splitting my PEP in 5 PEPs as it was getting really long due to a high number of things being required before properly defining higher kinded typevars. The PEPs will be as follow :
9995 : Defining kinds for actual types (TypeVars would still only represent only concrete types at this level)
9996 : Numerous extensions that naturally comes after defining kinds (like TypedDicts in Concatenate etc)
9997 : Reworking the TypeVar substitution system (defining `TypeTemplates` etc)
9998 : Adding Higher Kinded TypeVars with only basic features
9999 : Adding advanced higher kinded features (`@lift` decorator etc)

Again, no ETA, but I can give the current state of things :
9995 : Implementation missing
9996 : Incomplete, lot of things still missing (this is currently what I'm spending most of my time on)
9997 : Specification almost complete, no implementation
9998 : Most of rationale and specification is done, no implementation
9999 : Mostly ideas for now, require more in depth work

I plan on releasing 9995, 9996 and 9997 together at they feel quite connected to me. Then 9998, and finally 9999. Obviously will keep updating here sometimes (feel free to ping me if I don't give updates for too long).



---
