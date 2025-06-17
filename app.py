import streamlit as st
import matplotlib.pyplot as plt

# 換算式の辞書（論文式）
kit_formulas = {
    "Sekisui":   {"a": 3.77, "b": -2.39},
    "Denka-1":   {"a": 2.04, "b": -2.77},
    "Denka-2":   {"a": 2.08, "b": -2.73},
    "Shino-test":{"a": 2.48, "b": -5.01},
    "Nittobo":   {"a": 2.40, "b": -8.64},
    "Roche":     {"a": 1.00, "b":  0.00},
}

# リスク分類＋色付きメッセージ
def classify_lpa_risk(nmolL):
    if nmolL < 75:
        return "Low Risk（低リスク）", "success"
    elif nmolL < 125:
        return "Moderate Risk（中等度リスク）", "info"
    elif nmolL < 175:
        return "High Risk（高リスク）", "warning"
    else:
        return "Very High Risk（超高リスク）", "error"

st.set_page_config(page_title="Lp(a) Conversion & Risk Classification App", layout="centered")
st.title("Lp(a) Conversion & Risk Classification App")

st.markdown("""
検査キットの測定値（mg/dL）を**論文式でIFCC基準値（nmol/L）に換算し、そのままリスク分類まで自動表示します**。  
また、従来の2.2倍法（mg/dL×2.2）ともグラフで比較できます。
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

st.markdown(f"**IFCC conversion：{converted:.2f} nmol/L**")
st.markdown(f"**2.2x conversion）：{old_estimate:.2f} nmol/L**")

# そのままリスク分類
risk_text, risk_color = classify_lpa_risk(converted)
st.markdown("**リスク分類：**")
getattr(st, risk_color)(risk_text)

# グラフ（2.2倍法と論文換算の2値）
fig, ax = plt.subplots()
bars = ax.bar(
    [
        "IFCC conversion (nmol/L)",
        "2.2x conversion (nmol/L)"
    ],
    [converted, old_estimate],
    color=["#2ca02c", "#ff7f0e"]
)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}", ha='center')
ax.set_ylabel("Lp(a) level")
ax.set_title("Comparison of conversions")
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

st.info("参考: [Lp(a) Clinical Guidance](https://www.lpaclinicalguidance.com/)")

st.divider()
st.markdown("### 📖 参考文献")
st.markdown("""
Miida, T. et al. (2025).  
*Harmonization of Lipoprotein(a) Immunoassays Using A Serum Panel...*  
Journal of Atherosclerosis and Thrombosis, 32:580–595.  
DOI: [10.5551/jat.65238](https://doi.org/10.5551/jat.65238)
""")
