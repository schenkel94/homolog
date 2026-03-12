from discovery.discover_greenhouse import discover_companies

companies = discover_companies()

print("empresas encontradas:", len(companies))
print(companies[:20])