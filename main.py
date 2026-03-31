import streamlit as st
import math

# --- 1. 翻訳対策 & ページ設定 ---
st.set_page_config(page_title="期待値算出エンジン Pro [Free]", layout="centered")

st.components.v1.html(
    """
    <script>
        window.parent.document.documentElement.setAttribute('lang', 'ja');
        window.parent.document.documentElement.setAttribute('class', 'notranslate');
    </script>
    """,
    height=0,
)

# --- 2. サイドバー（誘導リンク & ホール設定） ---
with st.sidebar:
    st.header("🎰 機種選択")
    st.info("現在は「カスタム入力」モードです。")
    
    st.divider()
    st.subheader("🔥 専用解析エンジン（鍵付き）")
    st.caption("詳細なモード・周期補正に対応したプロ仕様版です。")
    
    # 将来的に各機種の鍵付きURLへ飛ばすリンク
    st.markdown("🔒 [スマスロ モンキーターンV](https://monkey-calc-6vnsqp7zjzewrzrhzh7kr7.streamlit.app/)")
    st.markdown("🔒 [甲鉄城のカバネリ 海門決戦](https://kabaneri-calc-bplugvhqvwesoebuwnq6gm.streamlit.app/)")
    
    st.divider()
    st.subheader("🏢 ホール設定")
    kashidashi_mai = st.selectbox("貸出枚数 (1kあたり)", [50, 47, 46], index=2)
    koukan_rate = st.number_input("交換率 (1kあたりの回収枚数)", value=5.2, step=0.1)

st.title("🛡️ 期待値算出エンジン：カスタム入力")
st.caption("※この無料版では特殊なモード補正等は行われません。")

# --- 3. メイン入力エリア（すべてゼロ/基準値スタート） ---
# カスタム時は初期値をすべてクリア
st.subheader("📍 基本スペック入力")
col1, col2 = st.columns(2)
with col1:
    conf_hit = st.number_input("初当り確率 (1/x)", value=0.0, step=1.0)
    final_base = st.number_input("50枚あたりの回転数(G)", value=32.0, step=0.1)
with col2:
    final_exp_out = st.number_input("期待獲得枚数(TY)", value=0, step=5)
    
st.divider()
st.subheader("📍 現在の状況入力")
col3, col4 = st.columns(2)
with col3:
    current_g = st.number_input("現在のハマりG数", value=0, min_value=0)
with col4:
    target_g = st.number_input("天井G数", value=0, min_value=0)

# --- 4. 計算ロジック（補正なしの純粋計算） ---
def calculate_custom_profit(target_ty):
    # 天井までの残り
    limit_rem_g = max(1, target_g - current_g)
    
    # 確率が未入力の場合は計算しない
    if conf_hit <= 0 or target_ty <= 0 or target_g <= 0:
        return 0, limit_rem_g, 0

    # 実効初当たり確率（天井までの距離で微調整のみ）
    base_prob = 1 / conf_hit
    if limit_rem_g > 400: effective_prob = base_prob * 1.1
    elif limit_rem_g > 100: effective_prob = base_prob * 2.0
    else: effective_prob = base_prob * 5.0

    p = effective_prob
    n = limit_rem_g
    avg_rem_g = (1/p) * (1 - math.pow(1 - p, n)) if p > 0 else n

    internal_avg_g = avg_rem_g + 32 
    inv_mai = internal_avg_g * (50 / final_base)
    inv_yen = (inv_mai / kashidashi_mai) * 1000
    out_yen = target_ty * (100 / koukan_rate)
    
    return out_yen - inv_yen, limit_rem_g, internal_avg_g

# 期待値算出
profit, rem_g, avg_g = calculate_custom_profit(final_exp_out)

# --- 5. 結果表示 ---
st.divider()
if profit >= 0:
    st.success(f"期待収支: ＋{math.floor(profit):,} 円")
else:
    st.error(f"期待収支: {math.floor(profit):,} 円")

m1, m2, m3 = st.columns(3)
with m1: st.metric("天井まで残り", f"{rem_g} G")
with m2: st.metric("平均投資", f"{math.ceil(avg_g * (50/final_base))} 枚")
with m3: st.metric("最大投資額", f"{math.ceil(math.ceil((rem_g+32)*(50/final_base))/kashidashi_mai)*1000:,} 円")
