import streamlit as st
import matplotlib.pyplot as plt

# リスク分類と色リスト（低→高リスク順）
risk_table = [
    {"range": "<75 nmol/L",      "class": "Low Risk",        "color": "#b7e4c7"},
    {"range": "75–124 nmol/L",  "class": "Moderate Risk",   "color": "#ffe066"},
    {"range": "125–174 nmol/L", "class": "High Risk",       "color": "#f4978e"},
    {"range": "≥175 nmol/L",    "class": "Very High Risk",  "color": "#d7263d"},
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

def classify_lpa_risk(nmolL):
    if nmolL < 75:    return 0
    elif nmolL < 125: return 1
    elif nmolL < 175: return 2
    else:             return 3

st.set_page_config(page_title="Lp(a) 換算＆リスク判定アプリ", layout="centered")
st.title("Lp(a) 換算 & リスク分類アプリ")

# --- リスク分類表（カラフルHTMLテーブル）
st.markdown("#### Lp(a) Risk Classification Table")
risk_html = "<table style='width:100%; text-align:center; border-radius:10px; border-collapse:separate; border-spacing:5px;'>"
risk_html += "<tr>" + "".join([f"<th style='padding:7px;'>{row['range']}</th>" for row in risk_table]) + "</tr>"
risk_html += "<tr>" + "".join([f"<td style='background:{row['color']};padding:12px; border-radius:8px; font-weight:bold'>{row['class']}</td>" for row in risk_table]) + "</tr>"
risk_html += "</table>"
st.markdown(risk_html, unsafe_allow_html=True)

st.markdown("""
Enter the Lp(a) value (mg/dL) from your assay kit.  
This app converts to IFCC value (nmol/L) using the published equation **and** the 2.2x method,  
**showing the risk classification for both side by side.**
""")

st.divider()

# --- 換算＆リスク比較
st.subheader("🧪 Assay Kit → IFCC Conversion & Risk Classification")
kit = st.selectbox("Select your assay kit", list(kit_formulas.keys()))
value = st.number_input("Enter measured value (mg/dL)", min_value=0.0, step=0.1)

a = kit_formulas[kit]["a"]
b = kit_formulas[kit]["b"]
converted = a * value + b         # IFCC換算
old_estimate = value * 2.2        # 2.2倍法

st.markdown(f"**IFCC conversion：{converted:.2f} nmol/L**")
st.markdown(f"**2.2x conversion：{old_estimate:.2f} nmol/L**")

# リスク分類（両方式）
risk_idx_ifcc = classify_lpa_risk(converted)
risk_idx_old  = classify_lpa_risk(old_estimate)
risk_class_ifcc = risk_table[risk_idx_ifcc]["class"]
risk_color_ifcc = risk_table[risk_idx_ifcc]["color"]
risk_class_old  = risk_table[risk_idx_old]["class"]
risk_color_old  = risk_table[risk_idx_old]["color"]

st.markdown("### Risk Classification Comparison")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**IFCC conversion**")
    st.markdown(f"<div style='background:{risk_color_ifcc};padding:16px;border-radius:10px;width:90%;font-weight:bold;text-align:center;margin-bottom:10px'>{risk_class_ifcc}<br><span style='font-size:14px;'>({converted:.2f} nmol/L)</span></div>", unsafe_allow_html=True)
with col2:
    st.markdown("**2.2x conversion**")
    st.markdown(f"<div style='background:{risk_color_old};padding:16px;border-radius:10px;width:90%;font-weight:bold;text-align:center;margin-bottom:10px'>{risk_class_old}<br><span style='font-size:14px;'>({old_estimate:.2f} nmol/L)</span></div>", unsafe_allow_html=True)

# 警告表示（2.2倍法で過小評価時のみ）
if risk_idx_old < risk_idx_ifcc:
    st.warning("⚠️ **2.2x conversion may underestimate risk compared to IFCC conversion!**\n\n2.2倍法ではリスク分類が過小評価されることがあります。必ずIFCC換算値でリスク評価しましょう。")

# グラフ
fig, ax = plt.subplots()
bars = ax.bar(
    ["IFCC conversion (nmol/L)", "2.2x conversion (nmol/L)"],
    [converted, old_estimate],
    color=["#2ca02c", "#ff7f0e"]
)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}", ha='center')
ax.set_ylabel("Lp(a) level")
ax.set_title("Comparison of conversions")
st.pyplot(fig)

st.caption("※ '2.2x conversion' means the conventional estimate (mg/dL × 2~2.5); here 2.2x is used for calculation.")

st.divider()

# --- 逆換算
with st.expander("🔄 IFCC (nmol/L) to each kit value (mg/dL)"):
    st.markdown("Enter IFCC value (nmol/L) to estimate each kit's mg/dL value.")
    nmol_input = st.number_input("IFCC value (nmol/L)", min_value=0.0, step=0.1, key="nmol_input")
    if nmol_input > 0:
        st.markdown("**Estimated values for each kit (mg/dL):**")
        table_data = {
            kit_name: round((nmol_input - f["b"]) / f["a"], 2)
            for kit_name, f in kit_formulas.items()
        }
        st.table(table_data)

st.divider()
st.markdown("### 📖 Reference")
st.markdown("""
Miida, T. et al. (2025).  
*Harmonization of Lipoprotein(a) Immunoassays Using A Serum Panel...*  
Journal of Atherosclerosis and Thrombosis, 32:580–595.  
DOI: [10.5551/jat.65238](https://doi.org/10.5551/jat.65238)
""")
st.info("[Lp(a) Clinical Guidance](https://www.lpaclinicalguidance.com/)")

import streamlit as st
import matplotlib.pyplot as plt

# リスク分類と色リスト（低→高リスク順）
risk_table = [
    {"range": "<75 nmol/L",      "class": "Low Risk",        "color": "#b7e4c7"},
    {"range": "75–124 nmol/L",  "class": "Moderate Risk",   "color": "#ffe066"},
    {"range": "125–174 nmol/L", "class": "High Risk",       "color": "#f4978e"},
    {"range": "≥175 nmol/L",    "class": "Very High Risk",  "color": "#d7263d"},
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

def classify_lpa_risk(nmolL):
    if nmolL < 75:    return 0
    elif nmolL < 125: return 1
    elif nmolL < 175: return 2
    else:             return 3

st.set_page_config(page_title="Lp(a) 換算＆リスク判定アプリ", layout="centered")
st.title("Lp(a) 換算 & リスク分類アプリ")

# --- リスク分類表（カラフルHTMLテーブル）
st.markdown("#### Lp(a) Risk Classification Table")
risk_html = "<table style='width:100%; text-align:center; border-radius:10px; border-collapse:separate; border-spacing:5px;'>"
risk_html += "<tr>" + "".join([f"<th style='padding:7px;'>{row['range']}</th>" for row in risk_table]) + "</tr>"
risk_html += "<tr>" + "".join([f"<td style='background:{row['color']};padding:12px; border-radius:8px; font-weight:bold'>{row['class']}</td>" for row in risk_table]) + "</tr>"
risk_html += "</table>"
st.markdown(risk_html, unsafe_allow_html=True)

st.markdown("""
Enter the Lp(a) value (mg/dL) from your assay kit.  
This app converts to IFCC value (nmol/L) using the published equation **and** the 2.2x method,  
**showing the risk classification for both side by side.**
""")

st.divider()

# --- 換算＆リスク比較
st.subheader("🧪 Assay Kit → IFCC Conversion & Risk Classification")
kit = st.selectbox("Select your assay kit", list(kit_formulas.keys()))
value = st.number_input("Enter measured value (mg/dL)", min_value=0.0, step=0.1)

a = kit_formulas[kit]["a"]
b = kit_formulas[kit]["b"]
converted = a * value + b         # IFCC換算
old_estimate = value * 2.2        # 2.2倍法

st.markdown(f"**IFCC conversion：{converted:.2f} nmol/L**")
st.markdown(f"**2.2x conversion：{old_estimate:.2f} nmol/L**")

# リスク分類（両方式）
risk_idx_ifcc = classify_lpa_risk(converted)
risk_idx_old  = classify_lpa_risk(old_estimate)
risk_class_ifcc = risk_table[risk_idx_ifcc]["class"]
risk_color_ifcc = risk_table[risk_idx_ifcc]["color"]
risk_class_old  = risk_table[risk_idx_old]["class"]
risk_color_old  = risk_table[risk_idx_old]["color"]

st.markdown("### Risk Classification Comparison")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**IFCC conversion**")
    st.markdown(f"<div style='background:{risk_color_ifcc};padding:16px;border-radius:10px;width:90%;font-weight:bold;text-align:center;margin-bottom:10px'>{risk_class_ifcc}<br><span style='font-size:14px;'>({converted:.2f} nmol/L)</span></div>", unsafe_allow_html=True)
with col2:
    st.markdown("**2.2x conversion**")
    st.markdown(f"<div style='background:{risk_color_old};padding:16px;border-radius:10px;width:90%;font-weight:bold;text-align:center;margin-bottom:10px'>{risk_class_old}<br><span style='font-size:14px;'>({old_estimate:.2f} nmol/L)</span></div>", unsafe_allow_html=True)

# 警告表示（2.2倍法で過小評価時のみ）
if risk_idx_old < risk_idx_ifcc:
    st.warning("⚠️ **2.2x conversion may underestimate risk compared to IFCC conversion!**\n\n2.2倍法ではリスク分類が過小評価されることがあります。必ずIFCC換算値でリスク評価しましょう。")

# グラフ
fig, ax = plt.subplots()
bars = ax.bar(
    ["IFCC conversion (nmol/L)", "2.2x conversion (nmol/L)"],
    [converted, old_estimate],
    color=["#2ca02c", "#ff7f0e"]
)
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 2, f"{yval:.1f}", ha='center')
ax.set_ylabel("Lp(a) level")
ax.set_title("Comparison of conversions")
st.pyplot(fig)

st.caption("※ '2.2x conversion' means the conventional estimate (mg/dL × 2~2.5); here 2.2x is used for calculation.")

st.divider()

# --- 逆換算
with st.expander("🔄 IFCC (nmol/L) to each kit value (mg/dL)"):
    st.markdown("Enter IFCC value (nmol/L) to estimate each kit's mg/dL value.")
    nmol_input = st.number_input("IFCC value (nmol/L)", min_value=0.0, step=0.1, key="nmol_input")
    if nmol_input > 0:
        st.markdown("**Estimated values for each kit (mg/dL):**")
        table_data = {
            kit_name: round((nmol_input - f["b"]) / f["a"], 2)
            for kit_name, f in kit_formulas.items()
        }
        st.table(table_data)

st.divider()
st.markdown("### 📖 Reference")
st.markdown("""
Miida, T. et al. (2025).  
*Harmonization of Lipoprotein(a) Immunoassays Using A Serum Panel...*  
Journal of Atherosclerosis and Thrombosis, 32:580–595.  
DOI: [10.5551/jat.65238](https://doi.org/10.5551/jat.65238)
""")
st.info("[Lp(a) Clinical Guidance](https://www.lpaclinicalguidance.com/)")
