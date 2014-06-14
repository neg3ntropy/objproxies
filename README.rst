Simple Proxy Types
==================

The ``objproxies`` module provides some useful base classes for creating
proxies and wrappers for ordinary Python objects.  Proxy objects automatically
delegate all attribute access and operations to the proxied object.  Wrappers
are similar, but can be subclassed to allow additional attributes and
operations to be added to the wrapped object.

Note that these proxy types are not intended to be tamper-proof; the unproxied
form of an object can be readily accessed using a proxy's ``__subject__``
attribute, and some proxy types even allow this attribute to be set.  (This can
be handy for algorithms that lazily create circular structures and thus need to
be able to hand out "forward reference" proxies.)

.. contents:: **Table of Contents**

Development status
******************

At the moment this is a straightforward Python 3 port of `ProxyTypes
<http://cheeseshop.python.org/pypi/ProxyTypes>`_ wrote by Phillip J. Eby for
a part of `PEAK <http://www.eby-sarna.com/mailman/listinfo/peak>`_.

The namespace was changed from ``peak.util.proxies`` to ``objproxies``. Other
than that it should be a compatible replacement.

So far the following was accomplished:

* Streamlined files and setup
* Ported unittests and doctests
* Cleaned up syntax

TODO
++++

* Add test for the various Wrappers
* Turn the module in a package, separate functionalities in different modules
* Make sure that any new Python 3 magic method is supported
* Simplify code wherever possible

Contributions and bug reports are welcome.

Proxy Basics
************

Here's a quick demo of the ``ObjectProxy`` type::

    >>> from objproxies import ObjectProxy
    >>> p = ObjectProxy(42)

    >>> p
    42

    >>> isinstance(p, int)
    True

    >>> p.__class__
    <class 'int'>

    >>> p*2
    84

    >>> 'X' * p
    'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

    >>> hex(p)
    '0x2a'

    >>> chr(p)
    '*'

    >>> p ^ 1
    43

    >>> p ** 2
    1764

As you can see, a proxy is virtually indistinguishable from the object it
proxies, except via its ``__subject__`` attribute, and its ``type()``::

    >>> p.__subject__
    42

    >>> type(p)
    <class 'objproxies.ObjectProxy'>

You can change the ``__subject__`` of an ``ObjectProxy``, and it will then
refer to something else::

    >>> p.__subject__ = 99
    >>> p
    99
    >>> p-33
    66

    >>> p.__subject__ = "foo"
    >>> p
    'foo'

All operations are delegated to the subject, including ``setattr`` and
``delattr``::

    >>> class Dummy: pass
    >>> d = Dummy()
    >>> p = ObjectProxy(d)

    >>> p.foo = "bar"
    >>> d.foo
    'bar'

    >>> del p.foo
    >>> hasattr(d,'foo')
    False

Callback Proxies
****************

Sometimes, you may want a proxy's subject to be determined dynamically whenever
the proxy is used.  For this purpose, you can use the ``CallbackProxy`` type,
which accepts a callback function and creates a proxy that will invoke the
callback in order to get the target.  Here's a quick example of a counter that
gets incremented each time it's used, from zero to three::

    >>> from objproxies import CallbackProxy

    >>> callback = iter(range(4)).__next__
    >>> counter = CallbackProxy(callback)

    >>> counter
    0
    >>> counter
    1
    >>> str(counter)
    '2'
    >>> hex(counter)
    '0x3'

    >>> counter
    Traceback (most recent call last):
      ...
    StopIteration

As you can see, the callback is automatically invoked on any attempt to use the
proxy.  This is a somewhat silly example; a better one would be something like
a ``thread_id`` proxy that is always equal to the ID # of the thread it's
running in.

A callback proxy's callback can be obtained or changed via the ``get_callback``
and ``set_callback`` functions::

    >>> from objproxies import get_callback, set_callback
    >>> set_callback(counter, lambda: 42)

    >>> counter
    42

    >>> type(get_callback(counter))
    <class 'function'>

Lazy Proxies
************

A ``LazyProxy`` is similar to a ``DynamicProxy``, but its callback is called
at most once, and then cached::

    >>> from objproxies import LazyProxy

    >>> def callback():
    ...     print("called")
    ...     return 42

    >>> lazy = LazyProxy(callback)
    >>> lazy
    called
    42
    >>> lazy
    42

You can use the ``get_callback`` and ``set_callback`` functions on lazy
proxies, but it has no effect if the callback was already called::

    >>> set_callback(lazy, lambda: 99)
    >>> lazy
    42

But you can use the ``get_cache`` and ``set_cache`` functions to tamper with
the cached value::

    >>> from objproxies import get_cache, set_cache
    >>> get_cache(lazy)
    42
    >>> set_cache(lazy, 99)
    >>> lazy
    99

Wrappers
********

The ``ObjectWrapper``, ``CallbackWrapper`` and ``LazyWrapper`` classes are
similar to their proxy counterparts, except that they are intended to be
subclassed in order to add custom extra attributes or methods.  Any attribute
that exists in a subclass of these classes will be read or written from the
wrapper instance, instead of the wrapped object.  For example::

    >>> from objproxies import ObjectWrapper
    >>> class NameWrapper(ObjectWrapper):
    ...     name = None
    ...     def __init__(self, ob, name):
    ...         ObjectWrapper.__init__(self, ob)
    ...         self.name = name
    ...     def __str__(self):
    ...         return self.name

    >>> w = NameWrapper(42, "The Ultimate Answer")
    >>> w
    42

    >>> print(w)
    The Ultimate Answer

    >>> w * 2
    84

    >>> w.name
    'The Ultimate Answer'

Notice that any attributes you add must be defined *in the class*.  You can't
add arbitrary attributes at runtime, because they'll be set on the wrapped
object instead of the wrapper::

    >>> w.foo = 'bar'
    Traceback (most recent call last):
      ...
    AttributeError: 'int' object has no attribute 'foo'

Note that this means that all instance attributes must be implemented as either
slots, properties, or have a default value defined in the class body (like the
``name = None`` shown in the example above.

The ``CallbackWrapper`` and ``LazyWrapper`` base classes are basically the same
as ``ObjectWrapper``, except that they use a callback or cached lazy callback
instead of expecting an object as their subject.

Creating Custom Subclasses and Mixins
*************************************

In addition to all the concrete classes described above, there are also two
abstract base classes: ``AbstractProxy`` and ``AbstractWrapper``.  If you want
to create a mixin type that can be used with any of the concrete types, you
should subclass the abstract version and set ``__slots__`` to an empty list::

    >>> from objproxies import AbstractWrapper

    >>> class NamedMixin(AbstractWrapper):
    ...     __slots__ = []
    ...     name = None
    ...     def __init__(self, ob, name):
    ...         super(NamedMixin, self).__init__(ob)
    ...         self.name = name
    ...     def __str__(self):
    ...         return self.name

Then, when you mix it in with the respective base class, you can add back in
any necessary slots, or leave off ``__slots__`` to give the subclass instances
a dictionary of their own::

    >>> from objproxies import CallbackWrapper, LazyWrapper

    >>> class NamedObject(NamedMixin, ObjectWrapper): pass
    >>> class NamedCallback(NamedMixin, CallbackWrapper): pass
    >>> class NamedLazy(NamedMixin, LazyWrapper): pass

    >>> print(NamedObject(42, "The Answer"))
    The Answer

    >>> n = NamedCallback(callback, "Test")
    >>> n
    called
    42
    >>> n
    called
    42

    >>> n = NamedLazy(callback, "Once")
    >>> n
    called
    42
    >>> n
    42

Both the ``AbstractProxy`` and ``AbstractWrapper`` base classes work by
assuming that ``self.__subject__`` will be the wrapped or proxed object.  If
you don't want to use any of the standard three ways of defining
``__subject__`` (i.e., as an object, callback, or lazy callback), you will need
to subclass ``AbstractProxy`` or ``AbstractWrapper`` and provide your own way
of defining ``__subject__``.
