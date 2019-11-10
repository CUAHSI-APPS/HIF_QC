from bokeh.plotting import figure, output_file, show, save
from bokeh.embed import components
from bokeh.models import BoxAnnotation

class VisBuilder():
    def __init__(self):
        # FlagMgr = Flag('../SessionFiles/Flagging_Config.json')
        pass

    def BuildLineChart(self, x, y, flags=None):
        p = figure(title="Line", x_axis_type='datetime', plot_width=700, plot_height=400)
        p.line(x=x, y=y)

        i = 0

        while i < len(x)-1:
            if 'OK' in flags[i]:
                i += 1
            else:


                badrng_st = x[i-1]

                while i < len(x)-2 and 'OK' not in flags[i]:
                    i += 1

                badrng_end = x[i+1]

                badbox = BoxAnnotation(left=badrng_st, right=badrng_end, fill_alpha=0.4, fill_color='red')
                p.add_layout(badbox)

        return components(p)
