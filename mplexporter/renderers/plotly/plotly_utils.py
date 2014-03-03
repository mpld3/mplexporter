def convert_symbol(mpl_symbol):
    """Convert mpl marker symbol to plotly symbol and return symbol."""
    if mpl_symbol in SYMBOL_MAP:
        return SYMBOL_MAP[mpl_symbol]
    else:
        return 'dot'  # default


def convert_dash(mpl_dash):
    """Convert mpl line symbol to plotly line symbol and return symbol."""
    if mpl_dash in DASH_MAP:
        return DASH_MAP[mpl_dash]
    else:
        return 'solid'  # default


def get_x_domain(bounds):
    """Convert matplotlib (x0,width) to (x0,x1) and return."""
    return [bounds[0], bounds[0] + bounds[2]]


def get_y_domain(bounds):
    """Convert matplotlib (y0,height) to (y0,y1) and return."""
    return [bounds[1], bounds[1] + bounds[3]]


def convert_to_paper(x, y, layout):
    """Convert mpl display coordinates to plotly paper coordinates.

    Plotly references object positions with an (x, y) coordinate pair in either
    'data' or 'paper' coordinates which reference actual data in a plot or
    the entire plotly axes space where the bottom-left of the bottom-left
    plot has the location (x, y) = (0, 0) and the top-right of the top-right
    plot has the location (x, y) = (1, 1). Display coordinates in mpl reference
    objects with an (x, y) pair in pixel coordinates, where the bottom-left
    corner is at the location (x, y) = (0, 0) and the top-right corner is at
    the location (x, y) = (figwidth*dpi, figheight*dpi). Here, figwidth and
    figheight are in inches and dpi are the dots per inch resolution.

    """
    num_x = x - layout['margin']['l']
    den_x = layout['width'] - (layout['margin']['l'] + layout['margin']['r'])
    num_y = y - layout['margin']['b']
    den_y = layout['height'] - (layout['margin']['b'] + layout['margin']['t'])
    return num_x/den_x, num_y/den_y


def clean_dict(node, parent=None, node_key=None):
    """Remove None, 'none', 'None', and {} from a dictionary obj.

    When Plotly JSON dictionary entries are populated, Plotly will
    automatically fill in necessary items with defaults. However, if a
    nonsense entry is sent to plotly, it won't know to deal with it. This
    function removes some common 'nonsense' entries like empty dicts, None,
    'None', or 'none'.

    The clean_dict function will typically be called with a dictionary
    argument only, allowing parent and node_key to remain defaults. The
    choice of node reflects that this function works recursively.

    Positional arguments:
    node -- a dictionary that needs to be cleaned

    Keyword arguments:
    parent -- the dictionary that contains node (default None)
    node_key -- parent[node_key] == node (default None)

    """
    del_keys = []
    for key, item in node.items():
        if isinstance(item, dict):
            clean_dict(item, node, key)
        else:
            if item in [None, 'none', 'None']:
                del_keys += [key]
    for key in del_keys:
        del node[key]
    if parent is not None:
        if len(node) == 0:
            del parent[node_key]


def repair_key(d, key_path_tup, fix):
    """Repairs inappropriate keys caused by referencing self.ax_ct.

    This function allows inappropriate keys to be used in the
    PlotlyRenderer.layout and PlotlyRenderer.data dictionaries. This is done
    for the following reasons:

    - Code is made simpler by treating 1st axes instance the same as
    subsequent axes instances.
    - If future releases of Plotly accept keys such as 'xaxis1' or 'yaxis1',
    plotly_renderer.py and plolty_utils.py can be updated simply.

    Dictionaries need not be continuous for use with a key_path_tup. For
    example, layout['annotations'] is actually a list of annotation
    dictionaries. When repair_key() runs into such a list, it assumes that
    the list is populated by dictionaries and continues down the rest of the
    key_path_tup for each dictionary in the list.

    Positional arguments:
    d -- a plotly layout or data dictionary
    key_path_tup -- a tuple of dictionary keys that leads to the conflict
    fix -- the appropriate dictionary key for the key_path_tup

    """
    try:
        for num, key in enumerate(key_path_tup[:-1]):
            d = d[key]
            if isinstance(d, list):
                for sub_d in d:
                    repair_key(sub_d, key_path_tup[num+1:], fix)
        d[fix] = d.pop(key_path_tup[-1])
    except KeyError:
        pass
    except TypeError:
        pass


def repair_val(d, key_path_tup, repair_dict):
    """Repairs inappropriate values caused by referencing self.ax_ct.

    This function allows inappropriate values to be used in the
    PlotlyRenderer.layout and PlotlyRenderer.data dictionaries. This is done
    for the following reasons:

    - Code is made simpler by treating 1st axes instance the same as
    subsequent axes instances.
    - If future releases of Plotly accept values such as 'x1' or 'y1',
    plotly_renderer.py and plolty_utils.py can be updated simply.

    Dictionaries need not be continuous for use with a key_path_tup. For
    example, layout['annotations'] is actually a list of annotation
    dictionaries. When repair_val() runs into such a list, it assumes that
    the list is populated by dictionaries and continues down the rest of the
    key_path_tup for each dictionary in the list.

    Positional arguments:
    d -- a plotly layout or data dictionary
    key_path_tup -- a tuple of dictionary keys that leads to the conflict
    repair_dict -- a dictionary that contains {bad_value: good_value} entries

    """
    try:
        for num, key in enumerate(key_path_tup[:-1]):
            d = d[key]
            if isinstance(d, list):
                for sub_d in d:
                    repair_val(sub_d, key_path_tup[num+1:], repair_dict)
        for bug, fix in repair_dict.items():
            if d[key_path_tup[-1]] == bug:
                d[key_path_tup[-1]] = fix
    except KeyError:
        pass
    except TypeError:
        pass


def repair_data(data):
    """Fixes innapropriate keys and values in plotly data list.

    This function calls repair_key() and repair_val() for each entry in
    DATA_KEY_REPAIRS and DATA_VAL_REPAIRS. It assumes that the keys in these
    dictionaries are tuples with paths to known possible errors.

    Positional arguments:
    data -- a list of plotly data dictionaries

    """
    for data_dict in data:
        for key_path_tup, fix in DATA_KEY_REPAIRS.items():
            repair_key(data_dict, key_path_tup, fix)
        for key_path_tup, repair_dict in DATA_VAL_REPAIRS.items():
                repair_val(data_dict, key_path_tup, repair_dict)


def repair_layout(layout):
    """Fixes innapropriate keys and values in plotly layout dict.

    This function calls repair_key() and repair_val() for each entry in
    LAYOUT_KEY_REPAIRS and LAYOUT_VAL_REPAIRS. It assumes that the keys in
    these dictionaries are tuples with paths to known possible errors.

    Positional arguments:
    layout -- a plotly layout dictionary

    """
    for key_path_tup, fix in LAYOUT_KEY_REPAIRS.items():
        repair_key(layout, key_path_tup, fix)
    for key_path_tup, repair_dict in LAYOUT_VAL_REPAIRS.items():
            repair_val(layout, key_path_tup, repair_dict)


DASH_MAP = {
    '10,0': 'solid',
    '6,6': 'dash',
    '2,2': 'dot',
    '4,4,2,4': 'dashdot',
    'none': 'solid'
}

SYMBOL_MAP = {
    'o': 'dot',
    'v': 'triangle-down',
    '^': 'triangle-up',
    '<': 'triangle-left',
    '>': 'triangle-right',
    's': 'square',
    '+': 'cross',
    'x': 'x',
    'D': 'diamond',
    'd': 'diamond',
    '-': 'solid',
    '--': 'dash',
    '-.': 'dashdot'
}

DATA_KEY_REPAIRS = {}

LAYOUT_KEY_REPAIRS = {
    ('xaxis1',): 'xaxis',
    ('yaxis1',): 'yaxis'
}

DATA_VAL_REPAIRS = {
    ('xaxis',): {'x1': None},
    ('yaxis',): {'y1': None}
}

LAYOUT_VAL_REPAIRS = {
    ('xaxis', 'anchor'): {'y1': 'y'},
    ('yaxis', 'anchor'): {'x1': 'x'},
    ('annotations', 'xref'): {'x1': 'x'},
    ('annotations', 'yref'): {'y1': 'y'}
}