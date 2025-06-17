import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# リスク分類と色リスト（低→高リスク順）
risk_table = [
    {"range": "<75 nmol/L",      "class": "低リスク",      "color": "#b7e4c7"},
    {"range": "75～124 nmol/L",  "class": "中等度リスク",  "color": "#ffe066"},
    {"range": "125～174 nmol/L", "class": "高リスク",      "color": "#f4978e"},
    {"range": "≥175 nmol/L",     "class": "超高リスク",    "color": "#d7263d"},
]

# 換算式の辞書（論文式）
kit_formulas = {
    "Sekisui":   {"a": 3.77, "b": -2.39, "unit": "mg/dL"},
    "Denka-1":   {"a": 2.04, "b": -2.77, "unit": "mg/dL"},
    "Denka-2":   {"a": 2.08, "b": -2.73, "unit": "mg/dL"},
    "Shino-test":{"a": 2.48, "b": -5.01, "unit": "mg/dL"},
    "Nittobo":   {"a": 2.40, "b": -8.64, "unit": "mg/dL"},
    "Roche":     {"a": 1.16, "b": -1.94, "unit": "nmol/L"},  # Rocheのみnmol/L入力
}

def classify_lpa_risk(nmolL):
    if nmolL < 75:    return 0
    elif nmolL < 125: return 1
    elif nmolL < 175: return 2
    else:             return 3

st.set_page_config(page_title="Lp(a) 換算＆リスク判定アプリ", layout="centered")
st.title("Lp(a) 換算 ＆ リスク分類アプリ")

# --- リスク分類表（カラフルHTMLテーブル）
st.markdown("#### Lp(a) リスク分類表")
risk_html = "<table style='width:100%; text-align:center; border-radius:10px; border-collapse:separate; border-spacing:5px;'>"
risk_html += "<tr>" + "".join([f"<th style='padding:7px;'>{row['range']}</th>" for row in risk_table]) + "</tr>"
risk_html += "<tr>" + "".join([f"<td style='background:{row['color']};padding:12px; border-radius:8px; font-weight:bold'>{row['class']}</td>" for row in risk_table]) + "</tr>"
risk_html += "</table>"
st.markdown(risk_html, unsafe_allow_html=True)

st.markdown("""
アッセイキットの Lp(a) 測定値を入力してください。  
Rocheは「nmol/L」で、他は「mg/dL」で入力します。  
論文式によるIFCC換算値と2.2倍法の両方で換算し、**それぞれリスク分類も並べて表示します**。
""")

st.divider()

# --- 換算＆リスク比較
st.subheader("🧪 キット値 → IFCC換算＆リスク分類")

kit = st.selectbox("検査キットを選択してください", list(kit_formulas.keys()))
unit = kit_formulas[kit]["unit"]
if unit == "nmol/L":
    value = st.number_input(f"測定値を入力してください（{unit}）", min_value=0.0, step=0.1)
    # Rocheは「論文式換算（1.16×値−1.94）」、2.2倍法は非適用
    ifcc = kit_formulas[kit]["a"] * value + kit_formulas[kit]["b"]
    x22  = value
    x22_caption = "2.2倍法はnmol/L入力なので意味なし"
else:
    value = st.number_input(f"測定値を入力してください（{unit}）", min_value=0.0, step=0.1)
    ifcc = kit_formulas[kit]["a"] * value + kit_formulas[kit]["b"]
    x22  = value * 2.2
    x22_caption = ""

st.markdown(f"**IFCC換算値：{ifcc:.2f} nmol/L**")
st.markdown(f"**2.2倍法による換算値：{x22:.2f} nmol/L**{'（'+x22_caption+'）' if x22_caption else ''}")

# リスク分類（両方式）
risk_idx_ifcc = classify_lpa_risk(ifcc)
risk_idx_x22  = classify_lpa_risk(x22)
risk_class_ifcc = risk_table[risk_idx_ifcc]["class"]
risk_color_ifcc = risk_table[risk_idx_ifcc]["color"]
risk_class_x22  = risk_table[risk_idx_x22]["class"]
risk_color_x22  = risk_table[risk_idx_x22]["color"]

st.markdown("### リスク分類比較")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**IFCC換算値によるリスク分類**")
    st.markdown(f"<div style='background:{risk_color_ifcc};padding:16px;border-radius:10px;width:90%;font-weight:bold;text-align:center;margin-bottom:10px'>{risk_class_ifcc}<br><span style='font-size:14px;'>({ifcc:.2f} nmol/L)</span></div>", unsafe_allow_html=True)
with col2:
    st.markdown("**2.2倍法によるリスク分類**")
    st.markdown(f"<div style='background:{risk_color_x22};padding:16px;border-radius:10px;width:90%;font-weight:bold;text-align:center;margin-bottom:10px'>{risk_class_x22}<br><span style='font-size:14px;'>({x22:.2f} nmol/L)</span></div>", unsafe_allow_html=True)

if unit != "nmol/L" and risk_idx_x22 < risk_idx_ifcc:
    st.warning("⚠️ 従来の換算ではリスク分類が過小評価される場合があります。IFCC換算値でのリスク評価を考慮してください。")

# グラフ（ラベルのみ英語）
fig, ax = plt.subplots()
bars = ax.bar(
    ["IFCC conversion (nmol/L)", "2.2x conversion (nmol/L)"],
    [ifcc, x22],
    color=["#2ca02c", "#ff7f0e"]
)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}", ha='center')
ax.set_ylabel("Lp(a) level")
ax.set_title("Comparison of conversions")
st.pyplot(fig)

st.caption("※ Rocheはnmol/L入力。他はmg/dL×論文式または2.2倍法（mg/dL × 2~2.5、ここでは2.2倍）で計算。")

st.divider()

# --- 逆換算
with st.expander("🔄 IFCC値(nmol/L)から各キット値への逆換算（クリックで展開）"):
    st.markdown("""
IFCC値（nmol/L）を入力すると、各検査キットでのmg/dLまたはnmol/L値を推定します。  
Rocheのみ出力もnmol/Lです。
    """)
    nmol_input = st.number_input("IFCC値（nmol/L）", min_value=0.0, step=0.1, key="nmol_input")
    if nmol_input > 0:
        table_data = {}
        for kit_name, f in kit_formulas.items():
            if kit_name == "Roche":
                # 逆算: (IFCC + 1.94) / 1.16
                result = round((nmol_input + 1.94) / 1.16, 2)
                table_data[kit_name + " (nmol/L)"] = result
            else:
                result = round((nmol_input - f["b"]) / f["a"], 2)
                table_data[kit_name + " (mg/dL)"] = result
        st.markdown("**各キットでの推定値：**")
        st.table(table_data)

st.divider()
st.markdown("### 📖 参考文献")
st.markdown("""
Miida, T. et al. (2025).  
*Harmonization of Lipoprotein(a) Immunoassays Using A Serum Panel...*  
Journal of Atherosclerosis and Thrombosis, 32:580–595.  
DOI: [10.5551/jat.65238](https://doi.org/10.5551/jat.65238)
""")
st.info("[Lp(a) Clinical Guidance](https://www.lpaclinicalguidance.com/)")

# --- 補足資料
with st.expander("📊 補足資料：キットごと・換算法ごとのリスク分類比較"):
    st.markdown("""
1つの値を入力すると、すべてのキットで同じ値を使って換算・リスク分類を比較できます。  
Rocheはnmol/L、それ以外はmg/dLで入力してください。  
⚠️マークが出ている場合は「2.2倍法」でリスクが過小評価されています。
    """)

    common_value = st.number_input("共通の測定値を入力（mg/dL、Rocheはnmol/L）", min_value=0.0, step=0.1, key="common_value")

    data = []
    if common_value > 0:
        for kit, f in kit_formulas.items():
            if kit == "Roche":
                ifcc = 1.16 * common_value - 1.94
                x22  = common_value  # nmol/Lなので2.2倍法は意味なし
                idx_ifcc = classify_lpa_risk(ifcc)
                idx_x22  = classify_lpa_risk(x22)
                note = "2.2倍法は非適用"
            else:
                a = f["a"]
                b = f["b"]
                ifcc = a * common_value + b
                x22  = common_value * 2.2
                idx_ifcc = classify_lpa_risk(ifcc)
                idx_x22  = classify_lpa_risk(x22)
                note = "⚠️" if idx_x22 < idx_ifcc else ""
            row = {
                "キット名": kit,
                "入力値": common_value,
                "IFCC換算値 (nmol/L)": round(ifcc, 2),
                "IFCCリスク分類": risk_table[idx_ifcc]["class"],
                "2.2倍法 (nmol/L)": round(x22, 2),
                "2.2倍法リスク分類": risk_table[idx_x22]["class"],
                "注意": note
            }
            data.append(row)

    if data:
        df = pd.DataFrame(data)
        def color_row(row):
            color_ifcc = f'background-color: {risk_table[classify_lpa_risk(row["IFCC換算値 (nmol/L)"])]["color"]}'
            color_x22  = f'background-color: {risk_table[classify_lpa_risk(row["2.2倍法 (nmol/L)"])]["color"]}'
            return [
                "", "", "", color_ifcc, "", color_x22, ""
            ]
        st.markdown("#### リスク分類比較表")
        st.dataframe(
            df.style.apply(color_row, axis=1),
            use_container_width=True
        )
        st.caption("⚠️ : 2.2倍法ではリスク分類が過小評価されることがあります。Rocheはnmol/L入力・換算です。")
    else:
        st.info("値を入力すると比較表が表示されます。")
