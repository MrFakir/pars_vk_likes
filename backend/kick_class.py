import importlib
from data.auth_data.auth_vk import access_token1, access_token2
from backend.settings import API_LIST


def kick_class(dir_from_json):
    if dir_from_json['call'] in API_LIST:
        dir_from_json['call'] = API_LIST[dir_from_json['call']]
    call_name = getattr(importlib.import_module(dir_from_json['call'][0]), dir_from_json['call'][1])
    del dir_from_json['call']
    return call_name(**dir_from_json)


#  тестовые данные

# json_dir = {
#     'call': 'get_vk_post',
#     'auth_data': [access_token1, access_token2],
#     'group_id': '-159519198',
#     'limit': '2',
# }

json_dir = {
    'call': 'get_last_post',
    'auth_data': [access_token1, access_token2],
    'group_id': '-159519198',
}

# json_dir = {
#     'call': 'check_auth_data',
#     'auth_data': [access_token1, access_token2],
# }


# json_dir = {
#     'call': 'get_vk_likes',
#     'auth_data': [access_token1, access_token2],
#     'group_id': '-159519198',
#     'limit': '2',
# }
json_response = kick_class(dir_from_json=json_dir)
print(json_response)
