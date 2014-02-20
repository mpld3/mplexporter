from mplexporter.renderers import PlotlyRenderer, fig_to_plotly
import numpy as np
import matplotlib.pyplot as plt
username = 'IPython.Demo'
api_key = '1fw3zw2o13'


def plot_sin():
    # setup matplotlib plot
    x = np.arange(0,1.0,0.01)
    y1 = np.sin(2*np.pi*x)
    y2 = np.cos(4*np.pi*x)
    plt.figure(1)
    plt.subplot(211)
    plt.plot(x, y1, 'b--', label='sin')
    plt.subplot(212)
    plt.plot(x, y2, 'go', label='cos')
    plt.title("It's a Sign")
    plt.xlabel('time')
    plt.ylabel('amplitude')
    plt.legend().set_visible(True)

    # export info from matplotlib fig and render with plotly!
    fig = plt.gcf()
    plt.show()
    fig_to_plotly(fig, username, api_key)

if __name__ == '__main__':
    plot_sin()
