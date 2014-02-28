def convert_symbol(mpl_symbol):
    if mpl_symbol in symbol_map:
        return symbol_map[mpl_symbol]
    else:
        return 'dot'  # default


def convert_dash(mpl_dash):
    if mpl_dash in dash_map:
        return dash_map[mpl_dash]
    else:
        return 'solid'  # default


def get_x_domain(bounds):
    return [bounds[0], bounds[0] + bounds[2]]


def get_y_domain(bounds):
    return [bounds[1], bounds[1] + bounds[3]]


def clean_dict(node, parent=None, node_key=None):
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
    for data_dict in data:
        for key_path_tup, fix in data_key_repairs.items():
            repair_key(data_dict, key_path_tup, fix)
        for key_path_tup, repair_dict in data_val_repairs.items():
                repair_val(data_dict, key_path_tup, repair_dict)


def repair_layout(layout):
    for key_path_tup, fix in layout_key_repairs.items():
        repair_key(layout, key_path_tup, fix)
    for key_path_tup, repair_dict in layout_val_repairs.items():
            repair_val(layout, key_path_tup, repair_dict)


dash_map = {
    '10,0': 'solid',
    '6,6': 'dash',
    '2,2': 'dot',
    '4,4,2,4': 'dashdot',
    'none': 'solid'
}

symbol_map = {
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

data_key_repairs = {}

layout_key_repairs = {
    ('xaxis1',): 'xaxis',
    ('yaxis1',): 'yaxis'
}

data_val_repairs = {  # (1) keys with None get deleted, (2) empty dicts get deleted!
    ('xaxis',): {'x1': None},
    ('yaxis',): {'y1': None}
}

layout_val_repairs = {
    ('xaxis', 'anchor'): {'y1': 'y'},
    ('yaxis', 'anchor'): {'x1': 'x'},
    ('annotations', 'xref'): {'x1': 'x'},
    ('annotations', 'yref'): {'y1': 'y'}
}