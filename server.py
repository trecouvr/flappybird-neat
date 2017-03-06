from collections import OrderedDict
import json
import time
import pickle

import gevent
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource

from neat import config, population, chromosome, genome, visualize
from neat.nn import nn_pure as nn

from flappy import GameEngine


clients = []


class EchoApplication(WebSocketApplication):

    def on_open(self):
        print("Connection opened")
        clients.append(self.ws)

    def on_message(self, message):
        print("Message: %s" % message)

    def on_close(self, reason):
        print("Websocket connection closed {0}:".format(reason))
        clients.remove(self.ws)


def load(filename):
    with open(filename, 'rb') as f:
        winner = pickle.load(f)
    while True:
        eval_fitness([winner])


def main():
    chromosome.node_gene_type = genome.NodeGene
    def k(population):
        eval_fitness(population)
    population.Population.evaluate = k
    pop = population.Population()
    pop.epoch(300, report=True, save_best=False)

    winner = pop.stats[0][-1]
    print('Winner id: %d' % winner.id)

    # Let's check if it's really solved the problem
    #print('\nBest network output:')
    #brain = nn.create_ffphenotype(winner)

    # saves the winner
    print('Save winner')
    with open('winner_chromosome', 'wb') as f:
        pickle.dump(winner, f)
    print('Done')

    return

    while True:
        eval_fitness([winner])


def eval_fitness(population):
    print('Eval fitness')
    engine = GameEngine(len(population))
    for chromo, bird in zip(population, engine.birds):
        chromo.fitness = 0
        bird.brain = nn.create_ffphenotype(chromo)

    def next_pipes():
        pipe1 = pipe2 = None
        for pipe in engine.pipes:
            if not pipe.passed:
                if pipe1 is None:
                    pipe1 = (pipe.x, pipe.height)
                elif pipe2 is None:
                    pipe2 = (pipe.x, pipe.height)
                    break
                else:
                    raise ValueError('Should not be here')
        if pipe1 is None:
            pipe1 = (engine.width, engine.height / 2)
        if pipe2 is None:
            pipe2 = (engine.width, engine.height / 2)
        return pipe1, pipe2

    while not engine.is_end_game() and engine.ticks < 13000:
        commands = []
        pipe1, pipe2 = next_pipes()
        for bird in engine.birds:
            if bird.alive:
                output = bird.brain.sactivate([
                    bird.y,
                    bird.vy,
                    pipe1[0],
                    pipe1[1],
                    pipe2[0],
                    pipe2[1],
                ])
                bird.input_flap = output[0] > 0.5
        engine.do_tick()
        if True or engine.ticks % 10 == 0:
            for client in clients:
                gamestate = engine.dumpstate()
                data = json.dumps(gamestate)
                client.send(data, False)
            gevent.sleep(1/60.0)

    for chromo, bird in zip(population, engine.birds):
        chromo.fitness = bird.ticks


if __name__ == '__main__':
    import argparse
    config.load('brain_config')

    parser = argparse.ArgumentParser(description='Play flappybird.')
    parser.add_argument('--load', help='Load a chromosome')
    args = parser.parse_args()

    if args.load:
        gevent.spawn(load, args.load)
    else:
        gevent.spawn(main)

    WebSocketServer(
        ('0.0.0.0', 4000),
        Resource(OrderedDict({'/': EchoApplication}))
    ).serve_forever()
