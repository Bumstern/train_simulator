from abc import ABC, abstractmethod
from train_logic.train import Train
from train_logic.train_state import TrainState


class TrainStation(ABC):
    """ Base class of train station

    Attributes
    ----------
    station_name
        A name of the station. Must be unique. Read only

    """

    def __init__(self,
                 station_name: str,
                 oil_volume: int,
                 tracks_num: int):
        """

        Parameters
        ----------
        station_name
            A name of the station. Must be unique
        oil_volume
            Initial oil amount in storage
        tracks_num
            Number of railway tracks
        """
        self._station_name = station_name
        self._oil_volume = oil_volume
        self._tracks = [None] * tracks_num

    @property
    def station_name(self) -> str:
        """str:  A name of the station. Must be unique. Read only"""
        return self._station_name

    def has_free_tracks(self) -> bool:
        """ Checks station for free tracks

        Returns
        -------
        bool
            True if it has free tracks, False otherwise
        """

        for track in self._tracks:
            if track is None:
                return True
        return False

    def add_train_to_track(self, train: Train) -> bool:
        """ Add train to the first free track.

        Parameters
        ----------
        train
            Train to be added

        Returns
        -------
        bool
            True if train has successfully added, False otherwise
        """
        is_added = False
        for i, track in enumerate(self._tracks):
            if track is None:
                train.state = TrainState.In_cargo_process
                self._tracks[i] = train
                is_added = True
                break
        return is_added

    @abstractmethod
    def get_info(self) -> dict:
        """ Returns station information for logging purposes.

        Need to implement
        """
        pass

    @abstractmethod
    def update(self):
        """ Implements simulation step logic: fills trains storages and mine the oil.

        Need to implement
        """
        pass
