import requests

postHeaders = {
    'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
    'Origin': 'https://freepanel.ts3.cloud',
    'Referer': 'https://freepanel.ts3.cloud/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
}
urlLogin = "https://freepanel.ts3.cloud/login.php"
urlPanel = "https://freepanel.ts3.cloud"

data = {"email": "FreeUser_7185342690", "password": "GY0BJ6Eup8gTXsZn"}
serverName = {"serverName": "Carogna Virus"}

session = requests.Session()
test1 = session.post(urlLogin, headers=postHeaders, data=data)
test2 = session.post(urlPanel, headers=postHeaders, data=serverName)
print(test1.text)
print(test2.text)