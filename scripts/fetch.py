import os
import json
import datetime
import requests
from pathlib import Path

GRAPHQL_URL = "https://leetcode.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://leetcode.com/problemset/all/",
}

def fetch_question_progress(user_slug: str):
    """抓取單一使用者的 LeetCode Accepted 題數 (Easy/Medium/Hard/Total)"""
    headers = HEADERS.copy()
    headers["Referer"] = f"https://leetcode.com/{user_slug}/"

    query = """
    query userProfileUserQuestionProgressV2($userSlug: String!) {
      userProfileUserQuestionProgressV2(userSlug: $userSlug) {
        numAcceptedQuestions {
          count
          difficulty
        }
      }
    }
    """
    payload = {
        "query": query,
        "variables": {"userSlug": user_slug},
        "operationName": "userProfileUserQuestionProgressV2",
    }

    resp = requests.post(GRAPHQL_URL, json=payload, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        arr = data["data"]["userProfileUserQuestionProgressV2"]["numAcceptedQuestions"]

        result = {
            "EASY": 0,
            "MEDIUM": 0,
            "HARD": 0,
            "TOTAL": 0
        }
        for entry in arr:
            difficulty = entry["difficulty"]
            count = entry["count"]
            result[difficulty] = count
            result["TOTAL"] += count
        return result
    else:
        raise Exception(
            f"Query failed with status code {resp.status_code}: {resp.text}"
        )


if __name__ == "__main__":
    # 1. 你想要追蹤的多個使用者
    user_list = [
        "kevin1010607",
        "johnson684",
        "erictsai90",
        "ryanke91",
        "dasbd72",
        "huiyuiui",
    ]

    # 2. 設定今日日期 (YYYY-MM-DD)
    today = datetime.date.today().isoformat()

    # 3. 讀取現有的 daily_progress.json（若無則建空物件）
    data_file = Path("docs/daily_progress.json")
    if data_file.exists():
        with open(data_file, "r", encoding="utf-8") as f:
            daily_data = json.load(f)
    else:
        daily_data = {}

    # 4. 如果今天的key尚不存在，就初始化
    if today not in daily_data:
        daily_data[today] = {}

    # 5. 依序抓取每位使用者並更新到 daily_data
    for user in user_list:
        try:
            stats = fetch_question_progress(user)
            daily_data[today][user] = {
                "EASY": stats["EASY"],
                "MEDIUM": stats["MEDIUM"],
                "HARD": stats["HARD"],
                "TOTAL": stats["TOTAL"],
            }
        except Exception as e:
            # 若抓不到，就用 None 或其他方式標記
            daily_data[today][user] = {
                "EASY": None,
                "MEDIUM": None,
                "HARD": None,
                "TOTAL": None,
            }
            print(f"[Error] {user}: {e}")

    # 6. 寫回檔案
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 已更新 {today} 的數據到 {data_file}")
