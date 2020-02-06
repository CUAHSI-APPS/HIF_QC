from bokeh.plotting import figure, output_file, show, save
from bokeh.embed import components
from bokeh.models import BoxAnnotation, CategoricalColorMapper, ColumnDataSource
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

        source = ColumnDataSource({'x':x,'y':y,'label':flags})
        defaultLineColor = "#000000"

        # setting first color for OK to black since that the is default line color
        palette = [defaultLineColor]
        palette += [colorMap[i] for i in range(1,len(flagCodes))]
        color_mapper = CategoricalColorMapper(factors=list(self.FlagMgr.fetchFlagConfig().values()), palette=palette)
        # remove missing values
        if flags is not None:
            y = self.rmvMissingValues(y, flags)

        p = figure(title="Line", x_axis_type='datetime', plot_width=700, plot_height=400)
        p.line(x=x,y=y,line_color=defaultLineColor)
        r = p.circle(x='x', y='y', source=source, color={'field': 'label', 'transform': color_mapper},legend='label') #line_color="#000000", )
        r.visible  = False
        #p.legend.location = "top_left"
        #p.legend.click_policy="hide"

        i = 0
        while i < len(x)-1:
            if 'OK' in flags[i]:
                i += 1

            else:
                badrng_st = x[i]
                st = i
                while (i < len(x)-2) and (flags[i] == flags[i+1]) and (self.FlagMgr.returnGoodFlag() not in flags[i]):
                    i += 1
                badrng_end = x[i]
                end = i

                if (end - st) <= 1:
                    badrng_st = x[st-1]
                    badrng_end = x[end+1]

                color = None
                for c, flag in enumerate(flagCodes):
                    if flag['code'] == flags[st]:
                        color = colorMap[c]
                        break

                i += 1

                if flags[st] == self.FlagMgr.returnFlag('Basic Outlier Test'):
                    badbox = BoxAnnotation(left=badrng_st, right=badrng_end, fill_alpha=0.8, fill_color=color)
                else:
                    badbox = BoxAnnotation(left=badrng_st, right=badrng_end, fill_alpha=0.2, fill_color=color)
                p.add_layout(badbox)



        return components(p)
