import datetime
import requests
import base64
import threading
import argparse
import json
import re


def date_list(start_date_delta: int = 1, end_date_delta: int = -10, step: int = -1) -> list[tuple[str, str, str]]:
	"""
	获取从 start_date_delta 天到 end_date_delta 天的日期列表
	:param start_date_delta: 开始日期距今天的天数
	:param end_date_delta: 结束日期距今天的天数
	:param step: 步长
	:return: 日期列表，格式为 (年, 月, 日)
	"""
	dates = [datetime.datetime.now() + datetime.timedelta(days=i) for i in range(start_date_delta, end_date_delta, step)]
	return [(f"{d.year}", f"{d.month:02d}", f"{d.day:02d}") for d in dates]


ALL_URLS = [
    [f"https://clashfree.eu.org/wp-content/uploads/rss/{y}{m}{d}.txt" for (y, m, d) in date_list()],
    [f"https://oneclash.cc/wp-content/uploads/{y}/{m}/{y}{m}{d}.txt" for (y, m, d) in date_list()],
    [f"https://clashnode.com/wp-content/uploads/{y}/{m}/{y}{m}{d}.txt" for (y, m, d) in date_list()],
    [f"https://v2rayshare.com/wp-content/uploads/{y}/{m}/{y}{m}{d}.txt" for (y, m, d) in date_list()],
    [f"https://freenode.me/wp-content/uploads/{y}/{m}/{d}{n}.txt" for (y, m, d) in date_list() for n in range(9, -1, -1)] + [f"https://freenode.me/wp-content/uploads/{y}/{m}/{m}{d}{n}.txt" for (y, m, d) in date_list() for n in range(9, -1, -1)],
    ["https://jiang.netlify.com/"],
    ["https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2"],
    ["https://raw.githubusercontent.com/vpei/Free-Node-Merge/main/o/node.txt"],
    ["https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray"],
    ["https://raw.githubusercontent.com/peasoft/NoMoreWalls/master/list_raw.txt"],
    ["https://raw.githubusercontent.com/ermaozi/get_subscribe/main/subscribe/v2ray.txt"],
    ["https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/splitted/trojan.txt"],
    ["https://raw.githubusercontent.com/Bardiafa/Free-V2ray-Config/main/All_Configs_Sub.txt"],
    ["https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription1"],
    ["https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription2"],
    ["https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription3"],
    ["https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription4"],
    ["https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription5"],
    ["https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription6"],
    ["https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription7"],
    ["https://raw.githubusercontent.com/w1770946466/Auto_proxy/main/Long_term_subscription8"],
    ["https://raw.githubusercontent.com/freefq/free/master/v2"],
    ["https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub"],
]

max_url_count = 2048

threadLock = threading.Lock()
result_urls: set[str] = set()
exist_data: set[str] = set()


def is_node_valid(item: str) -> bool:
	if item in result_urls:
		return False
	if item.find("v2ray-plugin") >= 0:
		return False

	s = item.find("://")
	if s <= 0 or s + 3 >= len(item):
		print(f"Cannot split protocol and data of {item}")
		return False

	protocol = item[:s]
	data = item[s + 3:]

	if data in exist_data:
		return False
	exist_data.add(data)

	if protocol in ["ss", "ssr", "trojan", "vless", "vmess"]:
		if protocol == "vmess":
			# vmess 地址，Base64
			try:
				vmess_json = base64.urlsafe_b64decode(data).decode("utf-8")
				json_dict: dict[str, str] = json.loads(vmess_json)
				server = json_dict["add"]
				if re.match(r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$", json_dict["id"]) is None:
					return False
			except Exception as e:
				print(f"Cannot parse vmess url: {item} Error: {e}")
				return False
		else:
			if protocol == "ssr":
				try:
					data = base64.urlsafe_b64decode(data).decode("utf-8")
				except Exception as e:
					pass
			# type@ip.ip.ip.ip#name
			server = data.split(":")[0].split("?")[0].split("#")[0].split("@")[-1]

		if re.match(r"^(?:[-a-z0-9]+\.)+[a-z0-9]+$", server) is None:
			return False
		if server.find("127.0.0.1") >= 0 or server.find("localhost") >= 0:
			return False

		return True

	print(f"Unknown url: {item}")
	return False


def get_from_urls(url_list: str):
	"""
	从给定的一组 url 中获取首个有效的 url，并将订阅内容添加到 result_urls 中
	"""
	for url in url_list:
		try:
			if len(result_urls) >= max_url_count:
				return
			result = requests.get(url)
			if result.ok:
				result_str = result.content.decode("utf-8")
				if result_str.startswith(("ss://", "ssr://", "trojan://", "vmess://", "vless://")):
					node_list = result_str.splitlines()
				else:
					node_list = base64.urlsafe_b64decode(result.content).decode("utf-8").splitlines()
				threadLock.acquire()
				list_len = len(result_urls)
				if list_len < max_url_count:
					for node in node_list:
						node_str = node.strip()
						if is_node_valid(node_str):
							result_urls.add(node_str)
						else:
							print(f"Invalid node: {node_str}")
					print(f"{result.url} result: {len(result_urls) - list_len}")
				threadLock.release()
				return
		except Exception as e:
			print(f"{url} Error: {e}")


def main():
	global result_urls
	global max_url_count
	parser = argparse.ArgumentParser(description="获取V2Ray节点")
	parser.add_argument("-i", "--input", help="输入文件名", default="")
	parser.add_argument("-o", "--output", help="输出文件名", default="v2ray.txt")
	parser.add_argument("-m", "--max", help="保留节点数", default="2048")
	parser.add_argument("-u", "--urls", help="使用的订阅url列表,用|隔开,留空则使用内置所有url", default="")
	args = parser.parse_args()
	max_url_count = int(args.max)
	if len(args.input) > 0:
		try:
			with open(args.input, "r", encoding="utf-8") as f:
				result_urls = set(base64.urlsafe_b64decode(f.read()).decode("utf-8").splitlines())
		except Exception:
			result_urls = set()

	threads: list[threading.Thread] = []

	if len(args.urls) > 0:
		ALL_URLS.clear()
		for url_list in args.urls.split("|"):
			ALL_URLS.append([url_list])

	# 为每一组 url 创建一个线程
	for url_list in ALL_URLS:
		t = threading.Thread(target=get_from_urls, args=(url_list,))
		threads.append(t)
		t.start()

	# 等待所有线程完成
	for t in threads:
		t.join()

	result_list = list(result_urls)[:min(len(result_urls), max_url_count)]

	with open(args.output, "w", encoding="utf-8") as f:
		f.write(base64.b64encode("\n".join(result_list).encode("utf-8")).decode("utf-8"))


if __name__ == "__main__":
	main()
