import './App.css';
import { useState, useEffect } from 'react';

function App() {
  const [inputText, setInputText] = useState('');
  const [isDisabled, setIsDisabled] = useState(false);

  useEffect(() => {
    // ページ読み込み時にinputにフォーカスを当てる
    document.getElementById('input').focus();
  }, []);

  const extractMessages = () => {
    const chatElement = document.querySelector('.chat');
    const messages = [];
    chatElement.querySelectorAll('.input, .output').forEach(element => {
      messages.push({
        role: element.className === 'input' ? 'User' : 'Assistant',
        text: element.textContent
      });
    });
    return messages;
  };

  const handleChatButtonClick = async (event) => {
    event.preventDefault(); // フォームのデフォルトの送信動作を防ぐ
    setIsDisabled(true);

    // inputとbuttonを使えなくする
    const inputElement = document.getElementById('input');
    const buttonElement = document.getElementById('button');
    inputElement.disabled = true;
    buttonElement.disabled = true;

    // inputの文字を取り出して、chatにclass=inputのdivを作成
    const chatElement = document.querySelector('.chat');
    const newInputDiv = document.createElement('div');
    newInputDiv.className = 'input';
    newInputDiv.textContent = inputText;
    chatElement.insertBefore(newInputDiv, chatElement.querySelector('button'));

    // inputの文字を消す
    setInputText('');

    // chatクラスの中のinputとoutputクラスをすべて結合してmessagesを作成
    const messages = extractMessages();

    // localhost/chatにPOSTリクエストを送信
    const response = await fetch('http://localhost/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ messages }),
    });

    const result = await response.json();

    // chatにclass=outputのdivを作成して、その中にあるtextContentをサーバーからの回答にする
    const newOutputDiv = document.createElement('div');
    newOutputDiv.className = 'output';
    newOutputDiv.textContent = result.extracted_text; // サーバーからの回答を設定
    chatElement.insertBefore(newOutputDiv, chatElement.querySelector('button'));

    // inputとbuttonを使えるようにする
    inputElement.disabled = false;
    buttonElement.disabled = false;
    setIsDisabled(false);

    // 回答が返ってきたときにinputにフォーカスを当てる
    inputElement.focus();

    // 日記生成ボタンを表示する
    const diaryButton = chatElement.querySelector('button');
    diaryButton.style.display = 'block';
  };

  const handleDiaryButtonClick = async () => {
    // formを消す
    const formElement = document.querySelector('.form');
    formElement.style.display = 'none';

    // 日記生成ボタンを消す
    const diaryButton = document.querySelector('.chat button');
    diaryButton.style.display = 'none';

    // chatクラスの中のinputとoutputクラスをすべて結合してmessagesを作成
    const chatElement = document.querySelector('.chat');
    const messages = extractMessages();

    // localhost/diaryにPOSTリクエストを送信
    const response = await fetch('http://localhost/diary', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ messages }),
    });

    const result = await response.json();

    // chatにdivを生成、中にh2とpを作成
    const diaryDiv = document.createElement('div');
    diaryDiv.className = 'diary';

    const diaryTitle = document.createElement('h2');
    const today = new Date();
    const formattedDate = `${today.getFullYear()}年${String(today.getMonth() + 1).padStart(2, '0')}月${String(today.getDate()).padStart(2, '0')}日`;
    diaryTitle.textContent = formattedDate;

    const diaryContent = document.createElement('p');
    diaryContent.innerHTML = result.content; // サーバーからの回答を設定

    diaryDiv.appendChild(diaryTitle);
    diaryDiv.appendChild(diaryContent);
    chatElement.appendChild(diaryDiv);

    // ダウンロードリンクを作成してクリック
    const downloadLink = document.createElement('a');
    const diaryText = diaryContent.innerHTML.replace(/<br>/g, '\n'); // <br>を改行に変換
    const blob = new Blob([diaryText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    downloadLink.href = url;
    downloadLink.download = `${formattedDate}.txt`;
    downloadLink.click();
    URL.revokeObjectURL(url); // メモリを解放
  };

  return (
    <div className="App">
      <header>
        ポジレコ
      </header>
      <div className="chat">
        <button onClick={handleDiaryButtonClick}>
          日記生成
        </button>
      </div>
      <form className="form" onSubmit={handleChatButtonClick}>
        <input
          id="input"
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={isDisabled}
          autoComplete="off" // 自動補完を無効化
        />
        <button id="button" type="submit" disabled={isDisabled}></button>
      </form>
    </div>
  );
}

export default App;