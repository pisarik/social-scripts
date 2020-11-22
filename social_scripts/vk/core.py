from typing import Callable
from time import sleep

import vk
from tqdm import tqdm

from . import constants


def execute_vkscripts(
        vkapi: vk.API, vk_scripts, sleep_time=constants.SLEEP_TIME, v=5.95,
        desc_tqdm=None, break_condition: Callable[[list], bool] = None):
    """

    :param vkapi:
    :param vk_scripts:
    :param sleep_time:
    :param v:
    :param desc_tqdm:
    :param break_condition: retrieves results while condition is true
    :return:
    """
    results = []
    for code in tqdm(vk_scripts, desc=desc_tqdm):
        batch_results = vkapi.execute(code=code, v=v)

        if break_condition:
            cond = True
            for res in batch_results:
                cond = break_condition(res)
                if cond:
                    results.append(res)
            if not cond:
                break
        else:
            results.extend(results)
        sleep(sleep_time)

    return results
