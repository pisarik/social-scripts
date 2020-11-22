import pkgutil
from itertools import chain
from datetime import datetime

import numpy as np

from .core import execute_vkscripts
from . import constants


def get_batch_requests_for_posts(owner_id, n_posts, start_offset=0,
                                 post_filter='owner', v=5.95):
    """
    Return list of code that need to be run by vk.execute

    :param v: version
    :param post_filter: owner, others or all
    :param start_offset: from which start to download
    :param owner_id:
    :param n_posts: number of posts to be downloaded
    :return: list of codes to execute in VK
    """
    code_template = pkgutil.get_data(
        'social_scripts.vk',
        'vkscripts/get_posts_from_group_template.vkscript').decode('utf-8')

    offset = start_offset
    last_post = start_offset + n_posts  # end not included [offset, last_post)

    codes = []
    count = constants.MAX_GET_POSTS_COUNT
    max_requests = constants.EXECUTE_MAX_REQUESTS
    # accumulate batches
    while offset < last_post:
        # accumulate offsets for one batch
        offsets = np.linspace(offset, offset + max_requests * count,
                              max_requests, endpoint=False, dtype=int)
        offsets = offsets[offsets < last_post]

        code = code_template.format(owner_id=owner_id, offsets=list(offsets),
                                    count=count, filter=post_filter, version=v)
        codes.append(code)

        offset = offsets[-1] + count

    return codes


def get_posts(vkapi, owner_id, n_posts=None, start_offset=0,
              after: datetime = None, v=5.95):
    if n_posts is None:
        n_posts = vkapi.wall.get(
            owner_id=owner_id, offset=0, count=1, v=v)['count']
    assert n_posts >= 0, 'n_count must be >= 0'

    vk_scripts = get_batch_requests_for_posts(
        owner_id, n_posts, start_offset=start_offset)

    if after is not None:
        def break_condition(result):
            old_length = len(result['items'])
            result['items'] = [item for item in result['items']
                               if datetime.fromtimestamp(item['date']) > after]
            return old_length != len(result['items'])
    else:
        break_condition = None

    results = execute_vkscripts(vkapi, vk_scripts, v=v, desc_tqdm='posts',
                                break_condition=break_condition)
    all_posts = list(chain.from_iterable([r['items'] for r in results]))

    return all_posts[:n_posts]
