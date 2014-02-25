from mplexporter.renderers import PlotlyRenderer, fig_to_plotly
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
username = 'IPython.Demo'
api_key = '1fw3zw2o13'


def plot_sin():
    # setup matplotlib plot
    x = np.arange(0,1.0,0.01)
    y1 = np.sin(2*np.pi*x)
    y2 = np.cos(4*np.pi*x)
    plt.plot(x, y1, 'b--', label='sin')
    plt.plot(x, y2, 'go', label='cos')
    plt.title("It's a Sign")
    plt.xlabel('time')
    plt.ylabel('amplitude')
    plt.legend().set_visible(True)

    # export info from matplotlib fig and render with plotly!
    fig = plt.gcf()
    fig_to_plotly(fig, username, api_key)


def two_plots():
    plt.figure(1)
    plt.subplot(211)
    plt.plot([1,2,3],[4,5,6])
    plt.subplot(212)
    plt.plot([1,2,3],[3,6,2])
    plt.title('two subplots')

    fig = plt.gcf()
    fig_to_plotly(fig, username, api_key)


def four_plots():
    fig = plt.figure() # matplotlib.figure.Figure obj
    gs = gridspec.GridSpec(3, 3)
    ax1 = fig.add_subplot(gs[0,:])
    ax1.plot([1,2,3,4,5], [10,5,10,5,10], 'r-')
    ax2 = fig.add_subplot(gs[1,:-1])
    ax2.plot([1,2,3,4], [1,4,9,16], 'k-')
    ax3 = fig.add_subplot(gs[1:, 2])
    ax3.plot([1,2,3,4], [1,10,100,1000], 'b-')
    ax4 = fig.add_subplot(gs[2,0])
    ax4.plot([1,2,3,4], [0,0,1,1], 'g-')
    ax5 = fig.add_subplot(gs[2,1])
    ax5.plot([1,2,3,4], [1,0,0,1], 'c-')
    gs.update(hspace=0.5, wspace=0.5)
    fig_to_plotly(fig, username, api_key)

if __name__ == '__main__':
    four_plots()
