from ..exporter import Exporter
from ..renderers import PlotlyRenderer

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def test_simple_line():
    fig, ax = plt.subplots()
    ax.plot(range(10), '-k')
    ax.plot(range(5), '.k')

    renderer = PlotlyRenderer()
    exporter = Exporter(renderer)
    exporter.run(fig)
    assert SIMPLE_LINE['data'] == renderer.data
    assert SIMPLE_LINE['layout'] == renderer.layout


## dictionaries for tests

SIMPLE_LINE = {
    'data': [
        {'line': {'color': '#000000',
                  'dash': 'solid',
                  'opacity': 1,
                  'width': 1.0
                  },
         'mode': 'lines',
         'x': [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
         'xaxis': 'x',
         'y': [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0],
         'yaxis': 'y'
         },
        {'marker': {'color': '#000000',
                    'line': {'color': '#000000',
                             'width': 0.5
                             },
                    'opacity': 1,
                    'symbol': 'dot'
                    },
         'mode': 'markers',
         'x': [0.0, 1.0, 2.0, 3.0, 4.0],
         'xaxis': 'x',
         'y': [0.0, 1.0, 2.0, 3.0, 4.0],
         'yaxis': 'y'}
    ],
    'layout': {'height': 480,
               'showlegend': False,
               'title': '',
               'width': 640,
               'xaxis': {'range': (0.0, 9.0),
                         'showgrid': False,
                         'title': ''
               },
               'yaxis': {'domain': [0, 1],
                         'range': (0.0, 9.0),
                         'showgrid': False,
                         'title': ''
               }
    }
}