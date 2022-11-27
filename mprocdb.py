#/==================================================================\#
# mprocdb.py                                          (c) Mtvy, 2022 #
#\==================================================================/#
#                                                                    #
# Copyright (c) 2022. Mtvy (Matvei Prudnikov, m.d.prudnik@gmail.com) #
#                                                                    #
#\==================================================================/#

#/-----------------------------/ Libs \-----------------------------\#
from typing import (
    Callable, Tuple,
    Dict, List, Any
)

from progress.bar import IncrementalBar
from decouple     import config

import os, sys, json
import psycopg2, exclog

from psycopg2 import sql
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
GRY="\033[1;37m"; YLW="\033[1;33m"; DF="\033[0m"; GRN="\033[1;32m"; RED="\033[1;31m"

DBRESP = 'SELECT COUNT(1) FROM'
#\------------------------------------------------------------------/#

def _fprint(out, file=sys.stderr):
    print(out, file=file)


#\------------------------------------------------------------------/#
@exclog.logging(out=_fprint)
def __connect(conn_kwrgs) -> Tuple[Any, Any]:
    """This definition returns connection to database."""
    return psycopg2.connect(**conn_kwrgs)
#\------------------------------------------------------------------/#

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

#\------------------------------------------------------------------/#
@exclog.logging(out=_fprint)
def push_msg(msg : str | sql.SQL, conn_kwrgs, ftch=False, rmsg=False) -> Any | bool:
    """This definition sends message to database."""
    con = __connect(conn_kwrgs); data = [False, False]
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    print("pusssssss")
    if con:
        cur = con.cursor()
        cur.execute(msg)
        con.commit()
        if rmsg:
            data[0] = cur.fetchall()

        if ftch:
            cur.execute(ftch)
            data[1] = cur.fetchall()
        return data if data[0] or data[1] else True

    return False
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def get_db(_tb : str, _w_con : List, ftch=False, rmsg=True) -> List | bool:
    return push_msg(f'SELECT * FROM {_tb};', _w_con, ftch, rmsg)
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def insert_db(_tb : str, _set : List, _vls : List, _w_con : Dict) -> str | bool:
    txt = f'INSERT INTO {_tb} ('
    for it in _set:
        txt = f'{txt}{it}, '
    txt = f'{txt[:-2]}) VALUES ('
    for it in _vls:
        if it != 'null':
            txt = f"{txt}'{it}', "
        else:
            txt = f"{txt}{it}, "
    txt = f'{txt[:-2]})'

    return push_msg(txt, _w_con)
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def update_db(msg : str, _tb : str, _p_con : Dict) -> str | bool:
    return push_msg(f'{msg}; {DBRESP} {_tb}', _p_con)
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def delete_db(cnd : str, _tb : str, _p_con : Dict) -> str | bool:
    return push_msg(f'DELETE FROM {_tb} WHERE {cnd}; {DBRESP} {_tb}', _p_con)
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
@exclog.logging(out=_fprint)
def __dump_tables(_write : Callable[[str], None], _tbs : str, _w_con : Dict, **_) -> None:
    _write(f'\n\t{GRY}-----------DUMP-TBS-----------{DF}')

    for _tb in _tbs:
        _write(f'\t{GRY}[DUMP_{YLW}{_tb}{GRY}]{DF}')
        data = get_db(_tb, _w_con)
        if data:
            json.dump(data, open(f'{_tb}.json', 'w'))
            _write(f'\t{GRY}[DUMP_{YLW}{_tb}{GRY}][{GRN}True{GRY}]{DF}')
        else:
            _write(f'\t{GRY}[DUMP_{YLW}{_tb}{GRY}][{RED}False{GRY}]{DF}')


    _write(f'\t{GRY}------------------------------{DF}\n')
#\------------------------------------------------------------------/#    


#\------------------------------------------------------------------/#
@exclog.logging(out=_fprint)
def __load_tables(_write : Callable[[str], None], _ctbs : Dict, _w_con : Dict, **_) -> None:
    _write(f'\n\t{GRY}-----------LOAD-TBS-----------{DF}')
    for _tb in _ctbs.keys():
        elems = json.load(open(f'{_tb}.json'))[0]
        bar = IncrementalBar(f'\t{GRY}[LOAD_{_tb}]', max = len(elems))
        for elem in elems:
            bar.next(); vls = []
            for it, ind in zip(elem, range(len(elem))):
                if list(_ctbs[_tb].values())[ind] == 'serial':
                    continue
                if isinstance(it, str):
                    it = it.replace("'", "''")
                    vls.append(f"{it}")
                elif isinstance(it, int):
                    vls.append(f"'{it}'")
                elif isinstance(it, list):
                    vls.append(f'ARRAY {it}')
                elif isinstance(it, type(None)):
                    vls.append('null')
                else:
                    _write(f'\n\t{GRY}[LOAD_{_tb}][{RED}unsupported_type{GRY}]{DF}')
                    break
            else:
                if not insert_db(_tb, [it for it in _ctbs[_tb].keys() if _ctbs[_tb][it] != 'serial'], vls, _w_con): 
                    _write(f'\t{GRY}[LOAD_{_tb}][{RED}False{GRY}]{DF}\n')
                    break
                continue
            break
        else:
            _write(f'\n\t{GRY} │\n\t └[LOAD_{_tb}][{GRN}True{GRY}]{DF}')

        bar.finish()
    _write(f'\t{GRY}------------------------------{DF}\n')
#\------------------------------------------------------------------/# 


#\------------------------------------------------------------------/# 
@exclog.logging(out=_fprint)
def __cr_database(_write : Callable[[str], None], _w_con : Dict, _p_con : Dict, **_) -> None:
    _write(f'\n\t{GRY}----------CREATE-DB-----------{DF}')

    _write(f'\t{GRY}[CR_DB_{_w_con["dbname"]}]{DF}')
    if push_msg(psycopg2.sql.SQL("CREATE DATABASE {}").format(psycopg2.sql.Identifier(_w_con["dbname"])), _p_con):
        _write(f'\t{GRY}[CR_DB_{_w_con["dbname"]}][{GRN}True{GRY}]{DF}\n')
    else:
        _write(f'\t{GRY}[CR_DB_{_w_con["dbname"]}][{RED}False{GRY}]{DF}\n')

    _write(f'\t{GRY}[CR_USR_{_w_con["user"]}]{DF}')
    if push_msg(f"CREATE USER {_w_con['user']} WITH ENCRYPTED PASSWORD '{_w_con['password']}'", _p_con):
        _write(f'\t{GRY}[CR_DB_{_w_con["dbname"]}][{GRN}True{GRY}]{DF}\n')
    else:
        _write(f'\t{GRY}[CR_DB_{_w_con["dbname"]}][{RED}False{GRY}]{DF}\n')
    
    _write(f'\t{GRY}[GRANT_PRIVILEGES]{DF}')
    if push_msg(f'GRANT ALL PRIVILEGES ON DATABASE {_w_con["dbname"]} TO {_w_con["user"]}', _p_con):
        _write(f'\t{GRY}[GRANT_PRIVILEGES][{GRN}True{GRY}]{DF}\n')
    else:
        _write(f'\t{GRY}[GRANT_PRIVILEGES][{RED}False{GRY}]{DF}\n')

    _write(f'\t{GRY}[GRANT_USAGE]{DF}')
    if push_msg(f'ALTER DATABASE {_w_con["dbname"]} owner TO {_w_con["user"]}', _p_con):
        _write(f'\t{GRY}[GRANT_USAGE][{GRN}True{GRY}]{DF}\n')
    else:
        _write(f'\t{GRY}[GRANT_USAGE][{RED}False{GRY}]{DF}\n')
        
    _write(f'\t{GRY}------------------------------{DF}\n')
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/# 
@exclog.logging(out=_fprint)
def cr_tables(_write : Callable[[str], None], _ctbs : List, _w_con : Dict, **_) -> None:
    _write(f'\n\t{GRY}----------CREATE-TBS----------{DF}')
    for _ctb, _tb in zip(_ctbs.values(), _ctbs.keys()):
        txt = ''; _write(f'\t{GRY}[DB_{_tb}]{DF}')
        for _vtb, _ttb in zip(_ctb.keys(), _ctb.values()):
            if _ttb == 'serial':
                txt = f'{txt}id serial primary key, '
            else:
                txt = f'{txt}{_vtb} {_ttb}, '
        txt = txt[:-2]
        if push_msg(f'CREATE TABLE {_tb} ({txt})', _w_con):
            _write(f'\t{GRY}[DB_{_tb}][{GRN}True{GRY}]{DF}')
        else:
            _write(f'\t{GRY}[DB_{_tb}][{RED}False{GRY}]{DF}')
    
    _write(f'\t{GRY}------------------------------{DF}\n')
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/# 
def __help_msg(_write : Callable[[str], None], **_) -> None:
    _write(f"""\t{GRY}-------------Help-------------
            \r\t-h Get help message 
            \r\t-p Show params                            
            \r\t-d Create database                              
            \r\t-c Create database tables                       
            \r\t-s Get database tables json                     
            \r\t-l Load tables into clear database (json needed)
            \r\t-r Reset params
            \r\t-a Insert element into table
            \r\t-o Show tables elems
            \r\t------------------------------{DF}""")
#\------------------------------------------------------------------/# 


#\------------------------------------------------------------------/# 
def __show_prms(_write : Callable[[str], None], **prms) -> None:
    _write(f'\t{GRY}------------Params------------')
    for key, val in prms.items():
        if isinstance(val, dict):
            _write(f'\t{key} : {"{"}')
            for key, val in val.items():
                _write(f'\t\t{key}: {val}')
            _write(f'\t{"}"}')
        elif isinstance(val, list):
            _write(f'\t{key} : {"["}')
            for data in val:
                _write(f'\t\t{data}')
            _write(f'\t{"]"}')
        else:
            _write(f'\t{key} : {val}')
    _write(f'\t-----------------------------{DF}')
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def __save_txt(txt : str, _fl : str, _m = 'a', _c = 'utf-8') -> int:
    return open(_fl, _m, encoding = _c).write(txt)
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/# 
@exclog.logging(out=_fprint)
def __get_env():
    if os.path.exists('.env'):
        dct = {}; vt = {}
        for ctb in config('MDB_W_CTBS').split('; '):
            for ttb in ctb[ctb.find('(')+1: ctb.rfind(')')].split(', '):
                dct |= (lambda vr, tp, *_: {vr : tp})(*ttb.split())
            vt[ctb[13:ctb.find('(')-1]] = dct; dct = {}
        return {
            '_write'  : eval(config('MDB_W_WRITE')),
            '_p_con'  : {
                'dbname'   : config('MDB_D_DBNAME'), 
                'user'     : config('MDB_D_USER'), 
                'password' : config('MDB_D_PASSWORD'),
                'host'     : config('MDB_D_HOST'),
                'port'     : config('MDB_D_PORT')
            },
            '_w_con' : {
                'dbname'     : config('MDB_W_DBNAME'), 
                'user'    : config('MDB_W_USER'), 
                'password' : config('MDB_W_PASSWORD'),
                'host'     : config('MDB_D_HOST'),
                'port'     : config('MDB_D_PORT')
            },
            '_tbs'    : list(config('MDB_W_TBS').split(', ')),
            '_fl'     : config('MDB_W_FL'),
            '_ctbs'   : vt
        }
    return False
#\------------------------------------------------------------------/# 


#\------------------------------------------------------------------/# 
@exclog.logging(out=_fprint)
def __init_env():
    
    print(f'\t{GRY}------------Params------------\n\t() <- default params\n\t<> <- input example{DF}')
    w_write    = input(f'\t{YLW}Enter function to write logs (print): {DF}')
    d_dbname   = input(f'\t{YLW}Enter default database name (postgres): {DF}')
    d_user     = input(f'\t{YLW}Enter default user (postgres): {DF}')
    d_password = input(f'\t{YLW}Enter default password (postgres): {DF}')
    d_host     = input(f'\t{YLW}Enter default host (localhost): {DF}')
    d_port     = input(f'\t{YLW}Enter default port (5432): {DF}')
    w_dbname   = input(f'\t{YLW}Enter working database name: {DF}')
    w_user     = input(f'\t{YLW}Enter working user: {DF}')
    w_password = input(f'\t{YLW}Enter working password: {DF}')
    w_tbs      = input(f'\t{YLW}Enter working tables <tb1{RED}, {YLW}tb2>: {DF}')
    w_fl       = input(f'\t{YLW}Enter working file (tb.json): {DF}')
    w_ctbs     = input(f'\t{YLW}Enter create tables requests <CREATE TABLE...{RED}; {YLW}CREATE TA...>: {DF}')
    
    __save_txt(
        f'MDB_W_WRITE={"print" if w_write=="" else w_write}\n'
        f'MDB_D_DBNAME={"postgres" if d_dbname=="" else d_dbname}\n'
        f'MDB_D_USER={"postgres" if d_user=="" else d_user}\n'
        f'MDB_D_PASSWORD={"postgres" if d_password=="" else d_password}\n'
        f'MDB_D_HOST={"localhost" if d_host=="" else d_host}\n'
        f'MDB_D_PORT={"5432" if d_port=="" else d_port}\n'
        f'MDB_W_DBNAME={w_dbname}\n'
        f'MDB_W_USER={w_user}\n'
        f'MDB_W_PASSWORD={w_password}\n'
        f'MDB_W_TBS={w_tbs}\n'
        f'MDB_W_FL={"tb.json" if w_fl=="" else w_fl}\n'
        f'MDB_W_CTBS={w_ctbs}\n', '.env'
    )
    print(f'\t{GRY}-----------------------------{DF}')
#\------------------------------------------------------------------/# 


#\------------------------------------------------------------------/# 
@exclog.logging(out=_fprint)
def __console_elem_tb_insert(_write : Callable[[str], None], _ctbs : Dict, _w_con : List, **_) -> None:
    _write(f'\t{GRY}------------Params------------\n\t() <- default params. Enter to full insert.{DF}')
    tbs = input(f'\t{YLW}Enter table(-s) to use ({list(_ctbs.keys())}): {DF}').split(', ')
    for tb in tbs if tbs[0] else _ctbs.keys():
        vals = []
        _write(f'\n\t{GRY}[INSERT_{tb}]{DF}')
        for _vtb, _ttb in zip(_ctbs[tb].keys(), _ctbs[tb].values()):
            if _ttb != 'serial':
                data = input(f'\t{YLW}{_vtb} <{_ttb}> = (null) {DF}')
                vals.append(data if data else 'null')
    
        if insert_db(tb, [it for it in _ctbs[tb].keys() if _ctbs[tb][it] != 'serial'], vals, _w_con):
            _write(f'\t{GRY}[INSERT_{tb}][{GRN}True{GRY}]{DF}')
        else:
            _write(f'\t{GRY}[INSERT_{tb}][{RED}False{GRY}]{DF}')
    _write(f'\t{GRY}-----------------------------{DF}')
#\------------------------------------------------------------------/# 


#\------------------------------------------------------------------/# 
@exclog.logging(out=_fprint)
def __show_tb_elems(_write : Callable[[str], None], _ctbs : Dict, _w_con : Dict, **_) -> None:
    _write(f'\t{GRY}------------Params------------\n\t() <- default params. Enter to show all.{DF}')
    tbs = input(f'\t{YLW}Enter table(-s) to use ({list(_ctbs.keys())}): {DF}').split(', ')
    for tb in tbs if tbs[0] else _ctbs.keys():
        _write(f'\n\t{GRY}[SHOW_{YLW}{tb}{GRY}]{DF}')
        data = get_db(tb, _w_con, f'{DBRESP} {tb}')
        if data:
            _write(f'\t{GRY}│\n\t└[GOT_{YLW}{data[1][0][0]}{GRY}_ELEMS_FROM_{YLW}{tb}{GRY}]{DF}')

            max_len = 0
            for val in _ctbs[tb].keys():
                if len(str(val)) > max_len:
                    max_len = len(str(val))
            for it in data[0]:
                for el in it:
                    if len(str(el)) > max_len:
                        max_len = len(str(el))

            txt = ''
            for val in _ctbs[tb].keys():
                txt = f'{txt}{GRY}─|{YLW}{val}{" "*(max_len-len(str(val)))}{GRY}|{DF}'
            _write(f'\t{GRY} │\n\t ├{YLW}{txt}{DF}')
            for it in data[0]:
                txt = ''
                for el in it:
                    txt = f'{txt}{GRY}─|{YLW}{el}{" "*(max_len-len(str(el)))}{GRY}|{DF}'
                _write(f'\t{GRY} │\n\t ├{YLW}{txt}{DF}')

            _write(f'\t{GRY} │\n\t └[SHOW_{tb}][{GRN}True{GRY}]{DF}')
        else:
            _write(f'\t{GRY}[SHOW_{tb}][{RED}False{GRY}]{DF}')
    _write(f'\t{GRY}-----------------------------{DF}')
#\------------------------------------------------------------------/# 


#\------------------------------------------------------------------/# 
@exclog.logging(out=_fprint)
def __reset_env() -> Dict:
    if os.path.exists('.env'):
        os.remove('.env')
    __init_env()
    return __get_env()
#\------------------------------------------------------------------/# 


#\------------------------------------------------------------------/# 
@exclog.logging(out=_fprint)
def get_env():
    return __get_env()
#\------------------------------------------------------------------/# 
    

#\==================================================================/#
if __name__ == "__main__":

    print(f"""
        \r\t{GRY}╭╮╭╮╭╮╭╮{YLW}     {GRY}┬╖┬╖
        \r\t{GRY}|╯│ │││ {YLW}ʕᵔᴥᵔʔ{GRY}│║│╣
        \r\t{GRY}╰ ╯ ╰╯╰╯{YLW}     {GRY}┴╜┴╜
        \r\t{GRY}by Mtvy©{DF}
    """)
    
    DB_CNTRL = {
        '-s' : __dump_tables,
        '-l' : __load_tables,
        '-d' : __cr_database,
        '-c' : cr_tables,
        '-h' : __help_msg,
        '-p' : __show_prms,
        '-a' : __console_elem_tb_insert,
        '-o' : __show_tb_elems
    }

    _args = __get_env()
    if not _args:
        __init_env(); _args = __get_env()

    for _dvar in sys.argv: 
        if _dvar in DB_CNTRL: 
            DB_CNTRL[_dvar](**_args)
        elif _dvar == '-r':
            _args = __reset_env()
#\==================================================================/#