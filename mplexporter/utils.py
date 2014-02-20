"""
Utility Routines for Working with Matplotlib Objects
====================================================
"""
from matplotlib.colors import colorConverter
from matplotlib.path import Path
from matplotlib.markers import MarkerStyle
from matplotlib.transforms import Affine2D


def color_to_hex(color):
    """Convert matplotlib color code to hex color code"""
    rgb = colorConverter.to_rgb(color)
    return '#{0:02X}{1:02X}{2:02X}'.format(*(int(255 * c) for c in rgb))



def many_to_one(input_dict):
    """Convert a many-to-one mapping to a one-to-one mapping"""
    return dict((key, val)
                for keys, val in input_dict.items()
                for key in keys)

LINESTYLES = many_to_one({('solid', '-', (None, None)): "10,0",
                          ('dashed', '--'): "6,6",
                          ('dotted', ':'): "2,2",
                          ('dashdot', '-.'): "4,4,2,4",
                          ('', ' ', 'None', 'none'): "none"})


def get_dasharray(obj, i=None):
    """Get an SVG dash array for the given matplotlib linestyle"""
    if obj.__dict__.get('_dashSeq', None) is not None:
        return ','.join(map(str, obj._dashSeq))
    else:
        ls = obj.get_linestyle()
        if i is not None:
            ls = ls[i]

        dasharray = LINESTYLES.get(ls, None)
        if dasharray is None:
            warnings.warn("dash style '{0}' not understood: "
                          "defaulting to solid.".format(ls))
            dasharray = LINESTYLES['-']
        return dasharray


PATH_DICT = {Path.LINETO: 'L',
             Path.MOVETO: 'M',
             Path.STOP: 'STOP',
             Path.CURVE3: 'S',
             Path.CURVE4: 'C',
             Path.CLOSEPOLY: 'Z'}


def SVG_path(path, transform=None):
    """Return a list of SVG path tuples of a (transformed) path"""
    if transform is not None:
        path = path.transformed(transform)

    return [(PATH_DICT[path_code], vertices.tolist())
            for vertices, path_code in path.iter_segments(simplify=False)]
        

def get_line_style(line):
    """Return the line style dict for the line"""
    style = {}
    style['alpha'] = line.get_alpha()
    if style['alpha'] is None:
        style['alpha'] = 1
    style['color'] = color_to_hex(line.get_color())
    style['linewidth'] = line.get_linewidth()
    style['dasharray'] = get_dasharray(line)
    return style


def get_marker_style(line):
    """Return the marker style dict for the line"""
    style = {}
    style['alpha'] = line.get_alpha()
    if style['alpha'] is None:
        style['alpha'] = 1

    style['facecolor'] = color_to_hex(line.get_markerfacecolor())
    style['edgecolor'] = color_to_hex(line.get_markeredgecolor())
    style['edgewidth'] = line.get_markeredgewidth()

    style['marker'] = line.get_marker()
    markerstyle = MarkerStyle(line.get_marker())
    markersize = line.get_markersize()
    markertransform = (markerstyle.get_transform()
                       + Affine2D().scale(markersize, -markersize))
    style['markerpath'] = SVG_path(markerstyle.get_path(),
                                   markertransform)
    return style

def get_text_style(text):
    """Return the text style dict for a text instance"""
    style = {}
    style['alpha'] = text.get_alpha()
    if style['alpha'] is None:
        style['alpha'] = 1
    style['fontsize'] = text.get_size()
    style['color'] = color_to_hex(text.get_color())
    style['halign'] = text.get_horizontalalignment() # left, center, right
    style['valign'] = text.get_verticalalignment() # baseline, center, top
    style['rotation'] = text.get_rotation()
    return style

FIG_PARAMS = [
    'agg_filter',
    'alpha',
    'animated',
    'axes',
    'children',
    'clip_box',
    'clip_on',
    'clip_path',
    'contains',
    'default_bbox_extra_artists',
    'dpi',
    'edgecolor',
    'facecolor',
    'figheight',
    'figure',
    'figwidth',
    'frameon',
    'gid',
    'label',
    'path_effects',
    'picker',
    'rasterized',
    'size_inches',
    'sketch_params',
    'snap',
    'tight_layout',
    'transform',
    'transformed_clip_path_and_affine',
    'url',
    'visible',
    'window_extent',
    'zorder'
]

AX_PARAMS = [
    'adjustable',
    'agg_filter',
    'alpha',
    'anchor',
    'animated',
    'aspect',
    'autoscale_on',
    'autoscalex_on',
    'autoscaley_on',
    'axes',
    'axes_locator',
    'axis_bgcolor',
    'axisbelow',
    'children',
    'clip_box',
    'clip_on',
    'clip_path',
    'contains',
    'cursor_props',
    'data_ratio',
    'default_bbox_extra_artists',
    'figure',
    'frame_on',
    'geometry',
    'gid',
    'images',
    'label',
    'legend',
    'legend_handles_labels',
    'lines',
    'navigate',
    'navigate_mode',
    'path_effects',
    'picker',
    'position',
    'rasterization_zorder',
    'rasterized',
    'renderer_cache',
    'shared_x_axes',
    'shared_y_axes',
    'sketch_params',
    'snap',
    'subplotspec',
    'title',
    'transform',
    'transformed_clip_path_and_affine',
    'url',
    'visible',
    'window_extent',
    'xaxis',
    'xaxis_transform',
    'xbound',
    'xgridlines',
    'xlabel',
    'xlim',
    'xmajorticklabels',
    'xminorticklabels',
    'xscale',
    'xticklabels',
    'xticklines',
    'xticks',
    'yaxis',
    'yaxis_transform',
    'ybound',
    'ygridlines',
    'ylabel',
    'ylim',
    'ymajorticklabels',
    'yminorticklabels',
    'yscale',
    'yticklabels',
    'yticklines',
    'yticks',
    'zorder'
]