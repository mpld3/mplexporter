from numpy.testing import assert_, assert_allclose, assert_equal
from . import plt, matplotlib
from .. import utils


def test_path_data():
    circle = plt.Circle((0, 0), 1)
    vertices, codes = utils.SVG_path(circle.get_path())

    assert_allclose(vertices.shape, (25, 2))
    assert_equal(codes, ['M', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'Z'])


def test_linestyle():
    linestyles = {'solid': 'none', '-': 'none',
                  #'dashed': '6,6', '--': '6,6',
                  #'dotted': '2,2', ':': '2,2',
                  #'dashdot': '4,4,2,4', '-.': '4,4,2,4',
                  '': None, 'None': None}

    for ls, result in linestyles.items():
        line, = plt.plot([1, 2, 3], linestyle=ls)
        assert_equal(utils.get_dasharray(line), result)


def test_axis_w_fixed_formatter():
    positions, labels = [0, 1, 10], ['A','B','C']

    plt.xticks(positions, labels)
    props = utils.get_axis_properties(plt.gca().xaxis)

    assert_equal(props['tickvalues'], positions)
    # NOTE: Issue #471
    # assert_equal(props['tickformat'], labels)


def test_funcformatter_exports_major_ticklabels():
    # Test both log and normal cases:
    for scale, x, y in [
        ("linear", [0, 1], [0, 1]),
        ("log", [1, 10, 100], [0, 1, 2]),
    ]:
        fig, ax = plt.subplots()
        ax.set_xscale(scale)
        ax.plot([1, 10, 100], [0, 1, 2])
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, pos: f"t{pos}"))

        props = utils.get_axis_properties(ax.xaxis)
        plt.close(fig)

        assert_equal(props["scale"], scale)
        assert_equal(props["tickformat_formatter"], "func")
        assert_(props["tickvalues"] is not None)
        assert_equal(len(props["tickvalues"]), len(props["tickformat"]))
        assert_equal(props["tickformat"][:3], ["t0", "t1", "t2"])
