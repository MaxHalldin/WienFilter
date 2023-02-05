import sys
import matplotlib.pyplot as plt


from pythion._routines.grid_search import load_gridsearch_result, Heatmap


def read_yesno(prompt: str, default: bool):
    def_string = f" (default is {'yes' if default else 'no'})? "
    while True:
        message = input(prompt + def_string).strip().lower()
        if not message:
            return default
        if message in ['y', 'yes']:
            return True
        elif message in ['n', 'no']:
            return False
        else:
            print('Did not understand. Please enter yes/no, or leave blank for default')


def read_float(prompt, default):
    def_string = f" (default is {default}): "
    while True:
        message = input(prompt + def_string).strip()
        if not message:
            return default
        try:
            return float(message)
        except ValueError:
            print('Did not understand. Please enter a number, or leave blank for default')


def read_int(prompt, default):
    def_string = f" (default is {default}): "
    while True:
        message = input(prompt + def_string).strip()
        if not message:
            return default
        try:
            return int(message)
        except ValueError:
            print('Did not understand. Please enter an integer, or leave blank for default')


if len(sys.argv) < 2:
    input('No file selected, press enter to exit.')
    exit(0)


filename = sys.argv[1]

color_min = read_float('Minimum value of color scale', 1)
color_max = read_float('Maximum value of color scale', 1000)
is_log = read_yesno('Plot color with log scale', True)

if is_log:
    if color_min > 0 and not read_yesno('Do you want a linear range for low values', False):
        log_threshold = 0
    else:
        log_threshold = read_float('At what value should the linear/logarithmic transition be', 10)
else:
    log_threshold = None

n_labels = read_int('Maximum number of axis labels', 20)

load_gridsearch_result(filename, Heatmap.Settings(color_min, color_max, log_threshold, n_labels))
plt.show()