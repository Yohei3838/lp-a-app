import streamlit as st
import matplotlib.pyplot as plt

# リスク分類と色リスト（低→高リスク順）
risk_table = [
    {"範囲": "＜75 nmol/L",      "分類": "Low Risk（低リスク）",      "色": "#b7e4c7"},
    {"範囲": "75～124 nmol/L",  "分類": "Moderate Risk（中等度リスク）", "色": "#ffe066"},
    {"範囲": "125～174 nmol/L", "分類": "High Risk（高リスク）",     "色": "#f4978e"},
    {"範囲": "≧175 nmol/L",     "分類": "Very High Risk（超高リスク）",  "色": "#d7263d"},
]

# 換算式の辞書（論文式）
kit_formulas = {
    "Sekisui":   {"a": 3.77, "b": -2.39},
    "Denka-1":   {"a": 2.04, "b": -2.77},
    "Denka-2":   {"a": 2.08, "b": -2.73},
    "Shino-test":{"a": 2.48, "b": -5.01},
    "Nittobo":   {"a": 2.40, "b": -8.64},
    "Roche":     {"a": 1.00, "b":  0.00},
}

# リスク分類
def classify_lpa_risk(nmolL):
    if nmolL < 75:
        return 0
    elif nmolL < 125:
        return 1
    elif nmolL < 175:
        return 2
    else:
        return 3

st.set_page_config(page_title="Lp(a) 換算＆リスク判定アプリ", layout="centered")
st.title("Lp(a) 換算 & リスク分類アプリ")

st.markdown("#### Lp(a) リスク分類一覧")

# ▼ リスク分類表（グラデ色つきHTML）
risk_html = "<table style='width:100%; text-align:center; border-radius:10px; border-collapse:separate; border-spacing:5px;'>"
risk_html += "<tr>" + "".join([f"<th style='padding:7px;'>{row['範囲']}</th>" for row in risk_table]) + "</tr>"
risk_html += "<tr>" + "".join([f"<td style='background:{row['色']};padding:12px; border-radius:8px; font-weight:bold'>{row['分類']}</td>" for row in risk_table]) + "</tr>"
risk_html += "</table>"
st.markdown(risk_html, unsafe_allow_html=True)

st.markdown("""
本アプリでは検査キット値（mg/dL）→論文式によるIFCC基準値（nmol/L）に換算し、そのままリスク分類もカラー表示します。  
2.2倍法（従来法）との比較グラフも表示します。
""")

st.divider()

# ▼ ① キットごとの精密換算とリスク分類
st.subheader("🧪 検査キット → IFCC換算とリスク分類")
kit = st.selectbox("使った検査キットを選んでください", list(kit_formulas.keys()))
value = st.number_input("測定値を入力（mg/dL）", min_value=0.0, step=0.1)

a = kit_formulas[kit]["a"]
b = kit_formulas[kit]["b"]
converted = a * value + b  # 論文式によるIFCC換算
old_estimate = value * 2.2  # 従来の2.2倍法

st.markdown(f"**IFCC換算後：{converted:.2f} nmol/L**")
st.markdown(f"**2.2倍法（従来の概算値）：{old_estimate:.2f} nmol/L**")

# リスク分類インデックス＆カラー
risk_idx = classify_lpa_risk(converted)
risk_class = risk_table[risk_idx]["分類"]
risk_color = risk_table[risk_idx]["色"]

st.markdown("**リスク分類：**")
st.markdown(
    f"<div style='background:{risk_color};padding:16px;border-radius:10px;width:70%;font-weight:bold;text-align:center;margin-bottom:10px'>{risk_class}</div>",
    unsafe_allow_html=True
)

# グラフ（2.2倍法と論文換算の2値）
fig, ax = plt.subplots()
bars = ax.bar(
    ["IFCC換算 (nmol/L)", "2.2倍法 (nmol/L)\n(従来の概算: 2~2.5倍, 今回は2.2倍で計算)"],
    [converted, old_estimate],
    color=["#2ca02c", "#ff7f0e"]
)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}", ha='center')
ax.set_ylabel("Lp(a)値")
ax.set_title("換算値の比較")
st.pyplot(fig)

st.caption("※『2.2倍法』は従来使われてきた概算（mg/dL×2~2.5）。ここでは2.2倍で計算しています。")

st.divider()

# 逆換算（IFCC→各キットmg/dL）は折り畳みで
with st.expander("🔄 IFCC(nmol/L)から各キット値(mg/dL)への逆換算（クリックで展開）"):
    st.markdown("""
    IFCC（nmol/L）の値を入力すると、各検査キットでのmg/dL測定値を逆算で一覧表示します。
    """)
    nmol_input = st.number_input("IFCC基準値（nmol/L）を入力", min_value=0.0, step=0.1, key="nmol_input")
    if nmol_input > 0:
        st.markdown("**各キットでの推定値（mg/dL）：**")
        table_data = {
            kit_name: round((nmol_input - f["b"]) / f["a"], 2)
            for kit_name, f in kit_formulas.items()
        }
        st.table(table_data)


st.divider()
st.markdown("### 📖 参考文献・サイト")
st.markdown("""
Miida, T. et al. (2025).  
*Harmonization of Lipoprotein(a) Immunoassays Using A Serum Panel...*  
Journal of Atherosclerosis and Thrombosis, 32:580–595.  
DOI: [10.5551/jat.65238](https://doi.org/10.5551/jat.65238)
""")
st.info(" [Lp(a) Clinical Guidance](https://www.lpaclinicalguidance.com/)")
