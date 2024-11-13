# システムの概要
## backend
llamaとの対話を行うためのエンドポイントを実装したサーバーです．  
http://localhost/llama に対して以下のようなフォーマットのBodyを含んだリクエストを送るとllamaからの回答がjson形式で返ってきます．
```
{"prompt": "日本語で答えてください．アナタは誰ですか？ ","n_predict": 120}
```

## frontend
実装中

## modelの追加について
各々で使いたい言語モデルを追加してから使用して下さい．
以下に手順をまとめます．

- ルートディレクトリにmodelsフォルダを追加
- 追加したフォルダに任意のGGUF形式のモデルを配置(モデルはこの[リンク](https://huggingface.co/TheBloke)から探して下さい)
- docker-compose.ymlのLLAMA_ARG_MODELとcommandのモデル名を自分が追加したモデル名に変更

## 起動方法
- ルートディレクトリに移動
- Docker Desktopを立ち上げた状態で以下のコマンドを実行
```
docker-compose up -d
```
