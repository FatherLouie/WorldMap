import geopandas as gp
import matplotlib.pyplot as plt
import matplotlib.colors as col
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from data import country_capital

guesses = []

bg_colour = '#ccccff'
font_colour = '#3a11a0'
country_colour= '#208820'
colour_map = col.ListedColormap([bg_colour, country_colour])

#generate the geoDataFrame initially, with added GUESS column---------------------------------------------------------------
map = gp.read_file('C:\Ze actual stuff\Projects\Coding projects\WorldMap\WB-countries-Admin0_10m')
map["GUESS"] = [False for key in country_capital]


#update map as per guess made-----------------------------------------------------------------------------------------------
def update(placeholder):
    entry = box.get().title()
    for (key, value) in country_capital.items():
        if entry in value:
            box.delete(0, len(entry))
            map.loc[map["WB_NAME"] == key, "GUESS"] = True
            if entry not in guesses:
                guesses.append(entry)

    plt.close()
    ax = map.plot(figsize= (14, 7), column= "GUESS", cmap= colour_map)
    ax.set_axis_off()
    fig = ax.get_figure()
    fig.tight_layout()
    fig.set_facecolor(bg_colour)
    canvas = FigureCanvasTkAgg(fig, master= window)
    canvas.draw()
    canvas.get_tk_widget().place(y= 120)
    score.config(text= f'Score: {len(guesses)} / 197')
    score.lift()


#generate the UI------------------------------------------------------------------------------------------------------------
window = tk.Tk()
window.title("Colour by Country Capitals")
window.minsize(width= 1500, height= 900)
window.config(padx= 50, pady= 20, bg= bg_colour)
window.bind('<Return>', update)

txt = tk.Label(text= "Enter a country capital to colour the world map:", fg= font_colour, bg= bg_colour, font= ('Maiandra GD', 32, 'bold'))
txt.pack()

box = tk.Entry(width= 40, font= ('Maiandra GD', 20), justify= 'center', relief= 'flat', bg= '#ffffff')
box.pack(pady= 20)

score = tk.Label(text= f'Score: {len(guesses)} / 197', fg= font_colour, bg= bg_colour, font= ('Maiandra GD', 20, 'bold'))
score.pack()

window.mainloop()