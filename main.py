import streamlit as st
import math

# --- 0. ページ設定 (最上部で1回のみ) ---
st.set_page_config(page_title="期待値算出エンジン Pro", layout="centered")

# 翻訳防止
st.components.v1.html(
    """<script>window.parent.document.documentElement.setAttribute('lang', 'ja');
    window.parent.document.documentElement.setAttribute('class', 'notranslate');</script>""",
    height=0,
)

# --- 1. サイドバー：機種選択を1つに統合 ---
with st.sidebar:
    st.header("🎰 機種選択・設定")
    machine_mode = st.selectbox(
        "ターゲット機種", 
        ["カスタム入力", "スマスロ モンキーターンV", "L甲鉄城のカバネリ 海門決戦"], 
        index=2
    )
    st.divider()

# ==========================================================
# 🚤 【モンキーターンV / カスタム】（一切触れていません）
# ==========================================================
if machine_mode == "スマスロ モンキーターンV" or machine_mode == "カスタム入力":
    with st.sidebar:
        monkey_full_data = {
            "1": {"hit": "1/299.8", "rate": "97.9%",  "h_val": 299.8},
            "2": {"hit": "1/295.5", "rate": "98.9%",  "h_val": 295.5},
            "3": {"hit": "1/276.5", "rate": "101.0%", "h_val": 276.5},
            "4": {"hit": "1/258.8", "rate": "104.5%", "h_val": 258.8},
            "5": {"hit": "1/235.7", "rate": "110.2%", "h_val": 235.7},
            "6": {"hit": "1/222.9", "rate": "114.9%", "h_val": 222.9}
        }
        if machine_mode == "スマスロ モンキーターンV":
            st.subheader("📊 モンキー専用 公表値")
            selected_setting = st.radio("設定選択", ["1", "2", "3", "4", "5", "6"], horizontal=True)
            d = monkey_full_data[selected_setting]
            st.info(f"設定{selected_setting}\n\n初当り\n{d['hit']}\n\n機械割\n{d['rate']}")
            conf_hit = d['h_val']
        else:
            st.subheader("⚙️ カスタム設定")
            conf_hit = st.number_input("公表初当り確率 (1/x)", value=300.0, step=1.0)
        
        st.divider()
        kashidashi_mai = st.selectbox("貸出枚数 (1kあたり)", [50, 47, 46], index=2)
        koukan_rate = st.number_input("交換率 (1kあたりの回収枚数)", value=5.2, step=0.1)

    st.title(f"🛡️ {machine_mode}")
    d_base, d_target_g, d_exp_out, d_c1_pt, d_c6_pt, d_normal_pt = 32.3, 795, 485, 222, 444, 100
    
    if machine_mode == "スマスロ モンキーターンV":
        st.subheader("🕵️ モンキー専用：状況選択")
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            m_condition = st.radio("天井設定", ["通常時 (795G)", "リセット (495G)"])
            d_target_g, d_target_cycle = (795, 6) if "通常" in m_condition else (495, 4)
        with m_col2:
            m_rival_full = st.selectbox("状態・ライバル", ["なし", "榎木 (優出モード期待度50％以上)", "洞口 (シナリオ ギャンブラー以上)", "蒲生 (強チェで超抜チャレンジ濃厚)", "浜岡 (規定激走最大222pt)", "青島 (青島SG濃厚)", "モノクロ波多野 (最強のB2 or 艇王)"])
            if "浜岡" in m_rival_full: d_c1_pt = d_c6_pt = d_normal_pt = 222
            if "青島" in m_rival_full: d_exp_out = 800
            elif "モノクロ" in m_rival_full: d_exp_out = 1000
    else: d_target_cycle = 6
    
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
        t_pt = d_c1_pt if current_cycle == 1 else (d_c6_pt if current_cycle == target_cycle else d_normal_pt)
        target_pt = st.number_input("周期の天井pt", value=int(t_pt))

    st.divider()
    final_base = st.number_input("50枚あたりの回転数(G)", value=float(d_base), step=0.1)
    final_exp_out = st.number_input("期待獲得枚数(TY)", value=int(d_exp_out), step=5)
    
    limit_rem_g = max(1, target_g - current_g)
    base_prob = 1 / conf_hit
    ep = base_prob * (0.9 if limit_rem_g > 600 else 1.1 if limit_rem_g > 400 else 1.5 if limit_rem_g > 200 else 2.5 if limit_rem_g > 100 else 5.0)
    avg_rem_g = (1/ep) * (1 - math.pow(1 - ep, limit_rem_g)) if ep > 0 else limit_rem_g
    
    inv_mai = (avg_rem_g + 32) * (50 / final_base)
    expected_profit = (final_exp_out * (100 / koukan_rate)) - ((inv_mai / kashidashi_mai) * 1000)
    
    st.divider()
    if expected_profit >= 0: st.success(f"期待収支: ＋{math.floor(expected_profit):,} 円")
    else: st.error(f"期待収支: {math.floor(expected_profit):,} 円")
    res1, res2, res3 = st.columns(3)
    with res1: st.metric("天井まで残り", f"{limit_rem_g} G")
    with res2: st.metric("最大投資枚数", f"{math.ceil((limit_rem_g+32)*(50/final_base))} 枚")
    with res3: st.metric("最大投資額", f"{math.ceil(math.ceil((limit_rem_g+32)*(50/final_base))/kashidashi_mai)*1000:,} 円")

# ==========================================================
# 🛡️ 【L甲鉄城のカバネリ 海門決戦】表示 (ここを100%修正)
# ==========================================================
elif machine_mode == "L甲鉄城のカバネリ 海門決戦":
    with st.sidebar:
        st.header("🎰 機種・ホール設定")
        kaba_full_data = {
            "1": {"hit": "1/254.2", "st": "1/422.5", "rate": "97.5%",  "hit_val": 254.2},
            "2": {"hit": "1/242.3", "st": "1/405.9", "rate": "98.5%",  "hit_val": 242.3},
            "3": {"hit": "1/239.6", "st": "1/398.7", "rate": "100.8%", "hit_val": 239.6},
            "4": {"hit": "1/214.0", "st": "1/357.2", "rate": "106.0%", "hit_val": 214.0},
            "5": {"hit": "1/203.2", "st": "1/332.6", "rate": "111.0%", "hit_val": 203.2},
            "6": {"hit": "1/195.1", "st": "1/318.5", "rate": "114.9%", "hit_val": 195.1}
        }
        selected_setting = st.radio("設定選択", ["1", "2", "3", "4", "5", "6"], horizontal=True)
        d = kaba_full_data[selected_setting]
        
        # --- ここをご提示の形式に合わせました ---
        st.markdown(f"**設定 {selected_setting}**")
        st.markdown(f"初当り {d['hit']}")
        st.markdown(f"ST確率 {d['st']}")
        st.markdown(f"機械割 {d['rate']}")
        # --------------------------------------
        
        st.divider()
        kashidashi_mai = st.selectbox("貸出枚数 (1kあたり)", [50, 47, 46], index=2)
        koukan_rate = st.number_input("交換率 (1kあたりの枚数)", value=5.2, step=0.1)

    st.title(f"🛡️ L甲鉄城のカバネリ 海門決戦")
    mode_option = st.selectbox("滞在モード", ["通常時 (非短縮)", "リセット時", "短縮 (駆け抜け後)", "短縮 (上位後)"])
    d_target_g, d_target_cycle, d_ty = (996, 6, 630.7) if "通常" in mode_option else (596, 4, 577.3 if "リセット" in mode_option else (614.5 if "駆け抜け" in mode_option else 686.7))
    if st.checkbox("黒煙り（大）等：恩恵発動濃厚"): d_ty = 1200.0
    
    st.subheader("📍 現在の状況入力")
    col1, col2 = st.columns(2)
    with col1:
        current_g = st.number_input("現在のハマりG数", value=0, min_value=0)
        target_g = st.number_input("最大天井G数", value=int(d_target_g))
        current_diff_mai = st.number_input("現在の累計差枚数", value=0)
    with col2:
        current_cycle = st.number_input("現在の周期", value=1, min_value=1)
        target_cycle = st.number_input("最大天井周期", value=int(d_target_cycle))
        final_base = st.number_input("50枚あたりの回転数(G)", value=31.0, step=0.1)
    
    col3, col4 = st.columns(2)
    with col3: threw_count = st.number_input("スルー回数", value=0, min_value=0)
    with col4: final_exp_out = st.number_input("期待獲得枚数(TY)", value=float(d_ty), step=0.1)
    
    # ロジック計算
    limit_rem_g = max(1, target_g - current_g)
    real_ty = final_exp_out + (min(260.5, 260.5 * (current_diff_mai / 2400.0)) if current_diff_mai > 0 else 0.0)
    weight = {3:1.0, 2:0.75, 1:0.65}.get(str(threw_count), 0.60)
    base_prob = 1 / (d['hit_val'] / weight)
    boost = 20.0 if current_cycle >= target_cycle else (1.05 if current_g <= 150 else 1.25 if current_g <= 300 else 10.0 if current_g > (target_g-50) else 1.0)
    p = base_prob * boost
    
    # 期待収支用の平均投資
    avg_rem_g = (1/p) * (1 - math.pow(1 - p, limit_rem_g)) if p > 0 else limit_rem_g
    current_mochi_mai = max(0, current_diff_mai)
    avg_real_inv_mai = max(0, (avg_rem_g + 25) * (50 / final_base) - current_mochi_mai)
    expected_profit = (real_ty * (100 / koukan_rate)) - ((avg_real_inv_mai / kashidashi_mai) * 1000)
    
    # 最大投資計算 (天井直行時)
    max_inv_mai = max(0, (limit_rem_g + 25) * (50 / final_base) - current_mochi_mai)

    st.divider()
    if expected_profit >= 0: st.success(f"期待収支: ＋{math.floor(expected_profit):,} 円")
    else: st.error(f"期待収支: {math.floor(expected_profit):,} 円")
    res1, res2, res3 = st.columns(3)
    with res1: st.metric("天井まで残り", f"{limit_rem_g} G")
    with res2: st.metric("最大投資枚数", f"{math.ceil(max_inv_mai)} 枚")
    with res3: st.metric("最大投資額", f"{math.ceil(max_inv_mai/kashidashi_mai)*1000:,} 円")
