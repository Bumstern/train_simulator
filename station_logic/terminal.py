import math
from random import normalvariate

from station_logic.train_station import TrainStation
from train_logic.train import Train
from train_logic.train_state import TrainState


class Terminal(TrainStation):
    """ Terminal station where oil is produced """

    def __init__(self,
                 station_name: str,
                 oil_volume: int,
                 tracks_num: int,
                 emptying_speed: int,
                 mean_prod_speed: int,
                 std_prod_speed: int):
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
        mean_prod_speed
            Mean of oil producing speed
        std_prod_speed
            Std of oil producing speed
        """

        super().__init__(station_name, oil_volume, tracks_num)
        self._emptying_speed = emptying_speed
        self._mean_prod_speed = mean_prod_speed
        self._std_prod_speed = std_prod_speed
        self._last_oil_mined = None
        self._last_oil_given = None
        assert(tracks_num == 1)

    def get_info(self) -> dict:
        """ Get terminal condition info

        Returns
        -------
        dict
            <oil_amt> int: amount of oil in station storage
            <oil_mined> int: amount of mined oil during the last step
            <train_name> str: name of train
            <oil_collected> int: amount of train's collected oil during the last step
            <train_storage> int: amount of oil in train storage
        """

        train_name = None
        train_storage = None
        if self._tracks[0] is not None:
            train_name = self._tracks[0].name
            train_storage = self._tracks[0].oil_volume

        info = {'oil_amt': self._oil_volume,
                'oil_mined': self._last_oil_mined,
                'train_name': train_name,
                'oil_collected': self._last_oil_given,
                'train_storage': train_storage }
        return info

    def __pre_simulate(self, train: Train) -> bool:
        """ Preliminary simulation of train adding process to the track

        Parameters
        ----------
        train
            Train for add simulation process

        Returns
        -------
        bool
            True if train can be added successfully, False otherwise
        """

        can_add = False
        # Checking if there is enough oil to fully load the train
        if self._oil_volume >= train.storage_volume:
            can_add = True
        else:
            # Calculating average speed of filling the storage
            sum_speed = self._mean_prod_speed - self._emptying_speed
            if sum_speed < 0:
                has_steps = self._oil_volume // abs(sum_speed)
                need_steps = math.ceil(train.storage_volume / self._emptying_speed)
                # Checking that there are enough steps to fill the storage for the required number
                if has_steps >= need_steps:
                    can_add = True
            else:
                can_add = True
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
        track = self._tracks[0]
        # Checking if the track is free
        if track is None:
            # Pre-simulation of train loading process
            if self.__pre_simulate(train):
                # Update the state of the train to "In_cargo_process"
                train.state = TrainState.In_cargo_process
                # Putting the train on track
                self._tracks[0] = train
                is_added = True
        return is_added

    def __mine_oil(self):
        """ Mines oil according to normal distribution """

        oil_mined = int(normalvariate(self._mean_prod_speed, self._std_prod_speed))
        self._last_oil_mined = oil_mined
        self._oil_volume += oil_mined

    def __fill_trains(self):
        """ Fill trains on tracks with oil """

        self._last_oil_given = None
        train = self._tracks[0]
        # Checking if there is a train on the track
        if train is not None:
            # Checking whether it is possible to load the requested amount of oil in one step
            if self._oil_volume - self._emptying_speed > 0:
                overfilled_oil = train.fill_storage(self._emptying_speed)
                self._oil_volume -= self._emptying_speed
                self._oil_volume += overfilled_oil
                self._last_oil_given = self._emptying_speed - overfilled_oil # logging logic
            else:  # otherwise give as much as we can
                overfilled_oil = train.fill_storage(self._oil_volume)
                self._last_oil_given = self._oil_volume - overfilled_oil # logging logic
                self._oil_volume = 0
                self._oil_volume += overfilled_oil

    def __send_trains(self):
        """ Departure trains from the tracks """

        train = self._tracks[0]
        # Checking if there is a train on the track and it is full
        if (train is not None) and train.is_full():
            # Update the state of the train to "Ready"
            train.state = TrainState.Ready
            # Removing the train from the track
            self._tracks[0] = None

    def update(self):
        """ Updates station state """

        # Mine the oil
        self.__mine_oil()
        # Fill the trains on the tracks
        self.__fill_trains()
        # Trains departing
        self.__send_trains()
