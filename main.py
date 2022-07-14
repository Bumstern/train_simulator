from datetime import datetime, timedelta
import json

from station_logic.terminal import Terminal
from station_logic.entrepot import Entrepot
from train_logic.train import Train
from train_logic.train_state import TrainState
from train_logic.train_direction import TrainDirection
from manager.station_manager import StationManager
from manager.train_manager import TrainManager
from modeler import Modeler
from db_logger import Logger


def init_simulation_obj(starting_time: datetime, end_time: datetime) -> Modeler:
    terminals = []
    with open('init_data/terminals.json', 'r', encoding='utf-8') as f:
        terminal_params = json.load(f)
        for param in terminal_params:
            terminal = Terminal(**param)
            terminals.append(terminal)

    entrepots = []
    with open('init_data/entrepot.json', 'r', encoding='utf-8') as f:
        entrepot_params = json.load(f)
        for param in entrepot_params:
            entrepot = Entrepot(**param)
            entrepots.append(entrepot)

    station_manager = StationManager(stations=[*terminals, *entrepots])

    trains = []
    with open('init_data/trains.json', 'r', encoding='utf-8') as f:
        train_params = json.load(f)
        for param in train_params:
            param['state'] = TrainState(param['state'])
            param['direction'] = TrainDirection(param['direction'])
            train = Train(**param)
            trains.append(train)

    distances = []
    with open('init_data/distances.json', 'r', encoding='utf-8') as f:
        dist_params = json.load(f)
        for param in dist_params:
            elem = [param['point_a_name'], param['point_b_name'], param['distance']]
            distances.append(elem)

    train_manager = TrainManager(trains=trains, station_manager=station_manager, distances=distances)
    logger = Logger()
    simul = Modeler(starting_time=starting_time,
                    end_time=end_time,
                    station_manager=station_manager,
                    train_manager=train_manager,
                    logger=logger)
    return simul


# TODO: Написать docstrings к классам и методам
def main():
    starting_time = datetime(year=2021, month=11, day=1)
    end_time = starting_time + timedelta(days=30)
    simulator = init_simulation_obj(starting_time, end_time)
    simulator.simulate()


if __name__ == '__main__':
    main()
