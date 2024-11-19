from typing import Union
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import logging
import json
import  re

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
        chat.messages.insert(0, {"role": "Assistant", "text": "私はUserの1日の振り返りをサポートするAssistantです．私はUserとの会話の中でUserがやったことを褒め，Userの自己肯定感を高めます．出力は以降の会話に続くAsasistantである私の発言のみとします．"})
        response = requests.post(
            "http://llamacpp-server:3300/completion",
            headers={"Content-Type": "application/json"},
            json={"prompt": str(chat.messages), "n_predict": 200},
            timeout=90,  # タイムアウトを30秒に設定
            proxies={"http": None, "https": None}  # プロキシを無効にする
        )
        response.raise_for_status()  # ステータスコードが200番台でない場合に例外を発生させる
        logger.debug(f"Received response from llamacpp-server: {response.text}")

        # 正規表現で`text:`の直後の日本語部分を抽出
        match = re.search(r"text': '([^']+)", response.text)
        extracted_text = match.group(1) if match else None

        if extracted_text:
            logger.info(f"Extracted text: {extracted_text}")

        return {"original_response": response.json(), "extracted_text": extracted_text}
    except requests.exceptions.Timeout:
        logger.error("Request to llamacpp-server timed out")
        raise HTTPException(status_code=504, detail="Request to llamacpp-server timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException: {e}")
        raise HTTPException(status_code=500, detail="Service unavailable or request failed")
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"JSONDecodeError: {e}")
        raise HTTPException(status_code=502, detail="Invalid JSON response from llamacpp-server")

    
@app.post("/diary")
def ask_llama(chat: Chat):
    try:
        logger.debug(f"Get Request from frontend: {chat.messages}")
        chat.messages.append({"role": "User", "text": "以上の会話の内容を踏まえ，Userが今日一日で取り組んだことを日記の形式にしてまとめてください．"})
        response = requests.post(
            "http://llamacpp-server:3300/completion",
            headers={"Content-Type": "application/json"},
            json={"prompt": str(chat.messages), "n_predict": 180},
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