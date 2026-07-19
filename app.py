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

cash_images = {
    "5": "images/cash_5.png",
    "10": "images/cash_10.png",
    "20": "images/cash_20.png"
}

bg_base64 = get_image_base64(bg_path)
staff_normal_base = get_image_base64(staff_normal_path)
staff_happy_base = get_image_base64(staff_happy_path) if os.path.exists(staff_happy_path) else staff_normal_base
bg_style = f"background-image: url('data:image/jpeg;base64,{bg_base64}');" if bg_base64 else "background-color: #1e120c;"

# --- 3. デザインCSS設定（PC・タブレットに最適化された大画面で見やすいデザイン） ---
st.markdown(f"<style>.stApp {{{bg_style} background-size: cover; background-position: center; background-attachment: fixed;}}</style>", unsafe_allow_html=True)

st.markdown("""<style>
/* 画面全体の余白調整 */
.block-container { 
    max-width: 1200px !important;
    padding: 20px !important; 
    background-color: rgba(0, 0, 0, 0.5); 
    border-radius: 16px;
    margin-top: 20px;
    margin-bottom: 20px;
}

/* ゲーム全体のタイトル（大きく華やかに） */
.game-title { 
    color: #ffd700; 
    text-align: center; 
    font-family: 'Georgia', serif; 
    font-size: 2.2rem; 
    font-weight: bold; 
    text-shadow: 3px 3px 6px rgba(0,0,0,0.9); 
    margin: 10px 0px 20px 0px; 
}

/* 左右分割用のコンテナ（視認性を確保する不透明な高級ウッドブラウン） */
.column-container {
    background: rgba(30, 18, 12, 0.95);
    border: 4px solid #8b5a2b;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.7);
    margin-bottom: 15px;
}

/* キャラクター（お姉さん）のステージ部分（高さを十分に確保し美しく表示） */
.character-stage { 
    display: flex; 
    justify-content: center; 
    align-items: flex-end; 
    height: 300px; 
    margin-bottom: 15px; 
    position: relative; 
    overflow: hidden; 
    border-radius: 12px; 
    background: rgba(0,0,0,0.4); 
    border: 2px solid #5a381e;
}
.npc-large-img { 
    max-height: 95%; 
    width: auto; 
    object-fit: contain; 
    filter: drop-shadow(0px 6px 12px rgba(0,0,0,0.7)); 
    position: relative; 
    bottom: 0px; 
    z-index: 5; 
}

/* 手渡しアイテムの配置 */
.drink-present { 
    position: absolute; 
    bottom: 20px; 
    right: 20%; 
    width: 75px; 
    height: 75px; 
    object-fit: contain; 
    z-index: 10; 
    filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.6)); 
}
.food-present { 
    position: absolute; 
    bottom: 20px; 
    right: 40%; 
    width: 70px; 
    height: 70px; 
    object-fit: contain; 
    z-index: 11; 
    filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.6)); 
}

/* セリフ吹き出しエリア（文字を極限まで見やすく、大きく調整） */
.speech-window { 
    background: #0d0604; 
    border: 3px solid #ffd700; 
    border-radius: 14px; 
    padding: 18px; 
    color: #ffffff; 
    font-size: 1.45rem; 
    font-weight: bold; 
    box-shadow: 0 6px 15px rgba(0,0,0,0.7); 
    margin-bottom: 15px; 
    min-height: 90px; 
    line-height: 1.4;
}
.speech-sub-jp { 
    font-size: 1.0rem; 
    color: #c9b097; 
    font-weight: normal; 
    margin-top: 8px; 
    border-top: 1px dashed rgba(255, 215, 0, 0.3); 
    padding-top: 6px; 
}

/* 本物のカフェのレシートデザイン */
.receipt-memo { 
    background-color: #fffef2; 
    border-left: 3px dashed #999; 
    border-right: 3px dashed #999; 
    border-top: 2px solid #ccc; 
    border-bottom: 2px solid #ccc; 
    padding: 12px; 
    color: #2b1c11; 
    font-family: 'Courier New', monospace; 
    font-size: 0.95rem; 
    box-shadow: 0 6px 12px rgba(0,0,0,0.3); 
    margin-bottom: 15px; 
    line-height: 1.4; 
}
.receipt-header { 
    text-align: center; 
    font-weight: bold; 
    font-size: 1.1rem; 
    border-bottom: 2px dashed #2b1c11; 
    margin-bottom: 8px; 
    padding-bottom: 4px; 
}
.receipt-item-container { 
    display: flex; 
    flex-wrap: wrap; 
    justify-content: space-between; 
    gap: 8px; 
}
.receipt-item { 
    font-size: 0.9rem; 
    background: rgba(0,0,0,0.06); 
    padding: 4px 8px; 
    border-radius: 6px; 
    font-weight: bold;
}
.receipt-total { 
    border-top: 2px dashed #2b1c11; 
    margin-top: 8px; 
    padding-top: 6px; 
    font-weight: bold; 
    font-size: 1.15rem; 
    display: flex; 
    justify-content: space-between; 
    width: 100%; 
}

/* マイク録音エリア */
.mic-container { 
    background: rgba(255, 255, 255, 0.05); 
    border: 3px dashed rgba(215, 196, 158, 0.6); 
    padding: 12px; 
    border-radius: 12px; 
    text-align: center; 
    margin-bottom: 15px; 
}
.equalizer-wave { 
    display: flex; 
    justify-content: center; 
    align-items: center; 
    height: 18px; 
    gap: 4px; 
    margin: 4px 0; 
}
.wave-bar { 
    width: 4px; 
    height: 100%; 
    background-color: #ffd700; 
    border-radius: 2px; 
    animation: waveAnim 1.2s ease-in-out infinite; 
}
.wave-bar:nth-child(2) { animation-delay: 0.1s; background-color: #ff9900; }
.wave-bar:nth-child(3) { animation-delay: 0.2s; background-color: #ffd700; }
.wave-bar:nth-child(4) { animation-delay: 0.3s; background-color: #ff9900; }
@keyframes waveAnim { 0%, 100% { transform: scaleY(0.4); } 50% { transform: scaleY(1.0); } }

/* 発音スコア判定バッジ */
.pronunciation-badge-container { 
    margin-bottom: 12px; 
    background: #0d0604; 
    border: 2px solid #8b5a2b; 
    border-radius: 8px; 
    padding: 8px 12px; 
    display: flex; 
    align-items: center; 
    justify-content: space-between;
}
.badge-label { 
    color: #ffd700; 
    font-size: 0.9rem; 
    font-family: monospace; 
}
.pron-perfect { color: #00ff7f; font-weight: bold; font-size: 1.0rem; }
.pron-good { color: #ffd700; font-weight: bold; font-size: 1.0rem; }

/* スタンプカード */
.stamp-card-box { 
    background: #fffef8; 
    border: 3px solid #8b5a2b; 
    border-radius: 12px; 
    padding: 8px; 
    margin-top: 10px; 
    text-align: center; 
    box-shadow: 0 6px 12px rgba(0,0,0,0.15); 
}
.stamp-title { 
    font-size: 0.85rem; 
    font-weight: bold; 
    color: #4a2e16; 
    margin-bottom: 5px; 
}
.stamp-grid { 
    display: flex; 
    justify-content: center; 
    gap: 6px; 
    flex-wrap: wrap; 
}
.stamp-slot { 
    width: 30px; 
    height: 30px; 
    border-radius: 50%; 
    border: 2px dashed #ccc; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    font-size: 0.9rem; 
    background: #fff; 
    font-weight: bold;
    color: #777;
}
.stamp-active { 
    border: 2px solid #ff4500; 
    background: #ffe4e1; 
}

/* メニューカード看板 */
.menu-card {
    background: rgba(30, 18, 12, 0.85);
    border: 2.5px solid #8b5a2b;
    border-radius: 12px;
    padding: 10px;
    text-align: center;
    box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    margin-bottom: 8px;
}
.menu-card-title {
    color: #ffd700;
    font-weight: bold;
    font-size: 0.95rem;
    margin-bottom: 4px;
}

/* お札画像のタップ領域用のエフェクト（PC等でのホバー効果を復活） */
img.cash-img-btn {
    transition: transform 0.2s ease, filter 0.2s ease;
    cursor: pointer;
    border-radius: 6px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}
img.cash-img-btn:hover {
    transform: scale(1.08) translateY(-4px);
    filter: brightness(1.15) drop-shadow(0px 8px 12px rgba(255, 215, 0, 0.4));
}

/* デジタル会員証アワードのデザイン */
.award-card { 
    background: linear-gradient(135deg, #150d0a 0%, #2a1810 100%); 
    border: 4px solid #ffd700; 
    border-radius: 16px; 
    padding: 16px; 
    text-align: center; 
    color: white; 
    box-shadow: 0 10px 20px rgba(0,0,0,0.7); 
    margin: 12px 0; 
}
.award-title { 
    font-size: 1.3rem; 
    font-weight: bold; 
    color: #ffd700; 
}
.award-name { 
    font-size: 1.15rem; 
    font-family: 'Georgia', serif; 
    margin: 6px 0; 
    border-bottom: 2.5px dashed #ffd700; 
    padding-bottom: 6px; 
}
.award-badge { 
    font-size: 2.5rem; 
    margin: 8px 0; 
}
</style>""", unsafe_allow_html=True)

# --- 4. 永続的な状態の設定 ---
if "total_stamps" not in st.session_state:
    st.session_state.total_stamps = 0
if "kid_name" not in st.session_state:
    st.session_state.kid_name = "Guest"

# --- 5. ゲーム内会話状態の設定 ---
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

# --- 6. サイドバー設定 ---
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

# --- 7. 画面レイアウト構築 ---
st.markdown("<p class='game-title'>☕ La Café English Roleplay ☕</p>", unsafe_allow_html=True)

main_col, visual_col = st.columns([1.1, 0.9])

with visual_col:
    # 左右のカラムが綺麗に分離するようにクラスを適用
    st.markdown('<div class="column-container">', unsafe_allow_html=True)
    
    # 1. お姉さんステージ
    active_staff_base = staff_happy_base if st.session_state.emotion == "happy" else staff_normal_base
    staff_html = f'<img class="npc-large-img" src="data:image/png;base64,{active_staff_base}">' if active_staff_base else '<div style="font-size:50px; text-align:center;">👩‍🍳</div>'

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

    # 2. リアルタイム計算レシート (20ドル札対応の海外インフレ物価計算)
    # 基本料金
    drink_prices = {"coffee": 5.0, "tea": 5.5, "latte": 6.0}
    drink_p = drink_prices.get(st.session_state.ordered_drink, 0.0)
    
    # トッピング価格
    temp_p = 1.0 if st.session_state.drink_temp == "iced" else 0.0
    
    # サイズ追加料金
    size_prices = {"small": 0.0, "medium": 1.5, "large": 2.5}
    size_p = size_prices.get(st.session_state.ordered_size, 0.0)
    
    # フード料金
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
    <div class="receipt-memo">
        <div class="receipt-header">📋 {st.session_state.kid_name.upper()}'S RECEIPT</div>
        <div class="receipt-item-container">
            <div class="receipt-item">🥤 {drink_disp} (${drink_p:.2f})</div>
            <div class="receipt-item">🔥 {temp_disp} (+${temp_p:.2f})</div>
            <div class="receipt-item">📏 {size_disp} (+${size_p:.2f})</div>
            <div class="receipt-item">🥪 {food_disp} (+${food_p:.2f})</div>
            <div class="receipt-item">🏠 {place_disp}</div>
            <div class="receipt-item">💳 {payment_disp}</div>
        </div>
        <div class="receipt-total"><span>💰 TOTAL AMOUNT:</span> <span>${total_p:.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 3. スタンプカード
    stamp_slots_html = ""
    for i in range(1, 11):
        if i <= st.session_state.total_stamps:
            stamp_slots_html += "<div class='stamp-slot stamp-active'>💮</div>"
        else:
            stamp_slots_html += f"<div class='stamp-slot'>{i}</div>"
            
    st.markdown(f"""
    <div class="stamp-card-box">
        <div class="stamp-title">💮 CUSTOMER STAMP CARD</div>
        <div class="stamp-grid">{stamp_slots_html}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with main_col:
    st.markdown('<div class="column-container">', unsafe_allow_html=True)
    
    # 音声読み上げロジック
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

    # セリフウィンドウ（お姉さんのメッセージ）
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

    # 音声認識＆手動選択フロー
    if st.session_state.step < 7:
        # マイク入力
        st.markdown('<div class="mic-container">', unsafe_allow_html=True)
        st.markdown("<p style='color:#ffd700; font-weight:bold; margin-bottom:4px; font-size:1.0rem;'>🎤 English Speech Action (英語でしゃべる)</p>", unsafe_allow_html=True)
        st.markdown("<div class='equalizer-wave'><div class='wave-bar'></div><div class='wave-bar'></div><div class='wave-bar'></div><div class='wave-bar'></div></div>", unsafe_allow_html=True)
        
        mic_input = speech_to_text(
            start_prompt="🔴 PRESS TO SPEAK (おしてしゃべる)",
            stop_prompt="⏹️ STOP",
            language='en-US',
            use_container_width=True,
            key=f'speech_step_{st.session_state.step}' 
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.pronunciation_status:
            icon = "🌟 Perfect!" if st.session_state.pronunciation_status == "perfect" else "👍 Good Try!"
            i_class = "pron-perfect" if st.session_state.pronunciation_status == "perfect" else "pron-good"
            st.markdown(f"<div class='pronunciation-badge-container'><div class='badge-label'>🗣️ {st.session_state.p_heard_text} ➡️ {st.session_state.p_matched_keyword}</div><div class='{i_class}'>{icon}</div></div>", unsafe_allow_html=True)

        st.markdown("<p style='color:#ffffff; font-weight:bold; margin-bottom:6px; font-size:0.95rem;'>👇 Or touch the correct phrase button below:</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        keywords = []
        fuzzy_rules = None

        # --- STEP 1: ドリンクの選択 ---
        if st.session_state.step == 1:
            keywords = ["coffee", "latte", "tea"]
            
            # メニュー看板（見るだけのビジュアル要素）
            menu_col1, menu_col2, menu_col3 = st.columns(3)
            with menu_col1:
                st.markdown("<div class='menu-card'><p class='menu-card-title'>☕ Coffee</p><p style='color:#aaa; font-size:0.8rem; margin:0;'>$5.00</p></div>", unsafe_allow_html=True)
                if os.path.exists(item_images["coffee"]): st.image(item_images["coffee"], use_container_width=True)
            with menu_col2:
                st.markdown("<div class='menu-card'><p class='menu-card-title'>🥛 Latte</p><p style='color:#aaa; font-size:0.8rem; margin:0;'>$6.00</p></div>", unsafe_allow_html=True)
                if os.path.exists(item_images["latte"]): st.image(item_images["latte"], use_container_width=True)
            with menu_col3:
                st.markdown("<div class='menu-card'><p class='menu-card-title'>🍵 Tea</p><p style='color:#aaa; font-size:0.8rem; margin:0;'>$5.50</p></div>", unsafe_allow_html=True)
                if os.path.exists(item_images["tea"]): st.image(item_images["tea"], use_container_width=True)

            # 英語フレーズ選択ボタン
            with col1:
                if st.button("☕️ Coffee, please.", key='btn_coffee', use_container_width=True): user_choice = "Coffee, please."
            with col2:
                if st.button("🥛 Latte, please.", key='btn_latte', use_container_width=True): user_choice = "Latte, please."
            with col3:
                if st.button("🍵 Tea, please.", key='btn_tea', use_container_width=True): user_choice = "Tea, please."

        # --- STEP 2: 温度の選択 ---
        elif st.session_state.step == 2:
            keywords = ["hot", "iced"]
            fuzzy_rules = {"hot": ["thought", "hat", "heart", "pot"], "iced": ["ice", "eyes", "nice"]}
            with col1:
                if st.button("🔥 Hot, please.", key='btn_hot', use_container_width=True): user_choice = "Hot, please."
            with col2:
                if st.button("❄️ Iced, please.", key='btn_iced', use_container_width=True): user_choice = "Iced, please."

        # --- STEP 3: サイズの選択 ---
        elif st.session_state.step == 3:
            keywords = ["small", "medium", "large"]
            with col1:
                if st.button("🟢 Small, please.", key='btn_small', use_container_width=True): user_choice = "Small, please."
            with col2:
                if st.button("🟡 Medium, please.", key='btn_medium', use_container_width=True): user_choice = "Medium, please."
            with col3:
                if st.button("🔴 Large, please.", key='btn_large', use_container_width=True): user_choice = "Large, please."

        # --- STEP 4: フードの追加選択 ---
        elif st.session_state.step == 4:
            keywords = ["cake", "sandwich", "no"]
            
            # フード看板
            menu_col1, menu_col2, menu_col3 = st.columns(3)
            with menu_col1:
                st.markdown("<div class='menu-card'><p class='menu-card-title'>🍰 Cake</p><p style='color:#aaa; font-size:0.8rem; margin:0;'>+$6.50</p></div>", unsafe_allow_html=True)
                if os.path.exists(item_images["cake"]): st.image(item_images["cake"], use_container_width=True)
            with menu_col2:
                st.markdown("<div class='menu-card'><p class='menu-card-title'>🥪 Sandwich</p><p style='color:#aaa; font-size:0.8rem; margin:0;'>+$8.50</p></div>", unsafe_allow_html=True)
                if os.path.exists(item_images["sandwich"]): st.image(item_images["sandwich"], use_container_width=True)
            with menu_col3:
                st.markdown("<div class='menu-card'><p class='menu-card-title'>❌ No Food</p><p style='color:#aaa; font-size:0.8rem; margin:0;'>$0.00</p></div>", unsafe_allow_html=True)

            with col1:
                if st.button("🍰 Cake, please.", key='btn_cake', use_container_width=True): user_choice = "Cake, please."
            with col2:
                if st.button("🥪 Sandwich, please.", key='btn_sandwich', use_container_width=True): user_choice = "Sandwich, please."
            with col3:
                if st.button("❌ No, thank you.", key='btn_no_food', use_container_width=True): user_choice = "No, thank you."
                
        # --- STEP 5: 店内 or お持ち帰り ---
        elif st.session_state.step == 5:
            keywords = ["here", "go"]
            with col1:
                if st.button("🏠 For here, please.", key='btn_here', use_container_width=True): user_choice = "For here, please."
            with col2:
                if st.button("🛍️ To go, please.", key='btn_go', use_container_width=True): user_choice = "To go, please."
                
        # --- STEP 6: お会計（お札タップまたはマイクでお支払い） ---
        elif st.session_state.step == 6:
            keywords = ["5", "10", "20", "five", "ten", "twenty", "card"]
            fuzzy_rules = {"5": ["five dollars"], "10": ["ten dollars"], "20": ["twenty dollars"]}
            
            st.markdown("<p style='color:#ffd700; font-weight:bold; font-size:1.0rem; text-align:center; margin-bottom:10px;'>💳 Tap cash to pay (お札をタップして支払う)</p>", unsafe_allow_html=True)
            
            with col1:
                if total_p <= 5.0:
                    if os.path.exists(cash_images["5"]):
                        st.image(cash_images["5"], use_container_width=True, output_format="PNG")
                        if st.button("👉 Give $5.00", key='btn_img_pay_5', use_container_width=True): user_choice = "Here is 5 dollars."
                    else:
                        if st.button("💵 Here is $5.00", key='btn_pay_5', use_container_width=True): user_choice = "Here is 5 dollars."
                else:
                    st.markdown("<div style='text-align:center; opacity:0.35;'><span style='font-size:0.8rem; color:#fff; font-weight:bold;'>Not Enough</span></div>", unsafe_allow_html=True)
                    if os.path.exists(cash_images["5"]):
                        st.image(cash_images["5"], use_container_width=True, output_format="PNG")
                    st.button("💵 $5.00 (足りません)", key='btn_pay_5_dis', disabled=True, use_container_width=True)
            
            with col2:
                if total_p <= 10.0:
                    if os.path.exists(cash_images["10"]):
                        st.image(cash_images["10"], use_container_width=True, output_format="PNG")
                        if st.button("👉 Give $10.00", key='btn_img_pay_10', use_container_width=True): user_choice = "Here is 10 dollars."
                    else:
                        if st.button("💵 Here is $10.00", key='btn_pay_10', use_container_width=True): user_choice = "Here is 10 dollars."
                else:
                    st.markdown("<div style='text-align:center; opacity:0.35;'><span style='font-size:0.8rem; color:#fff; font-weight:bold;'>Not Enough</span></div>", unsafe_allow_html=True)
                    if os.path.exists(cash_images["10"]):
                        st.image(cash_images["10"], use_container_width=True, output_format="PNG")
                    st.button("💵 $10.00 (足りません)", key='btn_pay_10_dis', disabled=True, use_container_width=True)
            
            with col3:
                # 20ドル札は最高金額なので常に支払いに利用可能
                if os.path.exists(cash_images["20"]):
                    st.image(cash_images["20"], use_container_width=True, output_format="PNG")
                    if st.button("👉 Give $20.00", key='btn_img_pay_20', use_container_width=True): user_choice = "Here is 20 dollars."
                else:
                    if st.button("💵 Here is $20.00", key='btn_pay_20', use_container_width=True): user_choice = "Here is 20 dollars."

            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            if st.button("💳 Pay by card, please.", key='btn_pay_card_alt', use_container_width=True): user_choice = "Card, please."

        user_typed = st.chat_input("Or type here...")
        
        raw_input_text = None
        if mic_input: raw_input_text = mic_input
        elif user_choice: raw_input_text = user_choice
        elif user_typed: raw_input_text = user_typed

        if "prevent_overlap" not in st.session_state:
            st.session_state.prevent_overlap = {"step": 0, "text": ""}

        if raw_input_text and (st.session_state.prevent_overlap["step"] != st.session_state.step or st.session_state.prevent_overlap["text"] != raw_input_text):
            matched_key = fuzzy_match(raw_input_text, keywords, fuzzy_rules)
            st.session_state.prevent_overlap["step"] = st.session_state.step
            st.session_state.prevent_overlap["text"] = raw_input_text

            if matched_key:
                import time
                time.sleep(0.5)
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
                    # ランダムイベントとして、お姉さんがフードのおすすめを聞くか判断
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
                    if matched_key in ["cake", "sandwich"]:
                        st.session_state.ordered_food = matched_key
                    else:
                        st.session_state.ordered_food = "no"
                    st.session_state.current_npc_en = "Got it! Now, is that for here or to go?"
                    st.session_state.current_npc_jp = "かしこまりました！では、店内で召し上がりますか？お持ち帰りですか？"
                    st.session_state.step = 5
                elif st.session_state.step == 5:
                    st.session_state.ordered_place = matched_key
                    st.session_state.current_npc_en = f"Perfect! Your total is ${total_p:.2f}. How would you like to pay?"
                    st.session_state.current_npc_jp = f"合計で${total_p:.2f}です。お支払い方法（現金のお札の額、またはカード）を選んでね！"
                    st.session_state.step = 6
                elif st.session_state.step == 6:
                    # お釣りのリアルタイム計算とお姉さんの手渡しメッセージ演出
                    food_msg = f" and {st.session_state.ordered_food}" if (st.session_state.ordered_food and st.session_state.ordered_food != "no") else ""
                    food_msg_jp = f"と{st.session_state.ordered_food}" if (st.session_state.ordered_food and st.session_state.ordered_food != "no") else ""
                    
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
                        if st.session_state.change_amount > 0:
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
                time.sleep(0.5)
                st.session_state.pronunciation_status = None 
                st.session_state.current_npc_en = "Sorry, could you say that again?"
                st.session_state.current_npc_jp = "すみません、もう一度おっしゃっていただけますか？"
                st.session_state.speak_now = True
                st.rerun()
    else:
        # --- 8. クリアおめでとう・スタンプ獲得とアワードの表示 ---
        if not st.session_state.stamp_processed:
            st.session_state.total_stamps += 1
            st.session_state.stamp_processed = True
            st.rerun()

        st.balloons()
        st.snow()
        st.success("🎉 Good Job! Roleplay Completed!")

        # 会員証（アワードカード）の表示
        stamps = st.session_state.total_stamps
        if stamps >= 10:
            st.markdown(f"""<div class='award-card'><div class='award-title'>👑 GRAND CAFE MASTER 👑</div><div class='award-name'>Member: {st.session_state.kid_name}</div><div class='award-badge'>👑🏆👑</div><p style='margin:0; font-size:1.0rem; color:#ffd700; font-weight:bold;'>あなたは最高峰のカフェマスターです！</p></div>""", unsafe_allow_html=True)
        elif stamps >= 5:
            st.markdown(f"""<div class='award-card' style='border-color:#ff9900;'><div class='award-title' style='color:#ff9900;'>🥇 REGULAR VIP MEMBER 🥇</div><div class='award-name'>Member: {st.session_state.kid_name}</div><div class='award-badge'>🥇✨🎖️</div><p style='margin:0; font-size:1.0rem; color:#ff9900; font-weight:bold;'>いつもありがとう！常連VIP会員証</p></div>""", unsafe_allow_html=True)
        elif stamps >= 3:
            st.markdown(f"""<div class='award-card' style='border-color:#cd7f32;'><div class='award-title' style='color:#b5733d;'>🥈 BRONZE CUSTOMER 🥈</div><div class='award-name'>Member: {st.session_state.kid_name}</div><div class='award-badge'>🥈🥉✨</div><p style='margin:0; font-size:1.0rem; color:#b5733d; font-weight:bold;'>素晴らしい！ブロンズ会員証獲得！</p></div>""", unsafe_allow_html=True)

        if st.button("🔄 Play Again (もういちど遊ぶ)", key='btn_play_again_action', use_container_width=True):
            keys_to_reset = ["step", "emotion", "ordered_drink", "drink_temp", "ordered_size", "ordered_food", "ordered_place", "ordered_payment_type", "paid_amount", "change_amount", "has_food_event", "pronunciation_status", "p_heard_text", "p_matched_keyword", "prevent_overlap", "speak_now", "stamp_processed"]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
