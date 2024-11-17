from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
import json

app = FastAPI()

class Prompt(BaseModel):
    prompt: str
    n_predict: int

class Message(BaseModel):
    role: str
    text: str

class Chat(BaseModel):
    messages: list[Message]

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
        logger.debug(f"Get Request from frontend: {chat.messages}")
        chat.messages.insert(0, {"role": "User", "text": "あなたは会話形式でUserの1日の振り返りをサポートするAssistantです．あなたはUserのやったことを褒めることで，Userの自己肯定感を高めてください．Assistantの回答のみを日本語で出力してください．"})
        response = requests.post(
            "http://llamacpp-server:3300/completion",
            headers={"Content-Type": "application/json"},
            json={"prompt": str(chat.messages), "n_predict": 120},
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