import streamlit as st
import math

# --- 1. パスワードと機種の紐付け ---
# ここでパスワードと表示する機種を管理します
PASSWORDS = {
    "7639": "スマスロ モンキーターンV",
    "kaba888": "スマスロ 甲鉄城のカバネリ 海門決戦"
}

def check_password():
    if "authenticated_machine" not in st.session_state:
        st.session_state["authenticated_machine"] = None

    if st.session_state["authenticated_machine"] is None:
        st.title("🔑 認証が必要です")
        user_input = st.text_input("パスワードを入力してください", type="password")
        if st.button("ログイン"):
            if user_input in PASSWORDS:
                st.session_state["authenticated_machine"] = PASSWORDS[user_input]
                st.rerun()
            else:
                st.error("パスワードが違います")
        return None
    return st.session_state["authenticated_machine"]

# 認証チェック
target_machine = check_password()

if target_machine:
    # --- 共通ページ設定 ---
    st.set_page_config(page_title=f"{target_machine} 算出エンジン", layout="centered")
    
    # サイドバー：共通設定
    with st.sidebar:
        st.header("⚙️ ホール設定")
        kashidashi_mai = st.selectbox("貸出枚数 (1kあたり)", [50, 47, 46], index=2)
        koukan_rate = st.number_input("交換率 (1kあたりの回収枚数)", value=5.2, step=0.1)
        if st.button("ログアウト"):
            st.session_state["authenticated_machine"] = None
            st.rerun()

    # --- A. モンキーターンVの処理 ---
    if target_machine == "スマスロ モンキーターンV":
        st.title("🛡️ スマスロ モンキーターンV")
        
        # スペックデータ
        monkey_data = {
            "1": {"hit": 299.8, "rate": 97.9}, "2": {"hit": 295.5, "rate": 98.9},
            "3": {"hit": 276.5, "rate": 101.0}, "4": {"hit": 258.8, "rate": 104.5},
            "5": {"hit": 235.7, "rate": 110.2}, "6": {"hit": 222.9, "rate": 114.9}
        }
        
        setting = st.select_slider("設定選択", options=["1", "2", "3", "4", "5", "6"])
        conf_hit = monkey_data[setting]["hit"]
        
        col1, col2 = st.columns(2)
        with col1:
            m_cond = st.radio("状態", ["通常 (795G)", "リセット (495G)"])
            target_g = 795 if "通常" in m_cond else 495
            current_g = st.number_input("現在のハマりG", value=0)
        with col2:
            rival = st.selectbox("ライバルモード", ["なし", "榎木", "洞口", "蒲生", "浜岡", "青島", "モノクロ"])
            current_pt = st.number_input("保有pt", value=0)

        # 簡易計算ロジック
        ty = 485
        if rival == "青島": ty = 800
        elif rival == "モノクロ": ty = 1000
        
        rem_g = max(1, target_g - current_g)
        avg_inv_g = rem_g * 0.8  # 概算
        inv_mai = (avg_inv_g + 32) * (50 / 32.3)
        expected_profit = (ty * (100 / koukan_rate)) - ((inv_mai / kashidashi_mai) * 1000)

    # --- B. カバネリ 海門決戦の処理 ---
    elif target_machine == "スマスロ 甲鉄城のカバネリ 海門決戦":
        st.markdown("<style>main { background-color: #001f3f; color: white; }</style>", unsafe_allow_html=True)
        st.title("🛡️ スマスロ 甲鉄城のカバネリ 海門決戦")

        kaba_data = {
            "1": {"hit": 254.2, "st": 422.5, "rate": 97.5},
            "2": {"hit": 242.3, "st": 405.9, "rate": 98.5},
            "3": {"hit": 239.6, "st": 398.7, "rate": 100.8},
            "4": {"hit": 214.0, "st": 357.2, "rate": 106.0},
            "5": {"hit": 203.2, "st": 332.6, "rate": 111.0},
            "6": {"hit": 195.1, "st": 318.5, "rate": 114.9}
        }

        setting = st.select_slider("設定選択", options=["1", "2", "3", "4", "5", "6"])
        conf_hit = kaba_data[setting]["st"] # ST期待値をベースに計算

        st.subheader("📍 状況選択")
        k_col1, k_col2 = st.columns(2)
        with k_col1:
            state = st.radio("天井条件", ["通常 (996G)", "短縮/リセット (596G)"])
            target_g = 996 if "通常" in state else 596
        with k_col2:
            current_g = st.number_input("現在のハマりG", value=0, min_value=0)
            bonus_count = st.number_input("駿城スルー回数", value=0, min_value=0)

        # カバネリ専用ロジック
        base = 31.0
        ty = 450 # 通常ST平均
        
        # ゾーン期待度補正 (150G, 300G付近のブースト)
        boost = 1.0
        if current_g < 150: boost = 1.2
        elif current_g < 300: boost = 1.1

        rem_g = max(1, target_g - current_g)
        # 天井考慮の平均消化G数
        avg_rem_g = (rem_g * 0.75) / boost
        
        inv_mai = (avg_rem_g + 25) * (50 / base)
        inv_yen = (inv_mai / kashidashi_mai) * 1000
        out_yen = ty * (100 / koukan_rate)
        expected_profit = out_yen - inv_yen

    # --- 結果表示 (共通) ---
    st.divider()
    if expected_profit >= 0:
        st.success(f"期待収支: ＋{math.floor(expected_profit):,} 円")
    else:
        st.error(f"期待収支: {math.floor(expected_profit):,} 円")
    
    res1, res2 = st.columns(2)
    res1.metric("天井まで残り", f"{target_g - current_g} G")
    res2.metric("最大投資額", f"{math.ceil(math.ceil((target_g - current_g + 25)*(50/31))/kashidashi_mai)*1000:,} 円")
