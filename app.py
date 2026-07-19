import streamlit as st
from gtts import gTTS
import io
import base64
import os
import random
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
    "cake": "images/cake.png",
    "sandwich": "images/sandwich.png"
}

# アップロードされたお札画像のパス
cash_images = {
    "5": "images/cash_5.png",
    "10": "images/cash_10.png",
    "20": "images/cash_20.png"
}

bg_base64 = get_image_base64(bg_path)
staff_normal_base = get_image_base64(staff_normal_path)
staff_happy_base = get_image_base64(staff_happy_path) if os.path.exists(staff_happy_path) else staff_normal_base
bg_style = f"background-image: url('data:image/jpeg;base64,{bg_base64}');" if bg_base64 else "background-color: #2b1c11;"

# --- 3. 新・リアル価格シミュレーター用の価格設定 ---
DRINK_PRICES = {
    "coffee": 5.00,
    "latte": 6.00,
    "tea": 5.50
}
TEMP_PRICES = {
    "hot": 0.00,
    "iced": 1.00
}
SIZE_PRICES = {
    "small": 0.00,
    "medium": 1.50,
    "large": 2.50
}
FOOD_PRICES = {
    "none": 0.00,
    "cake": 6.50,
    "sandwich": 8.50
}

# --- 4. デザインCSS ---
st.markdown(f"<style>.stApp {{{bg_style} background-size: cover; background-position: center; background-attachment: fixed;}}</style>", unsafe_allow_html=True)

st.markdown("""<style>
/* 全体のレイアウト調整 */
.block-container { background-color: rgba(0, 0, 0, 0.15); padding: 0.25rem !important; }
.game-title { color: #ffffff; text-align: center; font-family: 'Arial', sans-serif; font-size: 1.5rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); margin: 2px 0 5px 0; }

/* キャラクター＆プレゼントエリア */
.character-stage { display: flex; justify-content: center; align-items: flex-end; height: 180px; margin-bottom: 4px; position: relative; overflow: hidden; border-radius: 10px; background: rgba(0,0,0,0.2); }
.npc-large-img { max-height: 100%; width: auto; object-fit: contain; filter: drop-shadow(0px 8px 12px rgba(0,0,0,0.5)); animation: subtleFloat 3s infinite ease-in-out; position: relative; bottom: 0px; z-index: 5; }
.drink-present { position: absolute; bottom: 5px; right: 10%; width: 60px; height: 60px; object-fit: contain; z-index: 10; filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.6)); animation: popIn 0.6s ease forwards; }
.food-present { position: absolute; bottom: 5px; right: 25%; width: 55px; height: 55px; object-fit: contain; z-index: 11; filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.6)); animation: popIn 0.7s ease forwards; }
@keyframes popIn { 0% { transform: scale(0); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
@keyframes subtleFloat { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }

/* セリフウィンドウ */
.speech-window { background: rgba(26, 15, 8, 0.95); border: 2px solid #d7c49e; border-radius: 10px; padding: 8px 12px; color: #ffffff; font-size: 1.0rem; font-weight: bold; box-shadow: 0 4px 15px rgba(0,0,0,0.5); margin-bottom: 4px; min-height: 50px; }
.speech-sub-jp { font-size: 0.75rem; color: #bfaaa0; font-weight: normal; margin-top: 2px; border-top: 1px dashed rgba(215, 196, 158, 0.3); padding-top: 2px; }

/* リアルなレシート */
.receipt-memo { background-color: #fffef0; border-left: 2px dashed #ccc; border-right: 2px dashed #ccc; border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; padding: 4px 8px; color: #333333; font-family: monospace; font-size: 0.7rem; box-shadow: 0 4px 8px rgba(0,0,0,0.15); margin-top: 2px; margin-bottom: 4px; line-height: 1.2; }
.receipt-header { text-align: center; font-weight: bold; font-size: 0.75rem; border-bottom: 1px dashed #333; margin-bottom: 2px; padding-bottom: 1px; }
.receipt-item-container { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 3px; }
.receipt-item { font-size: 0.65rem; background: rgba(0,0,0,0.05); padding: 1px 4px; border-radius: 4px; }
.receipt-total { border-top: 1px dashed #333; margin-top: 2px; padding-top: 1px; font-weight: bold; font-size: 0.75rem; display: flex; justify-content: space-between; width: 100%; }

/* 音声マイク＆イコライザー */
.mic-container { background: rgba(255, 255, 255, 0.08); border: 2px dashed rgba(215, 196, 158, 0.6); padding: 6px; border-radius: 10px; text-align: center; margin-bottom: 4px; }
.equalizer-wave { display: flex; justify-content: center; align-items: center; height: 15px; gap: 4px; margin: 2px 0; }
.wave-bar { width: 4px; height: 100%; background-color: #ffd700; border-radius: 2px; animation: waveAnim 1.2s ease-in-out infinite; }
.wave-bar:nth-child(2) { animation-delay: 0.1s; background-color: #ffb700; }
.wave-bar:nth-child(3) { animation-delay: 0.2s; background-color: #ff9900; }
.wave-bar:nth-child(4) { animation-delay: 0.3s; background-color: #ffb700; }
.wave-bar:nth-child(5) { animation-delay: 0.4s; background-color: #ffd700; }
@keyframes waveAnim { 0%, 100% { transform: scaleY(0.4); } 50% { transform: scaleY(1.0); } }

/* 発音判定バッジ */
.pronunciation-badge-container { margin-top: 3px; margin-bottom: 3px; background: rgba(43, 28, 17, 0.95); border: 1.5px solid #8b5a2b; border-radius: 8px; padding: 6px; display: flex; align-items: center; gap: 6px; }
.badge-label { color: #d7c49e; font-size: 0.7rem; font-family: monospace; }
.pron-perfect { color: #ffd700; font-weight: bold; font-size: 0.8rem; }
.pron-good { color: #50c878; font-weight: bold; font-size: 0.8rem; }
.stButton button { padding: 4px 8px !important; font-size: 0.8rem !important; height: auto !important; min-height: 35px !important; }

/* お店スタンプカード */
.stamp-card-box { background: rgba(255, 255, 255, 0.95); border: 2px solid #ffb700; border-radius: 8px; padding: 6px; margin-top: 4px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.stamp-title { font-size: 0.75rem; font-weight: bold; color: #8b5a2b; margin-bottom: 3px; }
.stamp-grid { display: flex; justify-content: center; gap: 5px; flex-wrap: wrap; }
.stamp-slot { width: 24px; height: 24px; border-radius: 50%; border: 1.5px dashed #ccc; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; background: #fff; }
.stamp-active { border: 1.5px solid #ff4500; background: #ffe4e1; animation: stampPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
@keyframes stampPop { 0% { transform: scale(0) rotate(-30deg); } 100% { transform: scale(1) rotate(0deg); } }

/* デジタル会員証アワードカード */
.award-card { background: linear-gradient(135deg, #1a1a1a 0%, #3a3a3a 100%); border: 3px solid #ffd700; border-radius: 12px; padding: 15px; text-align: center; color: white; box-shadow: 0 10px 20px rgba(0,0,0,0.6); margin: 10px 0; position: relative; overflow: hidden; }
.award-title { font-size: 1.3rem; font-weight: bold; color: #ffd700; text-shadow: 0 2px 4px rgba(0,0,0,0.8); margin-bottom: 5px; }
.award-name { font-size: 1.1rem; color: #ffffff; font-family: 'Courier New', monospace; margin: 5px 0; border-bottom: 1px dashed #ffd700; padding-bottom: 5px; }
.award-badge { font-size: 2.5rem; margin: 10px 0; animation: badgeGlow 2s infinite alternate; }
@keyframes badgeGlow { 0% { transform: scale(1); filter: drop-shadow(0 0 2px #ffd700); } 100% { transform: scale(1.05); filter: drop-shadow(0 0 10px #ffd700); } }

/* 🌟 メニュー提示用ビジュアルカード（画像をタップできなくし、見るだけのメニュー表に変更） */
.menu-display-card {
    background: rgba(255, 255, 255, 0.95);
    border: 2px solid #d7c49e;
    border-radius: 10px;
    padding: 8px;
    text-align: center;
    box-shadow: 0 3px 6px rgba(0,0,0,0.15);
    margin-bottom: 8px;
}
.menu-display-img {
    width: 100%;
    max-height: 85px;
    object-fit: contain;
    border-radius: 6px;
    margin-bottom: 4px;
}
.menu-display-label {
    font-size: 0.75rem;
    font-weight: bold;
    color: #4e3629;
}

/* 🌟 お札を直接タップ可能にする魔法のCSSオーバーレイ */
.cash-image-button-container {
    position: relative;
    width: 100%;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s ease, filter 0.3s ease;
    cursor: pointer;
    background: transparent;
}
.cash-image-button-container:hover {
    transform: translateY(-6px) scale(1.05);
    box-shadow: 0 10px 20px rgba(255, 215, 0, 0.4);
    filter: brightness(1.05);
}
.cash-bg-img {
    width: 100%;
    display: block;
    height: auto;
    object-fit: contain;
    border-radius: 10px;
}
.transparent-btn-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 10;
}
/* Streamlitボタンを完全に透明化して画像の上に引き伸ばす */
.transparent-btn-overlay div.stButton,
.transparent-btn-overlay div.stButton > button {
    width: 100% !important;
    height: 100% !important;
    background: transparent !important;
    border: none !important;
    color: transparent !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
}
.transparent-btn-overlay div.stButton > button:focus,
.transparent-btn-overlay div.stButton > button:active {
    background: transparent !important;
    color: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

/* お札が足りない時のグレーアウト表現 */
.cash-disabled-container {
    position: relative;
    width: 100%;
    border-radius: 10px;
    overflow: hidden;
    opacity: 0.3;
    filter: grayscale(100%);
    pointer-events: none;
    box-shadow: none;
}

/* お札未アップロード時の代替ボタンデザイン */
.cash-btn-box { background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); border: 2px solid #4caf50; border-radius: 8px; padding: 5px; text-align: center; box-shadow: 0 3px 6px rgba(0,0,0,0.15); font-weight: bold; color: #1b5e20; }
@media (max-width: 768px) { .character-stage { height: 150px !important; } }
</style>""", unsafe_allow_html=True)

# --- 5. 永続的なグローバル状態（スタンプ・お名前）の設定 ---
if "total_stamps" not in st.session_state:
    st.session_state.total_stamps = 0
if "kid_name" not in st.session_state:
    st.session_state.kid_name = "Guest"

# --- 6. ゲーム内会話状態の設定 ---
if "step" not in st.session_state:
    st.session_state.step = 1
    st.session_state.current_npc_en = "Hello! Welcome to our cafe! What can I get for you today?"
    st.session_state.current_npc_jp = "いらっしゃいませ！何にいたしますか？"
    st.session_state.emotion = "normal" 
    st.session_state.speak_now = True
    st.session_state.ordered_drink = None 
    st.session_state.drink_temp = None  
    st.session_state.ordered_size = None  
    st.session_state.ordered_food = None 
    st.session_state.ordered_place = None  
    st.session_state.ordered_payment_type = None 
    st.session_state.paid_amount = 0.0
    st.session_state.change_amount = 0.0
    st.session_state.has_food_event = False 
    st.session_state.pronunciation_status = None 
    st.session_state.p_heard_text = ""
    st.session_state.p_matched_keyword = ""
    st.session_state.stamp_processed = False

# --- 7. サイドバー設定 (お名前入力欄) ---
st.sidebar.markdown("### 👤カスタマー情報")
input_name = st.sidebar.text_input("お子さまのお名前 (英語)", value=st.session_state.kid_name)
if input_name:
    st.session_state.kid_name = input_name

st.sidebar.markdown("### ⚙️ Game Settings")
speed_option = st.sidebar.select_slider("🔊 Voice Speed", options=["Slow", "Normal", "Fast"], value="Normal")
speed_map = {"Slow": 0.85, "Normal": 1.0, "Fast": 1.15}
voice_speed = speed_map[speed_option]

voice_gender = st.sidebar.selectbox("🗣️ Voice Type", ["Female (UK)", "Female (US)", "Male (US)"])
voice_map = {"Female (UK)": {"lang": "en", "tld": "co.uk"}, "Female (US)": {"lang": "en", "tld": "com"}, "Male (US)": {"lang": "en", "tld": "com"}}
selected_voice = voice_map[voice_gender]

bgm_url = "https://archive.org/download/lofi-hiphop-cozy-vibes/Lo-Fi%20Hiphop%20-%20Cozy%20Vibes.mp3"
st.sidebar.audio(bgm_url, format="audio/mp3", loop=True)

# --- 8. 動的価格のリアルタイム計算 ---
drink_base_p = DRINK_PRICES.get(st.session_state.ordered_drink, 0.0) if st.session_state.ordered_drink else 0.0
temp_extra_p = TEMP_PRICES.get(st.session_state.drink_temp, 0.0) if st.session_state.drink_temp else 0.0
size_extra_p = SIZE_PRICES.get(st.session_state.ordered_size, 0.0) if st.session_state.ordered_size else 0.0
food_extra_p = FOOD_PRICES.get(st.session_state.ordered_food, 0.0) if st.session_state.ordered_food else 0.0

total_p = drink_base_p + temp_extra_p + size_extra_p + food_extra_p

# --- 9. 画面描画（左右カラムレイアウト） ---
st.markdown("<p class='game-title'>La Café English Roleplay</p>", unsafe_allow_html=True)

main_col, visual_col = st.columns([1.1, 0.9])

with visual_col:
    # 1. お姉さんステージ
    active_staff_base = staff_happy_base if st.session_state.emotion == "happy" else staff_normal_base
    staff_html = f'<img class="npc-large-img" src="data:image/png;base64,{active_staff_base}">' if active_staff_base else '<div style="font-size:60px; text-align:center;">👩‍🍳</div>'

    star_shower_html = ""
    if st.session_state.emotion == "happy":
        star_shower_html = "<div class='star-shower'><span class='star' style='left:10vw;'>🌟</span><span class='star' style='left:40vw;'>✨</span><span class='star' style='left:70vw;'>🌟</span></div>"

    drink_html = ""
    food_html = ""
    if st.session_state.step == 7: 
        if st.session_state.ordered_drink:
            local_drink_path = item_images.get(st.session_state.ordered_drink, "")
            if os.path.exists(local_drink_path):
                drink_html = f'<img class="drink-present" src="data:image/png;base64,{get_image_base64(local_drink_path)}">'
        if st.session_state.ordered_food and st.session_state.ordered_food != "none":
            local_food_path = item_images.get(st.session_state.ordered_food, "")
            if os.path.exists(local_food_path):
                food_html = f'<img class="food-present" src="data:image/png;base64,{get_image_base64(local_food_path)}">'

    st.markdown(f"<div class='character-stage'>{staff_html}{drink_html}{food_html}{star_shower_html}</div>", unsafe_allow_html=True)

    # 2. リアルタイム内訳・金額付きレシート表示
    drink_disp = f"{st.session_state.ordered_drink.capitalize()} (${drink_base_p:.2f})" if st.session_state.ordered_drink else "---"
    temp_disp = f"{st.session_state.drink_temp.capitalize()} (+${temp_extra_p:.2f})" if st.session_state.drink_temp else "---"
    size_disp = f"{st.session_state.ordered_size.capitalize()} (+${size_extra_p:.2f})" if st.session_state.ordered_size else "---"
    
    if st.session_state.ordered_food:
        if st.session_state.ordered_food == "none":
            food_disp = "No Food"
        else:
            food_disp = f"{st.session_state.ordered_food.capitalize()} (+${food_extra_p:.2f})"
    else:
        food_disp = "---"

    place_disp = "Here" if st.session_state.ordered_place == "here" else ("Go" if st.session_state.ordered_place == "go" else "---")
    payment_disp = st.session_state.ordered_payment_type.capitalize() if st.session_state.ordered_payment_type else "---"
    
    st.markdown(f"""
    <div class="receipt-memo">
        <div class="receipt-header">📋 {st.session_state.kid_name.upper()}'S ORDER STATUS</div>
        <div class="receipt-item-container">
            <div class="receipt-item">🥤 {drink_disp}</div>
            <div class="receipt-item">🔥 {temp_disp}</div>
            <div class="receipt-item">📏 {size_disp}</div>
            <div class="receipt-item">🍰 {food_disp}</div>
            <div class="receipt-item">🏠 {place_disp}</div>
            <div class="receipt-item">💳 {payment_disp}</div>
        </div>
        <div class="receipt-total"><span>💰 TOTAL:</span> <span>${total_p:.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 3. スタンプカード表示
    stamp_slots_html = ""
    for i in range(1, 11):
        if i <= st.session_state.total_stamps:
            stamp_slots_html += "<div class='stamp-slot stamp-active'>💮</div>"
        else:
            stamp_slots_html += f"<div class='stamp-slot'>{i}</div>"
            
    st.markdown(f"""
    <div class="stamp-card-box">
        <div class="stamp-title">💮 CAFE STAMP CARD (来店スタンプ)</div>
        <div class="stamp-grid">{stamp_slots_html}</div>
    </div>
    """, unsafe_allow_html=True)

with main_col:
    # 音声再生関数
    def play_audio(text, speed, voice_cfg):
        try:
            tts = gTTS(text=text, lang=voice_cfg["lang"], tld=voice_cfg["tld"], slow=False)
            if speed < 0.9: tts = gTTS(text=text, lang=voice_cfg["lang"], tld=voice_cfg["tld"], slow=True)
            fp = io.BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            b64 = base64.b64encode(fp.read()).decode()
            st.markdown(f'<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        except:
            pass

    if st.session_state.speak_now:
        play_audio(st.session_state.current_npc_en, voice_speed, selected_voice)
        st.session_state.speak_now = False

    # セリフウィンドウ
    st.markdown(f"<div class='speech-window'><div>{st.session_state.current_npc_en}</div><div class='speech-sub-jp'>{st.session_state.current_npc_jp}</div></div>", unsafe_allow_html=True)

    user_choice = None

    def fuzzy_match(input_text, keyword_list, fuzzy_rules=None):
        text = input_text.lower()
        matched = None
        exact_hit = False
        for k in keyword_list:
            if k in text:
                matched = k
                exact_hit = True
                break
        if not exact_hit and fuzzy_rules:
            for k, mistakes in fuzzy_rules.items():
                for mistake in mistakes:
                    if mistake in text:
                        matched = k
                        exact_hit = False 
                        break
                if matched: break
        if matched:
            st.session_state.p_heard_text = f'"{text}"'
            st.session_state.p_matched_keyword = f'"{matched.capitalize()}"'
            st.session_state.pronunciation_status = "perfect" if exact_hit else "good"
        return matched

    if st.session_state.step < 7:
        # マイクコンテナ
        st.markdown('<div class="mic-container">', unsafe_allow_html=True)
        st.markdown("<p style='color:#ffd700; font-weight:bold; margin-bottom:2px; font-size:0.85rem;'>🎤 声でしゃべって注文してみよう！ (英語)</p>", unsafe_allow_html=True)
        st.markdown("<div class='equalizer-wave'><div class='wave-bar'></div><div class='wave-bar'></div><div class='wave-bar'></div><div class='wave-bar'></div><div class='wave-bar'></div></div>", unsafe_allow_html=True)
        
        mic_input = speech_to_text(
            start_prompt="🔴 録音スタート (おしてしゃべる)",
            stop_prompt="⏹️ 録音おわり",
            language='en-US',
            use_container_width=True,
            key=f'speech_step_{st.session_state.step}' 
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.pronunciation_status:
            icon = "🌟 Perfect!" if st.session_state.pronunciation_status == "perfect" else "👍 Good Try!"
            i_class = "pron-perfect" if st.session_state.pronunciation_status == "perfect" else "pron-good"
            st.markdown(f"<div class='pronunciation-badge-container'><div class='badge-label'>🗣️ {st.session_state.p_heard_text} ➡️ 解釈: {st.session_state.p_matched_keyword}</div><div class='{i_class}'>{icon}</div></div>", unsafe_allow_html=True)

        st.markdown("<p style='color:#fff; font-weight:bold; margin-bottom:4px; font-size:0.8rem;'>👇 または英語フレーズを選んでボタンをおしてね！</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        keywords = []
        fuzzy_rules = None

        if st.session_state.step == 1:
            keywords = ["coffee", "latte", "tea"]
            
            # 1. コーヒー
            with col1:
                if os.path.exists(item_images["coffee"]):
                    b64_coffee = get_image_base64(item_images["coffee"])
                    st.markdown(f"""
                    <div class="menu-display-card">
                        <img src="data:image/png;base64,{b64_coffee}" class="menu-display-img">
                        <div class="menu-display-label">Coffee ($5.00)</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.button("☕️ Coffee, please.", key='btn_coffee_phrase', use_container_width=True)
                if st.session_state.get('btn_coffee_phrase'):
                    user_choice = "Coffee, please."
            
            # 2. ラテ
            with col2:
                if os.path.exists(item_images["latte"]):
                    b64_latte = get_image_base64(item_images["latte"])
                    st.markdown(f"""
                    <div class="menu-display-card">
                        <img src="data:image/png;base64,{b64_latte}" class="menu-display-img">
                        <div class="menu-display-label">Latte ($6.00)</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.button("🥛 Latte, please.", key='btn_latte_phrase', use_container_width=True)
                if st.session_state.get('btn_latte_phrase'):
                    user_choice = "Latte, please."
            
            # 3. 紅茶
            with col3:
                if os.path.exists(item_images["tea"]):
                    b64_tea = get_image_base64(item_images["tea"])
                    st.markdown(f"""
                    <div class="menu-display-card">
                        <img src="data:image/png;base64,{b64_tea}" class="menu-display-img">
                        <div class="menu-display-label">Tea ($5.50)</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.button("🍵 Tea, please.", key='btn_tea_phrase', use_container_width=True)
                if st.session_state.get('btn_tea_phrase'):
                    user_choice = "Tea, please."

        elif st.session_state.step == 2:
            keywords = ["hot", "iced"]
            fuzzy_rules = {"hot": ["thought", "hat", "heart", "pot"], "iced": ["ice", "eyes", "nice"]}
            with col1:
                if st.button("🔥 Hot, please. (+$0.00)", key='btn_hot', use_container_width=True): user_choice = "Hot, please."
            with col2:
                if st.button("❄️ Iced, please. (+$1.00)", key='btn_iced', use_container_width=True): user_choice = "Iced, please."

        elif st.session_state.step == 3:
            keywords = ["small", "medium", "large"]
            with col1:
                if st.button("🟢 Small, please. (+$0.00)", key='btn_small', use_container_width=True): user_choice = "Small, please."
            with col2:
                if st.button("🟡 Medium, please. (+$1.50)", key='btn_medium', use_container_width=True): user_choice = "Medium, please."
            with col3:
                if st.button("🔴 Large, please. (+$2.50)", key='btn_large', use_container_width=True): user_choice = "Large, please."

        elif st.session_state.step == 4:
            keywords = ["cake", "sandwich", "none"]
            fuzzy_rules = {"cake": ["chocolate cake", "sweet"], "sandwich": ["club sandwich", "bread"], "none": ["no food", "nothing", "no thanks"]}
            
            # 1. ケーキ
            with col1:
                if os.path.exists(item_images["cake"]):
                    b64_cake = get_image_base64(item_images["cake"])
                    st.markdown(f"""
                    <div class="menu-display-card">
                        <img src="data:image/png;base64,{b64_cake}" class="menu-display-img">
                        <div class="menu-display-label">Cake (+$6.50)</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.button("🍰 Cake, please.", key='btn_cake_phrase', use_container_width=True)
                if st.session_state.get('btn_cake_phrase'):
                    user_choice = "Chocolate cake, please."
            
            # 2. サンドイッチ
            with col2:
                if os.path.exists(item_images["sandwich"]):
                    b64_sandwich = get_image_base64(item_images["sandwich"])
                    st.markdown(f"""
                    <div class="menu-display-card">
                        <img src="data:image/png;base64,{b64_sandwich}" class="menu-display-img">
                        <div class="menu-display-label">Sandwich (+$8.50)</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.button("🥪 Sandwich, please.", key='btn_sandwich_phrase', use_container_width=True)
                if st.session_state.get('btn_sandwich_phrase'):
                    user_choice = "Sandwich, please."
            
            # 3. フードなし
            with col3:
                st.markdown(f"""
                <div class="menu-display-card" style="min-height: 122px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                    <div style="font-size: 1.8rem; margin-bottom: 3px;">❌</div>
                    <div class="menu-display-label">No Food</div>
                </div>
                """, unsafe_allow_html=True)
                st.button("No food, thank you.", key='btn_no_food_phrase', use_container_width=True)
                if st.session_state.get('btn_no_food_phrase'):
                    user_choice = "No food, thank you."
                
        elif st.session_state.step == 5:
            keywords = ["here", "go"]
            with col1:
                if st.button("🏠 For here, please.", key='btn_here', use_container_width=True): user_choice = "For here, please."
            with col2:
                if st.button("🛍️ To go, please.", key='btn_go', use_container_width=True): user_choice = "To go, please."
                
        elif st.session_state.step == 6:
            # --- 🌟 お札画像ボタンお会計システム (お札のみ直感タップ決済) ---
            keywords = ["5", "10", "20", "five", "ten", "twenty", "card"]
            fuzzy_rules = {"5": ["five dollars"], "10": ["ten dollars"], "20": ["twenty dollars"]}
            
            # --- 5ドル札の配置 ---
            with col1:
                if total_p <= 5.0:
                    if os.path.exists(cash_images["5"]):
                        b64_5 = get_image_base64(cash_images["5"])
                        st.markdown(f"""
                        <div class="cash-image-button-container">
                            <img src="data:image/png;base64,{b64_5}" class="cash-bg-img">
                            <div class="transparent-btn-overlay">
                        """, unsafe_allow_html=True)
                        if st.button("Pay $5.00", key='btn_pay_5_overlay', use_container_width=True): 
                            user_choice = "Here is 5 dollars."
                        st.markdown("</div></div>", unsafe_allow_html=True)
                    else:
                        if st.button("💵 Here is $5.00", key='btn_pay_5', use_container_width=True): 
                            user_choice = "Here is 5 dollars."
                else:
                    if os.path.exists(cash_images["5"]):
                        b64_5 = get_image_base64(cash_images["5"])
                        st.markdown(f"""
                        <div class="cash-disabled-container">
                            <img src="data:image/png;base64,{b64_5}" class="cash-bg-img">
                        </div>
                        <p style="color:#ff6b6b; text-align:center; font-size:0.65rem; margin:2px 0 0 0;">❌ 足りません</p>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='cash-btn-box' style='opacity:0.4; background:#ccc; border-color:#999; color:#666;'>❌ $5.00 (足りません)</div>", unsafe_allow_html=True)
            
            # --- 10ドル札の配置 ---
            with col2:
                if total_p <= 10.0:
                    if os.path.exists(cash_images["10"]):
                        b64_10 = get_image_base64(cash_images["10"])
                        st.markdown(f"""
                        <div class="cash-image-button-container">
                            <img src="data:image/png;base64,{b64_10}" class="cash-bg-img">
                            <div class="transparent-btn-overlay">
                        """, unsafe_allow_html=True)
                        if st.button("Pay $10.00", key='btn_pay_10_overlay', use_container_width=True): 
                            user_choice = "Here is 10 dollars."
                        st.markdown("</div></div>", unsafe_allow_html=True)
                    else:
                        if st.button("💵 Here is $10.00", key='btn_pay_10', use_container_width=True): 
                            user_choice = "Here is 10 dollars."
                else:
                    if os.path.exists(cash_images["10"]):
                        b64_10 = get_image_base64(cash_images["10"])
                        st.markdown(f"""
                        <div class="cash-disabled-container">
                            <img src="data:image/png;base64,{b64_10}" class="cash-bg-img">
                        </div>
                        <p style="color:#ff6b6b; text-align:center; font-size:0.65rem; margin:2px 0 0 0;">❌ 足りません</p>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='cash-btn-box' style='opacity:0.4; background:#ccc; border-color:#999; color:#666;'>❌ $10.00 (足りません)</div>", unsafe_allow_html=True)
            
            # --- 20ドル札の配置 ---
            with col3:
                if os.path.exists(cash_images["20"]):
                    b64_20 = get_image_base64(cash_images["20"])
                    st.markdown(f"""
                    <div class="cash-image-button-container">
                        <img src="data:image/png;base64,{b64_20}" class="cash-bg-img">
                        <div class="transparent-btn-overlay">
                    """, unsafe_allow_html=True)
                    if st.button("Pay $20.00", key='btn_pay_20_overlay', use_container_width=True): 
                        user_choice = "Here is 20 dollars."
                    st.markdown("</div></div>", unsafe_allow_html=True)
                else:
                    if st.button("💵 Here is $20.00", key='btn_pay_20', use_container_width=True): 
                        user_choice = "Here is 20 dollars."

            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            if st.button("💳 By card, please.", key='btn_pay_card_alt', use_container_width=True): 
                user_choice = "Card, please."

        user_typed = st.chat_input("Or type here...")
        
        raw_input_text = None
        if mic_input: raw_input_text = mic_input
        elif user_choice: raw_input_text = user_choice
        elif user_typed: raw_input_text = user_typed

        if "prevent_overlap" not in st.session_state:
            st.session_state.prevent_overlap = {"step": 0, "text": ""}

        # --- 10. ダイアログ選択後の次のステップ切り替え処理 ---
        if raw_input_text and (st.session_state.prevent_overlap["step"] != st.session_state.step or st.session_state.prevent_overlap["text"] != raw_input_text):
            matched_key = fuzzy_match(raw_input_text, keywords, fuzzy_rules)
            st.session_state.prevent_overlap["step"] = st.session_state.step
            st.session_state.prevent_overlap["text"] = raw_input_text

            if matched_key:
                import time
                time.sleep(1.0)
                st.session_state.pronunciation_status = None 
                
                if st.session_state.step == 1:
                    st.session_state.ordered_drink = matched_key
                    st.session_state.current_npc_en = "Excellent choice! Hot or iced? How would you like your drink?"
                    st.session_state.current_npc_jp = "いいですね！ホット（hot）か、アイス（iced）どちらにしますか？"
                    st.session_state.emotion = "happy"
                    st.session_state.step = 2
                elif st.session_state.step == 2:
                    st.session_state.drink_temp = matched_key
                    st.session_state.current_npc_en = f"Got it, {matched_key.capitalize()}! Now, what size would you like? Small, medium, or large?"
                    st.session_state.current_npc_jp = f"はい、{matched_key.capitalize()}ですね！サイズはどうしますか？"
                    st.session_state.step = 3
                elif st.session_state.step == 3:
                    st.session_state.ordered_size = matched_key
                    st.session_state.current_npc_en = "Okay! Would you like to add some delicious food today? We have cake and sandwiches!"
                    st.session_state.current_npc_jp = "かしこまりました！美味しそうなフード（ケーキやサンドイッチ）もご一緒にいかがですか？"
                    st.session_state.step = 4
                elif st.session_state.step == 4:
                    st.session_state.ordered_food = matched_key
                    st.session_state.current_npc_en = "Got it! Now, is that for here or to go?"
                    st.session_state.current_npc_jp = "かしこまりました！では、店内で召し上がりますか？お持ち帰りですか？"
                    st.session_state.step = 5
                elif st.session_state.step == 5:
                    st.session_state.ordered_place = matched_key
                    next_total = drink_base_p + temp_extra_p + size_extra_p + FOOD_PRICES.get(st.session_state.ordered_food, 0.0)
                    st.session_state.current_npc_en = f"Perfect! Your total is ${next_total:.2f}. How would you like to pay?"
                    st.session_state.current_npc_jp = f"合計で${next_total:.2f}です。お支払い方法（現金のお札の額、またはカード）を選んでね！"
                    st.session_state.step = 6
                elif st.session_state.step == 6:
                    food_msg = ""
                    food_msg_jp = ""
                    if st.session_state.ordered_food and st.session_state.ordered_food != "none":
                        food_msg = f" and {st.session_state.ordered_food}"
                        food_msg_jp = f"と{st.session_state.ordered_food == 'cake' and 'ケーキ' or 'サンドイッチ'}"
                    
                    if matched_key in ["5", "five"]:
                        st.session_state.ordered_payment_type = "cash ($5)"
                        st.session_state.paid_amount = 5.0
                    elif matched_key in ["10", "ten"]:
                        st.session_state.ordered_payment_type = "cash ($10)"
                        st.session_state.paid_amount = 10.0
                    elif matched_key in ["20", "twenty"]:
                        st.session_state.ordered_payment_type = "cash ($20)"
                        st.session_state.paid_amount = 20.0
                    else:
                        st.session_state.ordered_payment_type = "card"
                        st.session_state.paid_amount = total_p
                    
                    st.session_state.change_amount = st.session_state.paid_amount - total_p
                    
                    if st.session_state.ordered_payment_type.startswith("cash"):
                        if st.session_state.change_amount > 0.01: # 浮動小数点の誤差回避
                            st.session_state.current_npc_en = f"Thank you so much! Here is your change, ${st.session_state.change_amount:.2f}. And here is your drink{food_msg}. Enjoy!"
                            st.session_state.current_npc_jp = f"ありがとうございます！お釣りの${st.session_state.change_amount:.2f}です。ご注文のドリンク{food_msg_jp}もどうぞ。ごゆっくり！"
                        else:
                            st.session_state.current_npc_en = f"Thank you for the exact amount! Here is your drink{food_msg}. Enjoy your time!"
                            st.session_state.current_npc_jp = f"ちょうどのお支払いでありがとうございます！ご注文のドリンク{food_msg_jp}です。ごゆっくり！"
                    else:
                        st.session_state.current_npc_en = f"Thank you so much! Payment approved. Here is your drink{food_msg}. Enjoy your time!"
                        st.session_state.current_npc_jp = f"ありがとうございました！カード決済完了です。ご注文のドリンク{food_msg_jp}になります。ごゆっくり！"
                        
                    st.session_state.emotion = "happy"
                    st.session_state.step = 7 
                st.session_state.speak_now = True
                st.rerun()
            else:
                import time
                time.sleep(1.0)
                st.session_state.pronunciation_status = None 
                st.session_state.current_npc_en = "Sorry, could you say that again?"
                st.session_state.current_npc_jp = "すみません、もう一度おっしゃっていただけますか？"
                st.session_state.speak_now = True
                st.rerun()
    else:
        # --- 11. クリア時のスタンプ加算とアワード表示処理 ---
        if not st.session_state.stamp_processed:
            st.session_state.total_stamps += 1
            st.session_state.stamp_processed = True
            st.rerun()

        st.balloons()
        st.success("🎉 Order Completed!")

        stamps = st.session_state.total_stamps
        if stamps >= 10:
            st.markdown(f"""<div class='award-card'><div class='award-title'>👑 GRAND CAFE MASTER 👑</div><div class='award-name'>Member: {st.session_state.kid_name}</div><div class='award-badge'>👑🏆👑</div><p style='margin:0; font-size:0.8rem; color:#ffd700;'>あなたは最高峰のカフェマスターです！</p></div>""", unsafe_allow_html=True)
        elif stamps >= 5:
            st.markdown(f"""<div class='award-card' style='border-color:#ff9900;'><div class='award-title' style='color:#ff9900;'>🥇 REGULAR VIP MEMBER 🥇</div><div class='award-name'>Member: {st.session_state.kid_name}</div><div class='award-badge'>🥇✨🎖️</div><p style='margin:0; font-size:0.8rem; color:#ff9900;'>いつもありがとう！常連VIP会員証</p></div>""", unsafe_allow_html=True)
        elif stamps >= 3:
            st.markdown(f"""<div class='award-card' style='border-color:#cd7f32;'><div class='award-title' style='color:#b5733d;'>🥈 BRONZE CUSTOMER 🥈</div><div class='award-name'>Member: {st.session_state.kid_name}</div><div class='award-badge'>🥈🥉✨</div><p style='margin:0; font-size:0.8rem; color:#b5733d;'>素晴らしい！ブロンズ会員証獲得！</p></div>""", unsafe_allow_html=True)

        if st.button("Play Again (もういちど遊ぶ)", key='btn_play_again_action', use_container_width=True):
            keys_to_reset = ["step", "emotion", "ordered_drink", "drink_temp", "ordered_size", "ordered_food", "ordered_place", "ordered_payment_type", "paid_amount", "change_amount", "has_food_event", "pronunciation_status", "p_heard_text", "p_matched_keyword", "prevent_overlap", "speak_now", "stamp_processed"]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
