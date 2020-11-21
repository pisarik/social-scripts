import vk
from social_scripts.vk.posts import get_posts
from social_scripts.vk.likes import get_is_liked


def find_posts_liked_by_user(
        vkapi, user_id, posts_owner_id, n_posts=None, posts_offset=0, v=5.95):
    posts = get_posts(vkapi, posts_owner_id, n_posts, posts_offset, v=v)

    # filter posts
    for i, post in enumerate(posts):
        posts[i] = {key: post[key] for key in ['id', 'text', 'post_type']}

    likes = get_is_liked(vkapi, user_id, posts_owner_id, posts)

    return [post for like, post in zip(likes, posts) if like['liked']]


if __name__ == '__main__':
    with open('token') as f:
        access_token = f.read().rstrip()
    session = vk.Session(access_token)
    vkapi = vk.API(session)

    liked_posts = find_posts_liked_by_user(
        vkapi, user_id=1, posts_owner_id=-11982368, n_posts=200)
    print(liked_posts)
