# -*- coding: utf-8 -*-

"""
The free hypergraph category, i.e. diagrams with swaps and spiders.

Spiders are also known as dagger special commutative Frobenius algebras.

Summary
-------

.. autosummary::
    :template: class.rst
    :nosignatures:
    :toctree:

    Ob
    Ty
    Diagram
    Box
    Cup
    Cap
    Swap
    Spider
    Category
    Functor

.. admonition:: Functions

    .. autosummary::
        :template: function.rst
        :nosignatures:
        :toctree:

        coherence
"""

from __future__ import annotations

from discopy import compact, pivotal
from discopy.cat import factory
from discopy.utils import factory_name, assert_isatomic


class Ob(pivotal.Ob):
    """
    A hypergraph object is a self-dual pivotal object.

    Parameters:
        name : The name of the object.
    """
    l = r = property(lambda self: self)


@factory
class Ty(pivotal.Ty):
    """
    A hypergraph type is a pivotal type with hypergraph objects inside.

    Parameters:
        inside (frobenius.Ob) : The objects inside the type.
    """
    ob_factory = Ob


@factory
class Diagram(compact.Diagram):
    """
    A hypergraph diagram is a compact diagram with :class:`Spider` boxes.

    Parameters:
        inside(Layer) : The layers of the diagram.
        dom (Ty) : The domain of the diagram, i.e. its input.
        cod (Ty) : The codomain of the diagram, i.e. its output.
    """
    @classmethod
    def spiders(cls, n_legs_in: int, n_legs_out: int, typ: Ty) -> Diagram:
        """ Constructs a diagram of interleaving spiders. """
        result = cls.id().tensor(*[
            cls.spider_factory(n_legs_in, n_legs_out, x) for x in typ])
        for i, t in enumerate(typ):
            for j in range(n_legs_in - 1):
                result <<= result.dom[:i * j + i + j] @ cls.swap(
                    t, result.dom[i * j + i + j:i * n_legs_in + j]
                ) @ result.dom[i * n_legs_in + j + 1:]
            for j in range(n_legs_out - 1):
                result >>= result.cod[:i * j + i + j] @ cls.swap(
                    result.cod[i * j + i + j:i * n_legs_out + j], t
                ) @ result.cod[i * n_legs_out + j + 1:]
        return result


class Box(compact.Box, Diagram):
    """
    A hypergraph box is a compact box in a hypergraph diagram.

    Parameters:
        name (str) : The name of the box.
        dom (Ty) : The domain of the box, i.e. its input.
        cod (Ty) : The codomain of the box, i.e. its output.
    """
    __ambiguous_inheritance__ = (compact.Box, )
    ty_factory = Ty


class Cup(compact.Cup, Box):
    """
    A hypergraph cup is a compact cup in a hypergraph diagram.

    Parameters:
        left (pivotal.Ty) : The atomic type.
        right (pivotal.Ty) : Its adjoint.
    """
    __ambiguous_inheritance__ = (compact.Cup, )
    ty_factory = Ty


class Cap(compact.Cap, Box):
    """
    A hypergraph cap is a compact cap in a hypergraph diagram.

    Parameters:
        left (pivotal.Ty) : The atomic type.
        right (pivotal.Ty) : Its adjoint.
    """
    __ambiguous_inheritance__ = (compact.Cap, )
    ty_factory = Ty


class Swap(compact.Swap, Box):
    """
    A hypergraph swap is a compact swap in a hypergraph diagram.

    Parameters:
        left (pivotal.Ty) : The type on the top left and bottom right.
        right (pivotal.Ty) : The type on the top right and bottom left.
    """
    __ambiguous_inheritance__ = (compact.Swap, )
    ty_factory = Ty


class Spider(Box):
    """
    The spider with :code:`n_legs_in` and :code:`n_legs_out`
    on a given atomic type.

    Parameters:
        n_legs_in : The number of legs in.
        n_legs_out : The number of legs out.
        typ : The type of the spider.

    Examples
    --------
    >>> x = Ty('x')
    >>> spider = Spider(1, 2, x)
    >>> assert spider.dom == x and spider.cod == x @ x
    """
    def __init__(self, n_legs_in: int, n_legs_out: int, typ: Ty, **params):
        self.typ = typ
        assert_isatomic(typ)
        name = "Spider({}, {}, {})".format(n_legs_in, n_legs_out, typ)
        dom, cod = typ ** n_legs_in, typ ** n_legs_out
        cup_like = (n_legs_in, n_legs_out) in ((2, 0), (0, 2))
        params = dict(dict(
            draw_as_spider=not cup_like,
            draw_as_wires=cup_like,
            color="black", drawing_name=""), **params)
        Box.__init__(self, name, dom, cod, **params)

    def __repr__(self):
        return factory_name(type(self)) + "({}, {}, {})".format(
            len(self.dom), len(self.cod), repr(self.typ))

    def dagger(self):
        return type(self)(len(self.cod), len(self.dom), self.typ)

    def decompose(self):
        return self._decompose_spiders(len(self.dom), len(self.cod),
                                       self.typ)

    @classmethod
    def _decompose_spiders(cls, n_legs_in, n_legs_out, typ):
        if n_legs_out > n_legs_in:
            return cls._decompose_spiders(n_legs_out, n_legs_in,
                                          typ).dagger()

        if n_legs_in == 1 and n_legs_out == 0:
            return cls(1, 0, typ)
        if n_legs_in == 1 and n_legs_out == 1:
            return Id(typ)

        if n_legs_out != 1:
            return (cls._decompose_spiders(n_legs_in, 1, typ)
                    >> cls._decompose_spiders(1, n_legs_out, typ))

        if n_legs_in == 2:
            return cls(2, 1, typ)

        if n_legs_in % 2 == 1:
            return (cls._decompose_spiders(n_legs_in - 1, 1, typ)
                    @ Id(typ) >> cls(2, 1, typ))

        new_in = n_legs_in // 2
        half_spider = cls._decompose_spiders(new_in, 1, typ)
        return half_spider @ half_spider >> cls(2, 1, typ)

    @property
    def l(self):
        return type(self)(len(self.dom), len(self.cod), self.typ.l)

    @property
    def r(self):
        return type(self)(len(self.dom), len(self.cod), self.typ.r)


class Category(compact.Category):
    """
    A hypergraph category is a compact category with a method :code:`spiders`.

    Parameters:
        ob : The objects of the category, default is :class:`pivotal.Ty`.
        ar : The arrows of the category, default is :class:`Diagram`.
    """
    ob, ar = Ty, Diagram


class Functor(compact.Functor):
    """
    A hypergraph functor is a compact functor that preserves spiders.

    Parameters:
        ob (Mapping[Ty, Ty]) : Map from atomic :class:`Ty` to :code:`cod.ob`.
        ar (Mapping[Box, Diagram]) : Map from :class:`Box` to :code:`cod.ar`.
        cod (Category) : The codomain of the functor.
    """
    dom = cod = Category()

    def __call__(self, other):
        if isinstance(other, Spider):
            return self.cod.ar.spiders(
                len(other.dom), len(other.cod), self(other.typ))
        return super().__call__(other)


def coherence(factory):
    def method(cls, a: int, b: int, x: Ty, phase=None) -> Diagram:
        if len(x) == 0 and phase is None:
            return cls.id(x)
        if len(x) == 1:
            return factory(a, b, x, phase)
        if phase is not None:  # Coherence for phase shifters.
            shift = cls.tensor(*[factory(1, 1, obj, phase) for obj in x])
            return method(cls, a, 1, x) >> shift >> method(cls, 1, b, x)
        if (a, b) in [(1, 0), (0, 1)]: # Coherence for (co)units.
            return cls.tensor(*[factory(a, b, obj) for obj in x])
        # Coherence for binary (co)products.
        if (a, b) in [(1, 2), (2, 1)]:
            spiders, braids = (
                factory(a, b, x[0], phase) @ method(cls, a, b, x[1:], phase),
                x[0] @ cls.braid(x[0], x[1:]) @ x[1:])
            return spiders >> braids if (a, b) == (1, 2) else braids >> spiders
        if a == 1:  # We can now assume b > 2.
            return method(cls, 1, b - 1, x)\
                >> method(cls, 1, 2, x) @ (x ** (b - 2))
        if b == 1:  # We can now assume a > 2.
            return method(cls, 2, 1, x) @ (x ** (a - 2))\
                >> method(cls, a - 1, 1, x)
        return method(cls, a, 1, x) >> method(cls, 1, b, x)

    return classmethod(method)


for cls in [Diagram, Box, Swap, Cup, Cap]:
    cls.ty_factory = Ty

Diagram.cup_factory, Diagram.cap_factory = Cup, Cap
Diagram.braid_factory, Diagram.spider_factory = Swap, Spider

Id = Diagram.id
