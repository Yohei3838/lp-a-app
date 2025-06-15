import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Lp(a) 換算アプリ", layout="centered")
st.title("Lp(a) 値換算アプリ")

st.markdown("""
このアプリでは、検査キットで測定されたLp(a)の値を  
**国際標準（IFCC準拠, nmol/L）**に換算し、  
従来の「2.2倍法」との違いも**グラフで比較**できます。
""")

# 換算式（mg/dL → nmol/L）
kit_formulas = {
    "Sekisui":   {"a": 3.77, "b": -2.39},
    "Denka-1":   {"a": 2.04, "b": -2.77},
    "Denka-2":   {"a": 2.08, "b": -2.73},
    "Shino-test":{"a": 2.48, "b": -5.01},
    "Nittobo":   {"a": 2.40, "b": -8.64},
    "Roche":     {"a": 1.00, "b":  0.00},  # Rocheはnmol/L
}

# キット選択と入力
kit = st.selectbox("検査キットを選んでください", list(kit_formulas.keys()))
value = st.number_input("Lp(a) 測定値を入力してください（mg/dL）", min_value=0.0)

# IFCC換算
a = kit_formulas[kit]["a"]
b = kit_formulas[kit]["b"]
ifcc_nmol = a * value + b

# 従来法（2.2倍）
old_estimate = value * 2.2

# 結果表示
st.markdown(f"### IFCC換算値：**{ifcc_nmol:.2f} nmol/L**")
st.markdown(f"### 参考換算（2.2倍法）：**{old_estimate:.2f} nmol/L**")

# 📊 グラフ表示
fig, ax = plt.subplots()
bars = ax.bar(
    ["IFCC conversion", "Simple 2.2x conversion"], 
    [ifcc_nmol, old_estimate],
    color=["#1f77b4", "#ff7f0e"]
)
ax.set_ylabel("Lp(a) 値（nmol/L）")
ax.set_title("IFCC vs 2.2x conversion")
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}", ha='center')
st.pyplot(fig)

# ▼ IFCC値 → 各キットでの推定値
st.divider()
st.subheader("🔁 IFCC (nmol/L) → 各キットでの測定値（逆換算）")

nmol_input = st.number_input("IFCC（nmol/L）での値を入力", min_value=0.0)
st.markdown("各検査キットで測定した場合の推定値（mg/dL）：")

st.table({
    kit_name: round((nmol_input - f["b"]) / f["a"], 2)
    for kit_name, f in kit_formulas.items()
})

# 📖 出典
st.divider()
st.markdown("### 📖 参考文献")
st.markdown("""
Miida, T. et al. (2025).  
*Harmonization of Lipoprotein(a) Immunoassays Using A Serum Panel...*  
Journal of Atherosclerosis and Thrombosis, 32:580–595.  
DOI: [10.5551/jat.65238](https://doi.org/10.5551/jat.65238)
""")
