import datetime
import requests
import base64


def date_list(start_date_delta: int = 1, end_date_delta: int = -10, step: int = -1) -> list[(str, str, str)]:
	dates = [datetime.datetime.now() + datetime.timedelta(days=i) for i in range(start_date_delta, end_date_delta, step)]
	return [(f"{d.year}", f"{d.month:02d}", f"{d.day:02d}") for d in dates]


urls = [
    [f"https://clashfree.eu.org/wp-content/uploads/rss/{y}{m}{d}.txt" for (y, m, d) in date_list()],
    [f"https://oneclash.cc/wp-content/uploads/{y}/{m}/{y}{m}{d}.txt" for (y, m, d) in date_list()],
    [f"https://clashnode.com/wp-content/uploads/{y}/{m}/{y}{m}{d}.txt" for (y, m, d) in date_list()],
    [f"https://v2rayshare.com/wp-content/uploads/{y}/{m}/{y}{m}{d}.txt" for (y, m, d) in date_list()],
    [f"https://freenode.me/wp-content/uploads/{y}/{m}/{d}{n}.txt" for (y, m, d) in date_list() for n in range(9, -1, -1)] +
    [f"https://freenode.me/wp-content/uploads/{y}/{m}/{m}{d}{n}.txt" for (y, m, d) in date_list() for n in range(9, -1, -1)],
    ["https://jiang.netlify.com/"],
    ["https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2"],
]

# print(urls)
# exit(0)

datas = []
for url_list in urls:
	for url in url_list:
		result = requests.get(url)
		if result.ok:
			print(result.url)
			# print(result.content)
			server_list = base64.b64decode(result.content).decode("utf-8")
			for server in server_list.split("\n"):
				if datas.count(server) == 0:
					datas.append(server)
			break

# print(datas)

with open("v2ray.txt", "w") as f:
	f.write(base64.b64encode("\n".join(datas).encode("utf-8")).decode("utf-8"))
