from ..exporter import Exporter
from ..renderer import Renderer

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


FAKE_OUTPUT = """
opening figure
  opening axes
    draw line with 20 points
    draw 10 markers
  closing axes
closing figure
"""


class FakeRenderer(Renderer):
    def __init__(self):
        self.output = ""

    def open_figure(self, fig):
        self.output += "opening figure\n"

    def close_figure(self, fig):
        self.output += "closing figure\n"

    def open_axes(self, ax):
        self.output += "  opening axes\n"

    def close_axes(self, ax):
        self.output += "  closing axes\n"

    def draw_line(self, data, coordinates, style):
        self.output += "    draw line with {0} points\n".format(data.shape[0])

    def draw_markers(self, data, coordinates, style):
        self.output += "    draw {0} markers\n".format(data.shape[0])


def test_fakerenderer():
    fig, ax = plt.subplots()
    ax.plot(range(20), '-k')
    ax.plot(range(10), '.k')

    renderer = FakeRenderer()
    exporter = Exporter(renderer)
    exporter.run(fig)

    for line1, line2 in zip(renderer.output.strip().split(),
                            FAKE_OUTPUT.strip().split()):
        assert line1 == line2
