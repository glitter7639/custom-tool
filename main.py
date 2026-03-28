import streamlit as st
import math

# --- 0. 翻訳対策 & ページ設定 ---
st.set_page_config(page_title="スマスロ期待値算出エンジン Pro", layout="centered")
st.components.v1.html(
    """<script>window.parent.document.documentElement.setAttribute('lang', 'ja');
    window.parent.document.documentElement.setAttribute('class', 'notranslate');</script>""",
    height=0,
)

# --- 1. パスワード認証 ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 認証が必要です")
    password = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        if password == "7639":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    st.stop()

# --- 2. サイドバー（共通設定 & 機種選択） ---
with st.sidebar:
    st.header("🎰 設定・ホール環境")
    target_machine = st.selectbox("実践機種を選択", ["L甲鉄城のカバネリ 海門決戦", "LモンキーターンV"])
    
    st.divider()
    kashidashi_mai = st.selectbox("貸出枚数 (1kあたり)", [50, 47, 46], index=2)
    koukan_rate = st.number_input("交換率 (1kあたりの枚数)", value=5.2, step=0.1)

    kaba_data = {
        "1": {"hit": "1/254.2", "st": "1/422.5", "rate": "97.5%", "hit_val": 254.2},
        "2": {"hit": "1/242.3", "st": "1/405.9", "rate": "98.5%", "hit_val": 242.3},
        "3": {"hit": "1/239.6", "st": "1/398.7", "rate": "100.8%", "hit_val": 239.6},
        "4": {"hit": "1/214.0", "st": "1/357.2", "rate": "106.0%", "hit_val": 214.0},
        "5": {"hit": "1/203.2", "st": "1/332.6", "rate": "111.0%", "hit_val": 203.2},
        "6": {"hit": "1/195.1", "st": "1/318.5", "rate": "114.9%", "hit_val": 195.1}
    }
    monkey_data = {
        "1": {"hit": "1/299.8", "rate": "97.9%", "hit_val": 299.8},
        "2": {"hit": "1/291.5", "rate": "99.1%", "hit_val": 291.5},
        "4": {"hit": "1/259.0", "rate": "104.5%", "hit_val": 259.0},
        "5": {"hit": "1/238.9", "rate": "110.2%", "hit_val": 238.9},
        "6": {"hit": "1/222.9", "rate": "116.0%", "hit_val": 222.9}
    }

    if target_machine == "L甲鉄城のカバネリ 海門決戦":
        sel_set = st.radio("設定選択", ["1", "2", "3", "4", "5", "6"], horizontal=True)
        d = kaba_data[sel_set]
    else:
        sel_set = st.radio("設定選択", ["1", "2", "4", "5", "6"], horizontal=True)
        d = monkey_data[sel_set]

    st.markdown(f"**設定 {sel_set} スペック**")
    st.markdown(f"初当り: {d['hit']}")
    st.markdown(f"機械割: {d['rate']}")

st.title(f"🛡️ {target_machine}")

# --- 3. メインロジック分岐 ---
if target_machine == "L甲鉄城のカバネリ 海門決戦":
    st.subheader("🕵️ 滞在モード選択")
    mode_option = st.selectbox("現在の滞在モード", ["通常時 (非短縮)", "リセット時", "短縮 (駆け抜け後)", "短縮 (上位後)"])
    
    modes = {
        "通常時 (非短縮)": (996, 6, 630.7),
        "リセット時": (596, 4, 577.3),
        "短縮 (駆け抜け後)": (596, 4, 614.5),
        "短縮 (上位後)": (596, 4, 686.7)
    }
    d_target_g, d_target_cycle, d_ty = modes[mode_option]
    
    if st.checkbox("黒煙り（大）等：恩恵発動濃厚"): d_ty = 1200.0

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        current_g = st.number_input("現在のハマりG数", value=0, min_value=0)
        target_g = st.number_input("最大天井G数", value=int(d_target_g))
        current_diff_mai = st.number_input("現在の累計差枚数", value=0)
    with col2:
        current_cycle = st.number_input("現在の周期", value=1)
        target_cycle = st.number_input("最大天井周期", value=int(d_target_cycle))
        final_base = st.number_input("50枚あたりの回転数(G)", value=31.0)

    st.divider()
    col3, col4 = st.columns(2)
    with col3: threw_count = st.number_input("スルー回数", value=0)
    with col4: final_exp_out = st.number_input("期待獲得枚数(TY)", value=float(d_ty))

    max_bonus = 260.5
    yuri_boost = min(max_bonus, max_bonus * (current_diff_mai / 2400.0)) if current_diff_mai > 0 else 0
    real_ty = final_exp_out + yuri_boost
    
    weight = {3:1.0, 2:0.75, 1:0.65, 0:0.60}.get(min(threw_count, 3))
    p = (1 / (d['hit_val'] / weight))
    if current_g > (target_g - 50): p *= 10.0
    
    avg_rem_g = (1/p) * (1 - math.pow(1 - p, max(1, target_g - current_g))) if p > 0 else (target_g - current_g)
    real_inv_mai = max(0, ((avg_rem_g + 25) * (50 / final_base)) - max(0, current_diff_mai))

else:
    st.subheader("🚤 モンキーターンV 状況入力")
    col1, col2 = st.columns(2)
    with col1:
        current_g = st.number_input("現在のハマりG数", value=0)
        target_g = st.number_input("天井G数（通常795/短縮495）", value=795)
        current_diff_mai = st.number_input("現在の累計差枚数", value=0)
    with col2:
        current_pt = st.number_input("現在の激走ポイント", value=0)
        final_base = st.number_input("50枚あたりの回転数(G)", value=32.0)
        final_exp_out = st.number_input("期待獲得枚数(TY)", value=550.0)

    max_bonus_m = 1050.0 
    yuri_boost = min(max_bonus_m, max_bonus_m * (current_diff_mai / 2400.0)) if current_diff_mai > 0 else 0
    real_ty = final_exp_out + yuri_boost
    
    p_m = 1 / d['hit_val']
    avg_rem_g = (1/p_m) * (1 - math.pow(1 - p_m, max(1, target_g - current_g)))
    real_inv_mai = max(0, ((avg_rem_g + 20) * (50 / final_base)) - max(0, current_diff_mai))

expected_profit = (real_ty * (100 / koukan_rate)) - ((real_inv_mai / kashidashi_mai) * 1000)

st.divider()
if expected_profit >= 0:
    st.success(f"期待収支: ＋{math.floor(expected_profit):,} 円")
else:
    st.error(f"期待収支: {math.floor(expected_profit):,} 円")

res1, res2, res3 = st.columns(3)
with res1: st.metric("天井まで残り", f"{max(0, target_g - current_g)} G")
with res2: st.metric("追加投資枚数", f"{math.ceil(real_inv_mai)} 枚")
with res3: st.metric("補正後TY", f"{math.floor(real_ty)} 枚")
