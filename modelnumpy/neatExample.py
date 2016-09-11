from functools import partial
from neat import nn, population, statistics, activation_functions
import cellularAutomaton as ca
import numpy as np
import argparse

import os, glob, sys
from util import * #HexagonGenerator,SaveStatePicture,sort_nicely
sys.path.insert(0, '../')
from testGUI import *

# GUIDE
# initilize game object with some initialState, e.g. cellularAutomaton.initializeHexagonal(), and some parameters, e.g. cellularAutomaton.defaultParameters
# add your species with game.setNewSpecies(index, name, color, energy), only index and name are really needed
# now the iterations start
#       1. get the game state, it's a dict with {cells, neighbors, secondneighbors, futureStates, shape}
#       2. make your decisions for your species by filtering cells, neighbors is an array that can be used as a mask for the cells array
#       2.2 register your decisions with setDecisions(name, ['actions',targetvalue] where actions are valid actions and targetvalues are the neighbor index
#       3. call evolve()

# this is not how you have to make your decisions
# this is just some simple function that makes decisions for species 'Move' and 'Clone'
def makeDecision(state, spec):
    mask = state['cells'][:, 1] == spec
    N = np.sum(mask)
    if N < 1:
        return np.array([])
    dec = np.empty((N, 2), dtype=object)
    dec[:, 0] = 'stay'
    dec[:, 1] = 0
    cells = state['cells'][mask]
    neighbors = state['cells'][np.int_(state['neighbors'][mask])]
    secondneighbors = state['cells'][np.int_(state['secondneighbors'][mask])]

    if spec == 'Move':
        dec[:, 0] = 'move'
        dec[:, 1] = np.random.randint(0, len(neighbors[0]), N)

    if spec == 'Clone':
        dec[:, 0] = 'clone'
        dec[:, 1] = np.random.randint(0, len(neighbors[0]), N)

    return dec


def netDecision(state, spec, net):
    mask = state['cells'][:, 1] == spec
    N = np.sum(mask)
    if N < 1:
        return np.array([])
    dec = np.empty((N, 2), dtype=object)
    dec[:, 0] = 'stay'
    dec[:, 1] = 0
    cells = state['cells'][mask]
    neighbors = state['cells'][np.int_(state['neighbors'][mask])]
    secondneighbors = state['cells'][np.int_(state['secondneighbors'][mask])]
    # input will be self.energy, all 6 neighbors as -1,0,1 enemy,empty,friendly, then energies, 13 total, 19 if secondneighbors
    neighborvalues = np.zeros(np.shape(neighbors)[:2])
    neighborvalues[(neighbors[:, :, 1] != spec) & (neighbors[:, :, 1] != 'empty')] = -1
    neighborvalues[neighbors[:, :, 1] == spec] = 1
    neighborenergies = neighbors[:, :, 3]

    inputs = np.zeros((N, 13))
    inputs[:, 0] = cells[:, 3]
    inputs[:, 1:7] = neighborvalues
    inputs[:, 7:13] = neighborenergies
    # output will be stay, wall, clone 1-6, move 1-6, fight 1-6, infuse 1-6: 26 total
    outputs = np.zeros((N,26))
    for i in range(N):
        outputs[i] = net.serial_activate(inputs[i])
        #outputs[i] = net.activate(inputs[i])

    choices = np.argmax(outputs,axis=1)
    actions = np.empty((len(choices), 2),dtype='object')
    actions[:,0] = 'stay'
    actions[:,1] = 0

    actions[choices == 0] = [['stay', 0]]
    actions[choices == 1] = [['wall', 0]]
    mask = (choices > 1 ) & (choices < 8)
    actions[mask,0] = 'clone'
    actions[mask,1] = choices[mask] - 2
    mask = (choices > 7 ) & (choices < 14)
    actions[mask,0] = 'move'
    actions[mask,1] = choices[mask] - 8
    mask = (choices > 13 ) & (choices < 20)
    actions[mask,0] = 'fight'
    actions[mask,1] = choices[mask] - 14
    mask = (choices > 19 ) & (choices < 26)
    actions[mask,0] = 'infuse'
    actions[mask,1] = choices[mask] - 20
    return actions


def countSpecies(state, spec):
    return np.sum(state['cells'][:, 1] == spec)


# this is a fitness function for trainig single genomes alone
def eval_fitness_single(genomes):
    # multiple fights make for better statistics
    num_runs = 1
    for g in genomes:
        net = nn.create_recurrent_phenotype(g)
        achi = 0
        for _ in range(num_runs):
            mooreNeighborhood = ca.Neighborhood(gocl.initNeighborhood)
            gameOfLife = ca.CellularAutomaton(mooreNeighborhood)
            gameOfLife.parameters = gameOfLife.world['parameters']
            newSpecies(gameOfLife, {'species': 'test', 'color': 'Blue', 'position': {'x': 0, 'y': 0}})
            currentDecision = partial(netDecision, net=net)
            evolve = gameOfLife.evolve
            c = 0
            while c < 20:
                dec = {}
                recursionDecision(gameOfLife.world['space'], dec, currentDecision)
                gameOfLife.decisions = dec
                evolve()
                c += 1
            achi += countSpecies(gameOfLife.world['space'], 'test')
        g.fitness = achi / num_runs


# this is a fitness function for training genomes by letting them play on a common field
def eval_fitness_internalfight(allgenomes):
    num_runs = 3
    for g in allgenomes:
        g.fitness = 0
    # sadly, the number of genomes from neat-python is not fixed, so we only train some to fit %4
    genomes = allgenomes[:int(len(allgenomes) / 4) * 4]
    print(len(allgenomes), len(genomes))
    for _ in range(num_runs):
        # geht nur, wenn genomes durch 4 teilbar ist
        grouping = np.reshape(np.random.permutation(len(genomes)), (len(genomes) / 4, 4))
        for group in grouping:
            nets = []
            game = ca.CellularAutomaton(initialState=ca.initializeHexagonal(15, 15), param=ca.defaultParameters)
            for i, g in enumerate(group):
                nets.append(nn.create_feed_forward_phenotype(genomes[g]))
                game.setNewSpecies(int(i * 15*15/4), 'spec'+str(i))
            while game.step < 100:
                state = game.getState()
                for j, g in enumerate(group):
                      game.setDecisions('spec'+str(j), netDecision(state, 'spec'+str(j), nets[j]))
                game.evolve()
            for k, g in enumerate(group):
                genomes[g].fitness += countSpecies(game.getState(), 'spec'+str(k))
    # results of fights define the fitness
    for g in genomes:
        g.fitness = g.fitness / num_runs


# adding elu to activation functions
def elu(x):
    return x if x < 0 else np.exp(x) - 1


activation_functions.add('elu', elu)


def train():
    print("Starting...")
    pop = population.Population(os.path.join(os.path.dirname(__file__), 'nn_config'))
    # HINT change checkpoints for new try or reloading
    try:
        pop.load_checkpoint(os.path.join(os.path.dirname(__file__), 'checkpoints/popv1.cpt'))
    except:
        pass
    pop.run(eval_fitness_internalfight, 10)
    pop.save_checkpoint(os.path.join(os.path.dirname(__file__), 'checkpoints/popv1.cpt'))

    statistics.save_stats(pop.statistics)
    statistics.save_species_count(pop.statistics)
    statistics.save_species_fitness(pop.statistics)

    winner = pop.statistics.best_genome()
    print('\nBest genome:\n{!s}'.format(winner))


def visualizeWinners(checkpoint, config, picdir, rounds):
    pop = population.Population(config)
    pop.load_checkpoint(checkpoint)
    pop.run(eval_fitness_internalfight, 1)
    winner = pop.statistics.best_genome()
    p = []
    best4 = []
    for s in pop.species:
        p.extend(s.members)
    for c in np.random.choice(len(p),4,replace=False):
        best4.append(p[c])

    nets = {}
    nets['place1'] = nn.create_feed_forward_phenotype(winner)
    nets['place2'] = nn.create_feed_forward_phenotype(best4[1])
    nets['place3'] = nn.create_feed_forward_phenotype(best4[2])
    nets['place4'] = nn.create_feed_forward_phenotype(best4[3])

    filelist = glob.glob(os.path.join(picdir,'step*.png'))
    print(filelist)
    exit()
    for f in filelist:
        os.remove(f)

    game = ca.CellularAutomaton(initialState=ca.initializeHexagonal(15, 15), param=ca.defaultParameters)
    shape = game.getState()['shape']
    game.setNewSpecies(int(shape[1]*shape[0]/4*0), 'place1', 'red')
    game.setNewSpecies(int(shape[1]*shape[0]/4*1-1), 'place2', 'yellow')
    game.setNewSpecies(int(shape[1]*shape[0]/4*2-1), 'place3', 'green')
    game.setNewSpecies(int(shape[1]*shape[0]/4*3-1), 'place4', 'blue')

    saveStatePicture(game.getState(), picdir)

    while game.step < rounds:
        state = game.getState()
        for s in game.findSpecies():
            try:
                game.setDecisions(s,netDecision(state,s,nets[s]))
            except:
                pass
        game.evolve()
        saveStatePicture(state, picdir)

    app = QApplication(sys.argv)
    pics = sort_nicely(glob.glob(os.path.join(picdir,'step*.png')))
    ex = Example(pics)

    ex.show()
    sys.exit(app.exec_())

#===============================================================================
def main():
    parser = argparse.ArgumentParser(description='Train or let play NNs with neat')
    parser.add_argument('-f', default=False, action='store_true', help='show a fight')
    parser.add_argument('-t', default=False, action='store_true', help='train the population')
    parser.add_argument('-g', default=1, type=int, help='generations to train, will be multiplied by 10, checkpoints are saved after 10 generations')
    parser.add_argument('-r', default=300, type=int, help='rounds to fight')
    parser.add_argument('-p', default='pics/', help='directory for the pics of the fight')
    parser.add_argument('-c', default='checkpoints/somepop.cpt', type=str, help='checkpoint file to use, save and load')
    parser.add_argument('-C', default='nn_config', type=str, help='config file to use, should fit the netDecision function')

    args = parser.parse_args()

    FIGHTFLAG = args.f
    TRAINFLAG = args.t
    TRAINGENS = args.g
    FIGHTROUNDS = args.r
    PICDIR = args.p
    CHECKPOINT = args.c
    CONFIG = args.C

    if (TRAINFLAG == False) & (FIGHTFLAG == False):
        print("Both flags are False, use -f or -t to fight or train!")
    if TRAINFLAG:
        print("Starting training, saving in ",CHECKPOINT)
        for _ in range(TRAINGENS):
        train(CHECKPOINT, CONFIG)
    if FIGHTFLAG:
        print("Letting winner and 3 others fight, saving in ", PICDIR)
        visualizeWinners(CHECKPOINT, CONFIG, PICDIR, FIGHTROUNDS)

if __name__ == "__main__":
	main()
