from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import requests
import logging
import json
import  re
import os
import time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Prompt(BaseModel):
    prompt: str
    n_predict: int

class Message(BaseModel):
    role: str
    text: str

class Chat(BaseModel):
    messages: list[Message]
    mode: str

# ログ設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.post("/llama")
def ask_llama(prompt: Prompt):
    try:
        logger.debug(f"Sending request to llamacpp-server with prompt: {prompt.prompt}")
        response = requests.post(
            "http://llamacpp-server:3300/completion",
            headers={"Content-Type": "application/json"},
            json={"prompt": prompt.prompt, "n_predict": prompt.n_predict},
            timeout=60,  # タイムアウトを30秒に設定
            proxies={"http": None, "https": None}  # プロキシを無効にする
        )
        response.raise_for_status()  # ステータスコードが200番台でない場合に例外を発生させる
        logger.debug(f"Received response from llamacpp-server: {response.text}")
        return response.json()
    except requests.exceptions.Timeout:
        logger.error("Request to llamacpp-server timed out")
        raise HTTPException(status_code=504, detail="Request to llamacpp-server timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException: {e}")
        raise HTTPException(status_code=500, detail="Service unavailable or request failed")
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: {e}")
        raise HTTPException(status_code=502, detail="Invalid JSON response from llamacpp-server")

@app.post("/chat")
def ask_llama(chat: Chat):
    try:
        # ユーザーの入力に対し，指定したAIのmodeに沿ってユーザーを褒めながら返答を生成する
        logger.debug(f"Get Request from frontend: {chat.messages}")

        if chat.mode =="Boss":
            file_path = os.path.join(os.path.dirname(__file__), 'prompts/boss_prompt.txt')
        elif chat.mode =="Friend":
            file_path = os.path.join(os.path.dirname(__file__), 'prompts/friend_prompt.txt')
        elif chat.mode =="Commander":
            file_path = os.path.join(os.path.dirname(__file__), 'prompts/commander_prompt.txt')
        elif chat.mode =="Lady":
            file_path = os.path.join(os.path.dirname(__file__), 'prompts/lady_prompt.txt')


        # chatPrompt.txtを読み込む
        with open(file_path, 'r', encoding='utf-8') as file:
            prompt_data = json.load(file)

        # Messageオブジェクトを辞書に変換する関数
        def messageObj_to_dict(message):
            return {
                "role": message.role,
                "text": message.text
            }

        # chat.messagesの各Messageオブジェクトを辞書型に変換
        chat_messages_dict = [messageObj_to_dict(message) for message in chat.messages]
        
        # txtから読み込んだプロンプトとフロントエンドからの入力を結合
        chat.messages=prompt_data+chat_messages_dict
        message_txt=""
        for message in chat.messages:
            if message['role'] == "User":
                message_txt= message_txt + message["text"] + "\n"
            else:
                message_txt= message_txt + "A: "+ message["text"] + "\n"
        message_txt=message_txt+"A: "

        logger.debug(f"prompt: {message_txt}")
        
        # lamacpp-serverにプロンプトを送信
        response = requests.post(
            "http://llamacpp-server:3300/completion",
            headers={"Content-Type": "application/json"},
            json={"prompt": str(message_txt), "n_predict": 200},
            timeout=90,  # タイムアウトを90秒に設定
            proxies={"http": None, "https": None}  # プロキシを無効にする
        )
        response.raise_for_status()  # ステータスコードが200番台でない場合に例外を発生させる
        logger.debug(f"Received response from llamacpp-server: {response.text}")

        # レスポンスのcontentの文字列の最初の改行までを取得(Userへの返答文のみ取得)
        response_json = response.json()
        response_content = response_json.get("content", "")
        # レスポンスのcontentの文字列の最初の改行までを取得
        extracted_text = response_content.split("\n")[0]

        return {"original_response": response.json(), "extracted_text": extracted_text}
    
    # 例外処理
    except requests.exceptions.Timeout:
        logger.error("Request to llamacpp-server timed out")
        raise HTTPException(status_code=504, detail="Request to llamacpp-server timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException: {e}")
        raise HTTPException(status_code=500, detail="Service unavailable or request failed")
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: {e}")
        raise HTTPException(status_code=502, detail="Invalid JSON response from llamacpp-server")

    
@app.post("/userDiary")
def ask_llama(chat: Chat):
    try:
        # ユーザーの入力を元にLLMを使わずに日記を生成する　
        time.sleep(5)
        return {"user_diary": "今日は家の掃除をした．次に授業に出席した．"}
    except requests.exceptions.Timeout:
        logger.error("Request to llamacpp-server timed out")
        raise HTTPException(status_code=504, detail="Request to llamacpp-server timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException: {e}")
        raise HTTPException(status_code=500, detail="Service unavailable or request failed")
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: {e}")
        raise HTTPException(status_code=502, detail="Invalid JSON response from llamacpp-server")
    
@app.post("/LLMReview")
def ask_llama(chat: Chat):
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'prompts/diary_prompt.txt')

        if chat.mode =="Boss":
            file_path = os.path.join(os.path.dirname(__file__), 'prompts/boss_review_prompt.txt')
        elif chat.mode =="Friend":
            file_path = os.path.join(os.path.dirname(__file__), 'prompts/friend_review_prompt.txt')
        elif chat.mode =="Commander":
            file_path = os.path.join(os.path.dirname(__file__), 'prompts/commander_review_prompt.txt')
        elif chat.mode =="Lady":
            file_path = os.path.join(os.path.dirname(__file__), 'prompts/lady_review_prompt.txt')
        # プロンプトファイルを読み込み

        #file_path = os.path.join(os.path.dirname(__file__), 'prompts/diary_prompt.txt')
        with open(file_path, 'r', encoding='utf-8') as file:
            prompt_data = json.load(file)

        # プロンプトのバリデーション
        if not isinstance(prompt_data, list) or not prompt_data:
            raise HTTPException(status_code=400, detail="Invalid prompt format in diary_prompt.txt")
        instruction = prompt_data[0].get("instruction", "")
        examples = prompt_data[0].get("examples", [])

        if not instruction or not examples:
            raise HTTPException(status_code=400, detail="Prompt file is missing 'instruction' or 'examples'.")

        # ユーザーの行動を抽出
        user_messages = "\n".join([f"- {msg.text}" for msg in chat.messages if msg.role == "User"])

        # 完全なプロンプトの構築
        example_texts = "\n\n".join([
            "### 行動内容:\n" + "\n".join(f"- {act}" for act in ex["action"]) + f"\n### 総評:\n{ex['summary']}"
            for ex in examples
        ])

        full_prompt = f"{instruction}\n\n### 例:\n{example_texts}\n\n### ユーザーの行動:\n{user_messages}\n\n### 総評:"
        logger.debug(f"Generated Prompt: {full_prompt}")

        # Llamaサーバーへのリクエスト送信
        response = requests.post(
            "http://llamacpp-server:3300/completion",
            headers={"Content-Type": "application/json"},
            json={"prompt": full_prompt, "n_predict": -1},
            timeout=150
        )
        response.raise_for_status()

        # レスポンス処理
        response_json = response.json()
        logger.debug("Received response: " + json.dumps(response_json, ensure_ascii=False, indent=2))

        # 必要な部分を抽出
        response_content = response_json.get("content", "").strip()
        extracted_text = response_content.split("\n")[0]
        if not extracted_text:
            raise ValueError("Response content is empty.")
        
        # 総評を返却
        return {"llm_review": extracted_text}
        
    except requests.exceptions.Timeout:
        logger.error("Request to llamacpp-server timed out")
        raise HTTPException(status_code=504, detail="Request to llamacpp-server timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException: {e}")
        raise HTTPException(status_code=500, detail="Service unavailable or request failed")
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: {e}")
        raise HTTPException(status_code=502, detail="Invalid JSON response from llamacpp-server")