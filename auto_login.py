
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json
import sys

# 禁用 SSL 警告，因为内网 IP 通常使用自签名证书
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class InnerNetLoginer:
    def __init__(self, base_url, username, password):
        """
        初始化登录器
        :param base_url: 基础 URL，例如 https://172.20.0.138
        :param username: 用户名
        :param password: 密码
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        # 创建 Session 对象，自动处理 Cookie 和会话保持
        self.session = requests.Session()
        # 设置默认请求头，模拟浏览器行为
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        })

    def login(self, login_api_path="/"):#/api/login
        """
        执行登录操作
        :param login_api_path: 登录接口的路径，需根据实际抓包结果调整
        :return: Boolean 是否登录成功
        """
        login_url = f"{self.base_url}{login_api_path}"
        
        # 注意：不同的系统登录参数名可能不同，常见为 username/password 或 user/pwd
        # 如果是 JSON 格式提交，请使用 json=data 而不是 data=data
        payload = {
            "username": self.username,
            "password": self.password
        }

        try:
            print(f"正在尝试登录: {login_url}")
            # verify=False 跳过证书验证，适配内网自签名证书
            response = self.session.post(login_url, data=payload, verify=False, timeout=10)
            
            # 检查 HTTP 状态码
            if response.status_code == 200:
                # 进一步检查返回内容是否包含成功标识
                # 这里假设返回 JSON，具体需根据实际接口响应调整
                try:
                    resp_json = response.json()
                    # 示例：假设 code=200 或 success=true 表示成功
                    if resp_json.get('code') == 200 or resp_json.get('success') is True:
                        print("登录成功！")
                        return True
                    else:
                        print(f"登录失败，服务器返回: {resp_json}")
                        return False
                except json.JSONDecodeError:
                    # 如果返回的是 HTML 或非 JSON，简单判断是否包含错误关键词
                    if "error" not in response.text.lower() and "fail" not in response.text.lower():
                        print("登录请求已发送，响应非 JSON 格式，假设成功（请人工确认）")
                        return True
                    else:
                        print("登录失败，响应中包含错误信息")
                        return False
            else:
                print(f"登录请求失败，状态码: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"网络请求异常: {str(e)}")
            return False

    def access_protected_page(self, path="/#/asset-manager"):
        """
        访问受保护的页面
        :param path: 目标页面路径
        :return: 页面内容或 None
        """
        target_url = f"{self.base_url}{path}"
        try:
            print(f"正在访问受保护资源: {target_url}")
            # 使用 session 发起请求，会自动携带登录后的 Cookie
            response = self.session.get(target_url, verify=False, timeout=10)
            
            if response.status_code == 200:
                print("资源访问成功")
                # 对于 SPA (单页应用) 如 Vue/React，直接 get hash 路由可能只返回 index.html
                # 真正的数据通常需要通过额外的 API 获取
                return response.text
            elif response.status_code == 401 or response.status_code == 403:
                print("访问被拒绝，可能未登录或权限不足")
                return None
            else:
                print(f"访问失败，状态码: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"访问资源时发生异常: {str(e)}")
            return None

def main():
    # 配置信息
    TARGET_BASE_URL = "https://172.20.0.138"
    MY_USERNAME = "admin"      # 请替换为实际用户名
    MY_PASSWORD = "Dbapp#2025#zjsw"   # 请替换为实际密码
    
    # 注意：登录接口路径需要根据浏览器开发者工具 Network 面板抓包确定
    # 常见的有 /login, /api/login, /auth/signin 等
    LOGIN_API_PATH = "/#/risk" #"" #"/api/login"
    
    # 实例化登录器
    loginer = InnerNetLoginer(TARGET_BASE_URL, MY_USERNAME, MY_PASSWORD)
    
    # 1. 执行登录
    if loginer.login(login_api_path=LOGIN_API_PATH):
        # 2. 登录成功后，访问目标页面
        # 注意：/#/asset-manager 是前端路由，直接请求可能只能拿到入口 HTML
        # 如果需要获取资产数据，通常需要调用对应的数据 API，例如 /api/assets
        content = loginer.access_protected_page("/#/asset-manager")
        
        if content:
            # 这里可以根据需求解析 HTML 或保存文件
            print("页面内容长度:", len(content))
            # with open("page_source.html", "w", encoding="utf-8") as f:
            #     f.write(content)
    else:
        print("登录流程终止")

if __name__ == "__main__":
    main()
