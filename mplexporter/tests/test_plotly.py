from ..exporter import Exporter
from ..renderers import PlotlyRenderer

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

T1 = {
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

T2_OUTPUT = """
opening figure
  opening axis 1
    draw line with 20 points
  closing axis 1
  opening axis 2
    draw 10 markers
  closing axis 2
closing figure
"""


def test_1():
    fig, ax = plt.subplots()
    ax.plot(range(10), '-k')
    ax.plot(range(5), '.k')
    # plt.title('test1')

    renderer = PlotlyRenderer()
    exporter = Exporter(renderer)
    exporter.run(fig)
    assert T1['data'] == renderer.data
    assert T1['layout'] == renderer.layout


def test_2():
    plt.figure(1)
    plt.subplot(211)
    plt.plot(range(20), '-k')
    plt.subplot(212)
    plt.plot(range(10), '.k')
    fig = plt.gcf()

    renderer = PlotlyRenderer()
    exporter = Exporter(renderer)
    exporter.run(fig)

    for line1, line2 in zip(renderer.output.strip().split(),
                            T2_OUTPUT.strip().split()):
        assert line1 == line2