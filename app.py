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

# --- 3. デザインCSS (エラー絶対回避 ＆ PC・スマホ両対応1画面フィット) ---
# 3-1. 背景設定 (波カッコを2重エスケープしてPythonのエラーを完全防止)
st.markdown(f"""
<style>
.stApp {{
{bg_style}
background-size: cover;
background-position: center;
background-attachment: fixed;
}}
</style>
""", unsafe_allow_html=True)

# 3-2. 静的CSS (f-string不使用。行頭のインデントスペースを完全に排除して文字漏れバグを永久に回避)
st.markdown("""
<style>
/* 全体の余白を極限まで縮小 */
.block-container {
background-color: rgba(0, 0, 0, 0.15); 
padding: 0.5rem !important;
}
.game-title {
color: #ffffff;
text-align: center;
font-family: 'Helvetica Neue', Arial, sans-serif;
font-size: 1.5rem;
font-weight: bold;
text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
margin-top: 2px;
margin-bottom: 4px;
}

/* お姉さん表示エリア（高さ制限をしてスマホでのハミ出しを防御） */
.character-stage {
display: flex;
justify-content: center;
align-items: flex-end;
height: 280px; 
margin-bottom: 6px;
position: relative;
overflow: hidden; 
border-radius: 10px;
background: rgba(0,0,0,0.25);
}
.npc-large-img {
max-height: 100%; 
width: auto;
object-fit: contain;
filter: drop-shadow(0px 8px 12px rgba(0,0,0,0.5));
animation: subtleFloat 3s infinite ease-in-out;
position: relative;
bottom: 0px; 
z-index: 5;
}

/* 注文が完成したときのプレゼント画像 */
.drink-present {
position: absolute;
bottom: 10px; 
right: 15%; 
width: 90px; 
height: 90px;
object-fit: contain;
z-index: 10; 
filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.6));
animation: popIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}
.cookie-present {
position: absolute;
bottom: 10px; 
right: 25%; 
width: 75px; 
height: 75px;
object-fit: contain;
z-index: 11; 
filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.6));
animation: popIn 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}
@keyframes popIn {
0% { transform: scale(0) rotate(-15deg); opacity: 0; }
100% { transform: scale(1) rotate(0deg); opacity: 1; }
}
@keyframes subtleFloat {
0%, 100% { transform: translateY(0); }
50% { transform: translateY(-5px); }
}

/* セリフウィンドウ（フォントサイズ調整とスリム化） */
.speech-window {
background: rgba(26, 15, 8, 0.95); 
border: 2px solid #d7c49e;
border-radius: 10px;
padding: 8px 12px;
color: #ffffff;
font-size: 1.1rem;
font-weight: bold;
box-shadow: 0 4px 12px rgba(0,0,0,0.5);
margin-bottom: 6px;
min-height: 60px;
}
.speech-sub-jp {
font-size: 0.78rem;
color: #bfaaa0;
font-weight: normal;
margin-top: 3px;
border-top: 1px dashed rgba(215, 196, 158, 0.3);
padding-top: 3px;
}

/* 極薄型のステータスレシート（画面の圧迫を防ぐ） */
.receipt-memo {
background-color: #fffef0;
border-left: 2px dashed #ccc;
border-right: 2px dashed #ccc;
border-top: 1px solid #ccc;
border-bottom: 1px solid #ccc;
padding: 4px 8px;
color: #333333;
font-family: 'Courier New', Courier, monospace;
font-size: 0.75rem;
box-shadow: 0 4px 8px rgba(0,0,0,0.15);
margin-top: 3px;
margin-bottom: 3px;
line-height: 1.2;
}
.receipt-header {
text-align: center;
font-weight: bold;
font-size: 0.8rem;
border-bottom: 1px dashed #333;
margin-bottom: 3px;
padding-bottom: 1px;
}
.receipt-item-container {
display: flex;
flex-wrap: wrap;
justify-content: space-between;
gap: 4px;
}
.receipt-item {
font-size: 0.7rem;
background: rgba(0,0,0,0.04);
padding: 1px 5px;
border-radius: 3px;
}
.receipt-total {
border-top: 1px dashed #333;
margin-top: 3px;
padding-top: 1px;
font-weight: bold;
font-size: 0.8rem;
display: flex;
justify-content: space-between;
width: 100%;
}

/* キラキラ演出用のCSS */
.star-shower {
position: absolute;
top: -10px;
left: 0;
width: 100%;
height: 100%;
z-index: 100;
pointer-events: none;
overflow: hidden;
}
.star {
position: absolute;
top: -10px;
font-size: 20px;
animation: starFall 1.2s linear forwards;
}
@keyframes starFall {
0% { transform: translateY(-10px) rotate(0deg); opacity: 0; }
10% { transform: translateY(0px) rotate(30deg); opacity: 1; }
80% { opacity: 1; }
100% { transform: translateY(350px) rotate(360deg); opacity: 0; }
}

/* 録音コンテナのコンパクトデザイン */
.mic-container {
background: rgba(255, 255, 255, 0.06);
border: 2px dashed rgba(215, 196, 158, 0.5);
padding: 6px;
border-radius: 8px;
text-align: center;
margin-bottom: 6px;
}
.equalizer-wave {
display: flex;
justify-content: center;
align-items: center;
height: 18px;
gap: 3px;
margin: 4px 0;
}
.wave-bar {
width: 4px;
height: 100%;
background-color: #ffd700;
border-radius: 2px;
animation: waveAnim 1.2s ease-in-out infinite;
}
.wave-bar:nth-child(2) { animation-delay: 0.1s; background-color: #ffb700; }
.wave-bar:nth-child(3) { animation-delay: 0.2s; background-color: #ff9900; }
.wave-bar:nth-child(4) { animation-delay: 0.3s; background-color: #ffb700; }
.wave-bar:nth-child(5) { animation-delay: 0.4s; background-color: #ffd700; }
@keyframes waveAnim {
0%, 100% { transform: scaleY(0.4); }
50% { transform: scaleY(1.0); }
}

/* 判定バッジ */
.pronunciation-badge-container {
margin-top: 4px;
margin-bottom: 4px;
background: rgba(43, 28, 17, 0.95);
border: 1.5px solid #8b5a2b;
border-radius: 8px;
padding: 6px;
display: flex;
align-items: center;
gap: 6px;
}
.badge-icon-perfect { font-size: 20px; color: #ffd700; }
.badge-icon-good { font-size: 20px; color: #50c878; }
.badge-label { color: #d7c49e; font-size: 0.7rem; font-family: monospace; }
.pron-perfect { color: #ffd700; font-weight: bold; font-size: 0.85rem; }
.pron-good { color: #50c878; font-weight: bold; font-size: 0.85rem; }

/* 📱 スマートフォン表示（横幅768px以下）での極小化設定（縦スクロールを完全に排除！） */
@media (max-width: 768px) {
.block-container {
padding: 0.2rem !important;
}
.character-stage {
height: 160px !important; 
margin-bottom: 3px !important;
}
.npc-large-img {
max-height: 100% !important;
bottom: 0px !important;
}
.drink-present {
width: 55px !important;
height: 55px !important;
bottom: 3px !important;
right: 8% !important;
}
.cookie-present {
width: 45px !important;
height: 45px !important;
bottom: 3px !important;
right: 22% !important;
}
.speech-window {
font-size: 0.95rem !important;
padding: 6px 10px !important;
min-height: 45px !important;
margin-bottom: 3px !important;
}
.speech-sub-jp {
font-size: 0.72rem !important;
margin-top: 1px !important;
padding-top: 1px !important;
}
.receipt-memo {
padding: 3px 6px !important;
font-size: 0.65rem !important;
margin-top: 1px !important;
margin-bottom: 3px !important;
}
.receipt-header {
font-size: 0.7rem !important;
margin-bottom: 1px !important;
}
.receipt-item {
font-size: 0.6rem !important;
padding: 1px 3px !important;
}
.receipt-total {
font-size: 0.7rem !important;
margin-top: 1px !important;
padding-top: 1px !important;
}
.mic-container {
padding: 4px !important;
margin-bottom: 3px !important;
}
.mic-container p {
font-size: 0.75rem !important;
margin-bottom: 1px !important;
}
.equalizer-wave {
height: 12px !important;
margin: 1px 0 !important;
}
.stButton button {
padding: 3px 6px !important;
font-size: 0.75rem !important;
min-height: 32px !important;
}
}
</style>
""", unsafe_allow_html=True)

# --- 4. ゲームの初期状態の設定 ---
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

    # イベント用
    st.session_state.has_cookie_event = False 
    st.session_state.sold_out_item = None 
    st.session_state.block_next = False 

    # 発音データ
    st.session_state.pronunciation_status = None 
    st.session_state.p_heard_text = ""
    st.session_state.p_matched_keyword = ""

# --- 5. サイドバー (音声・メニュー設定) ---
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

bgm_url = "https://archive.org/download/lofi-hiphop-cozy-vibes/Lo-Fi%20Hiphop%20-%20Cozy%20Vibes.mp3"
st.sidebar.audio(bgm_url, format="audio/mp3", loop=True)

# --- 6. 画面描画（スマホでは「お姉さん」が最初に来るように左から配置） ---
st.markdown("<p class='game-title'>La Café English Roleplay</p>", unsafe_allow_html=True)

# visual_col(お姉さん・レシート)を1番目、main_col(セリフ・ボタン)を2番目に指定
# Streamlitはスマホ時に「1番目のカラムを上、2番目のカラムを下」に配置するため、必ずお姉さんが一番上に来ます！
visual_col, main_col = st.columns([0.9, 1.1])

with visual_col:
    # 1. キャラクター＆ステージ
    active_staff_base = staff_happy_base if st.session_state.emotion == "happy" else staff_normal_base
    staff_html = f'<img class="npc-large-img" src="data:image/png;base64,{active_staff_base}">' if active_staff_base else '<div style="font-size:80px; text-align:center;">👩‍🍳</div>'

    # 1行にフラット化されたHTMLコード（改行やインデントスペースを排除して文字漏れバグを100%回避）
    star_shower_html = ""
    if st.session_state.emotion == "happy":
        star_shower_html = '<div class="star-shower"><span class="star" style="left:10vw;">🌟</span><span class="star" style="left:25vw;">✨</span><span class="star" style="left:45vw;">🌟</span><span class="star" style="left:60vw;">💫</span><span class="star" style="left:75vw;">🌟</span><span class="star" style="left:90vw;">✨</span></div>'

    drink_html = ""
    cookie_html = ""
    if st.session_state.step == 7: 
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

    # フラットなHTMLでステージを描画
    st.markdown(f'<div class="character-stage">{staff_html}{drink_html}{cookie_html}{star_shower_html}</div>', unsafe_allow_html=True)

    # 2. 超コンパクトなステータスレシート（お買い物メモ）
    item_p = 3.50 if st.session_state.ordered_drink else 0.0
    cook_p = 1.50 if st.session_state.ordered_cookie else 0.0
    total_p = item_p + cook_p
    drink_disp = st.session_state.ordered_drink.capitalize() if st.session_state.ordered_drink else "---"
    temp_disp = st.session_state.drink_temp.capitalize() if st.session_state.drink_temp else "---"
    size_disp = st.session_state.ordered_size.capitalize() if st.session_state.ordered_size else "---"
    cookie_disp = "Cookie" if st.session_state.ordered_cookie else "---"
    place_disp = "Here" if st.session_state.ordered_place == "here" else ("Go" if st.session_state.ordered_place == "go" else "---")
    payment_disp = st.session_state.ordered_payment.capitalize() if st.session_state.ordered_payment else "---"
    
    st.markdown(f'<div class="receipt-memo"><div class="receipt-header">📋 ORDER STATUS (お買い物メモ)</div><div class="receipt-item-container"><div class="receipt-item">🥤 {drink_disp}</div><div class="receipt-item">🔥 {temp_disp}</div><div class="receipt-item">📏 {size_disp}</div><div class="receipt-item">🍪 {cookie_disp}</div><div class="receipt-item">🏠 {place_disp}</div><div class="receipt-item">💳 {payment_disp}</div></div><div class="receipt-total"><span>💰 TOTAL:</span> <span>${total_p:.2f}</span></div></div>', unsafe_allow_html=True)

with main_col:
    # 音声読み上げ用の関数
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

    if st.session_state.speak_now:
        play_audio(st.session_state.current_npc_en, voice_speed, selected_voice)
        st.session_state.speak_now = False

    # セリフウィンドウ（改行やインデントスペースを完全に排除）
    st.markdown(f'<div class="speech-window"><div>{st.session_state.current_npc_en}</div><div class="speech-sub-jp">{st.session_state.current_npc_jp}</div></div>', unsafe_allow_html=True)

    # --- 7. ユーザーのアクション（音声 ＆ ボタン操作） ---
    user_choice = None
    final_mic_input = None

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
        # コンパクトマイク録音エリア
        st.markdown('<div class="mic-container">', unsafe_allow_html=True)
        st.markdown("<p style='color:#ffd700; font-weight:bold; margin-bottom:2px; font-size:0.85rem;'>🎤 声でしゃべって注文してみよう！ (英語)</p>", unsafe_allow_html=True)
        st.markdown('<div class="equalizer-wave"><div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div><div class="wave-bar"></div></div>', unsafe_allow_html=True)
        
        mic_input = speech_to_text(
            start_prompt="🔴 録音スタート (おしてしゃべる)",
            stop_prompt="⏹️ 録音おわり",
            language='en-US',
            use_container_width=True,
            key=f'speech_{st.session_state.step}' 
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.pronunciation_status:
            icon = "🌟 Perfect Pronunciation!" if st.session_state.pronunciation_status == "perfect" else "👍 Good Try! (伝わったよ！)"
            i_class = "pron-perfect" if st.session_state.pronunciation_status == "perfect" else "pron-good"
            st.markdown(f'<div class="pronunciation-badge-container"><div class="badge-icon-{"perfect" if st.session_state.pronunciation_status == "perfect" else "good"}">{"🏆" if st.session_state.pronunciation_status == "perfect" else "🎖️"}</div><div><div class="badge-label">🗣️ あなたの声: {st.session_state.p_heard_text} ➡️ 解釈: {st.session_state.p_matched_keyword}</div><div class="{i_class}">{icon}</div></div></div>', unsafe_allow_html=True)

        st.markdown("<p style='color:#fff; font-weight:bold; margin-bottom:4px; font-size:0.8rem;'>👇 または、下のボタンをおして進めてね！</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        keywords = []
        fuzzy_rules = None

        if st.session_state.step == 1:
            keywords = ["coffee", "latte", "tea"]
            with col1:
                is_so = st.session_state.sold_out_item == "coffee"
                if st.button("☕️ Coffee", disabled=is_so, key='b_c', use_container_width=True): user_choice = "Coffee, please."
            with col2:
                is_so = st.session_state.sold_out_item == "latte"
                if st.button("🥛 Latte", disabled=is_so, key='b_l', use_container_width=True): user_choice = "Latte, please."
            with col3:
                is_so = st.session_state.sold_out_item == "tea"
                if st.button("🍵 Tea", disabled=is_so, key='b_t', use_container_width=True): user_choice = "Tea, please."

        elif st.session_state.step == 2:
            keywords = ["hot", "iced"]
            fuzzy_rules = {
                "hot": ["thought", "hat", "heart", "pot"],
                "iced": ["ice", "eyes", "nice", "asked"]
            }
            with col1:
                if st.button("🔥 Hot", key='b_h', use_container_width=True): user_choice = "Hot, please."
            with col2:
                if st.button("❄️ Iced", key='b_i', use_container_width=True): user_choice = "Iced, please."

        elif st.session_state.step == 3:
            keywords = ["small", "medium", "large"]
            with col1:
                if st.button("🟢 Small", key='b_s', use_container_width=True): user_choice = "Small, please."
            with col2:
                if st.button("🟡 Medium", key='b_m', use_container_width=True): user_choice = "Medium, please."
            with col3:
                if st.button("🔴 Large", key='b_lg', use_container_width=True): user_choice = "Large, please."

        elif st.session_state.step == 4:
            keywords = ["yes", "no"]
            with col1:
                if st.button("🍪 Yes", key='b_y', use_container_width=True): user_choice = "Yes, please!"
            with col2:
                if st.button("❌ No", key='b_n', use_container_width=True): user_choice = "No, thank you."
                
        elif st.session_state.step == 5:
            keywords = ["here", "go"]
            with col1:
                if st.button("🏠 For here", key='b_fh', use_container_width=True): user_choice = "For here, please."
            with col2:
                if st.button("🛍️ To go", key='b_tg', use_container_width=True): user_choice = "To go, please."
                
        elif st.session_state.step == 6:
            keywords = ["cash", "card"]
            with col1:
                if st.button("💵 Cash", key='b_ca', use_container_width=True): user_choice = "Cash, please."
            with col2:
                if st.button("💳 Card", key='b_cd', use_container_width=True): user_choice = "By card, please."

        user_typed = st.chat_input("Or type here...")
        
        raw_input_text = None
        if mic_input:
            raw_input_text = mic_input
        elif user_choice:
            raw_input_text = user_choice
        elif user_typed:
            raw_input_text = user_typed

        if "prevent_overlap" not in st.session_state:
            st.session_state.prevent_overlap = {"step": 0, "text": ""}

        if raw_input_text and (st.session_state.prevent_overlap["step"] != st.session_state.step or st.session_state.prevent_overlap["text"] != raw_input_text):
            
            matched_key = fuzzy_match(raw_input_text, keywords, fuzzy_rules)

            st.session_state.prevent_overlap["step"] = st.session_state.step
            st.session_state.prevent_overlap["text"] = raw_input_text

            if matched_key:
                import time
                time.sleep(1.2) 
                st.session_state.pronunciation_status = None 
                
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
                    st.session_state.step = 7 
                    st.session_state.play_again = True 

                st.session_state.speak_now = True
                st.rerun()

            else:
                import time
                time.sleep(1.2) 
                st.session_state.pronunciation_status = None 
                
                s_txt = "you didn't mention an item"
                s_txt_jp = "メニューから選んでみてくださいね。"
                if keywords:
                    s_txt = f"did you say {' or '.join([f"'{k}'" for k in keywords])}?"
                    s_txt_jp = f"{'か、'.join([f'{k}（{k}）' for k in keywords])}のどちらでしょうか？"
                    
                st.session_state.current_npc_en = f"Sorry, {s_txt}"
                st.session_state.current_npc_jp = f"すみません、{s_txt_jp}"
                st.session_state.emotion = "normal"
                st.session_state.speak_now = True
                st.rerun()

    else:
        st.balloons()
        st.success("🎉 Order Completed!")
        
        if st.button("Play Again (もういちど遊ぶ)", key='play_again', use_container_width=True):
            keys_to_reset = ["step", "emotion", "ordered_drink", "drink_temp", "ordered_size", "ordered_cookie", "ordered_place", "ordered_payment", "has_cookie_event", "pronunciation_status", "p_heard_text", "p_matched_keyword", "prevent_overlap", "speak_now", "play_again"]
            for key in keys_to_reset:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
