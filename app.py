import json
import random
import time
from playwright.sync_api import sync_playwright
import json


def get_least_followed():
    with open("least_followed.json", "r") as f:
        data = json.load(f)

    users = data["users"]
    return list(map(lambda user: user["username"], users))


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Instagram 257.1.0.13.119 (iPhone14,3; iOS 16_1; tr_TR; tr-TR; scale=3.00; 1284x2778; 409247554) AppleWebKit/420+"
        )

        try:
            with open("cookies.json", "r") as f:
                cookies = json.loads(f.read())
                context.add_cookies(cookies)
            page = context.new_page()
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
            page.get_by_text("Following").first.click()
            page.wait_for_load_state("networkidle")
            page.get_by_text("Unfollow").click()
            print(f"Unfollowed {user}")
            time.sleep(random.randint(1, 5))

        context.close()
        browser.close()


main()
