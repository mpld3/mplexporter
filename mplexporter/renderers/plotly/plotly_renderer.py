"""
Plotly Renderer.

A renderer class to be used with an exporter for rendering matplotlib plots
in Plotly.

Attributes:
    PlotlyRenderer -- a renderer class to be used with an Exporter obj
    fig_to_plotly -- a function to send an mpl figure to Plotly

"""
from . import plotly_utils
from .. base import Renderer
from ... exporter import Exporter


class PlotlyRenderer(Renderer):
    """A renderer class inheriting from base for rendering mpl plots in plotly.

    Attributes:
        username -- plotly username, required for fig_to_plotly (default None)
        api_key -- api key for given plotly username (defualt None)
        data -- a list of data dictionaries to be passed to plotly
        layout -- a layout dictionary to be passed to plotly
        axis_ct -- a reference to the number of axes rendered from mpl fig

    Inherited Methods (see renderers.base):
        ax_zoomable(ax) -- static method
        ax_has_xgrid(ax) -- static method
        ax_has_ygrid(ax) -- static method
        current_ax_zoomable(self) -- property
        current_ax_has_xgrid(self) -- property
        current_ax_has_ygrid(self) -- property
        draw_figure(self, fig, props) -- context manager
        draw_axes(self, ax, props) -- context manager

    Reimplemented Methods (see renderers.base):
        open_figure(self, fig, props)
        close_figure(self, fig)
        open_axes(self, ax, props)
        close_axes(self, ax)
        draw_line(self, **props)
        draw_markers(self, **props)
        draw_text(self, **props)

    """
    def __init__(self, username=None, api_key=None):
        """Initialize PlotlyRenderer obj.

        PlotlyRenderer obj is called on by an Exporter object to draw
        matplotlib objects like figures, axes, text, etc.

        """
        self.username = username
        self.api_key = api_key
        self.data = []
        self.layout = {}
        self.axis_ct = 0

    def open_figure(self, fig, props):
        """Creates a new figure by beginning to fill out layout dict.

        Currently, margins are set to zero to reconcile differences between
        mpl and plotly without complicated transforms. This will be changed
        in future revisions. Autosize is set to false so that the figure will
        mirror sizes set by mpl.

        """
        self.layout['width'] = int(props['figwidth']*props['dpi'])
        self.layout['height'] = int(props['figheight']*props['dpi'])
        self.layout['margin'] = {'l': 0, 'r': 0, 't': 0, 'b': 0, 'pad': 0}
        self.layout['autosize'] = False

    def close_figure(self, fig):
        """Closes figure by cleaning up data and layout dictionaries.

        The PlotlyRenderer's job is to create an appropriate set of data and
        layout dictionaries. When the figure is closed, some cleanup and
        repair is necessary. This method removes inappropriate dictionary
        entries, freeing up Plotly to use defaults and best judgements to
        complete the entries. This method is called by an Exporter object.

        Positional arguments:
        fig -- an mpl figure object.

        """
        plotly_utils.repair_data(self.data)
        plotly_utils.repair_layout(self.layout)
        for data_dict in self.data:
            plotly_utils.clean_dict(data_dict)
        try:
            for annotation_dict in self.layout['annotations']:
                plotly_utils.clean_dict(annotation_dict)
        except KeyError:
            pass
        plotly_utils.clean_dict(self.layout)
        self.layout['showlegend'] = False

    def open_axes(self, ax, props):
        """Setup a new axes object (subplot in plotly).

        Plotly stores information about subplots in different 'xaxis' and
        'yaxis' objects which are numbered. These are just dictionaries
        included in the layout dictionary. This function takes information
        from the Exporter, fills in appropriate dictionary entries,
        and updates the layout dictionary. PlotlyRenderer keeps track of the
        number of plots by incrementing the axis_ct attribute.

        Positional arguments:
        ax -- an mpl axes object. This will become a subplot in plotly.
        props -- selected axes properties from the exporter (a dict).

        """
        self.axis_ct += 1
        layout = {
            'xaxis{}'.format(self.axis_ct): {
                'range': props['xlim'],
                'showgrid': props['axes'][1]['grid']['gridOn'],
                'domain': plotly_utils.get_x_domain(props['bounds']),
                'anchor': 'y{}'.format(self.axis_ct)
            },
            'yaxis{}'.format(self.axis_ct): {
                'range': props['ylim'],
                'showgrid': props['axes'][0]['grid']['gridOn'],
                'domain': plotly_utils.get_y_domain(props['bounds']),
                'anchor': 'x{}'.format(self.axis_ct)
            }
        }
        for key, value in layout.items():
            self.layout[key] = value

    def close_axes(self, ax):
        """Close the axes object and clean up."""
        pass

    def draw_line(self, **props):
        """Create a data dict for a line obj.

        Props dict (key: value):
        'coordinates': 'data', 'axes', 'figure', or 'display'.
        'data': a list of xy pairs.
        'style': style dict from utils.get_line_style
        'mplobj': an mpl object, in this case the line object.

        """
        if props['coordinates'] == 'data':
            trace = {
                'mode': 'lines',
                'x': [xy_pair[0] for xy_pair in props['data']],
                'y': [xy_pair[1] for xy_pair in props['data']],
                'xaxis': 'x{}'.format(self.axis_ct),
                'yaxis': 'y{}'.format(self.axis_ct),
                'line': {
                    'opacity': props['style']['alpha'],
                    'color': props['style']['color'],
                    'width': props['style']['linewidth'],
                    'dash': plotly_utils.convert_dash(props['style'][
                        'dasharray'])
                }
            }
            self.data += trace,
        else:
            pass

    def draw_markers(self, **props):
        """Create a data dict for a line obj using markers.

        Props dict (key: value):
        'coordinates': 'data', 'axes', 'figure', or 'display'.
        'data': a list of xy pairs.
        'style': style dict from utils.get_marker_style
        'mplobj': an mpl object, in this case the line object.

        """
        if props['coordinates'] == 'data':
            trace = {
                'mode': 'markers',
                'x': [xy_pair[0] for xy_pair in props['data']],
                'y': [xy_pair[1] for xy_pair in props['data']],
                'xaxis': 'x{}'.format(self.axis_ct),
                'yaxis': 'y{}'.format(self.axis_ct),
                'marker': {
                    'opacity': props['style']['alpha'],
                    'color': props['style']['facecolor'],
                    'symbol': plotly_utils.convert_symbol(props['style'][
                        'marker']),
                    'line': {
                        'color': props['style']['edgecolor'],
                        'width': props['style']['edgewidth']
                    }
                }
            }
            # not sure whether we need to incorporate style['markerpath']
            self.data += trace,
        else:
            pass

    def draw_text(self, **props):
        """Create an annotation dict for a text obj.

        Currently, plotly uses either 'page' or 'data' to reference
        annotation locations. These refer to 'display' and 'data',
        respectively for the 'coordinates' key used in the Exporter.
        Appropriate measures are taken to transform text locations to
        reference one of these two options.

        Props dict (key: value):
        'coordinates': reference for position, 'data', 'axes', 'figure', etc.
        'position': x,y location of text in the given coordinates.
        'style': style dict from utils.get_text_style.
        'text': actual string content.

        """
        if 'annotations' not in self.layout:
            self.layout['annotations'] = []
        if props['text_type'] == 'xlabel':
            self.draw_xlabel(**props)
        elif props['text_type'] == 'ylabel':
            self.draw_ylabel(**props)
        elif props['text_type'] == 'title':
            self.draw_title(**props)
        else:  # just a regular text annotation...
            if True:  # props['coordinates'] is not 'data':
                x_px, y_px = props['mplobj'].get_transform().transform(
                    props['position'])
                x, y = plotly_utils.convert_to_paper(x_px, y_px, self.layout)
                xref = 'paper'
                yref = 'paper'
            else:
                x, y = props['position']
                xref = 'x{}'.format(self.axis_ct)
                yref = 'y{}'.format(self.axis_ct)
            annotation = {
                'text': props['text'],
                'x': x,
                'y': y,
                'xref': xref,
                'yref': yref,
                'font': {'color': props['style']['color'],
                         'size': props['style']['fontsize']
                },
                'showarrow': False  # change this later?
            }
            self.layout['annotations'] += annotation,

    def draw_title(self, **props):
        """Add a title to the current subplot in layout dictionary.

        Currently, titles are added as annotations.

        """
        x_px, y_px = props['mplobj'].get_transform().transform(props[
            'position'])
        x, y = plotly_utils.convert_to_paper(x_px, y_px, self.layout)
        annotation = {
            'text': props['text'],
            'font': {'color': props['style']['color'],
                     'size': props['style']['fontsize']
            },
            'xref': 'paper',
            'yref': 'paper',
            'x': x,
            'y': y,
            'showarrow': False  # no arrow for a title!
        }
        self.layout['annotations'] += annotation,

    def draw_xlabel(self, **props):
        """Add an xaxis label to the current subplot in layout dictionary."""
        self.layout['xaxis{}'.format(self.axis_ct)]['title'] = props['text']
        titlefont = {'size': props['style']['fontsize'],
                     'color': props['style']['color']
        }
        self.layout['xaxis{}'.format(self.axis_ct)]['titlefont'] = titlefont

    def draw_ylabel(self, **props):
        """Add a yaxis label to the current subplot in layout dictionary."""
        self.layout['yaxis{}'.format(self.axis_ct)]['title'] = props['text']
        titlefont = {'size': props['style']['fontsize'],
                     'color': props['style']['color']
        }
        self.layout['yaxis{}'.format(self.axis_ct)]['titlefont'] = titlefont


def fig_to_plotly(fig, username=None, api_key=None, notebook=False):
    """Convert a matplotlib figure to plotly dictionary and send.

    All available information about matplotlib visualizations are stored
    within a matplotlib.figure.Figure object. You can create a plot in python
    using matplotlib, store the figure object, and then pass this object to
    the fig_to_plotly function. In the background, mplexporter is used to
    crawl through the mpl figure object for appropriate information. This
    information is then systematically sent to the PlotlyRenderer which
    creates the JSON structure used to make plotly visualizations. Finally,
    these dictionaries are sent to plotly and your browser should open up a
    new tab for viewing! Optionally, if you're working in IPython, you can
    set notebook=True and the PlotlyRenderer will call plotly.iplot instead
    of plotly.plot to have the graph appear directly in the IPython notebook.

    Note, this function gives the user access to a simple, one-line way to
    render an mpl figure in plotly. If you need to trouble shoot, you can do
    this step manually by NOT running this fuction and entereing the following:

    ============================================================================
    from mplexporter import Exporter
    from mplexporter.renderers import PlotlyRenderer

    # create an mpl figure and store it under a varialble 'fig'

    renderer = PlotlyRenderer()
    exporter = Exporter(renderer)
    exporter.run(fig)
    ============================================================================

    You can then inspect the JSON structures by accessing these:

    renderer.layout -- a plotly layout dictionary
    renderer.data -- a list of plotly data dictionaries

    Positional arguments:
    fig -- a matplotlib figure object
    username -- a valid plotly username **
    api_key -- a valid api_key for the above username **
    notebook -- an option for use with an IPython notebook

    ** Don't have a username/api_key? Try looking here:
    https://plot.ly/plot

    ** Forgot your api_key? Try signing in and looking here:
    https://plot.ly/api/python/getting-started

    """
    import plotly
    renderer = PlotlyRenderer(username=username, api_key=api_key)
    Exporter(renderer).run(fig)
    py = plotly.plotly(renderer.username, renderer.api_key)
    if notebook:
        return py.iplot(renderer.data, layout=renderer.layout)
    else:
        py.plot(renderer.data, layout=renderer.layout)
