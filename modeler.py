from datetime import datetime, timedelta
from manager.station_manager import StationManager
from manager.train_manager import TrainManager
from db_logger import Logger


class Modeler:
    def __init__(self, starting_time: datetime, end_time: datetime,
                 station_manager: StationManager, train_manager: TrainManager, logger: Logger):
        self._station_manager = station_manager
        self._train_manager = train_manager
        self._starting_time = starting_time
        self._end_time = end_time
        self._logger = logger

    def print_info(self, now: datetime):
        station_info = self._station_manager.get_stations_info()
        train_info = self._train_manager.get_trains_info()
        print(now)
        for info in station_info:
            print(info)
        for info in train_info:
            print(info)

    def __add_info_to_db(self, now: datetime):
        stations_info = self._station_manager.get_stations_info()
        trains_info = self._train_manager.get_trains_info()
        self._logger.insert_data(stations_info, trains_info, now)

    def simulate(self):
        simulation_time = self._starting_time
        while simulation_time <= self._end_time:
            self._train_manager.update()
            self._station_manager.update()
            # self.print_info(simulation_time)
            self.__add_info_to_db(simulation_time)
            simulation_time += timedelta(hours=1)
