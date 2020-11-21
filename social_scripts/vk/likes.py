import pkgutil

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
    return execute_vkscripts(vkapi, vk_scripts, v=v, desc_tqdm='likes')
