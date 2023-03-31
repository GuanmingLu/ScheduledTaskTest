import requests

source_url = "https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online_Full_MultiMode.ini"

if __name__ == "__main__":
	try:
		result = requests.get(source_url)
		if result.ok:
			config = result.content.decode("utf-8").replace("gstatic", "google")
			with open("clashConfig.ini", "w", encoding="utf-8") as f:
				f.write(config)
			print("获取配置文件成功")
		else:
			print(f"获取配置文件失败: {result.status_code}")
	except Exception as e:
		print(f"获取配置文件失败: {e}")
