from pytest import raises
from discopy.rigid import *


def test_Ob_init():
    with raises(TypeError) as err:
        Ob('x', z='y')
    assert cat.Ob('x') == Ob('x')


def test_Ob_eq():
    assert Ob('a') == Ob('a').l.r and Ob('a') != 'a'


def test_Ob_hash():
    a = Ob('a')
    assert {a: 42}[a] == 42


def test_Ob_repr():
    assert repr(Ob('a', z=42)) == "rigid.Ob('a', z=42)"


def test_Ob_str():
    a = Ob('a')
    assert str(a) == "a" and str(a.r) == "a.r" and str(a.l) == "a.l"


def test_Ty_z():
    with raises(TypeError):
        Ty('x', 'y').z
    with raises(TypeError):
        Ty().z
    assert Ty('x').l.z == -1


def test_PRO_r():
    assert PRO(2).r == PRO(2)


def test_Diagram_cups():
    with raises(TypeError) as err:
        Diagram.cups('x', Ty('x'))
    assert str(err.value) == messages.type_err(Ty, 'x')
    with raises(TypeError) as err:
        Diagram.cups(Ty('x'), 'x')
    assert str(err.value) == messages.type_err(Ty, 'x')


def test_Diagram_caps():
    with raises(TypeError) as err:
        Diagram.caps('x', Ty('x'))
    assert str(err.value) == messages.type_err(Ty, 'x')
    with raises(TypeError) as err:
        Diagram.caps(Ty('x'), 'x')
    assert str(err.value) == messages.type_err(Ty, 'x')


def test_Diagram_normal_form():
    x = Ty('x')
    assert Id(x).transpose(left=True).normal_form() == Id(x.l)
    assert Id(x).transpose().normal_form() == Id(x.r)

    f = Box('f', Ty('a'), Ty('b') @ Ty('c'))
    assert f.normal_form() == f
    assert f.transpose().transpose(left=True).normal_form() == f
    assert f.transpose(left=True).transpose().normal_form() == f
    diagram = f\
        .transpose(left=True).transpose(left=True).transpose().transpose()
    assert diagram.normal_form() == f

    Eckmann_Hilton = Box('s0', Ty(), Ty()) @ Box('s1', Ty(), Ty())
    with raises(NotImplementedError) as err:
        Eckmann_Hilton.normal_form()
    assert str(err.value) == messages.is_not_connected(Eckmann_Hilton)


def test_Cup_init():
    with raises(TypeError):
        Cup('x', Ty('y'))
    with raises(TypeError):
        Cup(Ty('x'), 'y')
    t = Ty('n', 's')
    with raises(ValueError) as err:
        Cup(t, t.r)
    assert str(err.value) == messages.cup_vs_cups(t, t.r)
    with raises(ValueError) as err:
        Cup(Ty(), Ty())
    assert str(err.value) == messages.cup_vs_cups(Ty(), Ty().l)


def test_Cap_init():
    with raises(TypeError):
        Cap('x', Ty('y'))
    with raises(TypeError):
        Cap(Ty('x'), 'y')
    t = Ty('n', 's')
    with raises(ValueError) as err:
        Cap(t, t.l)
    assert str(err.value) == messages.cap_vs_caps(t, t.l)
    with raises(ValueError) as err:
        Cap(Ty(), Ty())
    assert str(err.value) == messages.cap_vs_caps(Ty(), Ty())


def test_Cup_Cap_dagger():
    n = Ty('n')
    assert Cap(n, n.l).dagger() == Cup(n, n.l)
    assert Cup(n, n.l).dagger() == Cap(n, n.l)


def test_Cup_Cap_adjoint():
    n = Ty('n')
    assert Cap(n, n.l).l == Cap(n.l.l, n.l)
    assert Cap(n, n.l).r == Cap(n, n.r)
    assert Cup(n, n.r).l == Cup(n, n.l)
    assert Cup(n, n.r).r == Cup(n.r.r, n.r)


def test_AxiomError():
    n, s = Ty('n'), Ty('s')
    with raises(AxiomError) as err:
        Cup(n, n)
    assert str(err.value) == messages.are_not_adjoints(n, n)
    with raises(AxiomError) as err:
        Cup(n, s)
    assert str(err.value) == messages.are_not_adjoints(n, s)
    with raises(AxiomError) as err:
        Cup(n, n.l.l)
    assert str(err.value) == messages.are_not_adjoints(n, n.l.l)
    with raises(AxiomError) as err:
        Cap(n, n.l.l)
    assert str(err.value) == messages.are_not_adjoints(n, n.l.l)


def test_adjoint():
    n, s = map(Ty, 'ns')
    Bob = Box('Bob', Ty(), n)
    eats = Box('eats', Ty(), n.r @ s)
    Bob_l = Box('Bob', Ty(), n.l, _z=-1)
    Bob_r = Box('Bob', Ty(), n.r, _z=1)
    eats_l = Box('eats', Ty(), s.l @ n, _z=-1)
    eats_r = Box('eats', Ty(), s.r @ n.r.r, _z=1)
    assert Bob.l.z == -1 and Bob.z == 0 and Bob.r.z == 1
    assert Bob.l == Bob_l and Bob.r == Bob_r
    assert eats.l == eats_l and eats.r == eats_r
    diagram = Bob @ eats >> Cup(n, n.r) @ Id(s)
    assert diagram.l == Bob_l >> eats_l @ Id(n.l) >> Id(s.l) @ Cup(n, n.l)
    assert diagram.r == Bob_r >> eats_r @ Id(n.r) >> Id(s.r) @ Cup(n.r.r, n.r)


def test_id_adjoint():
    assert Id(Ty('n')).r == Id(Ty('n').r)
    assert Id(Ty('n')).l == Id(Ty('n').l)
    assert Id().l == Id() == Id().r


def test_transpose_box():
    n = Ty('s')
    Bob = Box('Bob', Ty(), n)
    Bob_Tl = Box('Bob', n.l, Ty(), _z=-1, _dagger=True)
    Bob_Tr = Box('Bob', n.r, Ty(), _z=1, _dagger=True)
    assert Bob.transpose_box(0, left=True) == Cap(n.r, n) >> Bob_Tr @ Id(n)
    assert Bob.transpose_box(0) == Cap(n, n.l) >> Id(n) @ Bob_Tl


def test_sum_adjoint():
    x = Ty('x')
    two, boxes = Box('two', x, x), Box('boxes', x, x)
    two_boxes = two + boxes
    assert two_boxes.l == two.l + boxes.l
    assert two_boxes.l.r == two_boxes


def test_cup_chaining():
    n, s, p = map(Ty, "nsp")
    A = Box('A', Ty(), n @ p)
    V = Box('V', Ty(), n.r @ s @ n.l)
    B = Box('B', Ty(), p.r @ n)

    diagram = (A @ V @ B).cup(1, 5).cup(0, 1).cup(1, 2)
    expected_diagram = Diagram(
        dom=Ty(), cod=Ty('s'),
        boxes=[
            A, V, B, Swap(p, n.r), Swap(p, s), Swap(p, n.l), Cup(p, p.r),
            Cup(n, n.r), Cup(n.l, n)],
        offsets=[0, 2, 5, 1, 2, 3, 4, 0, 1])
    assert diagram == expected_diagram

    with raises(ValueError):
        Id(n @ n.r).cup(0, 2)
