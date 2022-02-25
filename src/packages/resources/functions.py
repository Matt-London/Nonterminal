from . import variables as var
from os import system, name

# Clears screen
# CREDIT: https://www.geeksforgeeks.org/clear-screen-python/
# By: mohit_negi
def clear():
    """
    Clears the screen

    :return: None
    """
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear') 