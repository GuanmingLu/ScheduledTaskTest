from Crypto.Cipher import AES
import requests
import base64
import random
import threading
import argparse

password = b'awdtif20190619ti'
iv = password

urls = [
    "https://www.xjq88f.xyz:20000/api/evmess?vip=true",
    "https://www.xch8kf.xyz:20000/api/evmess?vip=true",
    "https://www.xf5qdgyc.xyz:20000/api/evmess?vip=true",
    "https://www.lt71126.xyz:20000/api/evmess?vip=true",
    "https://www.hd327658.xyz:20000/api/evmess&vip=true",
    "https://www.09898434.xyz/api/evmess?deviceid=49c95313d64fb7c5unknown&apps=cd9186e318e291300db27867d958eae5",
    "https://www.xfjyqirx.xyz:20000/api/evmess&vip=true",
]

succeeded_urls: set[str] = set()
succeeded_urls_lock = threading.Lock()


def set_url_to_succeeded(url: str):
	succeeded_urls_lock.acquire()
	if not url in succeeded_urls:
		print(url)
		succeeded_urls.add(url)
	succeeded_urls_lock.release()


vmess_urls: list[str] = []
vmess_urls_lock = threading.Lock()


def save_request_content(content: bytes):
	vmess = AES.new(password, AES.MODE_CBC, iv).decrypt(base64.b64decode(content)).decode("utf-8")
	vmess = vmess.strip("\x00")
	# print(vmess)
	vmess_urls_lock.acquire()
	if vmess_urls.count(vmess) == 0:
		vmess_urls.append(vmess)
	vmess_urls_lock.release()


def access_url():
	url = random.choice(urls)
	try:
		result = requests.get(url, timeout=10)
		if result.ok and result.status_code == 200:
			set_url_to_succeeded(url)
			# print(result.content)
			save_request_content(result.content)
	except:
		pass


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="获取加密V2Ray节点（加速器）")
	parser.add_argument("-i", "--input", help="输入文件名", default="")
	parser.add_argument("-o", "--output", help="输出文件名", default="v2ray.txt")
	parser.add_argument("-t", "--threads", help="线程数", default=60, type=int)
	args = parser.parse_args()
	if len(args.input) > 0:
		try:
			with open(args.input, "r", encoding="utf-8") as f:
				vmess_urls = base64.b64decode(f.read()).decode("utf-8").splitlines()
		except Exception:
			vmess_urls = []

	threads: list[threading.Thread] = []

	# 创建线程
	for i in range(args.threads):
		t = threading.Thread(target=access_url)
		threads.append(t)
		t.start()

	# 等待所有线程完成
	for t in threads:
		t.join()

	# print(vmess_urls)

	with open(args.output, "w", encoding="utf-8") as f:
		f.write(base64.b64encode("\n".join(vmess_urls).encode("utf-8")).decode("utf-8"))
