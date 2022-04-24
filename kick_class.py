from data.auth_data.auth_vk import access_token1, access_token2


def kick_class(dir_from_json):
    call_name = getattr(__import__(dir_from_json['module']), dir_from_json['call'])
    del dir_from_json['module']
    del dir_from_json['call']
    return call_name(**dir_from_json)


# json_dir = {
#     'module': 'vk_parser',
#     'call': 'call_get_vk_post',
#     'auth_data': [access_token1, access_token2],
#     'group_id': '-159519198',
#     'limit': '2',
# }
# json_dir = {
#     'module': 'vk_parser',
#     'call': 'call_check_auth_data',
#     'auth_data': [access_token1, access_token2],
# }

json_dir = {
    'module': 'vk_parser',
    'call': 'call_get_vk_likes',
    'auth_data': [access_token1, access_token2],
    'group_id': '-159519198',
    'limit': '2',
}

json_response = kick_class(dir_from_json=json_dir)
print(json_response)
