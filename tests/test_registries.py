from elementalist.registries import CollectionRegistry


class Context:
    pass


class SubContext(Context):
    pass


class View:
    pass


class SubView(View):
    pass



def test_collection_registry():
    registry = CollectionRegistry()

    registry.create('test1', (Context, View))
    registry.create('test2', (Context, SubView))
    registry.create('test3', (SubContext, View))

    assert registry.lookup(Context(), View()) == None
