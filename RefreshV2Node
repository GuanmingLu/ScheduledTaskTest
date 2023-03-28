import datetime
import requests

list = [
    "https://clashnode.com/wp-content/uploads/{y}/{m}/{y}{m}{d}.txt",
    "https://v2rayshare.com/wp-content/uploads/{y}/{m}/{y}{m}{d}.txt",
    "https://freenode.me/wp-content/uploads/{y}/{m}/{d}{n}.txt",
]


def access_url(url: str, date: datetime.datetime) -> str:
	year = str(date.year)
	month = str(date.month).zfill(2)
	day = str(date.day).zfill(2)
	if url.find("{n}") != -1:
		for i in range(9, -1, -1):
			formatted_url = url.format(y=year, m=month, d=day, n=str(i))
			result = requests.get(url=formatted_url)
			if result.ok:
				return formatted_url
	else:
		formatted_url = url.format(y=year, m=month, d=day)
		result = requests.get(url=formatted_url)
		if result.ok:
			return formatted_url
	return ""


for url in list:
	for delta_day in range(1, -10, -1):
		date = datetime.datetime.now() + datetime.timedelta(days=delta_day)
		formatted_url = access_url(url, date)
		if formatted_url != "":
			print(formatted_url)
			break
