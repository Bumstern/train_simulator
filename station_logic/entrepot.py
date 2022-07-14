import math

from station_logic.train_station import TrainStation
from train_logic.train import Train
from train_logic.train_state import TrainState


class Entrepot(TrainStation):
    def __init__(self,
                 station_name: str,
                 oil_volume: int,
                 tracks_num: int,
                 emptying_speed: int,
                 filling_speed: int,
                 storage_volume: int,
                 unload_limit: int):
        super().__init__(station_name, oil_volume, tracks_num)
        self._emptying_speed = emptying_speed
        self._filling_speed = filling_speed
        self._storage_volume = storage_volume
        self._unload_limit = unload_limit
        self._unloader_train = None
        self._last_collected_oil_per_track = [None] * tracks_num

    def get_info(self) -> dict:
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
        # Вычисляем суммарный объем топлива (объем топлива в поездах + хранилище + пришедшем поезде),
        # а также кол-во свободных жд путей
        sum_oil_volume = self._oil_volume + train.oil_volume
        free_tracks_num = 0
        for train in self._tracks:
            if train is not None:
                sum_oil_volume += train.oil_volume
            else:
                free_tracks_num += 1

        can_add = True
        # Проверяем, что есть свободный жд путь
        if free_tracks_num == 0:
            can_add = False
        # Проверяем, что суммарный объем топлива не превышает вместимости хранилища
        elif sum_oil_volume <= self._storage_volume:
            # Проверяем, что пришедший поезд сможет разгружаться, не мешая разгр. поезду
            if sum_oil_volume >= self._unload_limit:
                if self._unloader_train is None:
                    if free_tracks_num < 2:
                        can_add = False
        else:  # превышает вместимость хранилища
            can_add = False
        return can_add

    def add_train_to_track(self, train: Train) -> bool:
        is_added = False
        # Пытаемся добавить поезд на путь, проводя предсимуляцию
        if self.__pre_simulate(train):
            is_added = True
            for i, track in enumerate(self._tracks):
                # Ищем первый свободный жд путь
                if track is None:
                    # Ставим на него поезд
                    train.state = TrainState.In_cargo_process
                    self._tracks[i] = train
                    break
        return is_added

    def __unloader_train_adding_logic(self):
        # Вычисляем суммарный объем топлива (объем топлива в поездах + хранилище),
        # а также кол-во свободных жд путей
        sum_oil_volume = self._oil_volume
        free_tracks_num = 0
        for train in self._tracks:
            if train is not None:
                sum_oil_volume += train.oil_volume
            else:
                free_tracks_num += 1

        # Проверяем, что разгр. нет и есть свободное место под него
        if self._unloader_train is None and free_tracks_num > 0:
            is_added = False
            # Проверить, что кол-во нефти в поездах и в хранилище >= объема хранилища разгр.
            if sum_oil_volume >= self._unload_limit:
                # Вычисляем минимальную скорость пополнения
                sum_speed = self._filling_speed - self._emptying_speed
                if sum_speed < 0:
                    has_steps = self._oil_volume // abs(sum_speed)
                    need_steps = math.ceil(self._unload_limit / self._emptying_speed)
                    # Проверяем, что хватает шагов для наполнения хранилища на необходимое кол-во
                    if has_steps >= need_steps:
                        is_added = True
                else:
                    is_added = True

            if is_added:
                # Создаем поезд-разгрузчик
                unloader_train = create_unload_train(self._station_name, self._unload_limit)

                for i, track in enumerate(self._tracks):
                    # Ищем первый свободный жд путь
                    if track is None:
                        # Добавляем поезд-разгрузчик
                        self._unloader_train = unloader_train
                        # Ставим на пути
                        self._tracks[i] = unloader_train
                        break

    def __fill_storage(self):
        # Собираем топливо
        collected_oil = 0
        self._last_collected_oil_per_track = [None] * len(self._tracks)
        for i, train in enumerate(self._tracks):
            if train is not None:
                # Проверяем является ли состав поездом-разгрузки
                if train == self._unloader_train:
                    # Погружаем топливо в поезд-разгрузки
                    oil_amt = self._emptying_speed - train.fill_storage(self._emptying_speed)
                    collected_oil -= oil_amt
                    # Логгирование
                    self._last_collected_oil_per_track[i] = oil_amt
                else:
                    # Разгружаем топливо из обычных поездов
                    oil_amt = train.empty_storage(self._filling_speed)
                    collected_oil += oil_amt
                    # Логгирование
                    self._last_collected_oil_per_track[i] = oil_amt
        # Пополняем хранилище на собранное значение
        self._oil_volume += collected_oil

    def __send_trains(self):
        for i, train in enumerate(self._tracks):
            if train is not None:
                # Проверяем является ли состав поездом-разгрузки
                if train == self._unloader_train:
                    # Полон ли поезд
                    if train.is_full():
                        # Убираем с путей
                        self._tracks[i] = None
                        # Убираем поезд-разгрузчик
                        self._unloader_train = None
                else:
                    # Пустой ли поезд
                    if train.is_empty():
                        # Обновляем его состояние на оконченное
                        train.state = TrainState.Ready
                        # Убираем с путей
                        self._tracks[i] = None

    def update(self):
        # Добавляем поезд-разгрузчик
        self.__unloader_train_adding_logic()
        # Разгружаем/погружаем поезда и пополняем хранилище
        self.__fill_storage()
        # Отправляем поезда
        self.__send_trains()


def create_unload_train(station_name: str, storage_volume: int):
    train = Train(name='Разгрузочный',
                  load_station_name=station_name,
                  unload_station_name='',
                  velocity=0,
                  storage_volume=storage_volume,
                  state=TrainState.In_cargo_process)
    return train
