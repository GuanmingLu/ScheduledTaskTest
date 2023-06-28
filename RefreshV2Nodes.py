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

vmess_urls: set[str] = set()
ss_servers: set[str] = set()
threadLock = threading.Lock()


def is_node_valid(item: str) -> bool:
	if item in vmess_urls:
		return False
	if item.find("v2ray-plugin") >= 0:
		return False
	if item.startswith("ss://"):
		start = item.find("@") + 1
		end = item.find("#")
		if start <= 0 or end <= 0 or start >= end:
			return False
		server = item[start:end]
		if server.find("127.0.0.1") >= 0 or server.find("localhost") >= 0 or server in ss_servers:
			return False
		ss_servers.add(server)
	return True


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
				node_list = base64.b64decode(result.content).decode("utf-8")
				threadLock.acquire()
				for node in node_list.splitlines():
					if is_node_valid(node):
						vmess_urls.add(node)
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
				vmess_urls = set(base64.b64decode(f.read()).decode("utf-8").splitlines())
		except Exception:
			vmess_urls = set()

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
