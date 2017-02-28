from bokeh.plotting import figure, curdoc, vplot
#from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d
from bokeh.embed import components
import MySQLdb
import datetime            # needed to read TIME from SQL

dbConnection = MySQLdb.connect(host='109.74.196.205', user='pi', passwd= 'SSartori12', db='Home')
cursor = dbConnection.cursor()
# sqlq = "SELECT * FROM temperature WHERE idtemperature % 50 = 0;"
sqlq = "SELECT * FROM temperature WHERE timestamp > '2016-02-13';"
cursor.execute(sqlq)
result = list(cursor.fetchall())

date_time=['date and time']
setPoint=['setPoint']
Temperature=['temp']

for item in result:
    date_time.append(item[1])
    setPoint.append(item[2])
    Temperature.append(item[3])

#print Temperature

colormap = {'setosa': 'red', 'versicolor': 'green', 'virginica': 'blue'}

# output_file("./temperature.html", title="24 St Leonards Road")

#p = figure(title = "Heating")
p = figure(width=800, height=850, x_axis_type="datetime")
p.y_range = Range1d(17, 22)

p.xaxis.axis_label = 'Time'
p.yaxis.axis_label = 'Temperature [C]'

# Style (removal)
#--------------------  
p.outline_line_width = 0
p.outline_line_color = "white"

p.yaxis.minor_tick_line_color = None
p.ygrid.band_fill_alpha = 0.1
p.ygrid.band_fill_color = "gray"
p.grid.bounds = (18.9, 20.1)

p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

p.line(date_time, Temperature, color="red")
p.line(date_time, setPoint, color="navy")

#--------------------  

## for html file
# show(p)

## for use with ' bokeh serve --show graph.py'
# curdoc().add_root(p)

## to generate script and div content to be inserted into html
if (1==1):
    script, div = components(p)
    f = open('script.php', 'w')
    f.write(script)
    f.close()
    f = open('div.php', 'w')
    f.write(div)
    f.close()

