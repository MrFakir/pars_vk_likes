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
    'get_last_post': ['vk.last_vk_post', 'call_get_last_post'],
    'parser_from_vk': ['com.auto_publish.parser_from_vk_to', 'call_parser_from_vk']
}

API_V_VK = '5.131'
API_V_INST = 'v13.0'

PLACE_HOLDER = 'https://scontent-otp1-1.cdninstagram.com/v/t51.2885-15/16790' \
             '232_632277373619133_4104592780410486784_n.jpg?stp=dst-jpg_e35&_' \
             'nc_ht=scontent-otp1-1.cdninstagram.com&_nc_cat=109&_nc_ohc=WOawnxo7' \
             'JxUAX-qx_aC&edm=ALQROFkBAAAA&ccb=7-4&ig_cache_key=MTQ1ODUzMjc4NTI5ODg4N' \
             'zI5NQ%3D%3D.2-ccb7-4&oh=00_AT_nLMLMTam1GovY7nss36Njbu2IKkEq5fA11eoXGvNR_g&o' \
             'e=6277732D&_nc_sid=30a2ef'

