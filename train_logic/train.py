from train_logic.train_state import TrainState
from train_logic.train_direction import TrainDirection


class Train:
    def __init__(self,
                 name: str,
                 load_station_name: str,
                 unload_station_name: str,
                 velocity: int,
                 storage_volume: int,
                 coord: int = 0,
                 state: TrainState = TrainState.Wait,
                 direction: TrainDirection = TrainDirection.To_load_station,
                 oil_volume: int = 0):
        self._name = name
        self._load_station_name = load_station_name
        self._unload_station_name = unload_station_name
        self._oil_volume = oil_volume
        self._velocity = velocity
        self._coord = coord
        self._state = state
        self._direction = direction
        self._storage_volume = storage_volume

    @property
    def name(self) -> str:
        return self._name

    @property
    def load_station_name(self) -> str:
        return self._load_station_name

    @property
    def unload_station_name(self) -> str:
        return self._unload_station_name

    @property
    def oil_volume(self) -> int:
        return self._oil_volume

    @property
    def storage_volume(self) -> int:
        return self._storage_volume

    @property
    def coord(self):
        return self._coord

    @coord.setter
    def coord(self, value: int):
        self._coord = value

    def fill_storage(self, value: int) -> int:
        """ Filling the train storage with oil

        Parameters
        ----------
        value
            Oil amount to fill the storage

        Returns
        -------
        int
            Returns excess oil value
        """

        if self._oil_volume + value <= self._storage_volume:
            self._oil_volume += value
            return 0
        else:
            diff = value - (self._storage_volume - self._oil_volume)
            self._oil_volume = self._storage_volume
            return diff

    def empty_storage(self, value: int) -> int:
        """ Emptying the train storage with oil

        Parameters
        ----------
        value
            Oil amount to empty the storage

        Returns
        -------
        int
            Returns available oil amount
        """

        if self._oil_volume - value >= 0:
            self._oil_volume -= value
            return value
        else:
            diff = value - self._oil_volume
            self._oil_volume = 0
            return diff

    def get_free_storage_space(self) -> int:
        return self._storage_volume - self._oil_volume

    def is_full(self) -> bool:
        return self._oil_volume == self._storage_volume

    def is_empty(self) -> bool:
        return self._oil_volume == 0

    @property
    def state(self) -> TrainState:
        return self._state

    @state.setter
    def state(self, value: TrainState):
        self._state = value

    @property
    def direction(self) -> TrainDirection:
        return self._direction

    def change_direction(self):
        """ Changes direction of train to the opposite """
        if self._direction == TrainDirection.To_load_station:
            self._direction = TrainDirection.To_unload_station
        elif self._direction == TrainDirection.To_unload_station:
            self._direction = TrainDirection.To_load_station
        else:
            raise NotImplementedError('No such direction')

    def __drive_step(self):
        if self._coord - self._velocity >= 0:
            self._coord -= self._velocity
        else:
            self._coord = 0

    def update(self):
        """ Updates train condition due to its state """
        if self._state == TrainState.Transit:
            self.__drive_step()
            if self._coord == 0:
                self._state = TrainState.Arrived
        elif self._state in [TrainState.Wait, TrainState.Ready,
                             TrainState.Arrived, TrainState.In_cargo_process]:
            pass
        else:
            raise NotImplementedError('No such state')

    # TODO: Имя, какая станция и дата прибытия/отправления
    def get_info(self) -> dict:
        """ Get train condition info

        Returns
        -------
        dict
            <name> str: train name
            <state> TrainState: train state
            <direction> TrainDirection: train direction
            <oil> int: oil amount in storage
            <coord> int: coordinate of the train
        """
        info = {'name': self._name,
                'state': self._state,
                'direction': self._direction,
                'oil': self._oil_volume,
                'coord': self._coord}
        return info
