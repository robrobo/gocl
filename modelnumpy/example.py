import cellularAutomaton as ca
import numpy as np
from test2 import HexagonGenerator
from PIL import Image, ImageDraw
from tkinter import *
from PIL import Image, ImageTk
from copy import deepcopy
from itertools import cycle

# GUIDE
# initilize game object with some initialState, e.g. cellularAutomaton.initializeHexagonal(), and some parameters, e.g. cellularAutomaton.defaultParameters
# add your species with game.setNewSpecies(index, name, color, energy), only index and name are really needed
# now the iterations start
#       1. get the game state, it's a dict with {cells, neighbors, secondneighbors, futureStates, shape}
#       2. make your decisions for your species by filtering cells, neighbors is an array that can be used as a mask for the cells array
#       2.2 register your decisions with setDecisions(name, ['actions',targetvalue] where actions are valid actions and targetvalues are the neighbor index
#       3. call evolve()

# Initialisieren
def main():
    game = ca.CellularAutomaton(initialState=ca.initializeHexagonal(10,10),param=ca.defaultParameters)

    root = Tk()
    root.geometry('500x500')
    canvas = Canvas(root, width=500, height=500)
    canvas.pack()
    slideshow = []
    game.setNewSpecies(3, 'Move', 'blue', 3)
    game.setNewSpecies(11, 'Clone', 'green', 30)
    hexagon_generator = HexagonGenerator(20)
    for _ in range(10):
        state = game.getState()
        colors = np.reshape(state['cells'][:,2], state['shape'])
        image = Image.new('RGB', (500, 500), 'white')
        draw = ImageDraw.Draw(image)
        for i in range(len(colors)):
            for j in range(len(colors[0])):
                 hexagon = hexagon_generator(i, j)
                 draw.polygon(hexagon, outline='black', fill=colors[i,j])
        image = ImageTk.PhotoImage(image)
        slideshow.append(canvas.create_image(250,250,image=image))

        for s in game.findSpecies():
            game.setDecisions(s,makeDecision(state,s))
        print(game.cells[game.cells[:,1] != 'empty',:4])
        game.evolve()

    print(game.cells[game.cells[:,1] != 'empty',:4])
    print(slideshow)
    for m in slideshow:
        pass
        #canvas.create_image(250,250,image=m)
    root.mainloop()
    exit()

# this is not how you have to make your decisions
# this is just some simple function that makes decisions for species 'Move' and 'Clone'
def makeDecision(state, spec):
    mask = state['cells'][:, 1] == spec
    N = np.sum(mask)
    if N < 1:
        return np.array([])
    dec = np.empty((N, 2),dtype=object)
    dec[:, 0] = 'stay'
    dec[:, 1] = 0
    cells = state['cells'][mask]
    neighbors = state['cells'][np.int_(state['neighbors'][mask])]
    secondneighbors = state['cells'][np.int_(state['secondneighbors'][mask])]

    if spec == 'Move':
        dec[:,0] = 'move'
        dec[:,1] = np.random.randint(0,len(neighbors[0]),N)

    if spec == 'Clone':
        dec[:,0] = 'clone'
        dec[:,1] = np.random.randint(0,len(neighbors[0]),N)

    return dec

if __name__ == "__main__":
    main()