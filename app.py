import json
import random
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import json


def sleep_random():
    time.sleep(random.randint(1, 5))


def get_least_followed():
    with open("least_followed.json", "r") as f:
        data = json.load(f)

    users = data["users"]
    return list(map(lambda user: user["username"], users))


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False,
            args=[
                "--disable-gpu",
                "--disable-setuid-sandbox",
                "--disable-accelerated-2d-canvas",
                "--no-zygote",
                "--frame-throttle-fps=10",
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-blink-features",
                "--disable-translate",
                "--safebrowsing-disable-auto-update",
                "--disable-sync",
                "--hide-scrollbars",
                "--disable-notifications",
                "--disable-logging",
                "--disable-permissions-api",
                "--ignore-certificate-errors",
                "--proxy-server='direct://'",
                "--proxy-bypass-list=*",
                "--host-resolver-rules=MAP www.googletagmanager.com 127.0.0.1, MAP www.google-analytics.com 127.0.0.1, MAP *.facebook.* 127.0.0.1, MAP assets.adobedtm.com 127.0.0.1, MAP s2.adform.net 127.0.0.1",
                "--no-first-run",
                "--disable-audio-output",
                "--disable-canvas-aa",
                "--disable-gl-drawing-for-tests",
                "--disable-dev-shm-usage",
            ],
        )
        context = browser.new_context(
            user_agent="Instagram 257.1.0.13.119 (iPhone14,3; iOS 16_1; tr_TR; tr-TR; scale=3.00; 1284x2778; 409247554) AppleWebKit/420+"
        )

        try:
            with open("cookies.json", "r") as f:
                cookies = json.loads(f.read())
                context.add_cookies(cookies)
            page = context.new_page()
            stealth_sync(page)
            page.evaluate(
                "() => { Object.defineProperty(navigator, 'webdriver', { get: () => undefined }) }"
            )
            context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
            )
        except FileNotFoundError:
            page = context.new_page()
            page.goto("https://www.instagram.com/accounts/login/")

            page.wait_for_selector('input[name="username"]')
            print("Please login to your Instagram account and press enter.")
            input()

            with open("cookies.json", "w") as f:
                f.write(json.dumps(context.cookies()))

        page.goto(
            "https://i.instagram.com/api/v1/friendships/smart_groups/least_interacted_with/?search_surface=follow_list_page&query=&enable_groups=true&rank_token=e667dad2-ccf4-461a-ba53-d83f9007cc7f"
        )
        content = page.text_content("body")
        with open("least_followed.json", "w") as f:
            f.write(content)

        least_followed_users = get_least_followed()
        for i in range(random.randint(10, len(least_followed_users))):
            user = least_followed_users[i]
            page.goto(f"https://www.instagram.com/{user}/")
            page.wait_for_load_state("networkidle")
            sleep_random()
            page.get_by_text("Following").first.click()
            page.wait_for_load_state("networkidle")
            sleep_random()
            page.get_by_text("Unfollow").click()
            print(f"Unfollowed {user}")
            sleep_random()

        context.close()
        browser.close()


main()
