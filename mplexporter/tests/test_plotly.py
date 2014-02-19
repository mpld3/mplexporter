from .. exporter import Exporter
from .. renderers.plotly import PlotlyRenderer

import numpy as np
import matplotlib.pyplot as plt
username = 'IPython.Demo'
api_key = '1fw3zw2o13'


def plot_sin():
    # setup matplotlib plot
    x = np.arange(0,1.0,0.01)
    y1 = np.sin(2*np.pi*x)
    y2 = np.cos(4*np.pi*x)
    plt.plot(x, y1, 'b--', label='sin')
    plt.plot(x, y2, 'ro', label='cos')
    plt.title("It's a Sign")
    plt.xlabel('time')
    plt.ylabel('amplitude')
    plt.legend().set_visible(True)

    # export info from matplotlib fig and render with plotly!
    fig = plt.gcf()
    renderer = PlotlyRenderer(username=username, api_key=api_key)
    exporter = Exporter(renderer)
    exporter.run(fig)

    # check output from PlotlyRenderer against expected output
    for line1, line2 in zip(renderer.output.strip().split(),
                        PLOT_SIN_OUTPUT.strip().split()):
        assert line1 == line2


PLOT_SIN_OUTPUT = """
opening figure
  opening axes
    draw line with 100 points
    draw 100 markers
  closing axes
closing figure
"""