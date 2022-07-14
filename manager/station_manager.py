from station_logic.train_station import TrainStation
from train_logic.train import Train


class StationManager:
    def __init__(self, stations: list[TrainStation]):
        station_names = set()
        for station in stations:
            if station.station_name in station_names:
                raise AttributeError('Station names must be unique')
            station_names.add(station.station_name)

        self._stations = dict()
        for station in stations:
            self._stations[station.station_name] = station

    def update(self):
        for station in self._stations.values():
            station.update()

    def add_train_to_station(self, train: Train, station_name: str) -> bool:
        if station_name not in self._stations.keys():
            raise AttributeError('No such station name')
        return self._stations[station_name].add_train_to_track(train)

    def get_station_names(self) -> list[str]:
        return list(self._stations.keys())

    def get_stations_info(self) -> list[dict]:
        info = []
        for station in self._stations.values():
            elem = {station.station_name: station.get_info()}
            info.append(elem)
        return info
