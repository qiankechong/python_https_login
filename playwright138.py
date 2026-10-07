import os
from pathlib import Path
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
'''
with sync_playwright() as p:
    # ignore_https_errors=True 是关键
    browser = p.chromium.launch(headless=False, ignore_https_errors=True)
    page = browser.new_page()

    page.goto("https://172.20.0.13")

    # 填写表单
    page.fill("input[name='username']", "your_user")
    page.fill("input[name='password']", "your_pass")
    page.click("button[type='submit']")

    # 等待导航完成
    page.wait_for_load_state("networkidle")
    print(page.title())

    browser.close()
'''
# 配置路径：使用 pathlib 确保跨平台兼容性
CURRENT_DIR = Path(__file__).resolve().parent
COOKIE_FILE = CURRENT_DIR / ".172_20_0_138_auth.json"
SCREENSHOT_FILE = CURRENT_DIR / "risk_page_screenshot.png"


# COOKIE_SAVE_PATH = os.path.join(os.path.dirname(__file__), ".172_20_0_138_auth.json")
# SCREENSHOT_SAVE_PATH = Path(__file__).resolve().parent / "risk_page_screenshot.png"

# 目标网站配置
TARGET_URL = "https://172.20.0.138"
LOGIN_PAGE = f"{TARGET_URL}/login" # 假设登录页路径，如果是单页应用可直接访问根路径
RISK_PAGE = f"{TARGET_URL}/#/risk"
ASSET_MANAGER_PAGE= f"{TARGET_URL}/#/asset-manager"
QUERY_RESULT_SCREENSHOT = CURRENT_DIR / "risk_query_result.png"
# 基础配置
SAVE_DIR = Path(__file__).resolve().parent / "risk_snapshots"
SAVE_DIR.mkdir(exist_ok=True)

with sync_playwright() as p:

    #初始化浏览器，忽略内网自签名证书的HTTPS错误
    browser = p.chromium.launch(headless=False)

    # 2. 创建上下文时，加入 ignore_https_errors=True
    # 这是处理自签名证书/无效证书的关键步骤
    context = browser.new_context(ignore_https_errors=True)

    # 创建浏览器上下文，优先加载本地已保存的登录凭证
    # context = browser.new_context(
    #     viewport={"width": 1920, "height": 1080},
    #     locale="zh-CN",
    #     timezone_id="Asia/Shanghai"
    # )
    # 3. 在上下文中创建页面
    page = context.new_page()
    is_logged_in = False

    '''
    # 3. 尝试加载本地保存的 Cookie
    if COOKIE_FILE.exists():
        try:
            with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                cookies = eval(f.read())
            if cookies:
                context.add_cookies(cookies)
                print("检测到本地登录凭证，正在尝试复用...")
                page.goto(RISK_PAGE)
                # 等待页面加载，如果重定向回登录页则说明凭证失效
                page.wait_for_load_state("networkidle", timeout=10000)

                # 简单判断是否还在登录页（根据实际URL或标题判断）
                if "login" not in page.url.lower():
                    print("凭证有效，登录成功。")
                    is_logged_in = True
                else:
                    print("凭证已过期，需要重新登录。")
                    COOKIE_FILE.unlink()  # 删除无效凭证
        except Exception as e:
            print(f"加载凭证出错: {e}，将执行全新登录。")
            if COOKIE_FILE.exists():
                COOKIE_FILE.unlink()
        '''


    # 4. 现在可以正常访问 https://172.20.0.138 了
    page.goto("https://172.20.0.138")

    # ... 后续你的登录逻辑 ...
    page.fill("input[name='username']", "admin")
    page.fill("input[name='password']", "Dbapp#2025#zjsw")

    # 如果需要人工输入验证码，使用 pause()
    print("请在浏览器中手动输入验证码，完成后点击调试栏的继续按钮")
    page.pause()

    '''
    # 人工操作完成后，点击登录按钮
    # 请根据实际网页源码修改登录按钮选择器
    login_btn = page.locator("button[type='submit']")
    if login_btn.is_visible():
        login_btn.click()
    else:
        # 备用选择器，防止 submit 类型不匹配
        page.click(".login-btn")'''

    page.click("button[type='submit']")

    print("登录成功，当前标题:", page.title())

    # 等待登录完成并跳转
    page.wait_for_load_state("networkidle")
    print("登录请求已提交，等待页面跳转...")

    # 保存新的 Cookie
    new_cookies = context.cookies()
    with open(COOKIE_FILE, "w", encoding="utf-8") as f:
        f.write(str(new_cookies))
    print("新登录凭证已保存。")

    '''
    # 自动导航到目标风险页面
    page.goto("https://172.20.0.138/#/risk")

    # 额外等待页面的风险模块核心元素渲染完成，避免截到空白加载页
    page.locator(".risk-dashboard-container").wait_for(state="visible", timeout=10000)
    page.wait_for_load_state("networkidle")

    # 执行全屏截图并保存
    page.screenshot(path=str(SCREENSHOT_SAVE_PATH), full_page=True)
    print(f"截图已成功保存至：{SCREENSHOT_SAVE_PATH.resolve()}")'''


    # page.pause()
    # # 等待核心内容加载，避免截到空白页
    # # 请根据实际页面特征修改等待条件，例如等待某个特定 class 出现
    # try:
    #     page.wait_for_selector(".risk-container", timeout=10000)
    # except:
    #     print("未检测到特定容器，等待网络空闲后截图...")
    #
    page.wait_for_load_state("networkidle")

    # 额外等待几秒确保动态图表渲染完成
    page.wait_for_timeout(2000)

    # 执行全屏截图
    page.screenshot(path=str(SCREENSHOT_FILE), full_page=True)
    print(f"截图成功！文件已保存至: {SCREENSHOT_FILE}")

    # # 可选：在 Mac 上自动打开图片
    # if os.name == 'posix':
    #     os.system(f"open {SCREENSHOT_FILE}")


    while True:
        # 5. 跳转到目标风险页面并截图
        print(f"正在跳转至: {RISK_PAGE}")
        page.goto(RISK_PAGE)

        # 额外等待几秒确保动态图表渲染完成
        page.wait_for_timeout(4000)

        # 自动点击右下角蓝色查询按钮
        page.get_by_role("button", name="查询").click()
        print("已触发查询操作，正在等待查询结果加载...")

        # 等待查询结果表格加载完成，避免截到加载中状态
        # page.locator(".risk-result-table").wait_for(state="visible", timeout=15000)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)
        time.sleep(10)

        # 生成带日时分秒的时间戳文件名
        now = datetime.now()

        filename = f"risk_query_result_{now.day:02d}{now.hour:02d}{now.minute:02d}{now.second:02d}.png"

        # 执行全屏截图，保存查询结果页面
        page.screenshot(path=str(SAVE_DIR/filename), full_page=True)

        print(f"查询结果截图已成功保存至：{QUERY_RESULT_SCREENSHOT.resolve()}")

    # 5. 跳转到目标风险页面并截图
    print(f"正在跳转至: {ASSET_MANAGER_PAGE}")
    page.goto(ASSET_MANAGER_PAGE)
    # 额外等待几秒确保动态图表渲染完成
    page.wait_for_timeout(4000)

    page.pause()
    browser.close()

