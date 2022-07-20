import math

from station_logic.train_station import TrainStation
from train_logic.train import Train
from train_logic.train_state import TrainState


class Entrepot(TrainStation):
    """ Entrepot station where oil is unloaded """

    def __init__(self,
                 station_name: str,
                 oil_volume: int,
                 tracks_num: int,
                 emptying_speed: int,
                 filling_speed: int,
                 storage_volume: int,
                 unload_limit: int):
        """
        Parameters
        ----------
        station_name
            A name of the station. Must be unique
        oil_volume
            Initial oil amount in storage
        tracks_num
            Number of railway tracks
        emptying_speed
            Speed of station storage emptying
        filling_speed
            Speed of station storage filling
        storage_volume
            Maximum oil amount that station can store
        unload_limit
            Unloader train storage size
        """

        super().__init__(station_name, oil_volume, tracks_num)
        self._emptying_speed = emptying_speed
        self._filling_speed = filling_speed
        self._storage_volume = storage_volume
        self._unload_limit = unload_limit
        self._unloader_train = None
        self._last_collected_oil_per_track = [None] * tracks_num

    def get_info(self) -> dict:
        """ Get entrepot condition info

        Returns
        -------
        dict
            <oil_amt> int: amount of oil in station storage
            <tracks> list: list of tracks where elements consist of -
                    <train_name> str: name of train on the track. None if track is free
                    <oil_collected> int: amount of train's collected oil during the last step
                    <storage> int: amount of oil in train storage
        """

        tracks_info = []
        for i, track in enumerate(self._tracks):
            elem = {'train_name': None, 'oil_collected': self._last_collected_oil_per_track[i], 'storage': None}
            if track is not None:
                elem['train_name'] = track.name
                elem['storage'] = track.oil_volume
            tracks_info.append(elem)
        info = {'oil_amt': self._oil_volume,
                'tracks': tracks_info}
        return info

    def __pre_simulate(self, train: Train) -> bool:
        """  Preliminary simulation of train adding process to the track

        Parameters
        ----------
        train
            Train for add simulation process

        Returns
        -------
        bool
            True if train can be added successfully, False otherwise
        """

        # Calculating the total amount of oil (the amount of oil in trains + storage + arriving train)
        # and the number of free railway tracks
        sum_oil_volume = self._oil_volume + train.oil_volume
        free_tracks_num = 0
        for train in self._tracks:
            if train is not None:
                sum_oil_volume += train.oil_volume
            else:
                free_tracks_num += 1

        can_add = True
        # Check if there is a free track on the station
        if free_tracks_num == 0:
            can_add = False
        # Checking that the total volume of oil does not exceed the storage capacity
        elif sum_oil_volume <= self._storage_volume:
            # We check that the incoming train will be able to unload without interfering with the unloading train
            if sum_oil_volume >= self._unload_limit:
                if self._unloader_train is None:
                    if free_tracks_num < 2:
                        can_add = False
        else:  # otherwise exceeds storage capacity
            can_add = False
        return can_add

    def add_train_to_track(self, train: Train) -> bool:
        """ Add a train to the track

        Parameters
        ----------
        train
            Train to add

        Returns
        -------
        bool
            True if train was added successfully, False otherwise
        """

        is_added = False
        # Trying to add a train to the track by doing a presimulation
        if self.__pre_simulate(train):
            is_added = True
            for i, track in enumerate(self._tracks):
                # Looking for the first free track
                if track is None:
                    # Put a train to this track
                    train.state = TrainState.In_cargo_process
                    self._tracks[i] = train
                    break
        return is_added

    def __unloader_train_adding_logic(self):
        """ Logic of adding an unloader train to the station """

        # Calculating the total amount of oil (the volume of oil in trains + storage)
        # and the number of free railway tracks
        sum_oil_volume = self._oil_volume
        free_tracks_num = 0
        for train in self._tracks:
            if train is not None:
                sum_oil_volume += train.oil_volume
            else:
                free_tracks_num += 1

        # Checks that there is no unloader train and there is free space for it
        if self._unloader_train is None and free_tracks_num > 0:
            is_added = False
            # Checks that the amount of oil in trains and station storages >=
            # the volume of the storage of the unloader train
            if sum_oil_volume >= self._unload_limit:
                # Calculating the minimum storage filling speed
                sum_speed = self._filling_speed - self._emptying_speed
                if sum_speed < 0:
                    has_steps = self._oil_volume // abs(sum_speed)
                    need_steps = math.ceil(self._unload_limit / self._emptying_speed)
                    # Checks that there are enough steps to fill the storage for the required number
                    if has_steps >= need_steps:
                        is_added = True
                else:
                    is_added = True

            if is_added:
                # Create an unloader train
                unloader_train = create_unload_train(self._station_name, self._unload_limit)

                for i, track in enumerate(self._tracks):
                    # Looking for the first free track
                    if track is None:
                        # Adding an unloader train
                        self._unloader_train = unloader_train
                        # Put unloader train to the track
                        self._tracks[i] = unloader_train
                        break

    def __fill_storage(self):
        """ Fill the station storage """

        # Collecting the oil
        collected_oil = 0
        self._last_collected_oil_per_track = [None] * len(self._tracks)
        for i, train in enumerate(self._tracks):
            if train is not None:
                # Checking if the train is an unloader train
                if train == self._unloader_train:
                    # Loading oil into the unloader train
                    oil_amt = self._emptying_speed - train.fill_storage(self._emptying_speed)
                    collected_oil -= oil_amt
                    # Logging logic
                    self._last_collected_oil_per_track[i] = oil_amt
                else:
                    # Unloading oil from train
                    oil_amt = train.empty_storage(self._filling_speed)
                    collected_oil += oil_amt
                    # Logging logic
                    self._last_collected_oil_per_track[i] = oil_amt
        # Filling the storage with the collected value
        self._oil_volume += collected_oil

    def __send_trains(self):
        """ Departure trains from the tracks """

        for i, train in enumerate(self._tracks):
            if train is not None:
                # Checking if the train is an unloader train
                if train == self._unloader_train:
                    # Is the train storage full
                    if train.is_full():
                        # Removing the train from the track
                        self._tracks[i] = None
                        # Removing the unloader train
                        self._unloader_train = None
                else:
                    # Is the train storage empty
                    if train.is_empty():
                        # Update train state to "Ready"
                        train.state = TrainState.Ready
                        # Removing the train from the track
                        self._tracks[i] = None

    def update(self):
        # Add unloader train
        self.__unloader_train_adding_logic()
        # Loading/unloading trains and fill the station storage
        self.__fill_storage()
        # Trains departing
        self.__send_trains()


def create_unload_train(station_name: str, storage_volume: int):
    """ Creates an unloader train

    Parameters
    ----------
    station_name
        Name of entrepot station
    storage_volume

    Returns
    -------
    Train
        New unloader train with 0 oil volume
    """

    train = Train(name='Разгрузочный',
                  load_station_name=station_name,
                  unload_station_name='',
                  velocity=0,
                  storage_volume=storage_volume,
                  state=TrainState.In_cargo_process)
    return train
