import streamlit as st
from gtts import gTTS
import io
import base64
import os
import random
# 💡音声録音用のライブラリをインポート
from streamlit_mic_recorder import speech_to_text

# --- 1. アプリの基本設定 ---
st.set_page_config(
    page_title="La Café - English Roleplay", 
    page_icon="☕",
    layout="wide"
)

# --- 2. 画像の読み込みと変換 ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

bg_path = "images/bg.jpg"       
staff_normal_path = "images/staff.png" 
staff_happy_path = "images/staff_happy.png" 

item_images = {
    "coffee": "images/coffee.png",
    "latte": "images/latte.png",
    "tea": "images/tea.png",
    "cookie": "images/cookie.png"
}

bg_base64 = get_image_base64(bg_path)
staff_normal_base = get_image_base64(staff_normal_path)
staff_happy_base = get_image_base64(staff_happy_path) if os.path.exists(staff_happy_path) else staff_normal_base

bg_style = f"background-image: url('data:image/jpeg;base64,{bg_base64}');" if bg_base64 else "background-color: #2b1c11;"

# --- お掃除フィルター (防止ブロック) ---
def clean_html(raw_html):
    import re
    # 連続する半角スペースを1つに縮める (コードブロック誤認防止)
    cleaned = re.sub(r' +', ' ', raw_html)
    return cleaned

# --- 3. デザインCSS ---
st.markdown(clean_html(f"""
    <style>
    .stApp {{
        {bg_style}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .block-container {{
        background-color: rgba(0, 0, 0, 0.15); 
        padding: 1rem !important;
    }}
    .game-title {{
        color: #ffffff;
        text-align: center;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 2.2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        margin-bottom: 10px;
    }}
    .character-stage {{
        display: flex;
        justify-content: center;
        align-items: flex-end;
        height: 480px; 
        margin-bottom: 15px;
        position: relative;
        overflow: hidden; 
    }}
    .npc-large-img {{
        max-height: 110%; 
        width: auto;
        object-fit: contain;
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.5));
        animation: subtleFloat 3s infinite ease-in-out;
        position: relative;
        bottom: -40px; 
        z-index: 5;
    }}
    /* ドリンクとクッキーの演出 */
    .drink-present {{
        position: absolute;
        bottom: 10px; 
        right: 20%; 
        width: 150px; 
        height: 150px;
        object-fit: contain;
        z-index: 10; 
        filter: drop-shadow(0px 12px 18px rgba(0,0,0,0.6));
        animation: popIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }}
    .cookie-present {{
        position: absolute;
        bottom: 10px; 
        right: 32%; 
        width: 120px; 
        height: 120px;
        object-fit: contain;
        z-index: 11; 
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.6));
        animation: popIn 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }}
    @keyframes popIn {{
        0% {{ transform: scale(0) rotate(-15deg); opacity: 0; }}
        100% {{ transform: scale(1) rotate(0deg); opacity: 1; }}
    }}
    @keyframes subtleFloat {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-8px); }}
    }}
    /* セリフウィンドウ */
    .speech-window {{
        background: rgba(26, 15, 8, 0.92); 
        border: 3px solid #d7c49e;
        border-radius: 12px;
        padding: 18px 25px;
        color: #ffffff;
        font-size: 1.4rem;
        font-weight: bold;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        margin-bottom: 15px;
        min-height: 110px;
    }}
    .speech-sub-jp {{
        font-size: 0.9rem;
        color: #bfaaa0;
        font-weight: normal;
        margin-top: 8px;
        border-top: 1px dashed rgba(215, 196, 158, 0.3);
        padding-top: 6px;
    }}
    /* レシートメモ */
    .receipt-memo {{
        background-color: #fffef0;
        border-left: 3px dashed #ccc;
        border-right: 3px dashed #ccc;
        border-top: 1px solid #ccc;
        border-bottom: 1px solid #ccc;
        padding: 15px;
        color: #333333;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1rem;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        margin-top: 15px;
        line-height: 1.4;
    }}
    .receipt-header {{
        text-align: center;
        font-weight: bold;
        font-size: 1.1rem;
        border-bottom: 1px dashed #333;
        margin-bottom: 10px;
        padding-bottom: 5px;
    }}
    .receipt-item {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
    }}
    .receipt-total {{
        border-top: 1px dashed #333;
        margin-top: 10px;
        padding-top: 5px;
        font-weight: bold;
        display: flex;
        justify-content: space-between;
    }}
    /* キラキラ・スターシャワー演出 (防止済み) */
    .star-shower {{
        position: absolute;
        top: -20px;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 100;
        pointer-events: none;
        overflow: hidden;
    }}
    .star {{
        position: absolute;
        top: -20px;
        font-size: 30px;
        animation: starFall 1.5s linear forwards;
    }}
    @keyframes starFall {{
        0% {{ transform: translateY(-20px) rotate(0deg); opacity: 0; }}
        10% {{ transform: translateY(0px) rotate(30deg); opacity: 1; }}
        80% {{ opacity: 1; }}
        100% {{ transform: translateY(110vh) rotate(360deg); opacity: 0; }}
    }}
    /* マイクコンテナと波形エフェクト */
    .mic-container {{
        background: rgba(255, 255, 255, 0.08);
        border: 2px dashed rgba(215, 196, 158, 0.6);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 15px;
    }}
    .equalizer-wave {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: 30px;
        gap: 5px;
        margin: 10px 0;
    }}
    .wave-bar {{
        width: 6px;
        height: 100%;
        background-color: #ffd700;
        border-radius: 3px;
        animation: waveAnim 1.2s ease-in-out infinite;
    }}
    .wave-bar:nth-child(2) {{ animation-delay: 0.1s; background-color: #ffb700; }}
    .wave-bar:nth-child(3) {{ animation-delay: 0.2s; background-color: #ff9900; }}
    .wave-bar:nth-child(4) {{ animation-delay: 0.3s; background-color: #ffb700; }}
    .wave-bar:nth-child(5) {{ animation-delay: 0.4s; background-color: #ffd700; }}
    @keyframes waveAnim {{
        0%, 100% {{ transform: scaleY(0.4); }}
        50% {{ transform: scaleY(1.0); }}
    }}
    /* 発音バッジ・お断りバッジ */
    .pronunciation-badge-container {{
        margin-top: 10px;
        background: rgba(43, 28, 17, 0.95);
        border: 2px solid #8b5a2b;
        border-radius: 10px;
        padding: 12px;
        text-align: left;
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    .badge-icon-perfect {{ font-size: 35px; color: #ffd700; animation: badgePop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
    .badge-icon-good {{ font-size: 35px; color: #50c878; animation: badgePop 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
    .badge-label {{ color: #d7c49e; font-size: 0.85rem; font-family: monospace; }}
    .pron-perfect {{ color: #ffd700; font-weight: bold; font-size: 1.1rem; }}
    .pron-good {{ color: #50c878; font-weight: bold; font-size: 1.1rem; }}
    @keyframes badgePop {{ 0% {{ transform: scale(0); }} 100% {{ transform: scale(1); }} }}
    </style>
"""), unsafe_allow_html=True)

# --- 4. 初期状態の設定 ---
if "step" not in st.session_state:
    st.session_state.step = 1 # 1:Drink, 2:Hot/Iced, 3:Size, 4:CookieEvent, 5:Place, 6:Payment, 7:Complete
    st.session_state.current_npc_en = "Hello! Welcome to our cafe! What can I get for you today?"
    st.session_state.current_npc_jp = "いらっしゃいませ！何にいたしますか？"
    st.session_state.emotion = "normal" 
    st.session_state.speak_now = True
    st.session_state.play_again = False

    # 注文データ
    st.session_state.ordered_drink = None 
    st.session_state.drink_temp = None  
    st.session_state.ordered_size = None  
    st.session_state.ordered_cookie = False 
    st.session_state.ordered_place = None  
    st.session_state.ordered_payment = None 

    # ゲームイベント用
    st.session_state.has_cookie_event = False 
    st.session_state.sold_out_item = None # 売り切れアイテム
    st.session_state.block_next = False # 売り切れブロック判定

    # 🌟【修正】発音スコア表示を確実にする
    st.session_state.pronunciation_status = None 
    st.session_state.p_heard_text = ""
    st.session_state.p_matched_keyword = ""

# --- 5. サイドバー設定 ---
st.sidebar.markdown("### ⚙️ Game Settings")
speed_option = st.sidebar.select_slider("🔊 Voice Speed (話す速さ)", options=["Slow (ゆっくり)", "Normal (ふつう)", "Fast (はやく)"], value="Normal (ふつう)")
speed_map = {"Slow (ゆっくり)": 0.85, "Normal (ふつう)": 1.0, "Fast (はやく)": 1.15}
voice_speed = speed_map[speed_option]

voice_gender = st.sidebar.selectbox(
    "🗣️ Voice Type (声のタイプ)",
    ["Female (UK) - やさしいお姉さん", "Female (US) - 元気なお姉さん", "Male (US) - 渋いマスター"]
)
voice_map = {
    "Female (UK) - やさしいお姉さん": {"lang": "en", "tld": "co.uk"},
    "Female (US) - 元気なお姉さん": {"lang": "en", "tld": "com"},
    "Male (US) - 渋いマスター": {"lang": "en", "tld": "com"} 
}
selected_voice = voice_map[voice_gender]

# 💡Lo-FiのBGMを追加
bgm_url = "https://archive.org/download/lofi-hiphop-cozy-vibes/Lo-Fi%20Hiphop%20-%20Cozy%20Vibes.mp3"
st.sidebar.audio(bgm_url, format="audio/mp3", loop=True)

st.sidebar.markdown(clean_html("""
<div class="menu-board">
    <div class="menu-title">☕️ CAFE MENU ☕️</div>
    💡 <b>DRINKS</b><br>
    ・Coffee ($3.50)<br>
    ・Latte ($3.50)<br>
    ・Tea ($3.50)<br>
    <br>
    🍪 <b>TODAY'S SWEETS</b><br>
    ・Chocolate Chip Cookie ($1.50)<br>
    <br>
    💡 <b>SIZE</b><br>
    ・Small / Medium / Large<br>
    <br>
    💡 <b>TEMP</b><br>
    ・Hot (温かい) / Iced (冷たい)<br>
    <br>
    💡 <b>PLACE</b><br>
    ・For here (店内) / To go (持ち帰り)<br>
    <br>
    💡 <b>PAYMENT</b><br>
    ・Cash (現金) / Card (カード)
</div>
"""), unsafe_allow_html=True)


# --- 6. 画面描画 ---
st.markdown("<p class='game-title'>La Café English Roleplay</p>", unsafe_allow_html=True)

main_col, visual_col = st.columns([1.1, 0.9])

with visual_col:
    active_staff_base = staff_happy_base if st.session_state.emotion == "happy" else staff_normal_base
    staff_html = f'<img class="npc-large-img" src="data:image/png;base64,{active_staff_base}">' if active_staff_base else '<div style="font-size:120px; text-align:center;">👩‍🍳</div>'

    # キラキラ・スターシャワー (修正済み)
    star_shower_html = ""
    if st.session_state.emotion == "happy":
        star_shower_html = clean_html(f"""
        <div class="star-shower">
            <span class="star" style="left: 10vw;">🌟</span>
            <span class="star" style="left: 25vw;">✨</span>
            <span class="star" style="left: 45vw;">🌟</span>
            <span class="star" style="left: 60vw;">💫</span>
            <span class="star" style="left: 75vw;">🌟</span>
            <span class="star" style="left: 90vw;">✨</span>
        </div>
        """)

    # 完成品のドリンクとクッキー
    drink_html = ""
    cookie_html = ""
    if st.session_state.step == 7: # 完成ステップ
        if st.session_state.ordered_drink:
            drink_type = st.session_state.ordered_drink
            local_drink_path = item_images.get(drink_type, "")
            if os.path.exists(local_drink_path):
                drink_base64 = get_image_base64(local_drink_path)
                drink_html = f'<img class="drink-present" src="data:image/png;base64,{drink_base64}">'
        if st.session_state.ordered_cookie:
            cookie_path = item_images.get("cookie", "")
            if os.path.exists(cookie_path):
                cookie_base64 = get_image_base64(cookie_path)
                cookie_html = f'<img class="cookie-present" src="data:image/png;base64,{cookie_base64}">'

    # ステージ描画
    st.markdown(clean_html(f"""
    <div class="character-stage">
        {staff_html}
        {drink_html}
        {cookie_html}
        {star_shower_html}
    </div>
    """), unsafe_allow_html=True)

    # リアルタイム注文メモ
    item_p = 3.50 if st.session_state.ordered_drink else 0.0
    cook_p = 1.50 if st.session_state.ordered_cookie else 0.0
    total_p = item_p + cook_p
    drink_disp = st.session_state.ordered_drink.capitalize() if st.session_state.ordered_drink else "---"
    temp_disp = st.session_state.drink_temp.capitalize() if st.session_state.drink_temp else "---"
    size_disp = st.session_state.ordered_size.capitalize() if st.session_state.ordered_size else "---"
    cookie_disp = "Chocolate Cookie" if st.session_state.ordered_cookie else "---"
    place_disp = "For Here" if st.session_state.ordered_place == "here" else ("To Go" if st.session_state.ordered_place == "go" else "---")
    payment_disp = st.session_state.ordered_payment.capitalize() if st.session_state.ordered_payment else "---"
    st.markdown(clean_html(f"""
    <div class="receipt-memo">
        <div class="receipt-header">📋 ORDER MEMO (レシート)</div>
        <div class="receipt-item"><span>🥤 Item:</span> <span>{drink_disp}</span></div>
        <div class="receipt-item"><span>🔥 Temp:</span> <span>{temp_disp}</span></div>
        <div class="receipt-item"><span>📏 Size:</span> <span>{size_disp}</span></div>
        <div class="receipt-item"><span>🍪 Sweet:</span> <span>{cookie_disp}</span></div>
        <div class="receipt-item"><span>🏠 Place:</span> <span>{place_disp}</span></div>
        <div class="receipt-item"><span>💳 Pay:</span> <span>{payment_disp}</span></div>
        <div class="receipt-total"><span>💰 TOTAL:</span> <span>${total_p:.2f}</span></div>
    </div>
    """), unsafe_allow_html=True)

with main_col:
    # 💡gTTSで音声合成＆オートプレイ
    def play_audio(text, speed, voice_cfg):
        try:
            tts = gTTS(text=text, lang=voice_cfg["lang"], tld=voice_cfg["tld"], slow=False)
            if speed < 0.9: tts = gTTS(text=text, lang=voice_cfg["lang"], tld=voice_cfg["tld"], slow=True)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            md = f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
        except:
            pass

    # 必要なときだけ音声を再生
    if st.session_state.speak_now:
        play_audio(st.session_state.current_npc_en, voice_speed, selected_voice)
        st.session_state.speak_now = False

    window_html = clean_html(f"""
    <div class="speech-window">
        <div>{st.session_state.current_npc_en}</div>
        <div class="speech-sub-jp">{st.session_state.current_npc_jp}</div>
    </div>
    """)
    st.markdown(window_html, unsafe_allow_html=True)

    # --- 7. 音声入力とボタン操作 (修正の中心) ---
    user_choice = None
    final_mic_input = None

    # [機能B] AIの優しい耳・発音補正 (あいまい判定)
    # 特定の単語の聞き取り間違いを優しくカバーする。
    def fuzzy_match(input_text, keyword_list, fuzzy_rules=None):
        text = input_text.lower()
        matched = None
        exact_hit = False

        # 1. 完全一致の確認
        for k in keyword_list:
            if k in text:
                matched = k
                exact_hit = True
                break
        
        # 2. 完全一致がなかった場合、あいまい補正ルールを確認
        if not exact_hit and fuzzy_rules:
            for k, mistakes in fuzzy_rules.items():
                for mistake in mistakes:
                    if mistake in text:
                        matched = k
                        exact_hit = False # 補正による一致
                        break
                if matched: break
        
        # 🌟【修正】発音スコア表示を session_state に保存して競合に勝つ
        if matched:
            st.session_state.p_heard_text = f'"{text}"'
            st.session_state.p_matched_keyword = f'"{matched.capitalize()}"'
            st.session_state.pronunciation_status = "perfect" if exact_hit else "good"
            
        return matched

    # 音声・ボタン入力ブロック
    if st.session_state.step < 7:
        
        # [機能A] 音声波形アニメーションマイク
        # 録音ボタンの周りにピコピコ動く波形エフェクトを追加
        st.markdown('<div class="mic-container">', unsafe_allow_html=True)
        st.markdown("<p style='color:#ffd700; font-weight:bold; margin-bottom:5px;'>🎤 声でしゃべって注文してみよう！ (英語)</p>", unsafe_allow_html=True)
        st.markdown(clean_html("""
            <div class="equalizer-wave">
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
            </div>
        """), unsafe_allow_html=True)
        
        # ブラウザのマイクから音声を取得し、en-USとしてリアルタイムテキスト化
        mic_input = speech_to_text(
            start_prompt="🔴 録音スタート (おしてしゃべる)",
            stop_prompt="⏹️ 録音おわり",
            language='en-US',
            use_container_width=True,
            key=f'speech_{st.session_state.step}' # ステップごとにキーをユニーク化
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # 🌟【修正】発音バッジ・競合防止の表示
        if st.session_state.pronunciation_status:
            icon = "🌟 Perfect Pronunciation!" if st.session_state.pronunciation_status == "perfect" else "👍 Good Try! (伝わったよ！)"
            i_class = "pron-perfect" if st.session_state.pronunciation_status == "perfect" else "pron-good"
            st.markdown(clean_html(f"""
                <div class="pronunciation-badge-container">
                    <div class="badge-icon-{"perfect" if st.session_state.pronunciation_status == "perfect" else "good"}">{"🏆" if st.session_state.pronunciation_status == "perfect" else "🎖️"}</div>
                    <div>
                        <div class="badge-label">🗣️ あなたの声: {st.session_state.p_heard_text} ➡️ お店の人の解釈: {st.session_state.p_matched_keyword}</div>
                        <div class="{i_class}">{icon}</div>
                    </div>
                </div>
            """), unsafe_allow_html=True)

        st.markdown("<p style='color:#fff; font-weight:bold; margin-bottom:5px;'>👇 または、ボタンか文字入力でもすすめられるよ！</p>", unsafe_allow_html=True)
        
        # --- ステップごとの入力判定 ---
        col1, col2, col3 = st.columns(3)
        keywords = []
        fuzzy_rules = None

        if st.session_state.step == 1:
            keywords = ["coffee", "latte", "tea"]
            with col1:
                is_so = st.session_state.sold_out_item == "coffee"
                lbl = "☕️ Coffee (Sold Out)" if is_so else "☕️ I'd like a coffee, please."
                if st.button(lbl, disabled=is_so, key='b_c'): user_choice = "Coffee, please."
            with col2:
                is_so = st.session_state.sold_out_item == "latte"
                lbl = "🥛 Latte (Sold Out)" if is_so else "🥛 A latte, please!"
                if st.button(lbl, disabled=is_so, key='b_l'): user_choice = "Latte, please."
            with col3:
                is_so = st.session_state.sold_out_item == "tea"
                lbl = "🍵 Tea (Sold Out)" if is_so else "🍵 Tea, please."
                if st.button(lbl, disabled=is_so, key='b_t'): user_choice = "Tea, please."

        elif st.session_state.step == 2:
            keywords = ["hot", "iced"]
            # [機能B] Hot/Iced の優しい耳補正
            fuzzy_rules = {
                "hot": ["thought", "hat", "heart", "pot"],
                "iced": ["ice", "eyes", "nice", "asked"]
            }
            with col1:
                if st.button("🔥 Hot, please!", key='b_h'): user_choice = "Hot, please."
            with col2:
                if st.button("❄️ Iced, please!", key='b_i'): user_choice = "Iced, please."

        elif st.session_state.step == 3:
            keywords = ["small", "medium", "large"]
            with col1:
                if st.button("🟢 Small, please.", key='b_s'): user_choice = "Small, please."
            with col2:
                if st.button("🟡 Medium, please.", key='b_m'): user_choice = "Medium, please."
            with col3:
                if st.button("🔴 Large, please.", key='b_lg'): user_choice = "Large, please."

        elif st.session_state.step == 4:
            keywords = ["yes", "no"]
            with col1:
                if st.button("🍪 Yes, please!", key='b_y'): user_choice = "Yes, please!"
            with col2:
                if st.button("❌ No, thank you.", key='b_n'): user_choice = "No, thank you."
                
        elif st.session_state.step == 5:
            keywords = ["here", "go"]
            with col1:
                if st.button("🏠 For here, please.", key='b_fh'): user_choice = "For here, please."
            with col2:
                if st.button("🛍️ To go, please.", key='b_tg'): user_choice = "To go, please."
                
        elif st.session_state.step == 6:
            keywords = ["cash", "card"]
            with col1:
                if st.button("💵 Cash, please.", key='b_ca'): user_choice = "Cash, please."
            with col2:
                if st.button("💳 By card, please.", key='b_cd'): user_choice = "By card, please."

        user_typed = st.chat_input("Or type your answer in English here...")
        
        # 💡優先順位：マイク入力 > ボタン選択 > タイピング
        raw_input_text = None
        if mic_input:
            raw_input_text = mic_input
        elif user_choice:
            raw_input_text = user_choice
        elif user_typed:
            raw_input_text = user_typed

        # 🌟【修正 中心】競合防止ゲートの導入
        # 一度処理したテキスト（Perfect判定されたもの）は `handled_text` に保存し、
        # 競合により一瞬戻るのを防ぐ
        if "prevent_overlap" not in st.session_state:
            st.session_state.prevent_overlap = {"step": 0, "text": ""}

        # 未処理の新しい入力がある場合のみ処理する
        if raw_input_text and (st.session_state.prevent_overlap["step"] != st.session_state.step or st.session_state.prevent_overlap["text"] != raw_input_text):
            
            # 優しい耳で判定
            matched_key = fuzzy_match(raw_input_text, keywords, fuzzy_rules)

            # 処理済みとして記録 (競合防止)
            st.session_state.prevent_overlap["step"] = st.session_state.step
            st.session_state.prevent_overlap["text"] = raw_input_text

            if matched_key:
                # [機能A] 正解シャワー演出のため、少し待機してからリロード
                import time
                time.sleep(1.2) # キラキラが見えるように
                st.session_state.pronunciation_status = None # バッジをリセット
                
                # --- ステップごとの処理 ---
                if st.session_state.step == 1:
                    if matched_key == st.session_state.sold_out_item:
                        st.session_state.current_npc_en = f"As I mentioned, we are sold out of {matched_key.capitalize()} today. Grrr! Could you choose another drink?"
                        st.session_state.current_npc_jp = f"さっき言ったとおり、今日は {matched_key.capitalize()} は売り切れちゃったの！Grrr! ほかのドリンクにしてくれる？"
                        st.session_state.emotion = "normal"
                    else:
                        st.session_state.ordered_drink = matched_key
                        st.session_state.current_npc_en = "Excellent choice! Hot or iced? How would you like your drink?"
                        st.session_state.current_npc_jp = "いいですね！ホット（hot）か、アイス（iced）どちらにしますか？"
                        st.session_state.emotion = "happy"
                        st.session_state.step = 2

                elif st.session_state.step == 2:
                    st.session_state.drink_temp = matched_key
                    st.session_state.current_npc_en = f"Got it, {matched_key.capitalize()}! Now, what size would you like? Small, medium, or large?"
                    st.session_state.current_npc_jp = f"はい、{matched_key.capitalize()}ですね！さて、サイズはどうしますか？"
                    st.session_state.step = 3
                
                elif st.session_state.step == 3:
                    st.session_state.ordered_size = matched_key
                    st.session_state.has_cookie_event = random.choice([True, False])
                    
                    if st.session_state.has_cookie_event:
                        st.session_state.current_npc_en = "Okay! By the way, would you like a chocolate chip cookie today? It goes great with your drink!"
                        st.session_state.current_npc_jp = "かしこまりました！ところで、今日はチョコチップクッキーもいかがですか？ドリンクにぴったりですよ！"
                        st.session_state.step = 4
                    else:
                        st.session_state.current_npc_en = "Okay! Is that for here or to go?"
                        st.session_state.current_npc_jp = "店内で召し上がりますか？それともお持ち帰りですか？"
                        st.session_state.step = 5

                elif st.session_state.step == 4:
                    if matched_key == "yes":
                        st.session_state.ordered_cookie = True
                        st.session_state.current_npc_en = "Thank you! I'll add a cookie to your order. Now, is that for here or to go?"
                        st.session_state.current_npc_jp = "ありがとうございます！クッキーを追加しますね。さて、店内で召し上がりますか？お持ち帰りですか？"
                    else:
                        st.session_state.ordered_cookie = False
                        st.session_state.current_npc_en = "No problem! Then, is that for here or to go?"
                        st.session_state.current_npc_jp = "かしこまりました！では、店内で召し上がりますか？お持ち帰りですか？"
                    st.session_state.step = 5

                elif st.session_state.step == 5:
                    cook_price = 1.50 if st.session_state.ordered_cookie else 0.0
                    total_price = 3.50 + cook_price
                    price_str = f"${total_price:.2f}"
                    st.session_state.ordered_place = matched_key
                    place_str_en = "for here" if matched_key == "here" else "to go"
                    place_str_jp = "店内で" if matched_key == "here" else "お持ち帰りで"
                    st.session_state.current_npc_en = f"Perfect, {place_str_en}! Your total is {price_str}. Cash or card?"
                    st.session_state.current_npc_jp = f"かしこまりました、{place_str_jp}ですね。合計で{price_str}です。お支払いは現金ですか、カードですか？"
                    st.session_state.step = 6

                elif st.session_state.step == 6:
                    st.session_state.ordered_payment = matched_key
                    c_msg = " and cookie" if st.session_state.ordered_cookie else ""
                    c_msg_jp = "とクッキー" if st.session_state.ordered_cookie else ""
                    p_msg_en = "cash" if matched_key == "cash" else "card"
                    p_msg_jp = "現金" if matched_key == "cash" else "カード"
                    
                    st.session_state.current_npc_en = f"Thank you so much! Here is your drink{c_msg}. Enjoy your time!"
                    st.session_state.current_npc_jp = f"ありがとうございました！{p_msg_jp}でのお会計ですね。ご注文のドリンク{c_msg_jp}です。ごゆっくりどうぞ！"
                    st.session_state.emotion = "happy"
                    st.session_state.step = 7 # 完成
                    st.session_state.play_again = True # 再プレイボタン表示へ

                st.session_state.speak_now = True
                st.rerun()

            else:
                # [機能A] 音声入力が失敗した場合の「もう一度チャレンジ」バッジ (防止済み)
                import time
                time.sleep(1.2) # バッジが見えるように
                st.session_state.pronunciation_status = None # バッジをリセット
                
                s_txt = f"you didn't mention an item"
                s_txt_jp = f"メニューから選んでみてくださいね。"
                if keywords:
                    s_txt = f"did you say {' or '.join([f"'{k}'" for k in keywords])}?"
                    s_txt_jp = f"{'か、'.join([f'{k}（{k}）' for k in keywords])}のどちらでしょうか？"
                    
                st.session_state.current_npc_en = f"Sorry, {s_txt}"
                st.session_state.current_npc_jp = f"すみません、{s_txt_jp}"
                st.session_state.emotion = "normal"
                st.session_state.speak_now = True
                st.rerun()

    else:
        # [Step 7] ゲーム完成
        st.balloons()
        st.success("🎉 Order Completed!")
        
        if st.button("Play Again (もういちど遊ぶ)", key='play_again'):
            # 状態を完全リセット
            keys_to_reset = ["step", "emotion", "ordered_drink", "drink_temp", "ordered_size", "ordered_cookie", "ordered_place", "ordered_payment", "has_cookie_event", "pronunciation_status", "p_heard_text", "p_matched_keyword", "prevent_overlap", "speak_now", "play_again"]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()