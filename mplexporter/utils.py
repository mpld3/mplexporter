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
