from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_JSON_DIR = Path(BASE_DIR, '../json_data')
TEMP_USERS_DATA = Path(BASE_DIR, '../temp_users_data')

API_LIST = {
    'check_auth_data': ['vk.vk_parser', 'call_check_auth_data'],
    'get_vk_post': ['vk.vk_parser', 'call_get_vk_post'],
    'call_get_vk_likes': ['vk.vk_parser', 'call_get_vk_likes'],
    'get_last_post': ['vk.last_vk_post', 'call_get_last_post']
}


