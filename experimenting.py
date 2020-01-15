url = f'https://meduza.io/api/w5/search?term=искусственный интеллект&page=1&per_page=100&locale=ru'
request = requests.get(url)
request_js = json.loads(request.content)
request_js['has_next']
request_js['collection']