from collections import defaultdict
import pandas as pd
import calendar
import helper

db = helper.get_mongodb()
data = pd.DataFrame(pd.read_json('data.json')['query_result']['data']['rows'])
print(data.describe())
print(data.head(10))


providers_pv = defaultdict(int)


for index, row in data.iterrows():
    name = row['e_page']
    providers = db.books.find({'name': name}, {'provider': 1})
    for item in providers:
        provider = item['provider']
        providers_pv[provider] += row['pv']
print(providers_pv)

print(calendar.monthrange(2018, 1)[1])
