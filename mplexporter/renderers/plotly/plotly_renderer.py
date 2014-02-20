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
        layout = {
            'title': properties['title'],
            'xaxis': {
                'range': properties['xlim'],
                'title': properties['xlabel'],
                'showgrid': properties['xgrid']
            },
            'yaxis': {
                'range': properties['ylim'],
                'title': properties['ylabel'],
                'showgrid': properties['ygrid'],
            }
        }
        for key, value in layout.items():
            self.layout[key] = value

    def close_axes(self, ax):
        self.output += "  closing axes\n"

    def draw_line(self, data, coordinates, style):
        if coordinates == 'data':
            self.output += "    draw line with {0} points\n".format(data.shape[0])
            trace = {
                'mode': 'lines',
                'x': [xy_pair[0] for xy_pair in data],
                'y': [xy_pair[1] for xy_pair in data],
                'line': {
                    'opacity': style['alpha'],
                    'width': style['linewidth'],
                    'dash': plotly_utils.convert_dash(style['dasharray'])
                }
            }
            self.data += trace,
        else:
            self.output += "    received {}-point line with 'figure' coordinates, skipping!".format(data.shape[0])

    def draw_markers(self, data, coordinates, style):
        if coordinates == 'data':
            self.output += "    draw {0} markers\n".format(data.shape[0])
            trace = {
                'mode': 'markers',
                'x': [xy_pair[0] for xy_pair in data],
                'y': [xy_pair[1] for xy_pair in data],
                'marker': {
                    'opacity': style['alpha'],
                    'color': style['facecolor'],
                    'symbol': plotly_utils.convert_symbol(style['marker']),
                    'line': {
                        'color': style['edgecolor'],
                        'width': style['edgewidth']
                    }
                }
            }
            # not sure whether we need to incorporate style['markerpath']
            self.data += trace,
        else:
            self.output += "    received {} markers with 'figure' coordinates, skipping!".format(data.shape[0])


def fig_to_plotly(fig, username=None, api_key=None, notebook=False):
    """Convert a matplotlib figure to plotly dictionary

    """
    renderer = PlotlyRenderer(username=username, api_key=api_key)
    Exporter(renderer).run(fig)
    py = plotly.plotly(renderer.username, renderer.api_key)
    if notebook:
        return py.iplot(renderer.data, layout=renderer.layout)
    else:
        py.plot(renderer.data, layout=renderer.layout)
