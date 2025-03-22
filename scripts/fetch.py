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
    """根據 user_slug 抓取該使用者的 LeetCode 解題進度（簡易版）"""
    headers = HEADERS.copy()
    headers.update({
        "Referer": f"https://leetcode.com/{user_slug}/",
    })

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

    response = requests.post(GRAPHQL_URL, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        data = data["data"]["userProfileUserQuestionProgressV2"]["numAcceptedQuestions"]
        result = {
            "EASY": 0,
            "MEDIUM": 0,
            "HARD": 0,
            "TOTAL": 0,
        }
        for entry in data:
            difficulty = entry["difficulty"]
            count = entry["count"]
            result[difficulty] = count
            result["TOTAL"] += count
        return result
    else:
        raise Exception(
            f"Query failed: status={response.status_code}, text={response.text}"
        )


if __name__ == "__main__":
    # 1. 多個使用者 (你想要抓的 LeetCode 用戶)
    user_list = [
        "kevin1010607",
        "johnson684",
        "erictsai90",
        "ryanke91",
        "dasbd72",
        "huiyuiui",
    ]

    # 2. 準備日期 key (以 YYYY-MM-DD 表示)
    today_str = datetime.date.today().isoformat()

    # 3. 讀取現有的 daily_progress.json（若檔案不存在，就初始化一個空字典）
    data_file = Path("docs/daily_progress.json")
    if data_file.exists():
        with open(data_file, "r", encoding="utf-8") as f:
            daily_data = json.load(f)
    else:
        daily_data = {}

    # daily_data 結構示意：
    # {
    #   "2025-03-21": {
    #       "kevin1010607": 120,
    #       "johnson684":  155,
    #       ...
    #   },
    #   "2025-03-22": {
    #       ...
    #   }
    # }

    # 4. 更新今日資料
    if today_str not in daily_data:
        daily_data[today_str] = {}

    for user in user_list:
        try:
            progress = fetch_question_progress(user)
            total_count = progress["TOTAL"]
            daily_data[today_str][user] = total_count
        except Exception as e:
            # 抓取失敗時可視情況記錄 -1 或其他處理方式
            daily_data[today_str][user] = None
            print(f"[Error] {user} -> {e}")

    # 5. 寫回 daily_progress.json
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 更新完畢：{today_str} 的資料已寫入 daily_progress.json")
