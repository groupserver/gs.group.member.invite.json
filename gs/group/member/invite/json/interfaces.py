from zope.interface import Interface
from zope.schema import Text 

class IApiTest(Interface):
    foo = Text(title=u'Some Foo',
                description=u"I don't know what this is",
                required=False)
