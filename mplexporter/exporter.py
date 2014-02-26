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
        The renderer object called by the exporter to create a figure
        visualization.  See mplexporter.Renderer for information on the
        methods which should be defined within the renderer.
    close_mpl : bool
        If True (default), close the matplotlib figure as it is rendered. This
        is useful for when the exporter is used within the notebook, or with
        an interactive matplotlib backend.
    """

    def __init__(self, renderer, close_mpl=True):
        self.close_mpl = close_mpl
        self.renderer = renderer

    def run(self, fig):
        """
        Run the exporter on the given figure

        Parmeters
        ---------
        fig : matplotlib.Figure instance
            The figure to export
        """
        # Calling savefig executes the draw() command, putting elements
        # in the correct place.
        fig.savefig(io.BytesIO(), format='png', dpi=fig.dpi)
        if self.close_mpl:
            import matplotlib.pyplot as plt
            plt.close(fig)
        self.crawl_fig(fig)

    @staticmethod
    def process_transform(transform, ax=None, data=None, return_trans=False):
        """Process the transform and convert data to figure or data coordinates

        Parameters
        ----------
        transform : matplotlib Transform object
            The transform applied to the data

        ax : matplotlib Axes object (optional)
            The axes the data is associated with

        data : ndarray (optional)
            The array of data to be transformed.

        return_trans : bool (optional)

        Returns
        -------
        properties : dict
            coordinates : string
                Coordinates is either "data", "axes", "figure", or "points", indicating data
                axes, figure, or raw point coordinates
            new_data : ndarray
                Data transformed to match the given coordinates.
                Returned only if data is specified
        """
        properties = {}
        if ax is None:
            coordinates = "figure"
        elif transform.contains_branch(ax.transData):
            coordinates = "data"
            transform = (transform - ax.transData)
        elif transform.contains_branch(ax.transAxes):
            coordinates = "figure"
        elif transform.contains_branch(ax.figure.transFigure):
            coordinates = "figure"
        else:
            coordinates = "points"
        properties['coordinates'] = coordinates

        if data is not None:
            properties['data'] = transform.transform(data)
        if return_trans:
            properties['transform'] = transform

        return properties

    def crawl_fig(self, fig):
        """Crawl the figure and process all axes"""
        properties = {'figwidth': fig.get_figwidth(),
                      'figheight': fig.get_figheight(),
                      'dpi': fig.dpi}
        with self.renderer.draw_figure(fig, properties):
            for ax in fig.axes:
                self.crawl_ax(ax)

    def crawl_ax(self, ax):
        """Crawl the axes and process all elements within"""
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
                      'dynamic': ax.get_navigate(),
                      'axes': [utils.get_axis_properties(ax.xaxis),
                               utils.get_axis_properties(ax.yaxis)]}

        with self.renderer.draw_axes(ax, properties):
            for line in ax.lines:
                self.draw_line(ax, line)
            for text in ax.texts:
                # xlabel and ylabel are passed as arguments to the axes
                # we don't want to pass them again here
                if text is ax.xaxis.label:
                    continue
                if text is ax.yaxis.label:
                    continue
                self.draw_text(ax, text)
            for patch in ax.patches:
                self.draw_patch(ax, patch)
            for collection in ax.collections:
                self.draw_collection(ax, collection)
            for image in ax.images:
                self.draw_image(ax, image)

    def draw_line(self, ax, line):
        """Process a matplotlib line and call renderer.draw_line"""
        properties = self.process_transform(line.get_transform(),
                                            ax, line.get_xydata())
        properties['linelabel'] = line.get_label()
        if line.get_linestyle() not in ['None', 'none', None]:
            properties['style'] = utils.get_line_style(line)
            self.renderer.draw_line(line, properties, mplobj=line)
        if line.get_marker() not in ['None', 'none', None]:
            properties['style'] = utils.get_marker_style(line)
            self.renderer.draw_markers(line, properties, line, mplobj=line)

    def draw_text(self, ax, text):
        """Process a matplotlib text object and call renderer.draw_text"""
        content = text.get_text()
        if content:
            transform = text.get_transform()
            position = text.get_position()
            code, position = self.process_transform(transform, ax,
                                                    position)
            style = utils.get_text_style(text)
            self.renderer.draw_text(content, position, code,
                                    style, mplobj=text)

    def draw_patch(self, ax, patch):
        """Process a matplotlib patch object and call renderer.draw_path"""
        vertices, pathcodes = utils.SVG_path(patch.get_path())
        transform = patch.get_transform()
        coordinates, vertices = self.process_transform(transform,
                                                       ax, vertices)
        linestyle = utils.get_path_style(patch)
        self.renderer.draw_path(vertices,
                                coordinates=coordinates,
                                pathcodes=pathcodes,
                                style=linestyle,
                                mplobj=patch)

    def draw_collection(self, ax, collection):
        """Process a matplotlib collection and call renderer.draw_collection"""
        (transform, transOffset,
         offsets, paths) = collection._prepare_points()

        offset_coordinates, offsets = self.process_transform(transOffset,
                                                             ax,
                                                             offsets)

        processed_paths = [utils.SVG_path(path) for path in paths]
        path_coordinates, tr = self.process_transform(transform, ax,
                                                      return_trans=True)
        processed_paths = [(tr.transform(path[0]), path[1])
                           for path in processed_paths]
        path_transforms = collection.get_transforms()
        styles = {'linewidth': collection.get_linewidths(),
                  'facecolor': collection.get_facecolors(),
                  'edgecolor': collection.get_edgecolors(),
                  'alpha': collection._alpha,
                  'zorder': collection.get_zorder()}

        offset_dict = {"data": "before",
                       "screen": "after"}
        offset_order = offset_dict[collection.get_offset_position()]

        self.renderer.draw_path_collection(processed_paths,
                                           path_coordinates,
                                           path_transforms,
                                           offsets,
                                           offset_coordinates,
                                           offset_order,
                                           styles,
                                           mplobj=collection)

    def draw_image(self, ax, image):
        """Process a matplotlib image object and call renderer.draw_image"""
        self.renderer.draw_image(imdata=utils.image_to_base64(image),
                                 extent=image.get_extent(),
                                 coordinates="data",
                                 style={"alpha": image.get_alpha(),
                                        "zorder": image.get_zorder()},
                                 mplobj=image)
