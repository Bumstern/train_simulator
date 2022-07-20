# Train simulator

## Problem formulation
Need to simulate the movement of trains between two terminals with oil production and a entrepot,
as well as simulate changes in oil residues at the terminals and entrepot.

## Task description
There are 2 terminals "Raduzhny" and "Zvezda", where oil is loaded onto trains, and a entrepot "Polyarny",
where trains unload transported oil. There are two train routes between Raduzhny and Polyarny, Zvezda and Polyarny.
Five train sets run between Raduzhny and Polyarny and 2 trains run between Zvezda and Polyarny.
At the Raduzhny and Zvezda terminals there is only one track where trains can load oil.
There are 3 tracks at the Polyarny entrepot, where trains can process a cargo operation.
As soon as 10,000 tons of oil are accumulated at the Polyarny unloader train will arrive
(It is need to simulate its loading, but it is not necessary to simulate the movement,
in addition, it is believed that there are an unlimited number of such trains and they are always in Polyarny
and are ready to start loading as the required amount of oil accumulates).
Train cannot arrive on the track if it is known that it will not be able to fully load/unload

## Class diagram
![Class diagram](https://user-images.githubusercontent.com/36205247/179873682-0ad951d9-d27b-4101-80e8-a64195cfefa3.png)
