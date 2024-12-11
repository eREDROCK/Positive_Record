import './App.css';
import { useState, useEffect } from 'react';

function App() {
  const [inputText, setInputText] = useState('');
  const [isDisabled, setIsDisabled] = useState(false);
  const [mode, setMode] = useState('Boss'); // 初期値を設定

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

    // ローディング要素を追加
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'left-loading';
    loadingDiv.innerHTML = '<div class="loader"></div>';
    chatElement.insertBefore(loadingDiv, chatElement.querySelector('button'));

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
      body: JSON.stringify({ messages, mode }), // modeを追加
    });

    const result = await response.json();

    // ローディング要素を削除
    chatElement.removeChild(loadingDiv);

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

  const handleDiaryButtonClick = () => {
    // formを消す
    const formElement = document.querySelector('.form');
    formElement.style.display = 'none';

    // 日記生成ボタンを消す
    const diaryButton = document.querySelector('.chat button');
    diaryButton.style.display = 'none';

    // chat内に要素を作成
    const chatElement = document.querySelector('.chat');
    chatElement.innerHTML = ''; // 既存の内容をクリア

    const diaryDiv = document.createElement('div');
    diaryDiv.className = 'diary';

    const dateHeader = document.createElement('h1');
    const today = new Date();
    const formattedDate = `${today.getFullYear()}年${today.getMonth() + 1}月${today.getDate()}日の日記`;
    dateHeader.textContent = formattedDate;
    diaryDiv.appendChild(dateHeader);

    const todayHeader = document.createElement('h2');
    todayHeader.textContent = 'きょうやったこと';
    diaryDiv.appendChild(todayHeader);

    const loading1 = document.createElement('div');
    loading1.className = 'center-loading';
    loading1.innerHTML = '<div class="loader"></div>'; // 中身を変更
    diaryDiv.appendChild(loading1);

    const reviewHeader = document.createElement('h2');
    reviewHeader.textContent = 'ふりかえり';
    diaryDiv.appendChild(reviewHeader);

    const loading2 = document.createElement('div');
    loading2.className = 'center-loading';
    loading2.innerHTML = '<div class="loader"></div>'; // 中身を変更
    diaryDiv.appendChild(loading2);

    chatElement.appendChild(diaryDiv);

    // messagesとmodeのオブジェクトを作成
    const messages = extractMessages();
    const requestBody = { messages, mode };

    // userDiaryにPOSTリクエストを送信
    fetch('http://localhost/userDiary', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody),
    })
      .then(response => response.json())
      .then(userDiaryResult => {
        // ローディング1のclassを消して、text-contentを結果.user_diaryの文字列を反映
        loading1.classList.remove('center-loading');
        loading1.textContent = userDiaryResult.user_diary;
      });

    // LLMReviewにPOSTリクエストを送信
    fetch('http://localhost/LLMReview', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody),
    })
      .then(response => response.json())
      .then(llmReviewResult => {
        // ローディング2のclassを消して、text-contentをllm_reviewの文字列を反映
        loading2.classList.remove('center-loading');
        loading2.textContent = llmReviewResult.llm_review;
      });
  };

  return (
    <div className="App">
      <header>
        <h1>
          ポジレコ
        </h1>
        <div>
          モード：
          <select className="mode-dropdown" value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="Boss">上司</option>
            <option value="Friend">親友</option>
            <option value="Commander">指揮官</option>
            <option value="Lady">お嬢様</option>
          </select>
        </div>
      </header>
      <div className='chatHeader'>
        今日の出来事を話してみましょう！
      </div>
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