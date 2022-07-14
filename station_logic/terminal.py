import math
from random import normalvariate

from station_logic.train_station import TrainStation
from train_logic.train import Train
from train_logic.train_state import TrainState


class Terminal(TrainStation):
    def __init__(self,
                 station_name: str,
                 oil_volume: int,
                 tracks_num: int,
                 emptying_speed: int,
                 mean_prod_speed: int,
                 std_prod_speed: int):
        super().__init__(station_name, oil_volume, tracks_num)
        self._emptying_speed = emptying_speed
        self._mean_prod_speed = mean_prod_speed
        self._std_prod_speed = std_prod_speed
        self._last_oil_mined = None
        self._last_oil_given = None
        assert(tracks_num == 1)

    def get_info(self) -> dict:
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
        # Функция будет предсимулировать погрузку поезда и
        # будет возвращать bool можно ли его сейчас поставить на пути
        # Работает только с 1 жд путем

        can_add = False
        # Проверяем хватает ли кол-ва нефти для полной погрузки поезда
        if self._oil_volume >= train.storage_volume:
            can_add = True
        else:
            # Вычисляем среднюю скорость пополнения
            sum_speed = self._mean_prod_speed - self._emptying_speed
            if sum_speed < 0:
                has_steps = self._oil_volume // abs(sum_speed)
                need_steps = math.ceil(train.storage_volume / self._emptying_speed)
                # Проверяем, что хватает шагов для наполнения хранилища на необходимое кол-во
                if has_steps >= need_steps:
                    can_add = True
            else:
                can_add = True
        return can_add

    def add_train_to_track(self, train: Train) -> bool:
        is_added = False
        track = self._tracks[0]
        # Проверяем свободен ли путь
        if track is None:
            # Производим предсимуляцию погрузки поезда
            if self.__pre_simulate(train):
                # Обновляем состояние поезда на то, что он находится в грузовом процессе
                train.state = TrainState.In_cargo_process
                # Ставим поезд на путь
                self._tracks[0] = train
                is_added = True
        return is_added

    def __mine_oil(self):
        oil_mined = int(normalvariate(self._mean_prod_speed, self._std_prod_speed))
        self._last_oil_mined = oil_mined
        self._oil_volume += oil_mined

    def __fill_trains(self):
        self._last_oil_given = None
        train = self._tracks[0]
        # Проверяем, что на путях стоит поезд
        if train is not None:
            # Проверяем можно ли погрузить запрашиваемое кол-во топлива за один шаг
            if self._oil_volume - self._emptying_speed > 0:
                overfilled_oil = train.fill_storage(self._emptying_speed)
                self._oil_volume -= self._emptying_speed
                self._oil_volume += overfilled_oil
                self._last_oil_given = self._emptying_speed - overfilled_oil # логгирование
            else:  # значит отдаем сколько есть
                overfilled_oil = train.fill_storage(self._oil_volume)
                self._last_oil_given = self._oil_volume - overfilled_oil # логгирование
                self._oil_volume = 0
                self._oil_volume += overfilled_oil

    def __send_trains(self):
        train = self._tracks[0]
        # Проверяем, что на путях есть поезд и он полон
        if (train is not None) and train.is_full():
            # Обновляем состояние поезда на оконченное
            train.state = TrainState.Ready
            # Убираем поезд с путей
            self._tracks[0] = None

    def update(self):
        # Добываем топливо
        self.__mine_oil()
        # Погружаем топливо в поезд
        self.__fill_trains()
        # Отправляем поезд
        self.__send_trains()
