"""
Matplotlib Exporter
===================
This submodule contains tools for crawling a matplotlib figure and exporting
relevant pieces to a renderer.
"""
from . import utils


class Exporter(object):
    """Matplotlib Exporter

    Parameters
    ----------
    renderer : Renderer object
        The render processes the Exporter output to create a visualization of
        a figure.
    close_mpl : bool
        If True (default), close the matplotlib figure as it is rendered. This
        is useful for when the exporter is used within the notebook, or with
        an interactive matplotlib backend.
    """

    def __init__(self, renderer, close_mpl=True):
        self.close_mpl = close_mpl
        self.renderer = renderer

    def run(self, fig):
        if self.close_mpl:
            import matplotlib.pyplot as plt
            plt.close(fig)
        self._crawl_fig(fig)

    def _process_transform(self, transform, ax=None, data=None):
        """Process the transform and convert data to figure or data coordinates

        Parameters
        ----------
        transform : matplotlib Transform object
            The transform applied to the data

        ax : matplotlib Axes object (optional)
            The axes the data is associated with

        data : ndarray (optional)
            The array of data to be transformed.

        Returns
        -------
        code : string
            Code is either "data" or "figure", indicating data coordinates
            or figure coordinates.
        new_data : ndarray
            Data transformed to either "data" or "figure" coordinates.
            Returned only if data is specified
        """
        if ax is not None and transform.contains_branch(ax.transData):
            code = "data"
            transform = (transform - ax.transData)
        else:
            code = "figure"

        if data is not None:
            return code, transform.transform(data)
        else:
            return code            

    def _crawl_fig(self, fig):
        with self.renderer.draw_figure(fig):
            for ax in fig.axes:
                self._crawl_ax(ax)

    def _crawl_ax(self, ax):
        with self.renderer.draw_axes(ax):
            self._extract_lines(ax)

    def _extract_lines(self, ax):
        for line in ax.lines:
            code, data = self._process_transform(line.get_transform(),
                                                 ax, line.get_xydata())
            linestyle = utils.get_line_style(line)
            if linestyle['dasharray'] not in ['None', 'none', None]:
                self.renderer.draw_line(data,
                                        coordinates=code,
                                        style=linestyle)

            markerstyle = utils.get_marker_style(line)
            if markerstyle['marker'] not in ['None', 'none', None]:
                self.renderer.draw_markers(data,
                                           coordinates=code,
                                           style=markerstyle)
