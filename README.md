<p align="center"> 
  <img width="500" alt="Снимок экрана 2022-11-02 в 17 58 11" src="https://user-images.githubusercontent.com/44533918/199547071-a8017e2f-d2af-4175-9c96-06bffc74f21f.png">
</p>
<h1 align="center"> Easy PostgresSQL DataBase processing. </h1>

## Setup
```bash
> git submodule add https://github.com/mtvy/mProcDB.git
> cd mProcDB
> pip install -r requirements.txt
> python3 mprocdb.py
```
<img width="1273" alt="Снимок экрана 2022-11-02 в 18 29 03" src="https://user-images.githubusercontent.com/44533918/199547460-dbfd4c8d-ab24-403f-abcd-a910357adc86.png">

## Functions
* ### Help
  ```bash
  > python3 mprocdb.py -h
  ```
  <img width="1276" alt="Снимок экрана 2022-11-02 в 18 33 05" src="https://user-images.githubusercontent.com/44533918/199547578-9e1f977b-ba86-404e-976f-0471cde3c9a7.png">

* ### Show params
  ```bash
  > python3 mprocdb.py -p
  ```
  <img width="1277" alt="Снимок экрана 2022-11-02 в 18 50 09" src="https://user-images.githubusercontent.com/44533918/199548301-ab9d910e-0140-4a89-8130-bea5a0f333fc.png">

* ### Create database and user with password
  ```bash
  > python3 mprocdb.py -d
  ```
  <img width="1273" alt="Снимок экрана 2022-11-02 в 18 45 38" src="https://user-images.githubusercontent.com/44533918/199548685-82b6015c-6a18-42fc-9413-6fafbf0d50a6.png">

* ### Create tables at new database
  ```bash
  > python3 mprocdb.py -c
  ```
  <img width="1277" alt="Снимок экрана 2022-11-02 в 18 45 56" src="https://user-images.githubusercontent.com/44533918/199548916-7c529771-d8df-4691-b9ad-5132948455c9.png">

* ### Dump tables into .json file
  ```bash
  > python3 mprocdb.py -s
  ```
  <img width="1275" alt="Снимок экрана 2022-11-02 в 19 02 12" src="https://user-images.githubusercontent.com/44533918/199549213-d889bd8a-700e-4fe8-b508-dca980908779.png">

* ### Add new elems into tables
  ```bash
  > python3 mprocdb.py -a
  ```
  <img width="1276" alt="Снимок экрана 2022-11-02 в 19 00 54" src="https://user-images.githubusercontent.com/44533918/199549962-18dcbca3-1ddf-487e-84fc-041902280a44.png">


* ### Dump tables into .json file
  ```bash
  > python3 mprocdb.py -s
  ```
  <img width="1275" alt="Снимок экрана 2022-11-02 в 19 02 12" src="https://user-images.githubusercontent.com/44533918/199550048-46d7f6ab-9547-43ca-8172-320dbd56fa00.png">

* ### Load tables from .json file into tables
  ```bash
  > python3 mprocdb.py -l
  ```
  <img width="1275" alt="Снимок экрана 2022-11-02 в 19 17 34" src="https://user-images.githubusercontent.com/44533918/199550145-74c8d95a-e520-48b6-9ae1-e6a8c12962a0.png">

* ### Show tables elems
  ```bash
  > python3 mprocdb.py -s
  ```
  <img width="1278" alt="Снимок экрана 2022-11-02 в 19 01 48" src="https://user-images.githubusercontent.com/44533918/199550485-3ea56f1a-1f31-4215-9f0f-f186e422a766.png">

* ### Reset main args at .env (change database, tables info)
  ```bash
  > python3 mprocdb.py -r
  ```
  

