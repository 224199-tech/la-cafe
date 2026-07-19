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
stamp_img_path = "images/stamp.png"  # 新しいカスタムスタンプ画像

item_images = {
    "coffee": "images/coffee.png",
    "latte": "images/latte.png",
    "tea": "images/tea.png",
    "cake": "images/cake.png",
    "sandwich": "images/sandwich.png"
}

cash_images = {
    "5": "images/cash_5.png",
    "10": "images/cash_10.png",
    "20": "images/cash_20.png"
}

bg_base64 = get_image_base64(bg_path)
staff_normal_base = get_image_base64(staff_normal_path)
staff_happy_base = get_image_base64(staff_happy_path) if os.path.exists(staff_happy_path) else staff_normal_base
stamp_base64 = get_image_base64(stamp_img_path)

bg_style = f"background-image: url('data:image/jpeg;base64,{bg_base64}');" if bg_base64 else "background-color: #1e120c;"

# --- 3. デザインCSS（PC・タブレット向け最適化版） ---
st.markdown(f"<style>.stApp {{{bg_style} background-size: cover; background-position: center; background-attachment: fixed;}}</style>", unsafe_allow_html=True)

st.markdown("""<style>
.block-container { 
    max-width: 1200px !important;
    padding: 30px 20px !important; 
    background-color: rgba(0, 0, 0, 0.5); 
    border-radius: 16px;
    margin-top: 20px;
}
.game-title { 
    color: #ffd700; 
    text-align: center; 
    font-family: 'Comic Sans MS', sans-serif; 
    font-size: 2.5rem; 
    font-weight: bold; 
    text-shadow: 3px 3px 6px rgba(0,0,0,0.9); 
    margin-bottom: 20px; 
}
.character-stage { 
    display: flex; 
    justify-content: center; 
    align-items: flex-end; 
    height: 320px; 
    margin-bottom: 15px; 
    position: relative; 
    overflow: hidden; 
}
.npc-large-img { 
    height: 100%; 
    width: auto; 
    object-fit: contain; 
    filter: drop-shadow(0px 8px 12px rgba(0,0,0,0.5)); 
}
.drink-present { 
    position: absolute; 
    bottom: 20px; 
    right: 20%; 
    width: 90px; 
    height: 90px; 
    object-fit: contain; 
    filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.5)); 
}
.food-present { 
    position: absolute; 
    bottom: 15px; 
    right: 35%; 
    width: 85px; 
    height: 85px; 
    object-fit: contain; 
    filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.5)); 
}
.speech-window { 
    background: rgba(27, 18, 12, 0.95); 
    border: 4px solid #d7c49e; 
    border-radius: 15px; 
    padding: 20px; 
    color: #ffffff; 
    font-size: 1.6rem; 
    font-weight: bold; 
    box-shadow: 0 8px 16px rgba(0,0,0,0.5); 
    margin-bottom: 20px; 
    min-height: 100px; 
}
.speech-sub-jp { 
    font-size: 1.1rem; 
    color: #c9b097; 
    font-weight: normal; 
    margin-top: 10px; 
    border-top: 1px dashed rgba(215, 196, 158, 0.4); 
    padding-top: 8px; 
}
/* お財布ボードのデザイン */
.wallet-box {
    background-color: #2e1c0c;
    border: 3px solid #ff9900;
    border-radius: 12px;
    padding: 12px;
    color: #ffffff;
    margin-bottom: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}
.wallet-title {
    font-size: 1.1rem;
    font-weight: bold;
    color: #ff9900;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
}
.wallet-row {
    display: flex;
    gap: 15px;
    font-size: 0.95rem;
}
/* レシートボードのデザイン */
.receipt-box { 
    background-color: #fffef2; 
    border: 2px solid #ccc; 
    border-radius: 8px; 
    padding: 15px; 
    color: #2b1c11; 
    font-family: 'Courier New', monospace; 
    font-size: 1.05rem; 
    box-shadow: 0 6px 12px rgba(0,0,0,0.15); 
    margin-bottom: 15px; 
}
.receipt-header { 
    text-align: center; 
    font-weight: bold; 
    font-size: 1.2rem; 
    border-bottom: 2px dashed #2b1c11; 
    margin-bottom: 10px; 
    padding-bottom: 5px; 
}
.receipt-total { 
    border-top: 2px dashed #2b1c11; 
    margin-top: 10px; 
    padding-top: 5px; 
    font-weight: bold; 
    font-size: 1.25rem; 
    display: flex; 
    justify-content: space-between; 
}
/* スタンプカードのデザイン */
.stamp-card-box { 
    background: #fffef8; 
    border: 3px solid #8b5a2b; 
    border-radius: 12px; 
    padding: 12px; 
    margin-top: 15px; 
    text-align: center; 
    box-shadow: 0 6px 12px rgba(0,0,0,0.15); 
}
.stamp-title { 
    font-size: 1.1rem; 
    font-weight: bold; 
    color: #4a2e16; 
    margin-bottom: 8px; 
}
.stamp-grid { 
    display: flex; 
    justify-content: center; 
    gap: 8px; 
    flex-wrap: wrap; 
}
.stamp-slot { 
    width: 45px; 
    height: 45px; 
    border-radius: 50%; 
    border: 2px dashed #ccc; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    font-size: 0.9rem; 
    background: #fff; 
    color: #aaa;
    position: relative;
    overflow: hidden;
}
.stamp-active { 
    border: 2px solid #ff4500; 
    background: #ffe4e1; 
    color: transparent;
}
.stamp-img {
    width: 90%;
    height: 90%;
    object-fit: contain;
}
.menu-card {
    background: rgba(255, 255, 255, 0.08);
    border: 2px solid #8b5a2b;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
    margin-bottom: 10px;
}
.menu-card-title {
    color: #ffd700;
    font-weight: bold;
    font-size: 1.1rem;
    margin-bottom: 5px;
}
.mic-container { 
    background: rgba(255, 255, 255, 0.05); 
    border: 3px dashed rgba(215, 196, 158, 0.5); 
    padding: 15px; 
    border-radius: 12px; 
    text-align: center; 
    margin-bottom: 15px; 
}
.pronunciation-badge-container { 
    margin-bottom: 15px; 
    background: #110905; 
    border: 2px solid #8b5a2b; 
    border-radius: 8px; 
    padding: 8px 15px; 
    display: flex; 
    align-items: center; 
    justify-content: space-between;
}
.award-card { 
    background: linear-gradient(135deg, #150d0a 0%, #2a1810 100%); 
    border: 4px solid #ffd700; 
    border-radius: 16px; 
    padding: 20px; 
    text-align: center; 
    color: white; 
    box-shadow: 0 12px 24px rgba(0,0,0,0.5); 
    margin: 15px 0; 
}
.award-title { font-size: 1.6rem; font-weight: bold; color: #ffd700; }
.award-name { font-size: 1.3rem; font-family: 'Courier New', monospace; margin: 10px 0; border-bottom: 2px dashed #ffd700; padding-bottom: 5px; }
.award-badge { font-size: 3.5rem; margin: 10px 0; }
</style>""", unsafe_allow_html=True)

# --- 4. 永続的な状態の設定 ---
if "total_stamps" not in st.session_state:
    st.session_state.total_stamps = 0
if "kid_name" not in st.session_state:
    st.session_state.kid_name = "Guest"

# --- 5. 【新規】ランダムお財布システム初期化 ---
def init_random_wallet():
    # 5ドル札(1〜2枚), 10ドル札(0〜2枚), 20ドル札(0~1枚)をランダムに支給
    st.session_state.wallet_5 = random.randint(1, 2)
    st.session_state.wallet_10 = random.randint(0, 2)
    st.session_state.wallet_20 = random.choice([0, 1])
    # 稀に全部0~1で詰まないよう、最低合計額が5ドル以上になる安全設計

if "wallet_5" not in st.session_state:
    init_random_wallet()

wallet_total = (st.session_state.wallet_5 * 5) + (st.session_state.wallet_10 * 10) + (st.session_state.wallet_20 * 20)

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

# --- 7. サイドバー設定 ---
st.sidebar.markdown("### 👤 カスタマー情報")
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

# --- 8. 画面レイアウト構築 ---
st.markdown("<p class='game-title'>☕ La Café English Roleplay ☕</p>", unsafe_allow_html=True)

main_col, visual_col = st.columns([1.2, 0.8])

with visual_col:
    # お姉さんステージ
    active_staff_base = staff_happy_base if st.session_state.emotion == "happy" else staff_normal_base
    staff_html = f'<img class="npc-large-img" src="data:image/png;base64,{active_staff_base}">' if active_staff_base else '<div style="font-size:80px; text-align:center;">👩‍🍳</div>'

    drink_html = ""
    food_html = ""
    if st.session_state.step == 7: 
        if st.session_state.ordered_drink:
            local_drink_path = item_images.get(st.session_state.ordered_drink, "")
            if os.path.exists(local_drink_path):
                drink_html = f'<img class="drink-present" src="data:image/png;base64,{get_image_base64(local_drink_path)}">'
        if st.session_state.ordered_food:
            local_food_path = item_images.get(st.session_state.ordered_food, "")
            if os.path.exists(local_food_path):
                food_html = f'<img class="food-present" src="data:image/png;base64,{get_image_base64(local_food_path)}">'

    st.markdown(f"<div class='character-stage'>{staff_html}{drink_html}{food_html}</div>", unsafe_allow_html=True)

    # 👛 【新機能】今日のおさいふ表示ボード
    st.markdown(f"""
    <div class="wallet-box">
        <div class="wallet-title"><span>👛 MY WALLET (きょうのおさいふ)</span> <span>Total: ${wallet_total:.2f}</span></div>
        <div class="wallet-row">
            <span>💵 $5.00 × <b>{st.session_state.wallet_5}</b></span>
            <span>💵 $10.00 × <b>{st.session_state.wallet_10}</b></span>
            <span>💵 $20.00 × <b>{st.session_state.wallet_20}</b></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # リアルタイム計算レシート
    drink_prices = {"coffee": 5.0, "tea": 5.5, "latte": 6.0}
    drink_p = drink_prices.get(st.session_state.ordered_drink, 0.0)
    temp_p = 1.0 if st.session_state.drink_temp == "iced" else 0.0
    size_prices = {"small": 0.0, "medium": 1.5, "large": 2.5}
    size_p = size_prices.get(st.session_state.ordered_size, 0.0)
    food_prices = {"cake": 6.5, "sandwich": 8.5}
    food_p = food_prices.get(st.session_state.ordered_food, 0.0)
    
    total_p = 0.0
    if st.session_state.ordered_drink:
        total_p = drink_p + temp_p + size_p + food_p

    drink_disp = st.session_state.ordered_drink.capitalize() if st.session_state.ordered_drink else "---"
    temp_disp = st.session_state.drink_temp.capitalize() if st.session_state.drink_temp else "---"
    size_disp = st.session_state.ordered_size.capitalize() if st.session_state.ordered_size else "---"
    food_disp = st.session_state.ordered_food.capitalize() if (st.session_state.ordered_food and st.session_state.ordered_food != "no") else "---"
    place_disp = "Here" if st.session_state.ordered_place == "here" else ("To Go" if st.session_state.ordered_place == "go" else "---")
    payment_disp = st.session_state.ordered_payment_type.upper() if st.session_state.ordered_payment_type else "---"
    
    st.markdown(f"""
    <div class="receipt-box">
        <div class="receipt-header">📋 {st.session_state.kid_name.upper()}'S RECEIPT</div>
        <div style="margin-bottom:8px;">▶ 🥤 Item: {drink_disp} (${drink_p:.2f})</div>
        <div style="margin-bottom:8px;">▶ 🔥 Temp: {temp_disp} (+${temp_p:.2f})</div>
        <div style="margin-bottom:8px;">▶ 📏 Size: {size_disp} (+${size_p:.2f})</div>
        <div style="margin-bottom:8px;">▶ 🥪 Food: {food_disp} (+${food_p:.2f})</div>
        <div style="margin-bottom:8px;">▶ 🏠 Place: {place_disp}</div>
        <div style="margin-bottom:12px;">▶ 💳 Pay: {payment_disp}</div>
        <div class="receipt-total"><span>TOTAL:</span> <span>${total_p:.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 💮 【新機能】画像スタンプカード
    stamp_slots_html = ""
    for i in range(1, 11):
        if i <= st.session_state.total_stamps:
            if stamp_base64:
                # 生成したスタンプ画像を埋め込む
                stamp_slots_html += f"<div class='stamp-slot stamp-active'><img class='stamp-img' src='data:image/png;base64,{stamp_base64}'></div>"
            else:
                # 画像がない時のセーフティ表示
                stamp_slots_html += "<div class='stamp-slot stamp-active'>☕</div>"
        else:
            stamp_slots_html += f"<div class='stamp-slot'>{i}</div>"
            
    st.markdown(f"""
    <div class="stamp-card-box">
        <div class="stamp-title">💮 CUSTOMER STAMP CARD</div>
        <div class="stamp-grid">{stamp_slots_html}</div>
    </div>
    """, unsafe_allow_html=True)

with main_col:
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
        st.markdown('<div class="mic-container">', unsafe_allow_html=True)
        st.markdown("<p style='color:#ffd700; font-weight:bold; font-size:1.1rem; margin-bottom:5px;'>🎤 Speak English (英語でこたえてね！)</p>", unsafe_allow_html=True)
        mic_input = speech_to_text(start_prompt="🔴 PUSH TO TALK (おしてね)", stop_prompt="⏹️ STOP", language='en-US', use_container_width=True, key=f'mic_{st.session_state.step}')
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.pronunciation_status:
            icon = "🌟 Perfect!!" if st.session_state.pronunciation_status == "perfect" else "👍 Good Job!"
            color = "#00ff7f" if st.session_state.pronunciation_status == "perfect" else "#ffd700"
            st.markdown(f"<div class='pronunciation-badge-container'><div style='color:#aaa; font-size:1.0rem;'>Heard: {st.session_state.p_heard_text} ➔ {st.session_state.p_matched_keyword}</div><div style='color:{color}; font-weight:bold; font-size:1.2rem;'>{icon}</div></div>", unsafe_allow_html=True)

        st.markdown("<p style='color:#ffffff; font-weight:bold; font-size:1.0rem; margin-bottom:5px;'>👇 Or click the phrase button (ボタンをおしてもいいよ):</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        keywords = []
        fuzzy_rules = None

        if st.session_state.step == 1:
            keywords = ["coffee", "latte", "tea"]
            menu_col1, menu_col2, menu_col3 = st.columns(3)
            with menu_col1:
                st.markdown("<div class='menu-card'><p class='menu-card-title'>☕ Coffee</p><p style='color:#ffd700; font-weight:bold;'>$5.00</p></div>", unsafe_allow_html=True)
                if os.path.exists(item_images["coffee"]): st.image(item_images["coffee"], use_container_width=True)
            with menu_col2:
                st.markdown("<div class='menu-card'><p class='menu-card-title'>🥛 Latte</p><p style='color:#ffd700; font-weight:bold;'>$6.00</p></div>", unsafe_allow_html=True)
                if os.path.exists(item_images["latte"]): st.image(item_images["latte"], use_container_width=True)
            with menu_col3:
                st.markdown("<div class='menu-card'><p class='menu-card-title'>🍵 Tea</p><p style='color:#ffd700; font-weight:bold;'>$5.50</p></div>", unsafe_allow_html=True)
                if os.path.exists(item_images["tea"]): st.image(item_images["tea"], use_container_width=True)

            with col1:
                if st.button("☕️ Coffee, please.", key='b_cf', use_container_width=True): user_choice = "coffee"
            with col2:
                if st.button("🥛 Latte, please.", key='b_lt', use_container_width=True): user_choice = "latte"
            with col3:
                if st.button("🍵 Tea, please.", key='b_te', use_container_width=True): user_choice = "tea"

        elif st.session_state.step == 2:
            keywords = ["hot", "iced"]
            fuzzy_rules = {"hot": ["hat", "pot", "heart"], "iced": ["ice", "eyes"]}
            with col1:
                if st.button("🔥 Hot, please.", key='b_ht', use_container_width=True): user_choice = "hot"
            with col2:
                if st.button("❄️ Iced, please.", key='b_ic', use_container_width=True): user_choice = "iced"

        elif st.session_state.step == 3:
            keywords = ["small", "medium", "large"]
            with col1:
                if st.button("🟢 Small, please.", key='b_sm', use_container_width=True): user_choice = "small"
            with col2:
                if st.button("🟡 Medium, please.", key='b_md', use_container_width=True): user_choice = "medium"
            with col3:
                if st.button("🔴 Large, please.", key='b_lg', use_container_width=True): user_choice = "large"

        elif st.session_state.step == 4:
            keywords = ["cake", "sandwich", "no"]
            menu_col1, menu_col2, menu_col3 = st.columns(3)
            with menu_col1:
                st.markdown("<div class='menu-card'><p class='menu-card-title'>🍰 Cake</p><p style='color:#ffd700; font-weight:bold;'>+$6.50</p></div>", unsafe_allow_html=True)
                if os.path.exists(item_images["cake"]): st.image(item_images["cake"], use_container_width=True)
            with menu_col2:
                st.markdown("<div class='menu-card'><p class='menu-card-title'>🥪 Sandwich</p><p style='color:#ffd700; font-weight:bold;'>+$8.50</p></div>", unsafe_allow_html=True)
                if os.path.exists(item_images["sandwich"]): st.image(item_images["sandwich"], use_container_width=True)
            with menu_col3:
                st.markdown("<div class='menu-card'><p class='menu-card-title'>❌ No Food</p><p style='color:#aaa;'>$0.00</p></div>", unsafe_allow_html=True)

            with col1:
                if st.button("🍰 Cake, please.", key='b_ck', use_container_width=True): user_choice = "cake"
            with col2:
                if st.button("🥪 Sandwich, please.", key='b_sw', use_container_width=True): user_choice = "sandwich"
            with col3:
                if st.button("❌ No, thank you.", key='b_nf', use_container_width=True): user_choice = "no"
                
        elif st.session_state.step == 5:
            keywords = ["here", "go"]
            with col1:
                if st.button("🏠 For here, please.", key='b_hr', use_container_width=True): user_choice = "here"
            with col2:
                if st.button("🛍️ To go, please.", key='b_tg', use_container_width=True): user_choice = "go"
                
        elif st.session_state.step == 6:
            keywords = ["5", "10", "20", "five", "ten", "twenty", "card"]
            
            # 👛 お財布と合計金額に基づいた動的な支払いチェック
            # お財布の所持数が0枚、または所持していても1枚の額面が合計に足りない場合はボタンが無効化されます。
            with col1:
                can_pay_5 = (st.session_state.wallet_5 > 0) and (5.0 >= total_p)
                if os.path.exists(cash_images["5"]):
                    st.image(cash_images["5"], use_container_width=True)
                if st.button("💵 Give $5.00", key='p_5', disabled=not can_pay_5, use_container_width=True): 
                    user_choice = "5"
                if not can_pay_5:
                    st.caption("※お財布にないか、金額が足りません")
            
            with col2:
                can_pay_10 = (st.session_state.wallet_10 > 0) and (10.0 >= total_p)
                if os.path.exists(cash_images["10"]):
                    st.image(cash_images["10"], use_container_width=True)
                if st.button("💵 Give $10.00", key='p_10', disabled=not can_pay_10, use_container_width=True): 
                    user_choice = "10"
                if not can_pay_10:
                    st.caption("※お財布にないか、金額が足りません")
            
            with col3:
                can_pay_20 = (st.session_state.wallet_20 > 0) and (20.0 >= total_p)
                if os.path.exists(cash_images["20"]):
                    st.image(cash_images["20"], use_container_width=True)
                if st.button("💵 Give $20.00", key='p_20', disabled=not can_pay_20, use_container_width=True): 
                    user_choice = "20"
                if not can_pay_20:
                    st.caption("※お財布にないか、金額が足りません")

            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            # 現金が一切足りなくて詰んだ時のセーフティ決済手段としてカードを残す
            if st.button("💳 Pay by card, please. (カードで払う)", key='b_card', use_container_width=True): 
                user_choice = "card"

        user_typed = st.chat_input("Or type here...")
        raw_input_text = mic_input or user_choice or user_typed

        if "prevent_overlap" not in st.session_state:
            st.session_state.prevent_overlap = {"step": 0, "text": ""}

        if raw_input_text and (st.session_state.prevent_overlap["step"] != st.session_state.step or st.session_state.prevent_overlap["text"] != raw_input_text):
            matched_key = fuzzy_match(raw_input_text, keywords, fuzzy_rules)
            st.session_state.prevent_overlap["step"] = st.session_state.step
            st.session_state.prevent_overlap["text"] = raw_input_text

            if matched_key:
                import time
                time.sleep(0.4)
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
                    st.session_state.has_food_event = random.choice([True, False])
                    if st.session_state.has_food_event:
                        st.session_state.current_npc_en = "Okay! By the way, would you like a chocolate cake or a club sandwich with that today?"
                        st.session_state.current_npc_jp = "かしこまりました！よろしければ、ケーキやクラブサンドイッチはいかがですか？"
                        st.session_state.step = 4
                    else:
                        st.session_state.ordered_food = "no"
                        st.session_state.current_npc_en = "Okay! Is that for here or to go?"
                        st.session_state.current_npc_jp = "店内で召し上がりますか？それともお持ち帰りですか？"
                        st.session_state.step = 5
                elif st.session_state.step == 4:
                    st.session_state.ordered_food = matched_key if matched_key in ["cake", "sandwich"] else "no"
                    st.session_state.current_npc_en = "Got it! Now, is that for here or to go?"
                    st.session_state.current_npc_jp = "かしこばりました！では、店内で召し上がりますか？お持ち帰りですか？"
                    st.session_state.step = 5
                elif st.session_state.step == 5:
                    st.session_state.ordered_place = matched_key
                    st.session_state.current_npc_en = f"Perfect! Your total is ${total_p:.2f}. How would you like to pay?"
                    st.session_state.current_npc_jp = f"合計で${total_p:.2f}です。お財布のなかみから払えるお札を選んで手渡してね！"
                    st.session_state.step = 6
                elif st.session_state.step == 6:
                    food_msg = f" and {st.session_state.ordered_food}" if (st.session_state.ordered_food and st.session_state.ordered_food != "no") else ""
                    food_msg_jp = f"と{st.session_state.ordered_food}" if (st.session_state.ordered_food and st.session_state.ordered_food != "no") else ""
                    
                    if matched_key in ["5", "five"]:
                        st.session_state.ordered_payment_type = "cash ($5)"
                        st.session_state.paid_amount = 5.0
                        st.session_state.wallet_5 -= 1
                    elif matched_key in ["10", "ten"]:
                        st.session_state.ordered_payment_type = "cash ($10)"
                        st.session_state.paid_amount = 10.0
                        st.session_state.wallet_10 -= 1
                    elif matched_key in ["20", "twenty"]:
                        st.session_state.ordered_payment_type = "cash ($20)"
                        st.session_state.paid_amount = 20.0
                        st.session_state.wallet_20 -= 1
                    else:
                        st.session_state.ordered_payment_type = "card"
                        st.session_state.paid_amount = total_p
                    
                    st.session_state.change_amount = st.session_state.paid_amount - total_p
                    
                    if st.session_state.ordered_payment_type.startswith("cash"):
                        if st.session_state.change_amount > 0:
                            st.session_state.current_npc_en = f"Thank you so much! Here is your change, ${st.session_state.change_amount:.2f}. And here is your drink{food_msg}. Enjoy!"
                            st.session_state.current_npc_jp = f"ありがとうございます！お釣りの${st.session_state.change_amount:.2f}です。ご注文のドリンク{food_msg_jp}もどうぞ！"
                        else:
                            st.session_state.current_npc_en = f"Thank you for the exact amount! Here is your drink{food_msg}. Enjoy!"
                            st.session_state.current_npc_jp = f"ぴったりのお支払いで助かります！ご注文のドリンク{food_msg_jp}です。どうぞ！"
                    else:
                        st.session_state.current_npc_en = f"Thank you so much! Payment approved. Here is your drink{food_msg}. Enjoy!"
                        st.session_state.current_npc_jp = f"ありがとうございました！カード決済完了です。ご注文のドリンク{food_msg_jp}になります。どうぞ！"
                        
                    st.session_state.emotion = "happy"
                    st.session_state.step = 7 
                st.session_state.speak_now = True
                st.rerun()
            else:
                import time
                time.sleep(0.4)
                st.session_state.pronunciation_status = None 
                st.session_state.current_npc_en = "Sorry, could you say that again?"
                st.session_state.current_npc_jp = "すみません、もう一度おっしゃっていただけますか？"
                st.session_state.speak_now = True
                st.rerun()
    else:
        if not st.session_state.stamp_processed:
            st.session_state.total_stamps += 1
            st.session_state.stamp_processed = True
            st.rerun()

        st.balloons()
        st.success("🎉 Good Job! Roleplay Completed!")

        stamps = st.session_state.total_stamps
        if stamps >= 10:
            st.markdown(f"""<div class='award-card'><div class='award-title'>👑 GRAND CAFE MASTER 👑</div><div class='award-name'>Member: {st.session_state.kid_name}</div><div class='award-badge'>👑🏆👑</div><p>最高峰のカフェ英語マスターの証明書です！</p></div>""", unsafe_allow_html=True)
        elif stamps >= 5:
            st.markdown(f"""<div class='award-card' style='border-color:#ff9900;'><div class='award-title' style='color:#ff9900;'>🥇 REGULAR VIP MEMBER 🥇</div><div class='award-name'>Member: {st.session_state.kid_name}</div><div class='award-badge'>🥇✨🎖️</div><p>いつもありがとう！常連VIP会員証</p></div>""", unsafe_allow_html=True)
        elif stamps >= 3:
            st.markdown(f"""<div class='award-card' style='border-color:#cd7f32;'><div class='award-title' style='color:#b5733d;'>🥈 BRONZE CUSTOMER 🥈</div><div class='award-name'>Member: {st.session_state.kid_name}</div><div class='award-badge'>🥈🥉✨</div><p>素晴らしい！ブロンズ会員証獲得！</p></div>""", unsafe_allow_html=True)

        if st.button("🔄 Play Again (新しいおさいふで遊ぶ)", key='b_again', use_container_width=True):
            keys_to_reset = ["step", "emotion", "ordered_drink", "drink_temp", "ordered_size", "ordered_food", "ordered_place", "ordered_payment_type", "paid_amount", "change_amount", "has_food_event", "pronunciation_status", "p_heard_text", "p_matched_keyword", "prevent_overlap", "speak_now", "stamp_processed"]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            init_random_wallet() # お財布を新しくランダムシャッフル
            st.rerun()
