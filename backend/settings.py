from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_JSON_DIR = Path(BASE_DIR, '../json_data')
TEMP_USERS_DATA = Path(BASE_DIR, 'temp_users_data')

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,'
              'image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
}

API_LIST = {
    'check_auth_data': ['vk.vk_parser', 'call_check_auth_data'],
    'get_vk_post': ['vk.vk_parser', 'call_get_vk_post'],
    'call_get_vk_likes': ['vk.vk_parser', 'call_get_vk_likes'],
    'get_last_post': ['vk.last_vk_post', 'call_get_last_post']
}

API_V_VK = '5.131'
API_V_INST = 'v13.0'

