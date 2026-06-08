from urllib.parse import quote
import requests
import argparse

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="将V2Ray节点转换为Clash配置文件")
	parser.add_argument("-u", "--url", help="v2Ray订阅地址", default="https://raw.githubusercontent.com/GuanmingLu/ScheduledTaskTest/main/v2-node.txt")
	parser.add_argument("-c", "--config", help="Clash配置文件模板", default="https://raw.githubusercontent.com/GuanmingLu/ScheduledTaskTest/main/clashConfig.ini")
	parser.add_argument("-o", "--output", help="输出文件名", default="clash.yaml")
	args = parser.parse_args()

	data = {
	    "target": "clash",
	    "url": args.url,
	    "exclude": "(CN_FreeNode|中国($|[^-])|移动|联通|电信)",
	    "config": args.config,
	    "udp": "true",
	}

	access_url = f"https://app.sublink.works/clash?config={quote(args.url, safe="")}&ua=&selectedRules=%5B%22Location%3ACN%22%2C%22Private%22%2C%22Non-China%22%2C%22Github%22%2C%22Google%22%2C%22Youtube%22%2C%22AI+Services%22%2C%22Telegram%22%5D&customRules=%5B%5D&group_by_country=true"

	print(access_url)

	try:
		result = requests.get(access_url)
		if result.ok:
			# print(result.content.decode("utf-8"))
			with open(args.output, "w", encoding="utf-8") as f:
				f.write(result.content.decode("utf-8"))
			print("获取订阅内容成功")
		else:
			print(f"获取订阅内容失败: {result.status_code}")
	except Exception as e:
		print(f"获取订阅内容失败: {e}")
