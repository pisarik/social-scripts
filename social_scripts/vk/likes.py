import pkgutil
import math
from itertools import chain

from .core import execute_vkscripts
from . import constants


def get_batch_requests_for_is_liked(user_id, owner_id, posts, v=5.95):
    """
    Return list of code that need to be run by vk.execute

    :param user_id:
    :param owner_id:
    :param posts: list of posts with fields id and post_type
    :param v: version
    :return: list of codes to execute in VK
    """
    code_template = pkgutil.get_data(
        'social_scripts.vk',
        'vkscripts/is_liked_by_user_template.vkscript').decode('utf-8')

    codes = []
    max_requests = constants.EXECUTE_MAX_REQUESTS

    # accumulate batches
    for i in range(0, len(posts), max_requests):
        batch = posts[i:i + max_requests]
        item_ids = [post['id'] for post in batch]
        post_types = [post['post_type'] for post in batch]

        code = code_template.format(user_id=user_id, owner_id=owner_id,
                                    item_ids=item_ids, post_types=post_types,
                                    version=v)
        codes.append(code)

    return codes


def get_is_liked(vkapi, user_id, owner_id, posts, v=5.95):
    vk_scripts = get_batch_requests_for_is_liked(user_id, owner_id, posts)
    results = execute_vkscripts(vkapi, vk_scripts, v=v, desc_tqdm='likes')
    likers = [r['items']]
    return


def get_batch_requests_for_get_likers(posts: list, v=5.95) -> list:
    """
    Return list of code that need to be run by vk.execute

    :param posts: list of posts with fields id and post_type
    :param v: version
    :return: list of codes to execute in VK
    """
    code_template = pkgutil.get_data(
        'social_scripts.vk', 'vkscripts/get_likers.vkscript').decode('utf-8')

    codes = []
    count = constants.MAX_GET_LIKES_COUNT

    offsets = []
    post_types = []
    owner_ids = []
    item_ids = []

    for post in posts:
        n_likes = post['likes']['count']
        n_calls = math.ceil(n_likes / count)

        offsets += list(range(0, n_likes, count))
        post_types += [post['post_type']] * n_calls
        item_ids += [post['id']] * n_calls
        owner_ids += [post['owner_id']] * n_calls

    max_requests = constants.EXECUTE_MAX_REQUESTS
    codes = [
        code_template.format(
            owner_ids=owner_ids[i: i + max_requests],
            item_ids=item_ids[i: i + max_requests],
            post_types=post_types[i: i + max_requests],
            offsets=offsets[i: i + max_requests],
            count=count,
            version=v)
        for i in range(0, len(offsets), max_requests)
    ]

    return codes


def get_posts_likers(vkapi, posts: list, v=5.95):
    vk_scripts = get_batch_requests_for_get_likers(posts)
    results = execute_vkscripts(vkapi, vk_scripts, desc_tqdm='likers')
    likers = list(chain.from_iterable([r['items'] for r in results]))
    return likers
