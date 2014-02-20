"""
Matplotlib Exporter
===================
This submodule contains tools for crawling a matplotlib figure and exporting
relevant pieces to a renderer.
"""
import io
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
        # Calling savefig executes the draw() command, putting elements
        # in the correct place.
        fig.savefig(io.BytesIO(), format='png', dpi=fig.dpi)
        if self.close_mpl:
            import matplotlib.pyplot as plt
            plt.close(fig)
        self._crawl_fig(fig)

    @staticmethod
    def _process_transform(transform, ax=None, data=None):
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
        properties = {'figwidth': fig.get_figwidth(),
                      'figheight': fig.get_figheight(),
                      'dpi': fig.dpi}
        with self.renderer.draw_figure(fig, properties):
            for ax in fig.axes:
                self._crawl_ax(ax)

    def _crawl_ax(self, ax):
        properties = {'xlim': ax.get_xlim(),
                      'ylim': ax.get_ylim(),
                      'xlabel': ax.get_xlabel(),
                      'ylabel': ax.get_ylabel(),
                      'title': ax.get_title(),
                      'bounds': ax.get_position().bounds,
                      'xgrid': bool(ax.xaxis._gridOnMajor
                                    and ax.xaxis.get_gridlines()),
                      'ygrid': bool(ax.yaxis._gridOnMajor
                                    and ax.yaxis.get_gridlines()),
                      'dynamic': ax.get_navigate()}
        with self.renderer.draw_axes(ax, properties):
            self._extract_lines(ax)
            self._extract_patches(ax)
            self._extract_texts(ax)

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

    def _extract_texts(self, ax):
        for text in ax.texts:
            # xlabel and ylabel are passed as arguments to the axes
            # we don't want to pass them again here
            if text is ax.xaxis.label:
                continue
            if text is ax.yaxis.label:
                continue

            content = text.get_text()
            if content:
                transform = text.get_transform()
                position = text.get_position()
                code, position = self._process_transform(transform, ax,
                                                         position)
                style = utils.get_text_style(text)
                self.renderer.draw_text(content, position, code, style)

    def _extract_patches(self, ax):
        for patch in ax.patches:
            vertices, pathcodes = utils.SVG_path(patch.get_path())
            transform = patch.get_transform()
            coordinates, vertices = self._process_transform(transform,
                                                            ax, vertices)
            linestyle = utils.get_path_style(patch)
            self.renderer.draw_path(vertices,
                                    coordinates=coordinates,
                                    pathcodes=pathcodes,
                                    style=linestyle)
