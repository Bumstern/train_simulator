from enum import Enum


class TrainState(Enum):
    Wait = 1
    Ready = 2
    Transit = 3
    Arrived = 4
    In_cargo_process = 5
