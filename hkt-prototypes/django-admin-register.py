# Context: django-stubs django/contrib/admin/decorators.pyi
# Reference: https://github.com/jorenham/hkt-survey/blob/main/django_admin_register.md
#
# Use case from django-stubs (typeddjango/django-stubs#3387):
# `django.contrib.admin.register` decorates a `ModelAdmin` subclass, binding it to a model.
# The decorator must:
# 1. Enforce that the registered model type matches the ModelAdmin's model type argument:
#    `@register(Quote)` on `ModelAdmin[Quote]` is valid, but `@register(Invoice)` on `ModelAdmin[Quote]`
#    must be rejected.
# 2. Preserve the exact `ModelAdmin` subclass constructor: decorating `CustomQuoteAdmin[Quote]`
#    returns `type[CustomQuoteAdmin[Quote]]`, not erased `type[ModelAdmin[Quote]]`.
#
# Without HKT:
# In standard Python, `register` is typed with an ordinary TypeVar:
#     _ModelAdminT = TypeVar("_ModelAdminT", bound=ModelAdmin[Any])
#     def register(*models: type[Model]) -> Callable[[type[_ModelAdminT]], type[_ModelAdminT]]: ...
# Because `ModelAdmin[Any]` erases the model parameter, type checkers silently accept mismatched models:
#     @admin.register(Invoice)
#     class QuoteAdmin(ModelAdmin[Quote]):  # Silently accepted! Mismatched model uncaught.
#         pass
#
# With HKT:
# The outer function binds `M: Model`, and the returned decorator object defines a generic
# `__call__` method parameterizing over the constructor `AdminT[X: Model]: ModelAdmin[X]`:
#     class _RegisterDecorator[M: Model]:
#         def __call__[AdminT[X: Model]: ModelAdmin[X]](
#             self, admin_cls: type[AdminT[M]], /
#         ) -> type[AdminT[M]]: ...
#
#     def register[M: Model](*models: type[M]) -> _RegisterDecorator[M]: ...
#
# Call sites:
# - `@register(Quote)` on `ModelAdmin[Quote]` binds `AdminT = ModelAdmin`, `M = Quote`.
# - `@register(Quote)` on `CustomQuoteAdmin[Quote]` binds `AdminT = CustomQuoteAdmin`, preserving subclass methods.
# - `@register(Invoice)` on `ModelAdmin[Quote]` fails type checking:
#   "type parameter 'M@ModelAdmin' is covariant, but 'Quote' is not a subtype of 'Invoice'".

from typing import Any, Protocol, reveal_type


class Model:
    pass


class ModelAdmin[M: Model]:
    pass


class _RegisterDecorator[M: Model](Protocol):
    def __call__[AdminT[X: Model]: ModelAdmin[X]](
        self, admin_cls: type[AdminT[M]], /
    ) -> type[AdminT[M]]:
        ...


def register[M: Model](*models: type[M]) -> _RegisterDecorator[M]:
    class Decorator:
        def __call__(self, admin_cls: Any) -> Any:
            return admin_cls

    return Decorator()


class Quote(Model):
    pass


class Invoice(Model):
    pass


class CustomQuoteAdmin[M: Model](ModelAdmin[M]):
    def custom_filter(self) -> str:
        return "custom"


# 1. Matching model on base ModelAdmin: Quote -> ModelAdmin[Quote]
@register(Quote)
class QuoteAdmin(ModelAdmin[Quote]):
    pass

reveal_type(QuoteAdmin, expected_text="type[ModelAdmin[Quote]]")

# 2. Matching model on specialized subclass: Quote -> CustomQuoteAdmin[Quote]
# Subclass constructor identity is preserved across decoration!
@register(Quote)
class CustomAdmin(CustomQuoteAdmin[Quote]):
    pass

reveal_type(CustomAdmin, expected_text="type[CustomQuoteAdmin[Quote]]")

# 3. Runtime functional validation
qa = QuoteAdmin()
assert isinstance(qa, ModelAdmin)

ca = CustomAdmin()
assert isinstance(ca, CustomQuoteAdmin)
assert ca.custom_filter() == "custom"
