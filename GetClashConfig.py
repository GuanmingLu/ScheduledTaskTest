import requests
import argparse

parser = argparse.ArgumentParser(description="获取Clash配置文件模板")
parser.add_argument("-u", "--url", help="配置文件地址", default="https://raw.githubusercontent.com/ACL4SSR/ACL4SSR/master/Clash/config/ACL4SSR_Online_Full_MultiMode.ini")
parser.add_argument("-o", "--output", help="输出文件名", default="clashConfig.ini")
args = parser.parse_args()

if __name__ == "__main__":
	try:
		result = requests.get(args.url)
		if result.ok:
			config = result.content.decode("utf-8").replace("gstatic", "google")
			with open(args.output, "w", encoding="utf-8") as f:
				f.write(config)
			print("获取配置文件成功")
		else:
			print(f"获取配置文件失败: {result.status_code}")
	except Exception as e:
		print(f"获取配置文件失败: {e}")
