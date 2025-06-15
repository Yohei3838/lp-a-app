import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Lp(a) 換算アプリ", layout="centered")
st.title("Lp(a) 値換算アプリ")

st.markdown("""
このアプリでは、検査キットで得られたLp(a)値を  
**IFCC（国際標準, nmol/L）** に換算できます。  
また、**IFCCの値から各検査キットでの測定値（mg/dL）も逆算**できます。
""")

# 換算式定義
kit_formulas = {
    "Sekisui":   {"a": 3.77, "b": -2.39},
    "Denka-1":   {"a": 2.04, "b": -2.77},
    "Denka-2":   {"a": 2.08, "b": -2.73},
    "Shino-test":{"a": 2.48, "b": -5.01},
    "Nittobo":   {"a": 2.40, "b": -8.64},
    "Roche":     {"a": 1.00, "b":  0.00},  # Rocheはすでにnmol/L
}

# ▼ キット値 → IFCC換算
st.subheader("🧪 キット値 → IFCC (nmol/L)")
kit = st.selectbox("検査キットを選択してください", list(kit_formulas.keys()))
value = st.number_input("キットで測定した値（mg/dL）を入力", min_value=0.0)

a = kit_formulas[kit]["a"]
b = kit_formulas[kit]["b"]
converted = a * value + b
st.markdown(f"✅ **IFCC換算後：{converted:.2f} nmol/L**")

# グラフ表示
fig, ax = plt.subplots()
ax.bar(["元の値 (mg/dL)", "IFCC換算後 (nmol/L)"], [value, converted])
ax.set_ylabel("Lp(a) 値")
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

# ▼ 出典
st.divider()
st.markdown("### 📖 参考文献")
st.markdown("""
Miida, T. et al. (2025).  
*Harmonization of Lipoprotein(a) Immunoassays Using A Serum Panel...*  
Journal of Atherosclerosis and Thrombosis, 32:580–595.  
DOI: [10.5551/jat.65238](https://doi.org/10.5551/jat.65238)
""")
