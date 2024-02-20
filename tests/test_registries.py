import pytest
from elementalist import registries


class Context:
    pass


class SubContext(Context):
    pass


class View:
    pass


class SubView(View):
    pass



def test_collection_registry():
    registry = registries.CollectionRegistry()

    t1 = registry.create('test1', (Context, View))
    t2 = registry.create('test2', (Context, SubView))
    t3 = registry.create('test3', (SubContext, View))

    assert registry.match(Context(), View()) == [t1]
    assert registry.match(SubContext(), View()) == [t3, t1]
    assert registry.match(SubContext(), SubView()) == [t2, t3, t1]



def test_mapping_registry():
    registry = registries.MappingRegistry()

    t1 = registry.create('test1', (Context, View))
    t2 = registry.create('test2', (Context, SubView))
    t3 = registry.create('test3', (SubContext, View))

    assert registry.match(Context(), View()) == [t1]
    assert registry.match(SubContext(), View()) == [t3, t1]
    assert registry.match(SubContext(), SubView()) == [t2, t3, t1]

    assert registry.lookup(Context(), View()) == t1
    assert registry.lookup(SubContext(), View()) == t3

    with pytest.raises(LookupError):
        # Ambiguity : could not determine the most precise.
        registry.lookup(SubContext(), SubView())


def test_named_registry():
    registry = registries.NamedElementRegistry()

    t1 = registry.create('test1', (Context, View), name="1")
    t1b = registry.create('test1b', (Context, SubView), name="1")
    t2 = registry.create('test2', (Context, SubView), name="2")
    t3 = registry.create('test3', (SubContext, View), name="3")

    assert registry.match(SubContext(), SubView()) == {
        "1": t1b, "2": t2, "3": t3
    }

    assert registry.get(Context(), View(), name="1") == t1
    assert registry.get(SubContext(), SubView(), name="1") == t1b
    assert registry.get(SubContext(), SubView(), name="2") == t2
    assert registry.get(SubContext(), SubView(), name="3") == t3


def test_specific_registry():
    registry = registries.SpecificElementRegistry()

    t1 = registry.create('test1', (Context, View), name="1")
    t1b = registry.create('test1b', (Context, SubView), name="1")
    t2 = registry.create('test2', (Context, SubView), name="2")
    t3 = registry.create('test3', (SubContext, View), name="3")

    assert registry.match(SubContext(), SubView()) == []
    assert registry.get(Context(), View(), name="1") == t1
