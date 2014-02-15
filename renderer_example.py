"""
Example Renderer
================
This shows an example of a do-nothing renderer, along with how to use it.
"""
import matplotlib.pyplot as plt

from mplexporter.renderer import Renderer
from mplexporter.exporter import Exporter


class ExampleRenderer(Renderer):
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


def run_example():
    fig, ax = plt.subplots()
    ax.plot(range(20), '-b')
    ax.plot(range(10), '.k')

    renderer = ExampleRenderer()
    exporter = Exporter(renderer)

    exporter.run(fig)
    print renderer.output


if __name__ == '__main__':
    run_example()
