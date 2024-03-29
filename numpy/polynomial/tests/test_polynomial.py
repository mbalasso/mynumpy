"""Tests for polynomial module.

"""
from __future__ import division

import numpy as np
import numpy.polynomial.polynomial as poly
from numpy.testing import (
        TestCase, assert_almost_equal, assert_raises,
        assert_equal, assert_, run_module_suite)

def trim(x) :
    return poly.polytrim(x, tol=1e-6)

T0 = [ 1]
T1 = [ 0,  1]
T2 = [-1,  0,   2]
T3 = [ 0, -3,   0,    4]
T4 = [ 1,  0,  -8,    0,   8]
T5 = [ 0,  5,   0,  -20,   0,   16]
T6 = [-1,  0,  18,    0, -48,    0,   32]
T7 = [ 0, -7,   0,   56,   0, -112,    0,   64]
T8 = [ 1,  0, -32,    0, 160,    0, -256,    0, 128]
T9 = [ 0,  9,   0, -120,   0,  432,    0, -576,   0, 256]

Tlist = [T0, T1, T2, T3, T4, T5, T6, T7, T8, T9]


class TestConstants(TestCase) :

    def test_polydomain(self) :
        assert_equal(poly.polydomain, [-1, 1])

    def test_polyzero(self) :
        assert_equal(poly.polyzero, [0])

    def test_polyone(self) :
        assert_equal(poly.polyone, [1])

    def test_polyx(self) :
        assert_equal(poly.polyx, [0, 1])


class TestArithmetic(TestCase) :

    def test_polyadd(self) :
        for i in range(5) :
            for j in range(5) :
                msg = "At i=%d, j=%d" % (i,j)
                tgt = np.zeros(max(i,j) + 1)
                tgt[i] += 1
                tgt[j] += 1
                res = poly.polyadd([0]*i + [1], [0]*j + [1])
                assert_equal(trim(res), trim(tgt), err_msg=msg)

    def test_polysub(self) :
        for i in range(5) :
            for j in range(5) :
                msg = "At i=%d, j=%d" % (i,j)
                tgt = np.zeros(max(i,j) + 1)
                tgt[i] += 1
                tgt[j] -= 1
                res = poly.polysub([0]*i + [1], [0]*j + [1])
                assert_equal(trim(res), trim(tgt), err_msg=msg)

    def test_polymulx(self):
        assert_equal(poly.polymulx([0]), [0])
        assert_equal(poly.polymulx([1]), [0, 1])
        for i in range(1, 5):
            ser = [0]*i + [1]
            tgt = [0]*(i + 1) + [1]
            assert_equal(poly.polymulx(ser), tgt)

    def test_polymul(self) :
        for i in range(5) :
            for j in range(5) :
                msg = "At i=%d, j=%d" % (i,j)
                tgt = np.zeros(i + j + 1)
                tgt[i + j] += 1
                res = poly.polymul([0]*i + [1], [0]*j + [1])
                assert_equal(trim(res), trim(tgt), err_msg=msg)

    def test_polydiv(self) :
        # check zero division
        assert_raises(ZeroDivisionError, poly.polydiv, [1], [0])

        # check scalar division
        quo, rem = poly.polydiv([2],[2])
        assert_equal((quo, rem), (1, 0))
        quo, rem = poly.polydiv([2,2],[2])
        assert_equal((quo, rem), ((1,1), 0))

        # check rest.
        for i in range(5) :
            for j in range(5) :
                msg = "At i=%d, j=%d" % (i,j)
                ci = [0]*i + [1,2]
                cj = [0]*j + [1,2]
                tgt = poly.polyadd(ci, cj)
                quo, rem = poly.polydiv(tgt, ci)
                res = poly.polyadd(poly.polymul(quo, ci), rem)
                assert_equal(res, tgt, err_msg=msg)


class TestEvaluation(TestCase):
    # coefficients of 1 + 2*x + 3*x**2
    c1d = np.array([1., 2., 3.])
    c2d = np.einsum('i,j->ij', c1d, c1d)
    c3d = np.einsum('i,j,k->ijk', c1d, c1d, c1d)

    # some random values in [-1, 1)
    x = np.random.random((3, 5))*2 - 1
    y = poly.polyval(x, [1., 2., 3.])


    def test_polyval(self) :
        #check empty input
        assert_equal(poly.polyval([], [1]).size, 0)

        #check normal input)
        x = np.linspace(-1,1)
        y = [x**i for i in range(5)]
        for i in range(5) :
            tgt = y[i]
            res = poly.polyval(x, [0]*i + [1])
            assert_almost_equal(res, tgt)
        tgt = x*(x**2 - 1)
        res = poly.polyval(x, [0, -1, 0, 1])
        assert_almost_equal(res, tgt)

        #check that shape is preserved
        for i in range(3) :
            dims = [2]*i
            x = np.zeros(dims)
            assert_equal(poly.polyval(x, [1]).shape, dims)
            assert_equal(poly.polyval(x, [1,0]).shape, dims)
            assert_equal(poly.polyval(x, [1,0,0]).shape, dims)

    def test_polyval2d(self):
        x1, x2, x3 = self.x
        y1, y2, y3 = self.y

        #test exceptions
        assert_raises(ValueError, poly.polyval2d, x1, x2[:2], self.c2d)

        #test values
        tgt = y1*y2
        res = poly.polyval2d(x1, x2, self.c2d)
        assert_almost_equal(res, tgt)

        #test shape
        z = np.ones((2,3))
        res = poly.polyval2d(z, z, self.c2d)
        assert_(res.shape == (2,3))

    def test_polyval3d(self):
        x1, x2, x3 = self.x
        y1, y2, y3 = self.y

        #test exceptions
        assert_raises(ValueError, poly.polyval3d, x1, x2, x3[:2], self.c3d)

        #test values
        tgt = y1*y2*y3
        res = poly.polyval3d(x1, x2, x3, self.c3d)
        assert_almost_equal(res, tgt)

        #test shape
        z = np.ones((2,3))
        res = poly.polyval3d(z, z, z, self.c3d)
        assert_(res.shape == (2, 3))

    def test_polygrid2d(self):
        x1, x2, x3 = self.x
        y1, y2, y3 = self.y

        #test values
        tgt = np.einsum('i,j->ij', y1, y2)
        res = poly.polygrid2d(x1, x2, self.c2d)
        assert_almost_equal(res, tgt)

        #test shape
        z = np.ones((2,3))
        res = poly.polygrid2d(z, z, self.c2d)
        assert_(res.shape == (2, 3)*2)

    def test_polygrid3d(self):
        x1, x2, x3 = self.x
        y1, y2, y3 = self.y

        #test values
        tgt = np.einsum('i,j,k->ijk', y1, y2, y3)
        res = poly.polygrid3d(x1, x2, x3, self.c3d)
        assert_almost_equal(res, tgt)

        #test shape
        z = np.ones((2,3))
        res = poly.polygrid3d(z, z, z, self.c3d)
        assert_(res.shape == (2, 3)*3)


class TestIntegral(TestCase):

    def test_polyint(self) :
        # check exceptions
        assert_raises(ValueError, poly.polyint, [0], .5)
        assert_raises(ValueError, poly.polyint, [0], -1)
        assert_raises(ValueError, poly.polyint, [0], 1, [0,0])

        # test integration of zero polynomial
        for i in range(2, 5):
            k = [0]*(i - 2) + [1]
            res = poly.polyint([0], m=i, k=k)
            assert_almost_equal(res, [0, 1])

        # check single integration with integration constant
        for i in range(5) :
            scl = i + 1
            pol = [0]*i + [1]
            tgt = [i] + [0]*i + [1/scl]
            res = poly.polyint(pol, m=1, k=[i])
            assert_almost_equal(trim(res), trim(tgt))

        # check single integration with integration constant and lbnd
        for i in range(5) :
            scl = i + 1
            pol = [0]*i + [1]
            res = poly.polyint(pol, m=1, k=[i], lbnd=-1)
            assert_almost_equal(poly.polyval(-1, res), i)

        # check single integration with integration constant and scaling
        for i in range(5) :
            scl = i + 1
            pol = [0]*i + [1]
            tgt = [i] + [0]*i + [2/scl]
            res = poly.polyint(pol, m=1, k=[i], scl=2)
            assert_almost_equal(trim(res), trim(tgt))

        # check multiple integrations with default k
        for i in range(5) :
            for j in range(2,5) :
                pol = [0]*i + [1]
                tgt = pol[:]
                for k in range(j) :
                    tgt = poly.polyint(tgt, m=1)
                res = poly.polyint(pol, m=j)
                assert_almost_equal(trim(res), trim(tgt))

        # check multiple integrations with defined k
        for i in range(5) :
            for j in range(2,5) :
                pol = [0]*i + [1]
                tgt = pol[:]
                for k in range(j) :
                    tgt = poly.polyint(tgt, m=1, k=[k])
                res = poly.polyint(pol, m=j, k=range(j))
                assert_almost_equal(trim(res), trim(tgt))

        # check multiple integrations with lbnd
        for i in range(5) :
            for j in range(2,5) :
                pol = [0]*i + [1]
                tgt = pol[:]
                for k in range(j) :
                    tgt = poly.polyint(tgt, m=1, k=[k], lbnd=-1)
                res = poly.polyint(pol, m=j, k=range(j), lbnd=-1)
                assert_almost_equal(trim(res), trim(tgt))

        # check multiple integrations with scaling
        for i in range(5) :
            for j in range(2,5) :
                pol = [0]*i + [1]
                tgt = pol[:]
                for k in range(j) :
                    tgt = poly.polyint(tgt, m=1, k=[k], scl=2)
                res = poly.polyint(pol, m=j, k=range(j), scl=2)
                assert_almost_equal(trim(res), trim(tgt))

    def test_polyint_axis(self):
        # check that axis keyword works
        c2d = np.random.random((3, 4))

        tgt = np.vstack([poly.polyint(c) for c in c2d.T]).T
        res = poly.polyint(c2d, axis=0)
        assert_almost_equal(res, tgt)

        tgt = np.vstack([poly.polyint(c) for c in c2d])
        res = poly.polyint(c2d, axis=1)
        assert_almost_equal(res, tgt)

        tgt = np.vstack([poly.polyint(c, k=3) for c in c2d])
        res = poly.polyint(c2d, k=3, axis=1)
        assert_almost_equal(res, tgt)


class TestDerivative(TestCase) :

    def test_polyder(self) :
        # check exceptions
        assert_raises(ValueError, poly.polyder, [0], .5)
        assert_raises(ValueError, poly.polyder, [0], -1)

        # check that zeroth deriviative does nothing
        for i in range(5) :
            tgt = [0]*i + [1]
            res = poly.polyder(tgt, m=0)
            assert_equal(trim(res), trim(tgt))

        # check that derivation is the inverse of integration
        for i in range(5) :
            for j in range(2,5) :
                tgt = [0]*i + [1]
                res = poly.polyder(poly.polyint(tgt, m=j), m=j)
                assert_almost_equal(trim(res), trim(tgt))

        # check derivation with scaling
        for i in range(5) :
            for j in range(2,5) :
                tgt = [0]*i + [1]
                res = poly.polyder(poly.polyint(tgt, m=j, scl=2), m=j, scl=.5)
                assert_almost_equal(trim(res), trim(tgt))

    def test_polyder_axis(self):
        # check that axis keyword works
        c2d = np.random.random((3, 4))

        tgt = np.vstack([poly.polyder(c) for c in c2d.T]).T
        res = poly.polyder(c2d, axis=0)
        assert_almost_equal(res, tgt)

        tgt = np.vstack([poly.polyder(c) for c in c2d])
        res = poly.polyder(c2d, axis=1)
        assert_almost_equal(res, tgt)


class TestVander(TestCase):
    # some random values in [-1, 1)
    x = np.random.random((3, 5))*2 - 1


    def test_polyvander(self) :
        # check for 1d x
        x = np.arange(3)
        v = poly.polyvander(x, 3)
        assert_(v.shape == (3, 4))
        for i in range(4) :
            coef = [0]*i + [1]
            assert_almost_equal(v[..., i], poly.polyval(x, coef))

        # check for 2d x
        x = np.array([[1, 2], [3, 4], [5, 6]])
        v = poly.polyvander(x, 3)
        assert_(v.shape == (3, 2, 4))
        for i in range(4) :
            coef = [0]*i + [1]
            assert_almost_equal(v[..., i], poly.polyval(x, coef))

    def test_polyvander2d(self) :
        # also tests polyval2d for non-square coefficient array
        x1, x2, x3 = self.x
        c = np.random.random((2, 3))
        van = poly.polyvander2d(x1, x2, [1, 2])
        tgt = poly.polyval2d(x1, x2, c)
        res = np.dot(van, c.flat)
        assert_almost_equal(res, tgt)

        # check shape
        van = poly.polyvander2d([x1], [x2], [1, 2])
        assert_(van.shape == (1, 5, 6))


    def test_polyvander3d(self) :
        # also tests polyval3d for non-square coefficient array
        x1, x2, x3 = self.x
        c = np.random.random((2, 3, 4))
        van = poly.polyvander3d(x1, x2, x3, [1, 2, 3])
        tgt = poly.polyval3d(x1, x2, x3, c)
        res = np.dot(van, c.flat)
        assert_almost_equal(res, tgt)

        # check shape
        van = poly.polyvander3d([x1], [x2], [x3], [1, 2, 3])
        assert_(van.shape == (1, 5, 24))


class TestCompanion(TestCase):

    def test_raises(self):
        assert_raises(ValueError, poly.polycompanion, [])
        assert_raises(ValueError, poly.polycompanion, [1])

    def test_dimensions(self):
        for i in range(1, 5):
            coef = [0]*i + [1]
            assert_(poly.polycompanion(coef).shape == (i, i))

    def test_linear_root(self):
        assert_(poly.polycompanion([1, 2])[0, 0] == -.5)


class TestMisc(TestCase) :

    def test_polyfromroots(self) :
        res = poly.polyfromroots([])
        assert_almost_equal(trim(res), [1])
        for i in range(1,5) :
            roots = np.cos(np.linspace(-np.pi, 0, 2*i + 1)[1::2])
            tgt = Tlist[i]
            res = poly.polyfromroots(roots)*2**(i-1)
            assert_almost_equal(trim(res),trim(tgt))

    def test_polyroots(self) :
        assert_almost_equal(poly.polyroots([1]), [])
        assert_almost_equal(poly.polyroots([1, 2]), [-.5])
        for i in range(2,5) :
            tgt = np.linspace(-1, 1, i)
            res = poly.polyroots(poly.polyfromroots(tgt))
            assert_almost_equal(trim(res), trim(tgt))

    def test_polyfit(self) :
        def f(x) :
            return x*(x - 1)*(x - 2)

        # Test exceptions
        assert_raises(ValueError, poly.polyfit, [1],    [1],     -1)
        assert_raises(TypeError,  poly.polyfit, [[1]],  [1],      0)
        assert_raises(TypeError,  poly.polyfit, [],     [1],      0)
        assert_raises(TypeError,  poly.polyfit, [1],    [[[1]]],  0)
        assert_raises(TypeError,  poly.polyfit, [1, 2], [1],      0)
        assert_raises(TypeError,  poly.polyfit, [1],    [1, 2],   0)
        assert_raises(TypeError,  poly.polyfit, [1],    [1],   0, w=[[1]])
        assert_raises(TypeError,  poly.polyfit, [1],    [1],   0, w=[1,1])

        # Test fit
        x = np.linspace(0,2)
        y = f(x)
        #
        coef3 = poly.polyfit(x, y, 3)
        assert_equal(len(coef3), 4)
        assert_almost_equal(poly.polyval(x, coef3), y)
        #
        coef4 = poly.polyfit(x, y, 4)
        assert_equal(len(coef4), 5)
        assert_almost_equal(poly.polyval(x, coef4), y)
        #
        coef2d = poly.polyfit(x, np.array([y,y]).T, 3)
        assert_almost_equal(coef2d, np.array([coef3,coef3]).T)
        # test weighting
        w = np.zeros_like(x)
        yw = y.copy()
        w[1::2] = 1
        yw[0::2] = 0
        wcoef3 = poly.polyfit(x, yw, 3, w=w)
        assert_almost_equal(wcoef3, coef3)
        #
        wcoef2d = poly.polyfit(x, np.array([yw,yw]).T, 3, w=w)
        assert_almost_equal(wcoef2d, np.array([coef3,coef3]).T)
        # test scaling with complex values x points whose square
        # is zero when summed.
        x = [1, 1j, -1, -1j]
        assert_almost_equal(poly.polyfit(x, x, 1), [0, 1])


    def test_polytrim(self) :
        coef = [2, -1, 1, 0]

        # Test exceptions
        assert_raises(ValueError, poly.polytrim, coef, -1)

        # Test results
        assert_equal(poly.polytrim(coef), coef[:-1])
        assert_equal(poly.polytrim(coef, 1), coef[:-3])
        assert_equal(poly.polytrim(coef, 2), [0])

    def test_polyline(self) :
        assert_equal(poly.polyline(3,4), [3, 4])


if __name__ == "__main__":
    run_module_suite()
