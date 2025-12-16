import os

import matplotlib
if MPLBE := os.environ.get('MPLBE', 'Agg'):
    matplotlib.use(MPLBE)
import matplotlib.pyplot as plt
