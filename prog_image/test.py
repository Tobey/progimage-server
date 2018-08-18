
from concurrent.futures import ThreadPoolExecutor

import time

c = [1,2,3,4,5]


def add_one(x):
    time.sleep(5)
    return x + 1
if __name__ == '__main__':


    with ThreadPoolExecutor(max_workers=10) as executor:
        future_list= [executor.submit(add_one, x).result()  for x in c]


    f = 1