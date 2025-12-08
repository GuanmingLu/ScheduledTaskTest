import datetime
import os
import requests
import threading
import re
import yaml


SCRIPT_DIR = os.path.split(os.path.realpath(__file__))[0]


# 更新后可用的订阅链接
successSubscribeUrls = []
successSubscribeUrls_lock = threading.Lock()
def generateSubscribeUrl(fileNameWithoutExt: str):
	"""
	生成订阅链接
	"""
	successSubscribeUrls_lock.acquire()
	try:
		successSubscribeUrls.append(f"https://raw.githubusercontent.com/GuanmingLu/ScheduledTaskTest/main/auto_update_yaml/{fileNameWithoutExt}.yaml")
	finally:
		successSubscribeUrls_lock.release()


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
	# https://clashnodeshare.github.io/uploads/2024/08/0-20240819.yaml
	{ "name": "clashnodeshare", "urls": [f"https://clashnodeshare.github.io/uploads/{y}/{m}/{n}-{y}{m}{d}.yaml" for (y, m, d) in date_list() for n in range(10)] },
	# https://clashnodesfree.github.io/uploads/2024/08/0-20240819.yaml
	{ "name": "clashnodesfree", "urls": [f"https://clashnodesfree.github.io/uploads/{y}/{m}/{n}-{y}{m}{d}.yaml" for (y, m, d) in date_list() for n in range(10)] },
	# https://nodeclash.github.io/uploads/2024/08/0-20240819.yaml
	{ "name": "nodeclash", "urls": [f"https://nodeclash.github.io/uploads/{y}/{m}/{n}-{y}{m}{d}.yaml" for (y, m, d) in date_list() for n in range(10)] },
	# https://freenode.openrunner.net/uploads/20240819-clash.yaml
	{ "name": "openrunner", "urls": [f"https://freenode.openrunner.net/uploads/{y}{m}{d}-clash.yaml" for (y, m, d) in date_list()] },
	# https://clashgithub.com/wp-content/uploads/rss/20240819.yml
    { "name": "clashgithub", "urls": [f"https://clashgithub.com/wp-content/uploads/rss/{y}{m}{d}.yml" for (y, m, d) in date_list()] },
    { "name": "oneclash", "urls": [f"https://oneclash.githubrowcontent.com/{y}/{m}/{y}{m}{d}.yaml" for (y, m, d) in date_list()] },
    { "name": "v2rayshare", "urls": [f"https://v2rayshare.githubrowcontent.com/{y}/{m}/{y}{m}{d}.yaml" for (y, m, d) in date_list()] },
]


def get_from_urls(items):
	"""
	从给定的一组 url 中获取首个有效的 url，并将订阅内容保存到文件中
	"""
	for url in items["urls"]:
		try:
			result = requests.get(url)
			if result.ok:
				print(url)
				note = f"[{re.sub(r"(clash)|(\.?ya?ml)", "", url)[-20:]}]"
				result_yaml = result.content.decode("utf-8")
				yaml_obj = yaml.load(result_yaml, Loader=yaml.FullLoader)
				yaml_obj["proxies"].insert(0, {
					"name": note,
					"server": "127.0.0.1",
					"port": 443,
					"type": "ss",
					"cipher": "aes-256-cfb",
					"password": "password"
				})
				yaml_obj["proxy-groups"][0]["proxies"].insert(0, note)
				result_yaml = yaml.dump(yaml_obj)
				# TODO 保存到文件
				filePath = SCRIPT_DIR + "/" + items["name"] + ".yaml"
				generateSubscribeUrl(items["name"])
				with open(filePath, "w", encoding="utf-8") as f:
					f.write("# " + url + "\n")
					f.write(result_yaml)
				return
		except Exception as e:
			print(f"{url} Error: {e}")


def main():

	threads: list[threading.Thread] = []

	# 为每一组 url 创建一个线程
	for url_list in ALL_URLS:
		t = threading.Thread(target=get_from_urls, args=(url_list,))
		threads.append(t)
		t.start()

	# 等待所有线程完成
	for t in threads:
		t.join()

	# 保存可用的订阅链接
	with open(SCRIPT_DIR + "/availableList.txt", "w", encoding="utf-8") as f:
		for url in successSubscribeUrls:
			f.write(url + "\n")


if __name__ == "__main__":
	main()
