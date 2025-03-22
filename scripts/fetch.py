import os
import requests

GRAPHQL_URL = "https://leetcode.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://leetcode.com/problemset/all/",
}


def fetch_question_progress(user_slug: str):
    # 動態更新 Referer
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
            f"Query failed with status code {response.status_code}: {response.text}"
        )


if __name__ == "__main__":
    # 1. 取得 LeetCode 使用者名稱（可改為你想要的使用者）
    user_slug = "ryanke91"

    # 2. 抓取資料
    progress = fetch_question_progress(user_slug)

    # 3. 將抓到的資料寫入到 docs/index.html
    #   (若你已經在 docs 裡有模板，可以先讀取後再插入數據)
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="utf-8">
    <title>LeetCode 進度報告 - {user_slug}</title>
</head>
<body>
    <h1>LeetCode 進度報告</h1>
    <p><strong>User:</strong> {user_slug}</p>
    <ul>
        <li>Easy: {progress["EASY"]}</li>
        <li>Medium: {progress["MEDIUM"]}</li>
        <li>Hard: {progress["HARD"]}</li>
        <li>Total: {progress["TOTAL"]}</li>
    </ul>
    <footer>
        <p>最後更新：由 GitHub Actions 自動執行</p>
    </footer>
</body>
</html>
"""

    # 把產生的內容寫入 docs/index.html
    # 注意：如果 docs/index.html 不存在，會自動建立檔案
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("資料抓取完成並已寫入 docs/index.html")
