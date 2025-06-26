document.addEventListener('DOMContentLoaded', () => {
    // --- 1. DOM要素の取得 ---
    const chatBox = document.getElementById('chat-box');
    const optionsContainer = document.getElementById('options-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const loadingOverlay = document.getElementById('loading');
    const inputArea = document.getElementById('input-area');

    // --- 2. 定数・変数の設定 ---
    // FastAPIサーバーのアドレスに合わせてください
    const API_URL = 'http://127.0.0.1:8000'; 
    
    // 会話履歴を保存する配列
    let conversationHistory = [];

    // --- 3. ヘルパー関数 ---

    /**
     * ローディング表示を切り替える関数
     * @param {boolean} show 表示する場合はtrue
     */
    const toggleLoading = (show) => {
        loadingOverlay.classList.toggle('hidden', !show);
        inputArea.style.pointerEvents = show ? 'none' : 'auto';
        inputArea.style.opacity = show ? 0.5 : 1;
    };

    /**
     * 選択肢ボタンと入力欄を更新する関数
     * @param {string[]} options 選択肢のテキスト配列
     * @param {boolean} freeTextAllowed 自由入力を許可するか
     * @param {string} placeholder プレースホルダーのテキスト
     */
    const updateOptions = (options, freeTextAllowed, placeholder = 'または、自由に入力してください...') => {
        optionsContainer.innerHTML = '';
        if (options && options.length > 0) {
            options.forEach(optionText => {
                const button = document.createElement('button');
                button.classList.add('option-btn');
                button.textContent = optionText;
                button.addEventListener('click', () => {
                    sendMessage(optionText);
                });
                optionsContainer.appendChild(button);
            });
        }
        userInput.disabled = !freeTextAllowed;
        userInput.placeholder = freeTextAllowed ? placeholder : '今は選択肢からお選びください。';
    };

    /**
     * チャットボックスにメッセージを表示する関数
     * @param {('user'|'ai')} sender 送信者
     * @param {object|string} data 表示するデータ
     */
    const addMessage = (sender, data) => {
        // ★★★ エラーの原因を特定するためのデバッグコードです ★★★
        console.log("--- addMessageが受け取ったデータ（ここから） ---");
        console.log("送信者 (sender):", sender);
        console.log("データ (data) そのもの:", data);
        if (typeof data === 'object' && data !== null) {
            console.log("data.type:", data.type);
            console.log("data.menus:", data.menus);
            console.log("data.menus は配列か?:", Array.isArray(data.menus));
        } else {
            console.log("データはオブジェクトではありません:", data);
        }
        console.log("--- addMessageが受け取ったデータ（ここまで） ---");
        // ★★★ デバッグコードここまで ★★★

        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);

        if (sender === 'ai' && data.type === 'suggestion') {
            let html = `<strong>${data.message}</strong>`;
            
            // ★★★ data.menusが存在するかをチェックする修正 ★★★
            if (data.menus && Array.isArray(data.menus)) {
                data.menus.forEach((menu, index) => {
                    html += `
                        <div class="suggestion-card">
                            <h4>提案 ${index + 1}：${menu.reason}</h4>
                            <div class="menu-set">
                                <p><strong>主菜:</strong> ${menu.main_dish.name} - <small>${menu.main_dish.description}</small></p>
                                <p><strong>副菜:</strong> ${menu.side_dish.name} - <small>${menu.side_dish.description}</small></p>
                                <p><strong>汁物:</strong> ${menu.soup.name} - <small>${menu.soup.description}</small></p>
                            </div>
                        </div>
                    `;
                });
            }
            messageElement.innerHTML = html;
        } else if (sender === 'ai') {
            messageElement.textContent = data.message;
        } else {
            messageElement.textContent = data;
        }
        
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    /**
     * AIからの応答を処理する関数
     * @param {object} data バックエンドからのレスポンスデータ
     */
    const handleAiResponse = (data) => {
        const aiMessageForHistory = data.message || "AIからの応答です。";
        conversationHistory.push({ role: 'model', content: aiMessageForHistory });
    
        addMessage('ai', data);
    
        if (data.type === 'question') {
            // ★★★ ここから修正 ★★★
            // AIの応答に free_text_allowed が含まれていればその値を使い、
            // 含まれていなければデフォルトで true (許可) にする
            const allowFreeText = data.free_text_allowed !== false;
            updateOptions(data.options, allowFreeText);
            // ★★★ ここまで修正 ★★★
        } else if (data.type === 'suggestion') {
            updateOptions([], false, 'ありがとうございました！');
            userInput.disabled = true;
            sendBtn.disabled = true;
        }
    };


    // --- 4. メインの通信関数 ---

    /**
     * バックエンドにメッセージを送信する関数
     * @param {string} messageText ユーザーの入力メッセージ
     */
    const sendMessage = async (messageText) => {
        if (!messageText.trim()) return;

        addMessage('user', messageText);
        
        // ★★★ 会話履歴のキー名を'content'に統一する修正 ★★★
        conversationHistory.push({ role: 'user', content: messageText });
        
        userInput.value = '';
        updateOptions([], false);
        toggleLoading(true);

        try {
            const response = await fetch(`${API_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: messageText,
                    history: conversationHistory,
                }),
            });

            if (!response.ok) {
                // サーバーからのエラーレスポンスを処理
                const errorData = await response.json().catch(() => ({ detail: "サーバーからの応答がJSON形式ではありません。" }));
                throw new Error(`HTTP error! status: ${response.status}, message: ${JSON.stringify(errorData)}`);
            }

            const data = await response.json();
            handleAiResponse(data);

        } catch (error) {
            console.error('Error:', error);
            handleAiResponse({type: 'question', message: `申し訳ありません、通信エラーです。(${error.message})`, options: ['再試行']});
        } finally {
            toggleLoading(false);
        }
    };

    /**
     * 会話を始める関数
     */
    const startConversation = async () => {
        toggleLoading(true);
        try {
            const response = await fetch(`${API_URL}/start`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            handleAiResponse(data);
        } catch (error) {
            console.error('Error starting conversation:', error);
            addMessage('ai', {message: 'エージェントの起動に失敗しました。ページをリロードしてください。'});
        } finally {
            toggleLoading(false);
        }
    };

    // --- 5. イベントリスナーの設定 ---
    sendBtn.addEventListener('click', () => sendMessage(userInput.value));
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !userInput.disabled) {
            sendMessage(userInput.value);
        }
    });

    // --- 6. 初期実行 ---
    startConversation();
});