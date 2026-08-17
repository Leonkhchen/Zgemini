document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    // 王陽明經典語錄資料庫
    const wangQuotes = [
        "知是行之始，行是知之成。若會得時，只說一個知，已自有行在；只說一個行，已自有知在。",
        "心外無物，心外無事，心外無理，心外無義，心外無善。",
        "出辭氣，無暴慢。朋友交，無欺忌。",
        "致良知。你良知上覺得這事當做，便做去；覺得這事不當做，便不做去。",
        "種樹者必培其根，種德者必養其心。",
        "無善無惡心之體，有善有惡意之動，知善知惡是良知，為善去惡是格物。",
        "人胸中各有個聖人，只自信不及，都自埋倒了。",
        "謙虛其心，宏大其量。",
        "靜時念念去其昏僻，動時念念去其貪著。",
        "你未看此花時，此花與汝同歸於寂；你來看此花時，則此花顏色一時明白起來。便知此花不在你的心外。"
    ];

    // 關鍵字回應
    const keywords = {
        "煩惱": "人生大病，只是一「傲」字。你且把心靜下來，向內求索，良知自會指引你。",
        "迷惘": "立志用功，如種樹然。方其根芽，猶未有幹；及其有幹，尚未有枝；枝而後葉，葉而後花、實。初種根時，只管栽培灌溉，勿作枝想，勿作葉想，勿作花想，勿作實想。懸想何益？但不忘栽培之功，怕沒有枝葉花實？",
        "知道": "只說一個知，已自有行在。你若真知道了，便會去做；若不去做，那便是還不知道。",
        "做不到": "行之明覺精察處便是知，知之真切篤實處便是行。莫將知行作兩截看。",
        "心": "心之本體，原是明瑩無滯的，只為私慾引蔽，無明妄想，才昏蔽了。須是常常反省。",
        "理": "心即理也，天下又有心外之事，心外之理乎？",
        "你好": "吾友，近來用功如何？",
        "謝謝": "不必言謝，但求諸心而已。"
    };

    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        let innerHTML = '';
        if (type === 'received') {
            innerHTML = `
                <div class="avatar">陽明</div>
                <div class="message-content">
                    <p>${text}</p>
                </div>
            `;
        } else {
            innerHTML = `
                <div class="message-content">
                    <p>${text}</p>
                </div>
            `;
        }

        messageDiv.innerHTML = innerHTML;
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function generateResponse(userText) {
        let response = "";
        
        // 簡單的關鍵字匹配
        for (const [key, val] of Object.entries(keywords)) {
            if (userText.includes(key)) {
                response = val;
                break;
            }
        }

        // 如果沒有匹配到關鍵字，就隨機回覆一句經典語錄
        if (!response) {
            const randomIndex = Math.floor(Math.random() * wangQuotes.length);
            response = wangQuotes[randomIndex];
        }

        return response;
    }

    function handleSend() {
        const text = userInput.value.trim();
        if (text) {
            addMessage(text, 'sent');
            userInput.value = '';
            userInput.focus();

            // 模擬思考延遲
            setTimeout(() => {
                const reply = generateResponse(text);
                addMessage(reply, 'received');
            }, 800 + Math.random() * 1000); // 800ms - 1800ms delay
        }
    }

    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSend();
        }
    });
});
