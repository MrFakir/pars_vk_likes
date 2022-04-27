from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_JSON_DIR = Path(BASE_DIR, 'json_data')
TEMP_USERS_DATA = Path(BASE_DIR, 'temp_users_data')

API_LIST = {
    'check_auth_data': ['vk_parser', 'call_check_auth_data'],
    'get_vk_post': ['vk_parser', 'call_get_vk_post'],
    'call_get_vk_likes': ['vk_parser', 'call_get_vk_likes'],
}
