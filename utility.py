#/==================================================================\#
# utility.py                                          (c) Mtvy, 2022 #
#\==================================================================/#
#                                                                    #
# Copyright (c) 2022. Mtvy (Matvei Prudnikov, m.d.prudnik@gmail.com) #
#                                                                    #
#\==================================================================/#

#/-----------------------------/ Libs \-----------------------------\#
from io            import open                as file_open
from os            import remove              as rmv
from os            import listdir             as get_files
from os.path       import exists              as isExist
from telebot.types import ReplyKeyboardMarkup as crMrkup
from telebot.types import KeyboardButton      as crBtn
from telebot       import TeleBot
from typing        import Any, Callable, List, Literal
from traceback     import format_exc as _exc
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def saveText(txt : str, _fl : str, _m = 'a', _c = 'utf-8') -> int:
    return open(_fl, _m, encoding = _c).write(txt)
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def logging(__write : Callable[[str], None]=print, __rtrn=False):
    """ Logging decorator with args. """
    RD="\033[1;35m"; GRY="\033[1;37m"; DF="\033[0m"
    def _logging(func : Callable) -> Any | Literal[False]:
        
        def wrap_func(*args, **kwargs) -> Any | Literal[False]:
            try:
                return func(*args, **kwargs)
            except:
                tr = _exc().split('\n')
                exc = f'{GRY}\t│\n\t└{RD}Erorr at: [{func.__name__}]{GRY}\n\t │\n\t └{RD}{tr[0]}'
                for line in tr[1:]:
                    exc = f'{exc}\n\t  {line}'
                __write(f"{exc}{DF}")
                
            return __rtrn

        return wrap_func
        
    return _logging
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def makeKey(btns : List):
    keyboard = crMrkup(resize_keyboard=True)
    
    keyboard.add(*[crBtn(btn) for btn in btns])
    
    return keyboard
#\------------------------------------------------------------------/#

#\------------------------------------------------------------------/#
def rmvFile(pth : str) -> bool:
    if isExist(pth):
        rmv(pth)
        return True
    return False
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def showFile(bot : TeleBot, 
             _id : int | str, 
             _fl : str, 
             cap : str, 
             txt : str) -> None:
    if isExist(_fl):
        bot.send_document(_id, open(_fl, 'rb'), caption=cap)
    else:
        bot.send_message(_id, txt)
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def delFile(bot   : TeleBot, 
            _id   : int | str,
            _fl   : str, 
            txt_t : str,
            txt_f : str) -> None:
    if rmvFile(_fl):
        bot.send_message(_id, txt_t)
    else:
        bot.send_message(_id, txt_f)
#\------------------------------------------------------------------/#
    

#\------------------------------------------------------------------/#
def openfileforRead(file = None, text = '') -> str:
    return text.join([i for i in file_open(file, encoding='utf-8')])
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def getData(_fl : str, splt : str) -> List[str | None]:
    if isExist(_fl):
        return list(openfileforRead(_fl).split(splt))
    else:
        return []
#\------------------------------------------------------------------/#


#\------------------------------------------------------------------/#
def getName(_post : str) -> str | Literal[False]:
    for file in get_files():
        if _post in file:
            return file
    return False
#\------------------------------------------------------------------/#
