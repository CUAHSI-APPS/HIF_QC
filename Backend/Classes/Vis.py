from bokeh.plotting import figure, output_file, show, save
from bokeh.embed import components
from bokeh.models import BoxAnnotation

class VisBuilder():
    def __init__(self):
        # FlagMgr = Flag('../SessionFiles/Flagging_Config.json')
        pass

    def rmvMissingValues(self, y, flags=None):
        for i, val in enumerate(y):
            if val == -9999.0:
                y[i] = float('nan')

        return y


    def BuildLineChart(self, x, y, flags=None):

        # remove missing values
        y = self.rmvMissingValues(y)

        p = figure(title="Line", x_axis_type='datetime', plot_width=700, plot_height=400)
        p.line(x=x, y=y)

        i = 0

        print("gets here?")

        while i < len(x)-1:
            if 'OK' in flags[i]:
                i += 1

            else:
                badrng_st = x[i]
                st = i

                while i < len(x)-2 and 'OK' not in flags[i]:
                    i += 1

                badrng_end = x[i]
                end = i


                if (end - st) <= 1:
                    badrng_st = x[st-1]
                    badrng_end = x[end+1]

                i += 1


                badbox = BoxAnnotation(left=badrng_st, right=badrng_end, fill_alpha=0.4, fill_color='red')
                p.add_layout(badbox)

        return components(p)
