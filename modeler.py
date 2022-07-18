from datetime import datetime, timedelta
from manager.station_manager import StationManager
from manager.train_manager import TrainManager
from db_logger import Logger


class Modeler:
    """ Runs a simulation for needed period of time """

    def __init__(self, starting_time: datetime, end_time: datetime,
                 station_manager: StationManager, train_manager: TrainManager, logger: Logger = None):
        """

        Parameters
        ----------
        starting_time
            Starting time of simulation
        end_time
            End time of simulation
        station_manager
            Station manager
        train_manager
            Train manager
        logger
            Logger to out to PostgreSQL
        """

        self._station_manager = station_manager
        self._train_manager = train_manager
        self._starting_time = starting_time
        self._end_time = end_time
        self._logger = logger

    def print_info(self, now: datetime):
        """ Prints stations and trains info to the console

        Parameters
        ----------
        now
           Current step of simulation process
        """

        station_info = self._station_manager.get_stations_info()
        train_info = self._train_manager.get_trains_info()
        print(now)
        for info in station_info:
            print(info)
        for info in train_info:
            print(info)

    def __add_info_to_db(self, now: datetime):
        """ Out stations and trains info to the PostgreSQL

        Parameters
        ----------
        now
            Current step of simulation process
        """

        stations_info = self._station_manager.get_stations_info()
        trains_info = self._train_manager.get_trains_info()
        self._logger.insert_data(stations_info, trains_info, now)

    def simulate(self):
        """ Simulation cycle """

        simulation_time = self._starting_time
        while simulation_time <= self._end_time:
            self._train_manager.update()
            self._station_manager.update()
            if self._logger is None:
                self.print_info(simulation_time)
            else:
                self.__add_info_to_db(simulation_time)
            simulation_time += timedelta(hours=1)
