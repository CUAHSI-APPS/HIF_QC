from bokeh.plotting import figure, output_file, show, save
from bokeh.embed import components
from bokeh.models import BoxAnnotation
from bokeh.palettes import Category20
from Backend.Classes.Flagging import *

class VisBuilder():
    def __init__(self):
        self.FlagMgr = Flag()
        pass

    def rmvMissingValues(self, y, flags=None):
        for i, val in enumerate(y):
            if flags[i] == self.FlagMgr.returnFlag('Missing Value Test'):
                y[i] = float('nan')

        return y


    def BuildLineChart(self, x, y, flags=None):
        # build color palette
        flagCodes = self.FlagMgr.returnAllFlagsAsArr()
        colorMap = Category20[len(flagCodes)]

        # remove missing values
        if flags is not None:
            y = self.rmvMissingValues(y, flags)

        p = figure(title="Line", x_axis_type='datetime', plot_width=700, plot_height=400)
        p.line(x=x, y=y)

        i = 0
        while i < len(x)-1:
            if 'OK' in flags[i]:
                i += 1

            else:
                badrng_st = x[i]
                st = i
                while i < len(x)-2 and self.FlagMgr.returnGoodFlag() not in flags[i]:
                    i += 1
                badrng_end = x[i]
                end = i

                if (end - st) <= 1:
                    badrng_st = x[st-1]
                    badrng_end = x[end+1]

                color = None
                for c, flag in enumerate(flagCodes):
                    print(flag['code'], flags[st], flush=True)
                    if flag['code'] == flags[st]:
                        color = colorMap[c]
                        break

                i += 1

                print(color, flush=True)

                badbox = BoxAnnotation(left=badrng_st, right=badrng_end, fill_alpha=0.4, fill_color=color)
                p.add_layout(badbox)

        return components(p)
