import datetime
import requests
import base64


def date_list(start_date_delta: int = 1, end_date_delta: int = -10, step: int = -1) -> list[datetime.datetime]:
	return [datetime.datetime.now() + datetime.timedelta(days=i) for i in range(start_date_delta, end_date_delta, step)]


urls = [
    [f"https://clashnode.com/wp-content/uploads/{date.year}/{date.month:02d}/{date.year}{date.month:02d}{date.day:02d}.txt" for date in date_list()],
    [f"https://v2rayshare.com/wp-content/uploads/{date.year}/{date.month:02d}/{date.year}{date.month:02d}{date.day:02d}.txt" for date in date_list()],
    [f"https://freenode.me/wp-content/uploads/{date.year}/{date.month:02d}/{date.day:02d}{num}.txt" for date in date_list() for num in range(9, -1, -1)] + [
        f"https://freenode.me/wp-content/uploads/{date.year}/{date.month:02d}/{date.month:02d}{date.day:02d}{num}.txt" for date in date_list()
        for num in range(9, -1, -1)
    ],
    ["https://jiang.netlify.com/"],
]

# print(urls)
# exit(0)

datas = ""
for url_list in urls:
	for url in url_list:
		result = requests.get(url)
		if result.ok:
			print(result.url)
			# print(result.content)
			server_list = base64.b64decode(result.content).decode("utf-8")
			if not server_list.endswith("\n"):
				server_list += "\n"
			datas += server_list
			break

# print(datas)

with open("v2ray.txt", "w") as f:
	f.write(base64.b64encode(datas.encode("utf-8")).decode("utf-8"))
