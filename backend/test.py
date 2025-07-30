import urllib.request
import urllib.parse
import dotenv
import os
dotenv.load_dotenv()
client_id = os.getenv('NAVER_CLIENT_ID')
client_secret = os.getenv('NAVER_CLIENT_SECRET')
query = urllib.parse.quote("생일 선물")
url = f"https://openapi.naver.com/v1/search/shop?query={query}&display=10"

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)
response = urllib.request.urlopen(request)
print(response.read().decode('utf-8'))
