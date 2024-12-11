from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
import json
import  re
import os

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
            timeout=90,  # タイムアウトを30秒に設定
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
        # LLMによる今日1日のユーザーの行動に対する評価の文章を生成　
        return {"llm_review": "朝から家の掃除をするのは難しいことですね．そしてちゃんと授業にも出席できています．当たり前を当たり前にこなすことは難しいことですからね．"}
    except requests.exceptions.Timeout:
        logger.error("Request to llamacpp-server timed out")
        raise HTTPException(status_code=504, detail="Request to llamacpp-server timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException: {e}")
        raise HTTPException(status_code=500, detail="Service unavailable or request failed")
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: {e}")
        raise HTTPException(status_code=502, detail="Invalid JSON response from llamacpp-server")