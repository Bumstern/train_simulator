from station_logic.train_station import TrainStation
from train_logic.train import Train


class StationManager:
    """ Manages stations logic """

    def __init__(self, stations: list[TrainStation]):
        """
        Parameters
        ----------
        stations
            List of train stations. Station names must be unique
        """

        station_names = set()
        for station in stations:
            if station.station_name in station_names:
                raise AttributeError('Station names must be unique')
            station_names.add(station.station_name)

        self._stations = dict()
        for station in stations:
            self._stations[station.station_name] = station

    def update(self):
        """ Updates stations state """

        for station in self._stations.values():
            station.update()

    def add_train_to_station(self, train: Train, station_name: str) -> bool:
        """ Add a train to the track of the current station

        Parameters
        ----------
        train
            Train to add
        station_name
            Name of station where train need to add

        Returns
        -------
        bool
            True if train was added successfully, False otherwise
        """

        if station_name not in self._stations.keys():
            raise AttributeError('No such station name')
        return self._stations[station_name].add_train_to_track(train)

    def get_station_names(self) -> list[str]:
        return list(self._stations.keys())

    def get_stations_info(self) -> list[dict]:
        """ Get stations logging info

        Returns
        -------
        list[dict]
            Terminal:
                <oil_amt> int: amount of oil in storage
                <oil_mined> int: amount of mined oil during last step
                <train_name> str: name of train on the track. None if track is free
                <oil_collected> int: amount of train's collected oil during last step
                <train_storage> int: amount of oil in train's storage
            Entrepot:
                <oil_amt> int: amount of oil in storage
                <tracks> list: list of tracks where elements consist of
                    <train_name> str: name of train on the track. None if track is free
                    <oil_collected> int: amount of train's collected oil during last step
                    <storage> int: amount of oil in train's storage
        """
        info = []
        for station in self._stations.values():
            elem = {station.station_name: station.get_info()}
            info.append(elem)
        return info
