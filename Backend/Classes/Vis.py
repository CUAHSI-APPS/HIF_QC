from bokeh.plotting import figure, output_file, show, save
from bokeh.embed import components

class VisBuilder():
    def __init__(self):
        pass

    def BuildLineChart(self, x, y, flags=None):
        p = figure(title="Line", x_axis_type='datetime', plot_width=700, plot_height=400)
        p.line(x=x, y=y)
        return components(p)
