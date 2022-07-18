from train_logic.train import Train
from train_logic.train_direction import TrainDirection
from train_logic.train_state import TrainState
from manager.station_manager import StationManager


class TrainManager:
    """ Manages trains logic """

    def __init__(self, trains: list[Train], station_manager: StationManager, distances: list[list]):
        """
        Parameters
        ----------
        trains
            List of trains. Train names must be unique
        station_manager
            Station manager object
        distances
            List of distances between stations.
            List consists of [station name A, station name B, distance]
        """

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
        """ Get trains logging info

        Returns
        -------
        list[dict]
            <train_name> str: name of the train
            <station_name> str: name of station where train is in cargo process
            <cargo_time> int: amount of steps for how long train is in cargo process
        """

        info = []
        for train in self._trains:
            # Checking if the train has just left
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
        """ Updates trains state that are not in buffer

        Parameters
        ----------
        train
            Train to add
        """

        if train.state == TrainState.Ready:
            train.change_direction()
            train.state = TrainState.Transit
            train.coord = self._dist_mx[train.load_station_name][train.unload_station_name]
            # for logging purposes
            self._trains_cargo_time[train.name] += 1
        elif train.state == TrainState.Arrived:
            # Finding out which station the train arrived at
            arrived_station_name = ''
            if train.direction == TrainDirection.To_load_station:
                arrived_station_name = train.load_station_name
            elif train.direction == TrainDirection.To_unload_station:
                arrived_station_name = train.unload_station_name
            else:
                raise NotImplementedError('No such direction')

            # Checking if there is a queue for loading process
            if len(self._buffers[arrived_station_name]) > 0:
                # Update status to "Wait"
                train.state = TrainState.Wait
                # Putting the train in the queue
                self._buffers[arrived_station_name].append(train)
            else:
                # Trying to set train to the station
                is_added = self._station_manager.add_train_to_station(train, arrived_station_name)
                # Checking that the train has been added to the station
                if not is_added:
                    # Update status to "Wait"
                    train.state = TrainState.Wait
                    # Putting the train in the queue
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
        """ Updates trains state """

        # Updates the states of trains that are NOT in queues
        for train in self._trains:
            # Handling train logic preconditions
            self.__set_train_preconditions(train)
            # Handling train logic
            train.update()

        # Updates the states of trains that are in queues
        for name in self._station_manager.get_station_names():
            buffer = self._buffers[name]
            is_added = True
            # Adding as many trains from the queue as we can
            while is_added:
                if len(buffer) > 0:
                    # Trying to set train to the station
                    is_added = self._station_manager.add_train_to_station(buffer[0], name)
                    if is_added:
                        # for logging purposes
                        self._trains_cargo_time[buffer[0].name] += 1
                        buffer.pop(0)
                else:
                    is_added = False
