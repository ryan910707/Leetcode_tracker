import os
import requests

GRAPHQL_URL = "https://leetcode.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://leetcode.com/problemset/all/",
}


def fetch_question_progress(user_slug: str):
    """根據給定的 user_slug 抓取該使用者的 LeetCode 解題進度"""
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
            f"Query failed to run with status code {response.status_code}: {response.text}"
        )


if __name__ == "__main__":
    # 1. 多個使用者 ID 列表
    user_list = [
        "kevin1010607",
        "johnson684",
        "erictsai90",
        "ryanke91",
        "dasbd72",
        "huiyuiui",
    ]
    
    # 2. 建立 HTML 表格內容
    table_rows = ""
    for user in user_list:
        try:
            progress = fetch_question_progress(user)
            table_rows += f"""
            <tr>
                <td>{user}</td>
                <td>{progress['EASY']}</td>
                <td>{progress['MEDIUM']}</td>
                <td>{progress['HARD']}</td>
                <td>{progress['TOTAL']}</td>
            </tr>
            """
        except Exception as e:
            # 如果抓不到，顯示錯誤訊息
            table_rows += f"""
            <tr>
                <td>{user}</td>
                <td colspan="4" style="color:red;">Error: {e}</td>
            </tr>
            """

    # 3. 建立完整 HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
    <meta charset="utf-8">
    <title>LeetCode 進度報告</title>
    <style>
      body {{
        font-family: Arial, sans-serif;
        margin: 20px;
      }}
      table {{
        border-collapse: collapse;
        width: 100%;
        max-width: 600px;
      }}
      th, td {{
        border: 1px solid #ccc;
        padding: 8px 12px;
      }}
      th {{
        background-color: #f5f5f5;
      }}
      tr:hover {{
        background-color: #f9f9f9;
      }}
    </style>
</head>
<body>
    <h1>LeetCode 進度報告</h1>
    <p>下表為多名使用者的 LeetCode Accepted 數量：</p>
    <table>
        <thead>
            <tr>
                <th>使用者</th>
                <th>Easy</th>
                <th>Medium</th>
                <th>Hard</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            {table_rows}
        </tbody>
    </table>
    <footer>
        <p style="margin-top: 20px;">最後更新：由 GitHub Actions 自動執行</p>
    </footer>
</body>
</html>
"""

    # 4. 寫入 docs/index.html（若無此檔則自動建立）
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("✅ 已寫入 docs/index.html")
