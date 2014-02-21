from ..exporter import Exporter
from ..renderers import PlotlyRenderer

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


T1_OUTPUT = """
opening figure
  opening axis 1
    draw line with 20 points
    draw 10 markers
  closing axis 1
closing figure
"""

T2_OUTPUT = """
opening figure
  opening axis 1
    draw line with 20 points
  closing axis 1
  opening axis 2
    draw 10 markers
  closing axis 2
closing figure
"""


def test_1():
    fig, ax = plt.subplots()
    ax.plot(range(20), '-k')
    ax.plot(range(10), '.k')

    renderer = PlotlyRenderer()
    exporter = Exporter(renderer)
    exporter.run(fig)

    for line1, line2 in zip(renderer.output.strip().split(),
                            T1_OUTPUT.strip().split()):
        assert line1 == line2


def test_2():
    plt.figure(1)
    plt.subplot(211)
    plt.plot(range(20), '-k')
    plt.subplot(212)
    plt.plot(range(10), '.k')
    fig = plt.gcf()

    renderer = PlotlyRenderer()
    exporter = Exporter(renderer)
    exporter.run(fig)
    plt.show()
    print renderer.output

    for line1, line2 in zip(renderer.output.strip().split(),
                            T2_OUTPUT.strip().split()):
        assert line1 == line2