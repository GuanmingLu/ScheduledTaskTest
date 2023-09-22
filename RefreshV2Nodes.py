import datetime
import requests
import base64
import threading
import argparse
import json


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


all_urls = [
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
    ["https://raw.githubusercontent.com/mahdibland/V2RayAggregator/master/sub/splitted/vmess.txt"],
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

result_urls: set[str] = set()

exist_datas: set[str] = set()
threadLock = threading.Lock()


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

	if protocol in ["ss", "ssr", "trojan", "vless"]:
		# ss 地址，type@ip.ip.ip.ip#name
		ss_data = data.split("#")[0]
		if ss_data.find("127.0.0.1") >= 0 or ss_data.find("localhost") >= 0 or ss_data in exist_datas:
			return False
		exist_datas.add(ss_data)
		return True
	if protocol == "vmess":
		# vmess 地址，Base64
		try:
			vmess_json = base64.urlsafe_b64decode(data).decode("utf-8")
			json_dict: dict[str, str] = json.loads(vmess_json)
			ss_data = json_dict["add"]
			port = json_dict["port"]
			id = json_dict["id"]
			host = json_dict["host"] if "host" in json_dict else ""
			vmess_data = f"{ss_data}:{port}~{id}^{host}"
			if ss_data.find("127.0.0.1") >= 0 or ss_data.find("localhost") >= 0 or vmess_data in exist_datas:
				return False
			exist_datas.add(vmess_data)
			return True
		except Exception as e:
			print(f"Cannot parse vmess url: {item} Error: {e}")
			return False

	print(f"Unknown url: {item}")
	return False


def get_from_urls(url_list: str):
	"""
	从给定的一组 url 中获取首个有效的 url，并将订阅内容添加到 vmess_urls 中
	"""
	for url in url_list:
		try:
			result = requests.get(url)
			if result.ok:
				result_str = result.content.decode("utf-8")
				if result_str.startswith(("ss://", "ssr://", "trojan://", "vmess://", "vless://")):
					node_list = result_str.splitlines()
				else:
					node_list = base64.urlsafe_b64decode(result.content).decode("utf-8").splitlines()
				threadLock.acquire()
				list_len = len(result_urls)
				for node in node_list:
					node_str = node.strip()
					if is_node_valid(node_str):
						result_urls.add(node_str)
				print(f"{result.url} result: {len(result_urls) - list_len}")
				threadLock.release()
				return
		except Exception as e:
			print(f"{url} Error: {e}")


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="获取V2Ray节点")
	parser.add_argument("-i", "--input", help="输入文件名", default="")
	parser.add_argument("-o", "--output", help="输出文件名", default="v2ray.txt")
	args = parser.parse_args()
	if len(args.input) > 0:
		try:
			with open(args.input, "r", encoding="utf-8") as f:
				result_urls = set(base64.urlsafe_b64decode(f.read()).decode("utf-8").splitlines())
		except Exception:
			result_urls = set()

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
		f.write(base64.b64encode("\n".join(result_urls).encode("utf-8")).decode("utf-8"))
