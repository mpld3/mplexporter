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
    plt.figure(1)
    plt.subplot(411)
    plt.plot([1,2,3],[4,5,6], 'k-', label='first')
    plt.xlabel('x1')
    plt.subplot(412)
    plt.plot([1,2,3],[3,6,2], 'b--', label='second')
    plt.xlabel('x2')
    plt.subplot(413)
    plt.plot([10,11,12,13], [1,0,1,0], 'g-.', label='third')
    plt.xlabel('x3')
    plt.subplot(414)
    plt.plot([20,21,22,23], [0,1,0,1], 'r-', label = 'fourth')
    plt.xlabel('x4')
    plt.title('four subplots')
    fig = plt.gcf()
    fig_to_plotly(fig, username, api_key)

if __name__ == '__main__':
    plot_sin()
