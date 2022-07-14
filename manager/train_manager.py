from train_logic.train import Train
from train_logic.train_direction import TrainDirection
from train_logic.train_state import TrainState
from manager.station_manager import StationManager


class TrainManager:
    def __init__(self, trains: list[Train], station_manager: StationManager, distances: list[list]):
        train_names = set()
        for train in trains:
            if train.name in train_names:
                raise AttributeError('Train names must be unique')
            train_names.add(train.name)

        self._trains = trains
        self._station_manager = station_manager
        self._buffers = dict()
        for name in station_manager.get_station_names():
            self._buffers[name] = []

        self._dist_mx = dict([(name, {}) for name in station_manager.get_station_names()])
        for dist in distances:
            self._dist_mx[dist[0]][dist[1]] = dist[2]
            self._dist_mx[dist[1]][dist[0]] = dist[2]

        self._trains_cargo_time = dict()
        for train in trains:
            self._trains_cargo_time[train.name] = -1

    def get_trains_info(self) -> list[dict]:
        info = []
        for train in self._trains:
            # Проверяем, что поезд только что уехал
            if train.state == TrainState.Transit and self._trains_cargo_time[train.name] > -1:
                train_info = {'train_name': train.name,
                              'station_name': None,
                              'cargo_time': self._trains_cargo_time[train.name]}
                if train.direction == TrainDirection.To_load_station:
                    train_info['station_name'] = train.unload_station_name
                elif train.direction == TrainDirection.To_unload_station:
                    train_info['station_name'] = train.load_station_name
                else:
                    raise NotImplementedError('No such direction')
                info.append(train_info)
                self._trains_cargo_time[train.name] = -1
        return info

    def __set_train_preconditions(self, train: Train):
        if train.state == TrainState.Ready:
            train.change_direction()
            train.state = TrainState.Transit
            train.coord = self._dist_mx[train.load_station_name][train.unload_station_name]
            # for logging purposes
            self._trains_cargo_time[train.name] += 1
        elif train.state == TrainState.Arrived:
            # Выясняем на какую станцию прибыл поезд
            arrived_station_name = ''
            if train.direction == TrainDirection.To_load_station:
                arrived_station_name = train.load_station_name
            elif train.direction == TrainDirection.To_unload_station:
                arrived_station_name = train.unload_station_name
            else:
                raise NotImplementedError('No such direction')

            # Проверяем наличие очереди на погрузку
            if len(self._buffers[arrived_station_name]) > 0:
                # Обновляем состояния на "В ожидании"
                train.state = TrainState.Wait
                # Ставим поезд в очередь
                self._buffers[arrived_station_name].append(train)
            else:
                # Пытаемся поставить поезд на погрузку
                is_added = self._station_manager.add_train_to_station(train, arrived_station_name)
                # Проверяем, что поезд был добавлен на погрузку
                if not is_added:
                    # Обновляем состояния на "В ожидании"
                    train.state = TrainState.Wait
                    # Cтавим поезд в очередь
                    self._buffers[arrived_station_name].append(train)
                else: # for logging purposes
                    self._trains_cargo_time[train.name] = 1
        elif train.state == TrainState.In_cargo_process:
            self._trains_cargo_time[train.name] += 1
        elif train.state in [TrainState.Wait, TrainState.Transit]:
            pass
        else:
            raise NotImplementedError('No such state')

    def update(self):
        # Обновляем состояния поездов, не находящихся в очередях
        for train in self._trains:
            # Обрабатываем предусловия логики поезда
            self.__set_train_preconditions(train)
            # Обрабатываем логику поезда
            train.update()

        # Обрабатываем поезда в очередях
        for name in self._station_manager.get_station_names():
            buffer = self._buffers[name]
            is_added = True
            # Добавляем столько поездов из очереди, сколько сможем
            while is_added:
                if len(buffer) > 0:
                    # Пытаемся добавить поезд
                    is_added = self._station_manager.add_train_to_station(buffer[0], name)
                    if is_added:
                        # for logging purposes
                        self._trains_cargo_time[buffer[0].name] += 1
                        buffer.pop(0)
                else:
                    is_added = False
