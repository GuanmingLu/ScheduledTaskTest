from urllib.parse import urlencode
import requests

urls = [
    "https://raw.githubusercontent.com/GuanmingLu/ScheduledTaskTest/main/v2ray.txt",
    "https://raw.githubusercontent.com/GuanmingLu/ScheduledTaskTest/main/acceleratorNodes.txt",
]

data = {
    "target": "clash",
    "url": "|".join(urls),
    "exclude": "(中国($|[^-])|移动|联通|电信)",
    "config": "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online_Full_MultiMode.ini",
}

access_url = "https://sub.xeton.dev/sub?" + urlencode(data)

print(access_url)

if __name__ == "__main__":
	try:
		result = requests.get(access_url)
		if result.ok:
			# print(result.content.decode("utf-8"))
			with open("clash.yaml", "w", encoding="utf-8") as f:
				f.write(result.content.decode("utf-8"))
			print("获取订阅内容成功")
		else:
			print(f"获取订阅内容失败: {result.status_code}")
	except Exception as e:
		print(f"获取订阅内容失败: {e}")
