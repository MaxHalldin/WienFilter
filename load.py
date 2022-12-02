import matplotlib.pyplot as plt
from pythion.gui import GridSearchResults
import sys

# Call like python load <filename.csv> minimum maximum log_threshold
# Use - to designate an empty argument- to designate an empty argument
filename = sys.argv[1]

GridSearchResults.from_file(filename)
plt.show()
