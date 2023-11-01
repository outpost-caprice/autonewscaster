import os
import requests
import traceback
from langchain.documentloaders import HNLoader
import openai

# 最後に確認したニュースのID
last_checked_id = None

# 要約用の関数
def summarize_content(content):
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            temperature=0,
            messages=[
                {"role": "system", "content": "あなたは優秀な要約アシスタントです。提供された文章をもとに、できる限り正確な内容にすることを意識して要約してください。"},
                {"role": "user", "content": content}
            ]
        )
        return completion.choices[0].message['content']
    except Exception as e:
        print(f"Error in summarization: {e}")
        traceback.print_exc()
        return "要約できませんでした"

# 意見生成用の関数
def generate_opinion(content):
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=0.6,
            messages=[
                {"role": "system", "content": "あなたは優秀な意見生成アシスタントです。提供された文章をもとに、感想や意見を生成してください。"},
                {"role": "user", "content": content}
            ]
        )
        return completion.choices[0].message['content']
    except Exception as e:
        print(f"Error in opinion generation: {e}")
        traceback.print_exc()
        return "意見を生成できませんでした"

# 新しいHacker Newsのコンテンツを確認する関数
def check_new_hn_content(request):
    global last_checked_id
    try:
        # Hacker Newsのトップページをロード
        loader = HNLoader("https://news.ycombinator.com/")
        data = loader.load()

        # トップニュースのIDを取得（仮に最初のニュースのIDを'new_id'とする）
        new_id = data[0]['id']

        # 新しいニュースがあるか確認
        if new_id != last_checked_id:
            # 新しいニュースの内容をすべて取得
            full_content = data[0]['page_content']

            # 内容を要約
            summary = summarize_content(full_content)

            # 意見を生成
            opinion = generate_opinion(summary)

            # IFTTTのWebhook URL
            webhook_url = os.getenv("IFTTT_WEBHOOK_URL")

            # IFTTTに送信するデータ
            data = {"value1": f"新しいニュースがあります(ID: {new_id})", "value2": summary, "value3": opinion}

            # IFTTTのWebhookを通じてSlackに投稿
            requests.post(webhook_url, json=data)

            # 最後に確認したニュースのIDを更新
            last_checked_id = new_id
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except openai.Error as e:
        print(f"OpenAI API error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()

# この関数を定期的に呼び出すコードが必要ですが、その部分は省略しています。
