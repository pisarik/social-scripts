import vk
import numpy as np
from time import sleep
from itertools import chain
from tqdm import tqdm

from utilities import trim_newline
from vk_scripts import vk_constants


def find_posts_liked_by_user(vkapi, user_id, posts_owner_id, n_posts=None,
                             posts_offset=0,
                             v=5.95):
    posts = get_posts(vkapi, posts_owner_id, n_posts, posts_offset, v=v)

    # filter posts
    for i, post in enumerate(posts):
        posts[i] = {key: post[key] for key in ['id', 'text', 'post_type']}

    likes = get_is_liked(vkapi, user_id, posts_owner_id, posts)

    return [post for like, post in zip(likes, posts) if like['liked']]


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

    with open('./get_posts_from_group_template.vkscript') as f:
        code_template = f.read()

    offset = start_offset
    last_post = start_offset + n_posts  # end not included [offset, last_post)

    codes = []
    count = vk_constants.MAX_GET_POSTS_COUNT
    max_requests = vk_constants.EXECUTE_MAX_REQUESTS
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


def get_batch_requests_for_is_liked(user_id, owner_id, posts, v=5.95):
    """
    Return list of code that need to be run by vk.execute

    :param user_id:
    :param owner_id:
    :param posts: list of posts with fields id and post_type
    :param v: version
    :return: list of codes to execute in VK
    """

    with open('./is_liked_by_user_template.vkscript') as f:
        code_template = f.read()

    codes = []
    max_requests = vk_constants.EXECUTE_MAX_REQUESTS

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


def execute_vk_scripts(vkapi, vk_scripts,
                       sleep_time=vk_constants.SLEEP_TIME, v=5.95,
                       desc_tqdm=None):
    results = []
    for code in tqdm(vk_scripts, desc=desc_tqdm):
        results.extend(vkapi.execute(code=code, v=v))
        sleep(sleep_time)

    return results


def get_posts(vkapi, owner_id, n_count=None, start_offset=0, v=5.95):
    if n_count is None:
        n_count = vkapi.wall.get(owner_id=owner_id, offset=0,
                                 count=1, v=v)['count']
    assert n_count >= 0, 'n_count must be >= 0'

    vk_scripts = get_batch_requests_for_posts(owner_id, n_count,
                                              start_offset=start_offset)

    all_posts = list(chain.from_iterable(
        [res['items'] for res in execute_vk_scripts(vkapi, vk_scripts,
                                                    v=v, desc_tqdm='posts')]
    ))

    return all_posts[:n_count]


def get_is_liked(vkapi, user_id, owner_id, posts, v=5.95):
    vk_scripts = get_batch_requests_for_is_liked(user_id, owner_id, posts)
    return execute_vk_scripts(vkapi, vk_scripts, v=v, desc_tqdm='likes')


if __name__ == '__main__':
    with open('../token') as f:
        access_token = trim_newline(f.read())
    session = vk.Session(access_token)
    vkapi = vk.API(session)

    liked_posts = find_posts_liked_by_user(vkapi,
                                           user_id=1,
                                           posts_owner_id=-11982368,
                                           n_posts=200,
                                           )
    print(liked_posts)
