from numpy.testing import assert_allclose, assert_equal
import matplotlib.pyplot as plt
from .. import utils


def test_path_data():
    circle = plt.Circle((0, 0), 1)
    vertices, codes = utils.SVG_path(circle.get_path())

    assert_allclose(vertices.shape, (25, 2))
    assert_equal(codes, ['M', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'Z'])

def test_axis_w_fixed_formatter():
    positions, labels = [0, 1, 10], ['A','B','C']

    plt.xticks(positions, labels)
    props = utils.get_axis_properties(plt.gca().xaxis)

    assert_equal(props['tickvalues'], positions)
    assert_equal(props['tickformat'], labels)
