# システムの概要
Dockerにより以下の3つのコンテナを立ち上げ，マイクロサービスとしてそれぞれ稼働させる
## llamacpp-server
Promptを受け取り，内容に応じて自然言語で回答を返す 
LLMの機能のみを持つLLMサーバー
## backend
フロントエンドからユーザーの入力を受け取り， Promptの加工をしてllamacpp-serverにリクエストを送る 
フロントエンドとLLMサーバーの仲介役となるバックエンドサーバー
## frontend
チャットアプリのようなUIでユーザーの入力を受け取り，LLMによる回答を表示する 
ユーザー側に表示されるコンテンツを配信するフロントエンドサーバー


# 動作方法
## modelの追加
各々で使いたい言語モデルを追加してから使用して下さい．
以下に手順をまとめます．

- ルートディレクトリにmodelsフォルダを追加
- 追加したmodelsフォルダに任意のGGUF形式のモデルを配置(モデルはこの[リンク](https://huggingface.co/TheBloke)から探して下さい)
- .envのMODEL_NAMEをダウンロードしたモデル名に変更
## 起動方法
- ルートディレクトリに移動
- Docker Desktopを立ち上げた状態で以下のコマンドを実行
```
docker-compose up -d
```

## 動作確認

### フロントエンド
以下のリンクにアクセス
```
http://localhost:3000/
```

### バックエンド
http://localhost/llama に対して以下のようなフォーマットのBodyを含んだPOSTリクエストを送るとllamaからの回答がjson形式で返ってきます．
```
{"prompt": "日本語で答えてください．アナタは誰ですか？ ","n_predict": 120}
```
# リポジトリのリンク
1月に完成することを目標に開発中です．
以下のリンクから最新の状態をご確認いただくことができます．
[https://github.com/eREDROCK/Positive_Record](https://github.com/eREDROCK/Positive_Record)
