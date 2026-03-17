import re
html = open('gupy_html.html', encoding='utf-8').read()
for match in set(re.findall(r'https://[^/]+\.gupy\.io/api/[^\"\'\\]]*', html)):
    print(match)
