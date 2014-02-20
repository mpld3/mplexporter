"""
Plotly Renderer
================
This is a renderer class to be used with an exporter for rendering plots in Plotly!
"""
import plotly

from . import plotly_utils
from .. base import Renderer
from ... exporter import Exporter


class PlotlyRenderer(Renderer):
    def __init__(self, username=None, api_key=None):
        self.output = ""
        self.username = username
        self.api_key = api_key
        self.data = []
        self.layout = {}
        self.axis_ct = 0

    def open_figure(self, fig, properties):
        self.output += "opening figure\n"
        self.layout['width'] = int(properties['figwidth']*properties['dpi'])
        self.layout['height'] = int(properties['figheight']*properties['dpi'])

    def close_figure(self, fig):
        self.output += "closing figure\n"

    def open_axes(self, ax, properties):
        self.output += "  opening axes\n"
        self.axis_ct += 1
        layout = {}
        layout['title'] = properties['title']
        xaxis = {}
        xaxis['range'] = properties['xlim']
        xaxis['title'] = properties['xlabel']
        xaxis['showgrid'] = properties['xgrid']
        yaxis = {}
        yaxis['range'] = properties['ylim']
        yaxis['title'] = properties['ylabel']
        yaxis['showgrid'] = properties['ygrid']
        layout['xaxis'] = xaxis
        layout['yaxis'] = yaxis
        self.layout = layout

    def close_axes(self, ax):
        self.output += "  closing axes\n"

    def draw_line(self, data, coordinates, style):
        self.output += "    draw line with {0} points\n".format(data.shape[0])
        data_dict = {'x': [], 'y': []}
        for xy_pair in data:
            data_dict['x'] += [xy_pair[0]]
            data_dict['y'] += [xy_pair[1]]
        data_dict['mode'] = 'lines'
        data_dict['line'] = {}
        data_dict['line']['opacity'] = style['alpha']
        data_dict['line']['width'] = style['linewidth']
        data_dict['line']['dash'] = plotly_utils.convert_dash(style['dasharray'])
        self.data += data_dict,

    def draw_markers(self, data, coordinates, style):
        self.output += "    draw {0} markers\n".format(data.shape[0])
        data_dict = {'x': [], 'y': []}
        for xy_pair in data:
            data_dict['x'] += [xy_pair[0]]
            data_dict['y'] += [xy_pair[1]]
        data_dict['mode'] = 'markers'
        data_dict['marker'] = {}
        data_dict['marker']['opacity'] = style['alpha']
        data_dict['marker']['color'] = style['facecolor']
        # need to incorporate style['edgecolor']
        data_dict['marker']['symbol'] = plotly_utils.convert_symbol(style['marker'])
        # not sure whether we need to incorporate style['markerpath']
        self.data += data_dict,


def fig_to_plotly(fig, username=None, api_key=None):
    """Convert a matplotlib figure to plotly dictionary

    """
    renderer = PlotlyRenderer(username=username, api_key=api_key)
    Exporter(renderer).run(fig)
    py = plotly.plotly(renderer.username, renderer.api_key)
    py.plot(renderer.data, layout=renderer.layout)
