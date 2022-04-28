from vk.vk_parser import VkTokens, GetVkPosts, GetVkLikes
from data.auth_data.auth_vk import access_token1, access_token2


def main():
    auth_tokens = VkTokens(access_token1, access_token2)
    get_group = GetVkPosts(group_id='-170301568', auth_data=auth_tokens)
    get_group.get_post_id()
    get_like = GetVkLikes(auth_data=auth_tokens, group_data=get_group)
    get_like.get_likes_from_group()


if __name__ == '__main__':
    main()
