from time import sleep

import vk
from tqdm import tqdm

from . import constants


def execute_vkscripts(
        vkapi: vk.API, vk_scripts, sleep_time=constants.SLEEP_TIME, v=5.95,
        desc_tqdm=None):
    results = []
    for code in tqdm(vk_scripts, desc=desc_tqdm):
        results.extend(vkapi.execute(code=code, v=v))
        sleep(sleep_time)

    return results
