import streamlit as st
import math

# --- 1. パスワード設定 ---
PASSWORD = "7639" 

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔑 認証が必要です")
        user_input = st.text_input("パスワードを入力してください", type="password")
        if st.button("ログイン"):
            if user_input == PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("パスワードが違います")
        return False
    return True

# --- 2. 実行メイン ---
if check_password():
    st.set_page_config(page_title="期待値算出エンジン Pro", layout="centered")
    st.components.v1.html(
        """<script>window.parent.document.documentElement.setAttribute('lang', 'ja');
        window.parent.document.documentElement.setAttribute('class', 'notranslate');</script>""",
        height=0,
    )

    # --- タブで機種を完全分離 ---
    tab_monkey, tab_kabaneri = st.tabs(["スマスロ モンキーターンV 🚤", "L甲鉄城のカバネリ 海門決戦 🛡️"])

    # ==========================================
    # 🚤 スマスロ モンキーターンV セクション
    # (元のコードを完全に維持)
    # ==========================================
    with tab_monkey:
        # サイドバーの設定をタブ内に反映させるための共通処理
        with st.sidebar:
            st.header("🎰 ホール共通設定")
            kashidashi_mai = st.selectbox("貸出枚数 (1kあたり)", [50, 47, 46], index=2, key="k_mai_m")
            koukan_rate = st.number_input("交換率 (1kあたりの回収枚数)", value=5.2, step=0.1, key="k_rate_m")
            st.divider()

        monkey_full_data = {
            "1": {"hit": "1/299.8", "rate": "97.9%",  "h_val": 299.8, "r_val": 97.9},
            "2": {"hit": "1/295.5", "rate": "98.9%",  "h_val": 295.5, "r_val": 98.9},
            "3": {"hit": "1/276.5", "rate": "101.0%", "h_val": 276.5, "r_val": 101.0},
            "4": {"hit": "1/258.8", "rate": "104.5%", "h_val": 258.8, "r_val": 104.5},
            "5": {"hit": "1/235.7", "rate": "110.2%", "h_val": 235.7, "r_val": 110.2},
            "6": {"hit": "1/222.9", "rate": "114.9%", "h_val": 222.9, "r_val": 114.9}
        }
        
        st.subheader("📊 設定・公表値")
        m_selected_setting = st.radio("設定選択", ["1", "2", "3", "4", "5", "6"], horizontal=True, key="m_set")
        m_d = monkey_full_data[m_selected_setting]
        st.info(f"設定{m_selected_setting} | 初当り: {m_d['hit']} | 機械割: {m_d['rate']}")
        
        m_conf_hit = m_d['h_val']

        d_base = 32.3
        d_target_g = 795
        d_exp_out = 485
        d_c1_pt = 222 
        d_c6_pt = 444
        d_normal_pt = 100

        st.subheader("🕵️ 状況選択")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            m_condition = st.radio("天井設定", ["通常時 (795G)", "リセット (495G)"], key="m_cond")
            d_target_g = 795 if "通常" in m_condition else 495
            d_target_cycle = 6 if "通常" in m_condition else 4
        with m_col2:
            m_rival = st.selectbox("状態・ライバル", ["なし", "榎木", "洞口", "蒲生", "浜岡", "青島", "モノクロ"], key="m_riv")
            if "浜岡" in m_rival: d_c1_pt, d_c6_pt, d_normal_pt = 222, 222, 222
            if "青島" in m_rival: d_exp_out = 800
            elif "モノクロ" in m_rival: d_exp_out = 1000

        col1, col2 = st.columns(2)
        with col1:
            m_current_g = st.number_input("現在のハマりG数", value=0, key="m_cg")
            m_target_g = st.number_input("適用天井G数", value=int(d_target_g), key="m_tg")
        with col2:
            m_current_cycle = st.number_input("現在の周期", value=1, key="m_cc")
            m_target_cycle = st.number_input("天井周期", value=int(d_target_cycle), key="m_tc")

        col3, col4 = st.columns(2)
        with col3:
            m_current_pt = st.number_input("現在の保有周期pt", value=0, key="m_pt")
        with col4:
            if m_current_cycle == 1: m_target_pt = st.number_input("1周期目天井pt", value=int(d_c1_pt), key="m_tpt1")
            elif m_current_cycle == m_target_cycle: m_target_pt = st.number_input("天井周期天井pt", value=int(d_c6_pt), key="m_tpt6")
            else: m_target_pt = st.number_input("通常周期天井pt", value=int(d_normal_pt), key="m_tptn")

        m_final_base = st.number_input("50枚あたりの回転数(G)", value=float(d_base), key="m_fb")
        m_final_exp_out = st.number_input("期待獲得枚数(TY)", value=int(d_exp_out), key="m_ty")

        # 計算
        m_limit_rem_g = max(1, m_target_g - m_current_g)
        m_p = 1 / m_conf_hit
        if m_limit_rem_g > 600: m_p *= 0.9
        elif m_limit_rem_g > 400: m_p *= 1.1
        elif m_limit_rem_g > 200: m_p *= 1.5
        elif m_limit_rem_g > 100: m_p *= 2.5
        else: m_p *= 5.0

        m_avg_rem_g = (1/m_p) * (1 - math.pow(1 - m_p, m_limit_rem_g))
        m_pt_factor = m_current_pt / m_target_pt if m_target_pt > 0 else 0
        m_avg_rem_g = m_avg_rem_g * (1 - (m_pt_factor * 0.35))
        
        m_inv_yen = ((m_avg_rem_g + 32) * (50 / m_final_base) / kashidashi_mai) * 1000
        m_out_yen = m_final_exp_out * (100 / koukan_rate)
        m_profit = m_out_yen - m_inv_yen

        st.divider()
        if m_profit >= 0: st.success(f"期待収支: ＋{math.floor(m_profit):,} 円")
        else: st.error(f"期待収支: {math.floor(m_profit):,} 円")

    # ==========================================
    # 🛡️ L甲鉄城のカバネリ 海門決戦 セクション
    # (独立ロジック)
    # ==========================================
    with tab_kabaneri:
        st.subheader("📊 設定・スペック")
        k_spec = {
            "1": [254.2, "97.5%"], "2": [242.3, "98.5%"], "3": [239.6, "100.8%"],
            "4": [214.0, "106.0%"], "5": [203.2, "111.0%"], "6": [195.1, "114.9%"]
        }
        k_set = st.radio("設定選択", ["1", "2", "3", "4", "5", "6"], horizontal=True, key="k_set")
        st.info(f"設定{k_set} | 初当り: 1/{k_spec[k_set][0]} | 機械割: {k_spec[k_set][1]}")
        
        k_mode = st.selectbox("滞在モード", ["通常", "リセット", "駆け抜け短縮", "美馬後短縮"], key="k_mode")
        k_targets = {"通常": (996, 630), "リセット": (596, 577), "駆け抜け短縮": (596, 614), "美馬後短縮": (596, 686)}
        
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            k_cg = st.number_input("現在のハマりG数", value=0, key="k_cg")
            k_tg = st.number_input("天井G数", value=k_targets[k_mode][0], key="k_tg")
            k_diff = st.number_input("累計差枚数 (重要)", value=0, key="k_diff")
        with col_k2:
            k_threw = st.number_input("スルー回数", value=0, key="k_threw")
            k_base = st.number_input("50枚あたりの回転数(G)", value=31.0, key="k_fb")
            k_ty_init = st.number_input("期待獲得枚数(TY)", value=k_targets[k_mode][1], key="k_ty")

        # カバネリ計算：上位83%固定(260.5枚)を差枚に応じて加算
        k_yuri_boost = min(260.5, 260.5 * (k_diff / 2400.0)) if k_diff > 0 else 0
        k_real_ty = k_ty_init + k_yuri_boost
        
        k_weight = {3:1.0, 2:0.75, 1:0.65, 0:0.60}.get(min(k_threw, 3))
        k_p = 1 / (k_spec[k_set][0] / k_weight)
        if k_cg > (k_tg - 50): k_p *= 5.0
        
        k_avg_rem_g = (1/k_p) * (1 - math.pow(1 - k_p, max(1, k_tg - k_cg)))
        k_inv_yen = ((k_avg_rem_g + 25) * (50 / k_base) / kashidashi_mai) * 1000
        k_profit = (k_real_ty * (100 / koukan_rate)) - k_inv_yen

        st.divider()
        if k_profit >= 0: st.success(f"期待収支: ＋{math.floor(k_profit):,} 円")
        else: st.error(f"期待収支: {math.floor(k_profit):,} 円")
        st.caption("※差枚がプラスであるほど上位ST期待値を加算する独自補正を適用中")
