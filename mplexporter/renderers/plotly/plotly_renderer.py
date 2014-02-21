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
        self.configure_subplots()
        self.layout['showlegend'] = False

    def open_axes(self, ax, properties):
        self.axis_ct += 1
        self.output += "  opening axis {}\n".format(self.axis_ct)
        if self.axis_ct == 1:
            layout = {
                'title': properties['title'],
                'xaxis': {
                    'range': properties['xlim'],
                    'title': properties['xlabel'],
                    'showgrid': properties['xgrid']
                },
                'yaxis': {
                    'domain': [0,1],
                    'range': properties['ylim'],
                    'title': properties['ylabel'],
                    'showgrid': properties['ygrid'],
                }
            }
        else:
            layout = {
                'title': properties['title'],
                'xaxis{}'.format(self.axis_ct): {
                    'range': properties['xlim'],
                    'title': properties['xlabel'],
                    'showgrid': properties['xgrid']
                },
                'yaxis{}'.format(self.axis_ct): {
                    'domain': [0,1],
                    'range': properties['ylim'],
                    'title': properties['ylabel'],
                    'showgrid': properties['ygrid'],
                }
            }
        for key, value in layout.items():
            self.layout[key] = value

    def close_axes(self, ax):
        self.output += "  closing axis {}\n".format(self.axis_ct)

    def draw_line(self, data, coordinates, style):
        if coordinates == 'data':
            self.output += "    draw line with {0} points\n".format(data.shape[0])
            if self.axis_ct == 1:
                trace = {
                    'mode': 'lines',
                    'x': [xy_pair[0] for xy_pair in data],
                    'y': [xy_pair[1] for xy_pair in data],
                    'line': {
                        'opacity': style['alpha'],
                        'color': style['color'],
                        'width': style['linewidth'],
                        'dash': plotly_utils.convert_dash(style['dasharray'])
                    }
                }
                self.data += trace,
            else:
                trace = {
                    'mode': 'lines',
                    'x': [xy_pair[0] for xy_pair in data],
                    'y': [xy_pair[1] for xy_pair in data],
                    'xaxis': 'x{}'.format(self.axis_ct),
                    'yaxis': 'y{}'.format(self.axis_ct),
                    'line': {
                        'opacity': style['alpha'],
                        'color': style['color'],
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

    def configure_subplots(self):
        num_plots = self.axis_ct
        if num_plots > 1:
            spacing = 0.3/num_plots # magic numbers! change this!
            plot_dim = (1 - spacing*(num_plots-1))/num_plots
            self.layout['yaxis']['domain'] = [1-plot_dim, 1]
            self.layout['xaxis']['anchor'] = 'y'
            for subplot_num in range(1, num_plots):
                domain_end = 1 - (plot_dim + spacing)*subplot_num
                domain_start = domain_end - plot_dim
                if domain_start < 0:
                    domain_start = 0
                self.layout['yaxis{}'.format(subplot_num + 1)]['domain'] = [domain_start, domain_end]
                self.layout['xaxis{}'.format(subplot_num + 1)]['anchor'] = 'y{}'.format(subplot_num + 1)


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
