import matplotlib.pyplot as plt
from pythion._gui.grid_search import GridSearchResults
import sys

filename = sys.argv[1]
GridSearchResults.from_file(filename)
plt.show()
