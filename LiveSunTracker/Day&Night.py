import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import requests
import geopandas as gp
import matplotlib.pyplot as plt
import matplotlib.patches as shp
from datetime import datetime
from numpy import arccos, tan
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

timezone = 330
days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
colours = ['#efef00', '#ef00ef', '#00efef', '#ff0000', '#00ff00', '#0000ff']
plot_data = []
attempts = 0


#world map set-up-----------------------------------------------------------------------------------------------------------
map = gp.read_file(gp.datasets.get_path('naturalearth_lowres'))
ax = map.plot(figsize= (15, 8), color= '#505050')


#getting current time for default plot--------------------------------------------------------------------------------------
date_time = str(datetime.now())
time = date_time.split()[1].split(':')


#diplay on tkinter----------------------------------------------------------------------------------------------------------
window = tk.Tk()
window.title("Day & Night")
window.minsize(width= 1500, height= 900)
window.config(bg= '#ffffff', padx= 20)

date_entry = DateEntry(window, locale= 'en_UK', selectmode= 'day', width= 10, justify= 'center')
date_entry.grid(row= 27, column= 0, columnspan= 3, pady= 0, padx= 0)

hour_box = ttk.Combobox(window, values= [str(i).zfill(2) for i in range(24)], state= 'readonly', width= 2)
hour_box.current(int(time[0]))
hour_box.grid(row= 28, column= 0, sticky= 'e')

colon = tk.Label(window, text= ':', bg= '#ffffff', font= ('Arial', 16, 'bold'))
colon.grid(row= 28, column= 1)

min_box = ttk.Combobox(window, values= [str(i).zfill(2) for i in range(60)], state= 'readonly', width= 2)
min_box.current(int(time[1]))
min_box.grid(row= 28, column= 2, sticky= 'w')

plot_button = tk.Button(window,
                        width= 12,
                        text= 'Plot',
                        command= lambda: plot(),
                        bg= '#dddddd',
                        relief= 'flat')
plot_button.grid(row= 29, column= 0, columnspan= 3, pady= 0, padx= 0)
overwrite_button = tk.Button(window,
                             width= 12,
                             text= 'Clear & Plot',
                             command= lambda: map_and_plot(),
                             bg= '#dddddd',
                             relief= 'flat')
overwrite_button.grid(row= 30, column= 0, columnspan= 3, pady= 0, padx= 0)


#computing plot shape and position on map-----------------------------------------------------------------------------------
def sun_shift(hour, min, noontime):
    min_passed = hour*60 + min - timezone
    del_x = noontime - min_passed
    return del_x/4

def days_after_solstice(month, day):
    output = 11
    for i in range(month - 1):
        output += days_in_months[i]
    output += day
    return output % 365


#getting noon time at (0, 0)------------------------------------------------------------------------------------------------
def noon_time(year, month, day):
    info = requests.get(url= f"https://api.sunrisesunset.io/json?lat=0&lng=0&date={year}-{month}-{day}")
    info.raise_for_status()
    data = info.json()
    noon = data['results']['solar_noon'].split(':')
    noon_min = int(noon[0])*60 + int(noon[1])
    return noon_min


#plotting the curve---------------------------------------------------------------------------------------------------------
def plot():
    global attempts
    attempts = 0

    temp = str(date_entry.get_date()).split('-')
    d = days_after_solstice(int(temp[1]), int(temp[2]))
    noon_min = noon_time(int(temp[0]), int(temp[1]), int(temp[2]))
    delta_x = sun_shift(int(hour_box.get()), int(min_box.get()), noon_min)
    
    frac = d/365
    tilt = 0.41 - 4*0.41*abs(frac - 0.5)

    plot_data.append((delta_x, tilt, date_entry.get_date(), f'{hour_box.get()}:{min_box.get()}'))
    phi_deg = [-89.999 + (i/1999)*179.998 for i in range(2000)]
    phi = [i*(3.1415/180) for i in phi_deg]
    plt.close()

    ax = map.plot(figsize= (15, 8), color= '#505050')
    for entry in plot_data:
        theta_p = [entry[0] + 180 + (180/3.1415)*arccos(tan(entry[1])*tan(i)) for i in phi]
        theta_n = [entry[0] - 180 - (180/3.1415)*arccos(tan(entry[1])*tan(i)) for i in phi]
        theta_p_mod = [(i + 180)%360 - 180 for i in theta_p]
        theta_n_mod = [(i + 180)%360 - 180 for i in theta_n]

        ax.scatter(x= theta_p_mod, y= phi_deg, color= colours[attempts % 6], s= 0.75)
        ax.scatter(x= theta_n_mod, y= phi_deg, color= colours[attempts % 6], s= 0.75)
        ax.add_patch(shp.Circle(xy= (entry[0], 0),
                                radius= 15,
                                color= colours[attempts % 6],
                                fill= True,
                                alpha= 0.4,
                                label= f'{entry[2]}, {entry[3]}'))
        attempts += 1

    plt.legend(loc= 'lower left', facecolor= '#383838', labelcolor= '#ffffff')
    ax.set_axis_off()
    fig = ax.get_figure()
    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master= window)
    canvas.get_tk_widget().grid(row= 0, column= 3, rowspan= 80)

def map_and_plot():
    global plot_data
    plot_data = []
    plt.close()
    plot()

map_and_plot()

window.mainloop()