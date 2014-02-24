"""
Matplotlib Exporter
===================
This submodule contains tools for crawling a matplotlib figure and exporting
relevant pieces to a renderer.
"""
import io
import base64
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
    def _process_transform(transform, ax=None, data=None, return_trans=False):
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
            if return_trans:
                return code, transform.transform(data), transform
            else:
                return code, transform.transform(data)
            
        else:
            if return_trans:
                return code, transform
            else:
                return code

    @staticmethod
    def image_base64_data(image):
        ax = image.axes
        binary_buffer = io.BytesIO()

        # image is saved in axes coordinates: we need to temporarily
        # set the correct limits to get the correct image, then undo it.
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ax.set_xlim(image.get_extent()[:2])
        ax.set_ylim(image.get_extent()[2:])
        image.write_png(binary_buffer)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        binary_buffer.seek(0)
        return base64.b64encode(binary_buffer.read()).decode('utf-8')

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
            self._extract_collections(ax)
            self._extract_images(ax)

    def _extract_lines(self, ax):
        for line in ax.lines:
            code, data = self._process_transform(line.get_transform(),
                                                 ax, line.get_xydata())
            linestyle = utils.get_line_style(line)
            if linestyle['dasharray'] not in ['None', 'none', None]:
                self.renderer.draw_line(data,
                                        coordinates=code,
                                        style=linestyle, mplobj=line)

            markerstyle = utils.get_marker_style(line)
            if markerstyle['marker'] not in ['None', 'none', None]:
                self.renderer.draw_markers(data,
                                           coordinates=code,
                                           style=markerstyle, mplobj=line)

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
                self.renderer.draw_text(content, position, code,
                                        style, mplobj=text)

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
                                    style=linestyle,
                                    mplobj=patch)

    def _extract_collections(self, ax):
        for collection in ax.collections:
            (transform, transOffset,
             offsets, paths) = collection._prepare_points()

            offset_coordinates, offsets = self._process_transform(transOffset,
                                                                  ax,
                                                                  offsets)
            processed_paths = [utils.SVG_path(path) for path in paths]
            path_coordinates, tr = self._process_transform(transform, ax,
                                                           return_trans=True)
            processed_paths = [(tr.transform(path[0]), path[1])
                               for path in processed_paths]
            path_transforms = collection.get_transforms()
            styles = {'linewidth':collection.get_linewidths(),
                      'facecolor':collection.get_facecolors(),
                      'edgecolor':collection.get_edgecolors(),
                      'alpha':collection._alpha,
                      'zorder':collection.get_zorder()}

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

    def _extract_images(self, ax):
        for image in ax.images:
            imdata = self.image_base64_data(image)
            self.renderer.draw_image(imdata=self.image_base64_data(image),
                                     extent=image.get_extent(),
                                     coordinates="data",
                                     style={"alpha": image.get_alpha(),
                                            "zorder": image.get_zorder()},
                                     mplobj=image)
