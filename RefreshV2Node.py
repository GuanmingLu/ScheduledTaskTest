import datetime
import requests
import base64

list = [
    "https://clashnode.com/wp-content/uploads/{y}/{m}/{y}{m}{d}.txt",
    "https://v2rayshare.com/wp-content/uploads/{y}/{m}/{y}{m}{d}.txt",
    "https://freenode.me/wp-content/uploads/{y}/{m}/{d}{n}.txt",
]


def access_url(url: str, date: datetime.datetime) -> requests.Response:
	year = str(date.year)
	month = str(date.month).zfill(2)
	day = str(date.day).zfill(2)
	if url.find("{n}") != -1:
		for i in range(9, -1, -1):
			formatted_url = url.format(y=year, m=month, d=day, n=str(i))
			result = requests.get(url=formatted_url)
			if result.ok:
				return result
	else:
		formatted_url = url.format(y=year, m=month, d=day)
		result = requests.get(url=formatted_url)
		if result.ok:
			return result
	return None

datas = ""
for url in list:
	for delta_day in range(1, -10, -1):
		date = datetime.datetime.now() + datetime.timedelta(days=delta_day)
		result = access_url(url, date)
		if result is not None:
			print(result.url)
			# print(result.content)
			datas += base64.b64decode(result.content).decode("utf-8")
			if not datas.endswith("\n"):
				datas += "\n"
			break

# print(datas)

with open("v2ray.txt", "w") as f:
	f.write(datas)
