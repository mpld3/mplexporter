"""
Matplotlib Exporter
===================
This submodule contains tools for crawling a matplotlib figure and exporting
relevant pieces to a renderer.
"""
import warnings
import io
from . import utils

import matplotlib


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
        code : string
            Code is either "data", "figure", or "points", indicating data
            coordinates, figure coordinates, or raw point coordinates
        new_data : ndarray
            Data transformed to match the given coordinate code.
            Returned only if data is specified
        """
        if ax is None:
            code = "figure"
        elif transform.contains_branch(ax.transData):
            code = "data"
            transform = (transform - ax.transData)
        elif transform.contains_branch(ax.transAxes):
            code = "figure"
        elif transform.contains_branch(ax.figure.transFigure):
            code = "figure"
        else:
            code = "points"

        if data is not None:
            if return_trans:
                return code, transform.transform(data), transform
            else:
                return code, transform.transform(data)
        else:
            if return_trans:
                return code, transform
            else:
                return code

    def crawl_fig(self, fig):
        """Crawl the figure and process all axes"""
        with self.renderer.draw_figure(fig=fig,
                                       props=utils.get_figure_properties(fig)):
            for ax in fig.axes:
                self.crawl_ax(ax)

    def crawl_ax(self, ax):
        """Crawl the axes and process all elements within"""
        with self.renderer.draw_axes(ax=ax,
                                     props=utils.get_axes_properties(ax)):
            for line in ax.lines:
                self.draw_line(ax, line)
            for text in ax.texts:
                self.draw_text(ax, text)
            for artist in ax.artists:
                # TODO: process other artists
                if isinstance(artist, matplotlib.text.Text):
                    self.draw_text(ax, artist)
            for patch in ax.patches:
                self.draw_patch(ax, patch)
            for collection in ax.collections:
                self.draw_collection(ax, collection)
            for image in ax.images:
                self.draw_image(ax, image)

            # TODO: figure out how to specify legends appropriately...

            #legend = ax.get_legend()
            #if legend is not None:
            #    for child in ax.legend_.get_children():
            #        if child is legend.legendPatch:
            #            self.draw_patch(ax, child)
            #        if isinstance(child, matplotlib.patches.Patch):
            #            self.draw_patch(ax, child)
            #        elif isinstance(child, matplotlib.text.Text):
            #            if not (child is ax.legend_.get_children()[-1]
            #                    and child.get_text() == 'None'):
            #                self.draw_text(ax, child)
            #        elif isinstance(child, matplotlib.lines.Line2D):
            #            self.draw_line(ax, child)
            #        elif isinstance(child, matplotlib.offsetbox.PackerBase):
            #            pass
            #        else:
            #            warnings.warn("Legend element %s not impemented"
            #                          & child)

    def draw_line(self, ax, line):
        """Process a matplotlib line and call renderer.draw_line"""
        coordinates, data = self.process_transform(line.get_transform(),
                                                    ax, line.get_xydata())
        linestyle = utils.get_line_style(line)
        if linestyle['dasharray'] not in ['None', 'none', None]:
            self.renderer.draw_line(data=data,
                                    coordinates=coordinates,
                                    style=linestyle, mplobj=line)

        markerstyle = utils.get_marker_style(line)
        if markerstyle['marker'] not in ['None', 'none', None]:
            self.renderer.draw_markers(data=data,
                                       coordinates=coordinates,
                                       style=markerstyle, mplobj=line)

    def draw_text(self, ax, text):
        """Process a matplotlib text object and call renderer.draw_text"""
        content = text.get_text()
        if content:
            transform = text.get_transform()
            position = text.get_position()
            coordinates, position = self.process_transform(transform, ax,
                                                           position)
            style = utils.get_text_style(text)
            self.renderer.draw_text(text=content, position=position,
                                    coordinates=coordinates,
                                    style=style, mplobj=text)

    def draw_patch(self, ax, patch):
        """Process a matplotlib patch object and call renderer.draw_path"""
        vertices, pathcodes = utils.SVG_path(patch.get_path())
        transform = patch.get_transform()
        coordinates, vertices = self.process_transform(transform,
                                                       ax, vertices)
        linestyle = utils.get_path_style(patch, fill=patch.get_fill())
        self.renderer.draw_path(data=vertices,
                                coordinates=coordinates,
                                pathcodes=pathcodes,
                                style=linestyle,
                                mplobj=patch)

    def draw_collection(self, ax, collection):
        """Process a matplotlib collection and call renderer.draw_collection"""
        (transform, transOffset,
         offsets, paths) = collection._prepare_points()

        offset_coords, offsets = self.process_transform(transOffset,
                                                        ax,
                                                        offsets)

        processed_paths = [utils.SVG_path(path) for path in paths]
        path_coords, tr = self.process_transform(transform, ax,
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

        self.renderer.draw_path_collection(paths=processed_paths,
                                           path_coordinates=path_coords,
                                           path_transforms=path_transforms,
                                           offsets=offsets,
                                           offset_coordinates=offset_coords,
                                           offset_order=offset_order,
                                           styles=styles,
                                           mplobj=collection)

    def draw_image(self, ax, image):
        """Process a matplotlib image object and call renderer.draw_image"""
        self.renderer.draw_image(imdata=utils.image_to_base64(image),
                                 extent=image.get_extent(),
                                 coordinates="data",
                                 style={"alpha": image.get_alpha(),
                                        "zorder": image.get_zorder()},
                                 mplobj=image)
