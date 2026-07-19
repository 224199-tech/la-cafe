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
    "cookie": "images/cookie.png"
}

bg_base64 = get_image_base64(bg_path)
staff_normal_base = get_image_base64(staff_normal_path)
staff_happy_base = get_image_base64(staff_happy_path) if os.path.exists(staff_happy_path) else staff_normal_base
bg_style = f"background-image: url('data:image/jpeg;base64,{bg_base64}');" if bg_base64 else "background-color: #2b1c11;"

# --- 3. デザインCSS (1画面超圧縮 ＆ HTML文字漏れ絶対回避の1行フラット設計) ---
st.markdown(f"<style>.stApp {{{bg_style} background-size: cover; background-position: center; background-attachment: fixed;}}</style>", unsafe_allow_html=True)

st.markdown("""<style>
.block-container { background-color: rgba(0, 0, 0, 0.15); padding: 0.25rem !important; }
.game-title { color: #ffffff; text-align: center; font-family: 'Arial', sans-serif; font-size: 1.5rem; font-weight: bold; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); margin: 2px 0 5px 0; }
.character-stage { display: flex; justify-content: center; align-items: flex-end; height: 180px; margin-bottom: 4px; position: relative; overflow: hidden; border-radius: 10px; background: rgba(0,0,0,0.2); }
.npc-large-img { max-height: 100%; width: auto; object-fit: contain; filter: drop-shadow(0px 8px 12px rgba(0,0,0,0.5)); animation: subtleFloat 3s infinite ease-in-out; position: relative; bottom: 0px; z-index: 5; }
.drink-present { position: absolute; bottom: 5px; right: 10%; width: 60px; height: 60px; object-fit: contain; z-index: 10; filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.6)); animation: popIn 0.6s ease forwards; }
.cookie-present { position: absolute; bottom: 5px; right: 25%; width: 50px; height: 50px; object-fit: contain; z-index: 11; filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.6)); animation: popIn 0.7s ease forwards; }
@keyframes popIn { 0% { transform: scale(0); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
@keyframes subtleFloat { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
.speech-window { background: rgba(26, 15, 8, 0.95); border: 2px solid #d7c49e; border-radius: 10px; padding: 8px 12px; color: #ffffff; font-size: 1.0rem; font-weight: bold; box-shadow: 0 4px 15px rgba(0,0,0,0.5); margin-bottom: 4px; min-height: 50px; }
.speech-sub-jp { font-size: 0.75rem; color: #bfaaa0; font-weight: normal; margin-top: 2px; border-top: 1px dashed rgba(215, 196, 158, 0.3); padding-top: 2px; }
.receipt-memo { background-color: #fffef0; border-left: 2px dashed #ccc; border-right: 2px dashed #ccc; border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; padding: 4px 8px; color: #333333; font-family: monospace; font-size: 0.7rem; box-shadow: 0 4px 8px rgba(0,0,0,0.15); margin-top: 2px; margin-bottom: 4px; line-height: 1.2; }
.receipt-header { text-align: center; font-weight: bold; font-size: 0.75rem; border-bottom: 1px dashed #333; margin-bottom: 2px; padding-bottom: 1px; }
.receipt-item-container { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 3px; }
.receipt-item { font-size: 0.65rem; background: rgba(0,0,0,0.05); padding: 1px 4px; border-radius: 4px; }
.receipt-total { border-top: 1px dashed #333; margin-top: 2px; padding-top: 1px; font-weight: bold; font-size: 0.75rem; display: flex; justify-content: space-between; width: 100%; }
.mic-container { background: rgba(255, 255, 255, 0.08); border: 2px dashed rgba(215, 196, 158, 0.6); padding: 6px; border-radius: 10px; text-align: center; margin-bottom: 4px; }
.equalizer-wave { display: flex; justify-content: center; align-items: center; height: 15px; gap: 4px; margin: 2px 0; }
.wave-bar { width: 4px; height: 100%; background-color: #ffd700; border-radius: 2px; animation: waveAnim 1.2s ease-in-out infinite; }
.wave-bar:nth-child(2) { animation-delay: 0.1s; background-color: #ffb700; }
.wave-bar:nth-child(3) { animation-delay: 0.2s; background-color: #ff9900; }
.wave-bar:nth-child(4) { animation-delay: 0.3s; background-color: #ffb700; }
.wave-bar:nth-child(5) { animation-delay: 0.4s; background-color: #ffd700; }
@keyframes waveAnim { 0%, 100% { transform: scaleY(0.4); } 50% { transform: scaleY(1.0); } }
.pronunciation-badge-container { margin-top: 3px; margin-bottom: 3px; background: rgba(43, 28, 17, 0.95); border: 1.5px solid #8b5a2b; border-radius: 8px; padding: 6px; display: flex; align-items: center; gap: 6px; }
.badge-label { color: #d7c49e; font-size: 0.7rem; font-family: monospace; }
.pron-perfect { color: #ffd700; font-weight: bold; font-size: 0.8rem; }
.pron-good { color: #50c878; font-weight: bold; font-size: 0.8rem; }
.stButton button { padding: 4px 8px !important; font-size: 0.8rem !important; height: auto !important; min-height: 35px !important; }
.stamp-card-box { background: rgba(255, 255, 255, 0.95); border: 2px solid #ffb700; border-radius: 8px; padding: 6px; margin-top: 4px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.stamp-title { font-size: 0.75rem; font-weight: bold; color: #8b5a2b; margin-bottom: 3px; }
.stamp-grid { display: flex; justify-content: center; gap: 5px; flex-wrap: wrap; }
.stamp-slot { width: 24px; height: 24px; border-radius: 50%; border: 1.5px dashed #ccc; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; background: #fff; }
.stamp-active { border: 1.5px solid #ff4500; background: #ffe4e1; animation: stampPop 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
@keyframes stampPop { 0% { transform: scale(0) rotate(-30deg); } 100% { transform: scale(1) rotate(0deg); } }
.award-card { background: linear-gradient(135deg, #1a1a1a 0%, #3a3a3a 100%); border: 3px solid #ffd700; border-radius: 12px; padding: 15px; text-align: center; color: white; box-shadow: 0 10px 20px rgba(0,0,0,0.6); margin: 10px 0; position: relative; overflow: hidden; }
.award-title { font-size: 1.3rem; font-weight: bold; color: #ffd700; text-shadow: 0 2px 4px rgba(0,0,0,0.8); margin-bottom: 5px; }
.award-name { font-size: 1.1rem; color: #ffffff; font-family: 'Courier New', monospace; margin: 5px 0; border-bottom: 1px dashed #ffd700; padding-bottom: 5px; }
.award-badge { font-size: 2.5rem; margin: 10px 0; animation: badgeGlow 2s infinite alternate; }
@keyframes badgeGlow { 0% { transform: scale(1); filter: drop-shadow(0 0 2px #ffd700); } 100% { transform: scale(1.05); filter: drop-shadow(0 0 10px #ffd700); } }
@media (max-width: 768px) { .character-stage { height: 150px !important; } }
</style>""", unsafe_allow_html=True)

# --- 4. 永続的なグローバル状態（スタンプ・お名前）の設定 ---
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
    st.session_state.ordered_cookie = False 
    st.session_state.ordered_place = None  
    st.session_state.ordered_payment_type = None 
    st.session_state.paid_amount = 0.0
    st.session_state.change_amount = 0.0
    st.session_state.has_cookie_event = False 
    st.session_state.pronunciation_status = None 
    st.session_state.p_heard_text = ""
    st.session_state.p_matched_keyword = ""
    st.session_state.stamp_processed = False

# --- 6. サイドバー設定 (お名前入力欄) ---
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

# --- 7. 画面描画（カラム比率最適化） ---
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
    cookie_html = ""
    if st.session_state.step == 7: 
        if st.session_state.ordered_drink:
            local_drink_path = item_images.get(st.session_state.ordered_drink, "")
            if os.path.exists(local_drink_path):
                drink_html = f'<img class="drink-present" src="data:image/png;base64,{get_image_base64(local_drink_path)}">'
        if st.session_state.ordered_cookie:
            local_cookie_path = item_images.get("cookie", "")
            if os.path.exists(local_cookie_path):
                cookie_html = f'<img class="cookie-present" src="data:image/png;base64,{get_image_base64(local_cookie_path)}">'

    st.markdown(f"<div class='character-stage'>{staff_html}{drink_html}{cookie_html}{star_shower_html}</div>", unsafe_allow_html=True)

    # 2. 横長スリムレシート
    item_p = 3.50 if st.session_state.ordered_drink else 0.0
    cook_p = 1.50 if st.session_state.ordered_cookie else 0.0
    total_p = item_p + cook_p
    drink_disp = st.session_state.ordered_drink.capitalize() if st.session_state.ordered_drink else "---"
    temp_disp = st.session_state.drink_temp.capitalize() if st.session_state.drink_temp else "---"
    size_disp = st.session_state.ordered_size.capitalize() if st.session_state.ordered_size else "---"
    cookie_disp = "Cookie" if st.session_state.ordered_cookie else "---"
    place_disp = "Here" if st.session_state.ordered_place == "here" else ("Go" if st.session_state.ordered_place == "go" else "---")
    payment_disp = st.session_state.ordered_payment_type.capitalize() if st.session_state.ordered_payment_type else "---"
    
    st.markdown(f"""
    <div class="receipt-memo">
        <div class="receipt-header">📋 {st.session_state.kid_name.upper()}'S ORDER STATUS</div>
        <div class="receipt-item-container">
            <div class="receipt-item">🥤 {drink_disp}</div>
            <div class="receipt-item">🔥 {temp_disp}</div>
            <div class="receipt-item">📏 {size_disp}</div>
            <div class="receipt-item">🍪 {cookie_disp}</div>
            <div class="receipt-item">🏠 {place_disp}</div>
            <div class="receipt-item">💳 {payment_disp}</div>
        </div>
        <div class="receipt-total"><span>💰 TOTAL:</span> <span>${total_p:.2f}</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 3. リアルタイムスタンプカード表示
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

    # ロジック処理
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

        st.markdown("<p style='color:#fff; font-weight:bold; margin-bottom:4px; font-size:0.8rem;'>👇 またはボタンをタップでも進められるよ！</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        keywords = []
        fuzzy_rules = None

        if st.session_state.step == 1:
            keywords = ["coffee", "latte", "tea"]
            with col1:
                if st.button("☕️ Coffee", key='btn_coffee', use_container_width=True): user_choice = "Coffee, please."
            with col2:
                if st.button("🥛 Latte", key='btn_latte', use_container_width=True): user_choice = "Latte, please."
            with col3:
                if st.button("🍵 Tea", key='btn_tea', use_container_width=True): user_choice = "Tea, please."

        elif st.session_state.step == 2:
            keywords = ["hot", "iced"]
            fuzzy_rules = {"hot": ["thought", "hat", "heart", "pot"], "iced": ["ice", "eyes", "nice"]}
            with col1:
                if st.button("🔥 Hot", key='btn_hot', use_container_width=True): user_choice = "Hot, please."
            with col2:
                if st.button("❄️ Iced", key='btn_iced', use_container_width=True): user_choice = "Iced, please."

        elif st.session_state.step == 3:
            keywords = ["small", "medium", "large"]
            with col1:
                if st.button("🟢 Small", key='btn_small', use_container_width=True): user_choice = "Small, please."
            with col2:
                if st.button("🟡 Medium", key='btn_medium', use_container_width=True): user_choice = "Medium, please."
            with col3:
                if st.button("🔴 Large", key='btn_large', use_container_width=True): user_choice = "Large, please."

        elif st.session_state.step == 4:
            keywords = ["yes", "no"]
            with col1:
                if st.button("🍪 Yes", key='btn_yes', use_container_width=True): user_choice = "Yes, please!"
            with col2:
                if st.button("❌ No", key='btn_no', use_container_width=True): user_choice = "No, thank you."
                
        elif st.session_state.step == 5:
            keywords = ["here", "go"]
            with col1:
                if st.button("🏠 For here", key='btn_here', use_container_width=True): user_choice = "For here, please."
            with col2:
                if st.button("🛍️ To go", key='btn_go', use_container_width=True): user_choice = "To go, please."
                
        elif st.session_state.step == 6:
            # 【新お会計システム】合計金額に合わせて出せるお札を自動判定
            keywords = ["5", "10", "20", "five", "ten", "twenty", "card"]
            fuzzy_rules = {"5": ["five dollars"], "10": ["ten dollars"], "20": ["twenty dollars"]}
            
            # 合計金額に応じて出せる最低金額のボタンのみ有効にする
            with col1:
                if total_p <= 5.0:
                    if st.button("💵 Here is $5.00", key='btn_pay_5', use_container_width=True): user_choice = "Here is 5 dollars."
                else:
                    st.button("💵 $5.00 (足りません)", key='btn_pay_5_dis', disabled=True, use_container_width=True)
            with col2:
                if total_p <= 10.0:
                    if st.button("💵 Here is $10.00", key='btn_pay_10', use_container_width=True): user_choice = "Here is 10 dollars."
                else:
                    st.button("💵 $10.00 (足りません)", key='btn_pay_10_dis', disabled=True, use_container_width=True)
            with col3:
                if st.button("💵 Here is $20.00", key='btn_pay_20', use_container_width=True): user_choice = "Here is 20 dollars."
                
            # カード支払い用の選択肢も予備で配置
            if st.button("💳 By card, please.", key='btn_pay_card_alt', use_container_width=True): user_choice = "Card, please."

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
                    st.session_state.has_cookie_event = random.choice([True, False])
                    if st.session_state.has_cookie_event:
                        st.session_state.current_npc_en = "Okay! By the way, would you like a chocolate chip cookie today? It goes great with your drink!"
                        st.session_state.current_npc_jp = "かしこまりました！ところで、チョコチップクッキーもいかがですか？"
                        st.session_state.step = 4
                    else:
                        st.session_state.current_npc_en = "Okay! Is that for here or to go?"
                        st.session_state.current_npc_jp = "店内で召し上がりますか？それともお持ち帰りですか？"
                        st.session_state.step = 5
                elif st.session_state.step == 4:
                    st.session_state.ordered_cookie = (matched_key == "yes")
                    st.session_state.current_npc_en = "Got it! Now, is that for here or to go?"
                    st.session_state.current_npc_jp = "かしこまりました！では、店内で召し上がりますか？お持ち帰りですか？"
                    st.session_state.step = 5
                elif st.session_state.step == 5:
                    st.session_state.ordered_place = matched_key
                    st.session_state.current_npc_en = f"Perfect! Your total is ${total_p:.2f}. How would you like to pay?"
                    st.session_state.current_npc_jp = f"合計で${total_p:.2f}です。お支払い方法（現金のお札の額、またはカード）を選んでね！"
                    st.session_state.step = 6
                elif st.session_state.step == 6:
                    # 現金お支払い時の金額判定とお釣り計算演出
                    c_msg = " and cookie" if st.session_state.ordered_cookie else ""
                    c_msg_jp = "とクッキー" if st.session_state.ordered_cookie else ""
                    
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
                            st.session_state.current_npc_en = f"Thank you so much! Here is your change, ${st.session_state.change_amount:.2f}. And here is your drink{c_msg}. Enjoy!"
                            st.session_state.current_npc_jp = f"ありがとうございます！お釣りの${st.session_state.change_amount:.2f}です。ご注文のドリンク{c_msg_jp}もどうぞ。ごゆっくり！"
                        else:
                            st.session_state.current_npc_en = f"Thank you for the exact amount! Here is your drink{c_msg}. Enjoy your time!"
                            st.session_state.current_npc_jp = f"ちょうどのお支払いでありがとうございます！ご注文のドリンク{c_msg_jp}です。ごゆっくり！"
                    else:
                        st.session_state.current_npc_en = f"Thank you so much! Payment approved. Here is your drink{c_msg}. Enjoy your time!"
                        st.session_state.current_npc_jp = f"ありがとうございました！カード決済完了です。ご注文のドリンク{c_msg_jp}になります。ごゆっくり！"
                        
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
        # --- 8. クリア時のスタンプ加算とアワード表示処理 ---
        if not st.session_state.stamp_processed:
            st.session_state.total_stamps += 1
            st.session_state.stamp_processed = True
            st.rerun()

        st.balloons()
        st.success("🎉 Order Completed!")

        # 🎖️ デジタル会員証演出
        stamps = st.session_state.total_stamps
        if stamps >= 10:
            st.markdown(f"""<div class='award-card'><div class='award-title'>👑 GRAND CAFE MASTER 👑</div><div class='award-name'>Member: {st.session_state.kid_name}</div><div class='award-badge'>👑🏆👑</div><p style='margin:0; font-size:0.8rem; color:#ffd700;'>あなたは最高峰のカフェマスターです！</p></div>""", unsafe_allow_html=True)
        elif stamps >= 5:
            st.markdown(f"""<div class='award-card' style='border-color:#ff9900;'><div class='award-title' style='color:#ff9900;'>🥇 REGULAR VIP MEMBER 🥇</div><div class='award-name'>Member: {st.session_state.kid_name}</div><div class='award-badge'>🥇✨🎖️</div><p style='margin:0; font-size:0.8rem; color:#ff9900;'>いつもありがとう！常連VIP会員証</p></div>""", unsafe_allow_html=True)
        elif stamps >= 3:
            st.markdown(f"""<div class='award-card' style='border-color:#cd7f32;'><div class='award-title' style='color:#b5733d;'>🥈 BRONZE CUSTOMER 🥈</div><div class='award-name'>Member: {st.session_state.kid_name}</div><div class='award-badge'>🥈🥉✨</div><p style='margin:0; font-size:0.8rem; color:#b5733d;'>素晴らしい！ブロンズ会員証獲得！</p></div>""", unsafe_allow_html=True)

        if st.button("Play Again (もういちど遊ぶ)", key='btn_play_again_action', use_container_width=True):
            keys_to_reset = ["step", "emotion", "ordered_drink", "drink_temp", "ordered_size", "ordered_cookie", "ordered_place", "ordered_payment_type", "paid_amount", "change_amount", "has_cookie_event", "pronunciation_status", "p_heard_text", "p_matched_keyword", "prevent_overlap", "speak_now", "stamp_processed"]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
