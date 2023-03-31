from concurrent.futures import thread
import datetime
import requests
import base64
import threading
import argparse


def date_list(start_date_delta: int = 1, end_date_delta: int = -10, step: int = -1) -> list[(str, str, str)]:
	"""
	获取从 start_date_delta 天到 end_date_delta 天的日期列表
	:param start_date_delta: 开始日期距今天的天数
	:param end_date_delta: 结束日期距今天的天数
	:param step: 步长
	:return: 日期列表，格式为 (年, 月, 日)
	"""
	dates = [datetime.datetime.now() + datetime.timedelta(days=i) for i in range(start_date_delta, end_date_delta, step)]
	return [(f"{d.year}", f"{d.month:02d}", f"{d.day:02d}") for d in dates]


all_urls = [
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

vmess_urls: list[str] = []
threadLock = threading.Lock()


def get_from_urls(url_list):
	"""
	从给定的一组 url 中获取首个有效的 url，并将订阅内容添加到 vmess_urls 中
	"""
	for url in url_list:
		try:
			result = requests.get(url)
			if result.ok:
				print(result.url)
				# print(result.content)
				server_list = base64.b64decode(result.content).decode("utf-8")
				threadLock.acquire()
				for server in server_list.splitlines():
					if vmess_urls.count(server) == 0:
						vmess_urls.append(server)
				threadLock.release()
				return
		except Exception as e:
			print(f"从 {url} 获取订阅内容失败: {e}")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="获取V2Ray节点")
	parser.add_argument("-i", "--input", help="输入文件名", default="")
	parser.add_argument("-o", "--output", help="输出文件名", default="v2ray.txt")
	args = parser.parse_args()
	if len(args.input) > 0:
		try:
			with open(args.input, "r", encoding="utf-8") as f:
				vmess_urls = base64.b64decode(f.read()).decode("utf-8").splitlines()
		except Exception:
			vmess_urls = []

	threads: list[threading.Thread] = []

	# 为每一组 url 创建一个线程
	for url_list in all_urls:
		t = threading.Thread(target=get_from_urls, args=(url_list,))
		threads.append(t)
		t.start()

	# 等待所有线程完成
	for t in threads:
		t.join()

	# print(vmess_urls)

	with open(args.output, "w", encoding="utf-8") as f:
		f.write(base64.b64encode("\n".join(vmess_urls).encode("utf-8")).decode("utf-8"))
