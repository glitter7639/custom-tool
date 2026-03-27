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

# --- 2. パスワードチェックが成功した時だけ以下を実行 ---
if check_password():
    # --- 0. 翻訳対策 & ページ設定 ---
    st.set_page_config(page_title="期待値算出エンジン Pro", layout="centered")

    st.components.v1.html(
        """
        <script>
            window.parent.document.documentElement.setAttribute('lang', 'ja');
            window.parent.document.documentElement.setAttribute('class', 'notranslate');
        </script>
        """,
        height=0,
    )

    # --- 1. サイドバー（3列指定表記） ---
    with st.sidebar:
        st.header("🎰 機種・ホール設定")
        machine_select = st.selectbox("ターゲット機種", ["カスタム入力", "スマスロ モンキーターンV"])
        
        st.divider()

        monkey_full_data = {
            "1": {"hit": "1/299.8", "rate": "97.9%",  "h_val": 299.8, "r_val": 97.9},
            "2": {"hit": "1/295.5", "rate": "98.9%",  "h_val": 295.5, "r_val": 98.9},
            "3": {"hit": "1/276.5", "rate": "101.0%", "h_val": 276.5, "r_val": 101.0},
            "4": {"hit": "1/258.8", "rate": "104.5%", "h_val": 258.8, "r_val": 104.5},
            "5": {"hit": "1/235.7", "rate": "110.2%", "h_val": 235.7, "r_val": 110.2},
            "6": {"hit": "1/222.9", "rate": "114.9%", "h_val": 222.9, "r_val": 114.9}
        }

        if machine_select == "スマスロ モンキーターンV":
            st.subheader("📊 モンキー専用 公表値")
            selected_setting = st.radio("設定選択", ["1", "2", "3", "4", "5", "6"], horizontal=True)
            d = monkey_full_data[selected_setting]
            
            st.info(f"設定{selected_setting}\n\n初当り\n{d['hit']}\n\n機械割\n{d['rate']}")
            conf_hit = d['h_val']
            conf_rate = d['r_val']
        else:
            st.subheader("⚙️ 汎用設定")
            conf_rate = st.number_input("機械割 (%)", value=97.3, step=0.1)
            conf_hit = st.number_input("公表初当り確率 (1/x)", value=300.0, step=1.0)
        
        st.divider()
        kashidashi_mai = st.selectbox("貸出枚数 (1kあたり)", [50, 47, 46], index=2)
        koukan_rate = st.number_input("交換率 (1kあたりの回収枚数)", value=5.2, step=0.1)

    st.title(f"🛡️ {machine_select}")

    # --- 2. 初期値設定 ---
    d_base = 32.3 if machine_select == "スマスロ モンキーターンV" else 32.0
    d_target_g = 795
    d_exp_out = 485
    d_c1_pt = 222 
    d_c6_pt = 444
    d_normal_pt = 100

    # --- 3. モンキー専用：状況選択 ---
    if machine_select == "スマスロ モンキーターンV":
        st.subheader("🕵️ モンキー専用：状況選択")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            m_condition = st.radio("天井設定", ["通常時 (795G)", "リセット (495G)"])
            d_target_g = 795 if "通常" in m_condition else 495
            d_target_cycle = 6 if "通常" in m_condition else 4
        with m_col2:
            m_rival_full = st.selectbox("状態・ライバル", [
                "なし", 
                "榎木 (優出モード期待度50％以上)", 
                "洞口 (シナリオ　ギャンブラー以上)", 
                "蒲生 (強チェで超抜チャレンジ濃厚)", 
                "浜岡 (規定激走最大222pt)", 
                "青島 (青島SG濃厚)", 
                "モノクロ波多野 (最強のB2 or 艇王)",
            ])
            
            # 浜岡選択時、全ての周期pt期待値を222に固定
            if "浜岡" in m_rival_full:
                d_c1_pt = 222
                d_c6_pt = 222
                d_normal_pt = 222
                
            if "青島" in m_rival_full: d_exp_out = 800
            elif "モノクロ" in m_rival_full: d_exp_out = 1000
        st.divider()
    else:
        d_target_cycle = 6

    # --- 4. メイン入力 ---
    st.subheader("📍 現在の状況入力")
    col1, col2 = st.columns(2)
    with col1:
        current_g = st.number_input("現在のハマりG数", value=0, min_value=0)
        target_g = st.number_input("適用天井G数", value=int(d_target_g))
    with col2:
        current_cycle = st.number_input("現在の周期", value=1, min_value=1)
        target_cycle = st.number_input("天井周期", value=int(d_target_cycle))

    st.divider()
    col3, col4 = st.columns(2)
    with col3:
        total_current_g = st.number_input("AT間（累計）現在G", value=0)
        total_target_g = st.number_input("AT間（累計）天井G", value=0)
    with col4:
        current_pt = st.number_input("現在の保有周期pt", value=0)
        # 周期pt天井の動的切り替え
        if machine_select == "スマスロ モンキーターンV":
            if current_cycle == 1:
                target_pt = st.number_input("1周期目の天井pt", value=int(d_c1_pt))
            elif current_cycle == target_cycle:
                target_pt = st.number_input("天井周期の天井pt", value=int(d_c6_pt))
            else:
                target_pt = st.number_input("通常周期の天井pt", value=int(d_normal_pt))
        else:
            target_pt = st.number_input("通常周期の天井pt", value=int(d_normal_pt))

    st.divider()
    final_base = st.number_input("50枚あたりの回転数(G)", value=float(d_base), step=0.1)
    final_exp_out = st.number_input("期待獲得枚数(TY)", value=int(d_exp_out), step=5)

    # --- 5. 計算ロジック ---
    limit_rem_g = max(1, target_g - current_g)
    base_prob = 1 / conf_hit

    if limit_rem_g > 600: effective_prob = base_prob * 0.9
    elif limit_rem_g > 400: effective_prob = base_prob * 1.1
    elif limit_rem_g > 200: effective_prob = base_prob * 1.5
    elif limit_rem_g > 100: effective_prob = base_prob * 2.5
    else: effective_prob = base_prob * 5.0

    p = effective_prob
    n = limit_rem_g
    avg_rem_g = (1/p) * (1 - math.pow(1 - p, n)) if p > 0 else n

    pt_factor = current_pt / target_pt if target_pt > 0 else 0
