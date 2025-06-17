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

# 簡易換算
def mgdl_to_nmolL(val): return val * 2.4
def nmolL_to_mgdl(val): return val / 2.4

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

st.set_page_config(page_title="Lp(a) 換算＆リスク判定アプリ", layout="centered")
st.title("Lp(a) 換算 & リスク分類アプリ")

st.markdown("""
このアプリでは、  
- 検査キット別の精密換算（論文式、mg/dL→nmol/L）
- 簡易単位換算（mg/dL ↔ nmol/L）＋リスク分類
- **逆換算**（IFCC値から各キットのmg/dLへ）  
を一括して確認できます。
""")

st.divider()

# ▼ ① キットごとの精密換算（論文式）
st.subheader("🧪 検査キット → IFCC換算 (論文式)")
with st.expander("使い方を見る"):
    st.markdown("""
    使った検査キットと測定値（mg/dL）を入力すると、論文式に基づきIFCC基準値（nmol/L）に換算します。
    """)

kit = st.selectbox("使った検査キットを選んでください", list(kit_formulas.keys()))
value = st.number_input("測定値を入力（mg/dL）", min_value=0.0, step=0.1)

a = kit_formulas[kit]["a"]
b = kit_formulas[kit]["b"]
converted = a * value + b

st.markdown(f"**IFCC換算後：{converted:.2f} nmol/L**")

# 棒グラフ（元の値・IFCC換算後・従来2.2倍法）
old_estimate = value * 2.2
fig, ax = plt.subplots()
bars = ax.bar(
    [
        "元の値 (mg/dL)",
        "IFCC換算 (nmol/L)",
        "2.2倍法\n(従来の概算: 2~2.5倍, 今回は2.2倍で計算)"
    ],
    [value, converted, old_estimate],
    color=["#1f77b4", "#2ca02c", "#ff7f0e"]
)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}", ha='center')
ax.set_ylabel("Lp(a)値")
ax.set_title("各換算法による値の比較")
st.pyplot(fig)

st.caption("※『2.2倍法』は従来使われてきた概算（mg/dL×2~2.5）。ここでは2.2倍で計算しています。")

st.divider()

# ▼ ② 簡易換算 & リスク分類（折り畳みで表示）
with st.expander("📊 簡易換算 & Lp(a)リスク分類（クリックで展開）"):
    st.markdown("""
    国際標準のnmol/Lまたはmg/dLどちらからでも換算できます。  
    さらにリスク分類も自動表示されます（参考値）。
    """)
    unit2 = st.selectbox("単位を選択", ["mg/dL", "nmol/L"], key="unit2")
    value2 = st.number_input(f"Lp(a) の値（{unit2}）を入力してください", min_value=0.0, step=0.1, key="value2")

    if unit2 == "mg/dL":
        nmolL2 = mgdl_to_nmolL(value2)
        mgdl2 = value2
    else:
        nmolL2 = value2
        mgdl2 = nmolL_to_mgdl(value2)

    st.markdown("**換算値：**")
    st.write(f"{mgdl2:.1f} mg/dL ≒ {nmolL2:.1f} nmol/L")

    risk_text, risk_color = classify_lpa_risk(nmolL2)
    st.markdown("**推定リスク分類：**")
    # 色付きメッセージで警告を強調
    getattr(st, risk_color)(risk_text)

# ▼ ③ 逆換算：IFCC値から各キットのmg/dLを推定
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
