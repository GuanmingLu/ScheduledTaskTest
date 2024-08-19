import datetime
import requests
import base64
import threading
import argparse
import json
import re

SCRIPT_DIR = os.path.split(os.path.realpath(__file__))[0]


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
    # [f"https://clashfree.eu.org/wp-content/uploads/rss/{y}{m}{d}.txt" for (y, m, d) in date_list()],
    { "name": "clashgithub", "urls": [f"https://clashgithub.com/wp-content/uploads/rss/{y}{m}{d}.txt" for (y, m, d) in date_list()] },
    # [f"https://oneclash.cc/wp-content/uploads/{y}/{m}/{y}{m}{d}.txt" for (y, m, d) in date_list()],
    { "name": "oneclash", "urls": [f"https://oneclash.githubrowcontent.com/{y}/{m}/{y}{m}{d}.txt" for (y, m, d) in date_list()] },
    # [f"https://v2rayshare.com/wp-content/uploads/{y}/{m}/{y}{m}{d}.txt" for (y, m, d) in date_list()],
    { "name": "v2rayshare", "urls": [f"https://v2rayshare.githubrowcontent.com/{y}/{m}/{y}{m}{d}.txt" for (y, m, d) in date_list()] },
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
				result_yaml = result.content.decode("utf-8")
				result_str = f"# {url}\n{result_yaml}"
				# TODO 保存到文件
				filePath = SCRIPT_DIR + "/" + name = items["name"]
				with open(filePath, "w", encoding="utf-8") as f:
					f.write(result_str)
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


if __name__ == "__main__":
	main()
