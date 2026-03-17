import json
from bs4 import BeautifulSoup
html = open('gupy_html.html', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__')
if script:
    data = json.loads(script.string)
    open('next_data.json', 'w', encoding='utf-8').write(json.dumps(data, indent=2))
else:
    print('No NEXT DATA found')
