import streamlit as st
from gtts import gTTS
import io
import base64
import os
import random
from streamlit_mic_recorder import speech_to_text

st.set_page_config(
    page_title="La Café - English Roleplay", 
    page_icon="☕",
    layout="wide"
)

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

st.markdown("""
    <style>
    .block-container {
        background-color: rgba(0, 0, 0, 0.15); 
        padding: 0.5rem !important;
    }
    .game-title {
        color: #ffffff;
        text-align: center;
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-size: 1.6rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        margin-top: 2px;
        margin-bottom: 5px;
    }
    .character-stage {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        height: 240px; 
        margin-bottom: 8px;
        position: relative;
        overflow: hidden; 
        border-radius: 10px;
        background: rgba(0,0,0,0.2);
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
    .drink-present {
        position: absolute;
        bottom: 10px; 
        right: 15%; 
        width: 80px; 
        height: 80px;
        object-fit: contain;
        z-index: 10; 
        filter: drop-shadow(0px 6px 10px rgba(0,0,0,0.6));
        animation: popIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    .cookie-present {
        position: absolute;
        bottom: 10px; 
        right: 25%; 
        width: 60px; 
        height: 60px;
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
    .speech-window {
        background: rgba(26, 15, 8, 0.95); 
        border: 2px solid #d7c49e;
        border-radius: 10px;
        padding: 10px 15px;
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        margin-bottom: 8px;
        min-height: 60px;
    }
    .speech-sub-jp {
        font-size: 0.8rem;
        color: #bfaaa0;
        font-weight: normal;
        margin-top: 4px;
        border-top: 1px dashed rgba(215, 196, 158, 0.3);
        padding-top: 4px;
    }
    .receipt-memo {
        background-color: #fffef0;
        border-left: 2px dashed #ccc;
        border-right: 2px dashed #ccc;
        border-top: 1px solid #ccc;
        border-bottom: 1px solid #ccc;
        padding: 6px 10px;
        color: #333333;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.8rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        margin-top: 5px;
        margin-bottom: 8px;
        line-height: 1.2;
    }
    .receipt-header {
        text-align: center;
        font-weight: bold;
        font-size: 0.85rem;
        border-bottom: 1px dashed #333;
        margin-bottom: 4px;
        padding-bottom: 2px;
    }
    .receipt-item-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        gap: 5px;
    }
    .receipt-item {
        font-size: 0.75rem;
        background: rgba(0,0,0,0.05);
        padding: 2px 6px;
        border-radius: 4px;
    }
    .receipt-total {
        border-top: 1px dashed #333;
        margin-top: 4px;
        padding-top: 2px;
        font-weight: bold;
        font-size: 0.85rem;
        display: flex;
        justify-content: space-between;
        width: 100%;
    }
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
    .mic-container {
        background: rgba(255, 255, 255, 0.08);
        border: 2px dashed rgba(215, 196, 158, 0.6);
        padding: 8px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 8px;
    }
    .equalizer-wave {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 20px;
        gap: 4px;
        margin: 5px 0;
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
    .pronunciation-badge-container {
        margin-top: 5px;
        margin-bottom: 5px;
        background: rgba(43, 28, 17, 0.95);
        border: 1.5px solid #8b5a2b;
        border-radius: 8px;
        padding: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .badge-icon-perfect { font-size: 24px; color: #ffd700; }
    .badge-icon-good { font-size: 24px; color: #50c878; }
    .badge-label { color: #d7c49e; font-size: 0.75rem; font-family: monospace; }
    .pron-perfect { color: #ffd700; font-weight: bold; font-size: 0.9rem; }
    .pron-good { color: #50c878; font-weight: bold; font-size: 0.9rem; }
    .menu-board {
        background-color: #1e251c;
        border: 3px double #8b5a2b;
        border-radius: 6px;
        padding: 8px;
        color: #f5f5f5;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.75rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        margin-top: 10px;
    }
    .menu-title {
        color: #ffd700;
        text-align: center;
        font-weight: bold;
        border-bottom: 1.5px dashed #ffd700;
        margin-bottom: 4px;
        padding-bottom: 2px;
    }

    @media (max-width: 768px) {
        .block-container {
            padding: 0.25rem !important;
        }
        .character-stage {
            height: 150px !important; 
            margin-bottom: 4px !important;
        }
        .npc-large-img {
            max-height: 100% !important;
            bottom: 0px !important;
        }
        .drink-present {
            width: 50px !important;
            height: 50px !important;
            bottom: 5px !important;
            right: 10% !important;
        }
        .cookie-present {
            width: 40px !important;
            height: 40px !important;
            bottom: 5px !important;
            right: 25% !important;
        }
        .speech-window {
            font-size: 0.95rem !important;
            padding: 6px 10px !important;
            min-height: 45px !important;
            margin-bottom: 4px !important;
        }
        .speech-sub-jp {
            font-size: 0.7rem !important;
            margin-top: 2px !important;
            padding-top: 2px !important;
        }
        .receipt-memo {
            padding: 4px 8px !important;
            font-size: 0.65rem !important;
            margin-top: 2px !important;
            margin-bottom: 4px !important;
        }
        .receipt-header {
            font-size: 0.7rem !important;
            margin-bottom: 2px !important;
        }
        .receipt-item {
            font-size: 0.6rem !important;
            padding: 1px 4px !important;
        }
        .receipt-total {
            font-size: 0.7rem !important;
            margin-top: 2px !important;
            padding-top: 1px !important;
        }
        .mic-container {
            padding: 4px !important;
            margin-bottom: 4px !important;
        }
        .mic-container p {
            font-size: 0.75rem !important;
            margin-bottom: 2px !important;
        }
        .equalizer-wave {
            height: 12px !important;
            margin: 2px 0 !important;
        }
        .stButton button {
            padding: 4px 6px !important;
            font-size: 0.75rem !important;
            height: auto !important;
            min-height: 32px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

if "step" not in st.session_state:
    st.session_state.step = 1 
    st.session_state.current_npc_en = "Hello! Welcome to our cafe! What can I get for you today?"
    st.session_state.current_npc_jp = "いらっしゃいませ！何にいたしますか？"
    st.session_state.emotion = "normal" 
    st.session_state.speak_now = True
    st.session_state.play_again = False

    st.session_state.ordered_drink = None 
    st.session_state.drink_temp = None  
    st.session_state.ordered_size = None  
    st.session_state.ordered_cookie = False 
    st.session_state.ordered_place = None  
    st.session_state.ordered_payment = None 

    st.session_state.has_cookie_event = False 
    st.session_state.sold_out_item = None 
    st.session_state.block_next = False 

    st.session_state.pronunciation_status = None 
    st.session_state.p_heard_text = ""
    st.session_state.p_matched_keyword = ""

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

st.markdown("<p class='game-title'>La Café English Roleplay</p>", unsafe_allow_html=True)

visual_col, main_col = st.columns([0.9, 1.1])

with visual_col:
    # Render the character panel
    active_staff_base = staff_happy_base if st.session_state.emotion == "happy" else staff_normal_base
    staff_html = f'<img class="npc-large-img" src="data:image/png;base64,{active_staff_base}">' if active_staff_base else '<div style="font-size:80px; text-align:center;">👩‍🍳</div>'

    star_shower_html = ""
    if st.session_state.emotion == "happy":
        star_shower_html = """
        <div class="star-shower">
            <span class="star" style="left: 10vw;">🌟</span>
            <span class="star" style="left: 25vw;">✨</span>
            <span class="star" style="left: 45vw;">🌟</span>
            <span class="star" style="left: 60vw;">💫</span>
            <span class="star" style="left: 75vw;">🌟</span>
            <span class="star" style="left: 90vw;">✨</span>
        </div>
        """

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

    st.markdown(f"""
    <div class="character-stage">
        {staff_html}
        {drink_html}
        {cookie_html}
        {star_shower_html}
    </div>
    """, unsafe_allow_html=True)

    # Render ultra-slim order status memo
    item_p = 3.50 if st.session_state.ordered_drink else 0.0
    cook_p = 1.50 if st.session_state.ordered_cookie else 0.0
    total_p = item_p + cook_p
    drink_disp = st.session_state.ordered_drink.capitalize() if st.session_state.ordered_drink else "---"
    temp_disp = st.session_state.drink_temp.capitalize() if st.session_state.drink_temp else "---"
    size_disp = st.session_state.ordered_size.capitalize() if st.session_state.ordered_size else "---"
    cookie_disp = "Cookie" if st.session_state.ordered_cookie else "---"
    place_disp = "Here" if st.session_state.ordered_place == "here" else ("Go" if st.session_state.ordered_place == "go" else "---")
    payment_disp = st.session_state.ordered_payment.capitalize() if st.session_state.ordered_payment else "---"
    
    st.markdown(f"""
    <div class="receipt-memo">
        <div class="receipt-header">📋 ORDER STATUS (お買い物メモ)</div>
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

with main_col:
    # Audio player generator helper
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

    # Dialogue speech bubble
    window_html = f"""
    <div class="speech-window">
        <div>{st.session_state.current_npc_en}</div>
        <div class="speech-sub-jp">{st.session_state.current_npc_jp}</div>
    </div>
    """
    st.markdown(window_html, unsafe_allow_html=True)

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
        # Micro-compact microphone panel
        st.markdown('<div class="mic-container">', unsafe_allow_html=True)
        st.markdown("<p style='color:#ffd700; font-weight:bold; margin-bottom:2px; font-size:0.8rem;'>🎤 声でしゃべって注文してみよう！ (英語)</p>", unsafe_allow_html=True)
        st.markdown("""
            <div class="equalizer-wave">
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
                <div class="wave-bar"></div>
            </div>
        """, unsafe_allow_html=True)
        
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
            st.markdown(f"""
                <div class="pronunciation-badge-container">
                    <div class="badge-icon-{"perfect" if st.session_state.pronunciation_status == "perfect" else "good"}">{"🏆" if st.session_state.pronunciation_status == "perfect" else "🎖️"}</div>
                    <div>
                        <div class="badge-label">🗣️ あなたの声: {st.session_state.p_heard_text} ➡️ 解釈: {st.session_state.p_matched_keyword}</div>
                        <div class="{i_class}">{icon}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<p style='color:#fff; font-weight:bold; margin-bottom:5px; font-size:0.8rem;'>👇 または、ボタンか文字入力でもすすめられるよ！</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        keywords = []
        fuzzy_rules = None

        if st.session_state.step == 1:
            keywords = ["coffee", "latte", "tea"]
            with col1:
                is_so = st.session_state.sold_out_item == "coffee"
                lbl = "☕️ Coffee"
                if st.button(lbl, disabled=is_so, key='b_c', use_container_width=True): user_choice = "Coffee, please."
            with col2:
                is_so = st.session_state.sold_out_item == "latte"
                lbl = "🥛 Latte"
                if st.button(lbl, disabled=is_so, key='b_l', use_container_width=True): user_choice = "Latte, please."
            with col3:
                is_so = st.session_state.sold_out_item == "tea"
                lbl = "🍵 Tea"
                if st.button(lbl, disabled=is_so, key='b_t', use_container_width=True): user_choice = "Tea, please."

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
        # Final celebratory layout
        st.balloons()
        st.success("🎉 Order Completed!")
        
        if st.button("Play Again (もういちど遊ぶ)", key='play_again', use_container_width=True):
            keys_to_reset = ["step", "emotion", "ordered_drink", "drink_temp", "ordered_size", "ordered_cookie", "ordered_place", "ordered_payment", "has_cookie_event", "pronunciation_status", "p_heard_text", "p_matched_keyword", "prevent_overlap", "speak_now", "play_again"]
            for key in keys_to_reset:
                if key in st.session_state:
                    st.session_state[key] = None
            
            # Reset default values strictly
            st.session_state.step = 1
            st.session_state.emotion = "normal"
            st.session_state.current_npc_en = "Hello! Welcome to our cafe! What can I get for you today?"
            st.session_state.current_npc_jp = "いらっしゃいませ！何にいたしますか？"
            st.session_state.speak_now = True
            st.rerun()
