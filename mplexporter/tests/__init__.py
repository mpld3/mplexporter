import os

MPLBE = os.environ.get('MPLBE', 'Agg')

if MPLBE:
    import matplotlib
    matplotlib.use(MPLBE)

import matplotlib.pyplot as plt
