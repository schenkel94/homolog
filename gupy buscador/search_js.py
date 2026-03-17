import re, requests
html = open('gupy_html.html', encoding='utf-8').read()
scripts = re.findall(r'src="(/_next/static/[^"\'\\]+\.js)"', html)
urls = set()
for s in scripts:
    try:
        text = requests.get('https://portal.gupy.io' + s).text
        # look for typical api endpoints or 'gupy.io'
        matches = re.findall(r'https://[^/]+\.gupy\.io[/a-zA-Z0-9_.-]*', text)
        urls.update(matches)
    except Exception as e: print(e)
print('\n'.join(urls)[:2000])
