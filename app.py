import streamlit as st

# ページ設定（スマホ対応）
st.set_page_config(page_title="Lp(a) 換算アプリ", layout="centered")

# タイトルと説明
st.title("Lp(a) 換算アプリ（双方向）")
st.markdown("""
このアプリでは、検査キットによって異なるLp(a)の値を  
**国際基準（IFCC, nmol/L）** と **従来の単位（mg/dL）** の間で自由に変換できます。

🧪 検査キットごとの換算式（Miidaら, 2025）に基づき、  
✅ 「mg/dL → nmol/L」  
✅ 「nmol/L → mg/dL」  
の両方向で変換できます。
""")

st.divider()

# ▼ 変換方向を選ぶ
direction = st.radio("変換したい方向を選んでください", ["mg/dL → nmol/L", "nmol/L → mg/dL"])

# ▼ 検査キットの選択肢
kit = st.selectbox("使った検査キットをえらんでね", 
                   ["Sekisui", "Denka-1", "Denka-2", "Shino-test", "Nittobo", "Roche"])

# ▼ 換算式：mg/dL → nmol/L（IFCC換算）
def to_ifcc_nmol(kit, val):
    if kit == "Sekisui":
        return 3.77 * val - 2.39
    elif kit == "Denka-1":
        return 2.04 * val - 2.77
    elif kit == "Denka-2":
        return 2.08 * val - 2.73
    elif kit == "Shino-test":
        return 2.48 * val - 5.01
    elif kit == "Nittobo":
        return 2.40 * val - 8.64
    elif kit == "Roche":
        return val  # Rocheはすでにnmol/L
    else:
        return None

# ▼ 参考換算：nmol/L → mg/dL（目安）
def to_mg_dl_from_nmol(nmol):
    return nmol / 2.4  # よく使われる係数（参考値）

# ▼ 入力と出力
if direction == "mg/dL → nmol/L":
    value = st.number_input("Lp(a) の値を入力（mg/dL）", min_value=0.0)
    nmol = to_ifcc_nmol(kit, value)
    mg_dl = value  # 入力値
    st.markdown("### ✅ 結果")
    st.markdown(f"- IFCC準拠の Lp(a)（換算後）：**{nmol:.2f} nmol/L**")
    st.markdown(f"- 元の値（参考）：**{mg_dl:.2f} mg/dL**")
    st.caption("※ 各キットごとの回帰式に基づいてnmol/Lに換算。")

elif direction == "nmol/L → mg/dL":
    value = st.number_input("Lp(a) の値を入力（nmol/L）", min_value=0.0)
    mg_dl = to_mg_dl_from_nmol(value)
    nmol = value  # 入力値
    st.markdown("### ✅ 結果")
    st.markdown(f"- おおよその換算値：**{mg_dl:.2f} mg/dL**")
    st.markdown(f"- 元の値：**{nmol:.2f} nmol/L**")
    st.caption("※ 1 mg/dL ≈ 2.4 nmol/L の係数を使った目安換算です。")

# ▼ 論文出典表示
st.divider()
st.markdown("### 📖 参考文献")
st.markdown("""
- Miida, T., Hirayama, S., Fukushima, Y., et al. (2025).  
  *Harmonization of Lipoprotein(a) Immunoassays Using A Serum Panel Value Assigned with The IFCC-Endorsed Mass Spectrometry-Based Reference Measurement Procedure.*  
  **Journal of Atherosclerosis and Thrombosis**, 32:580–595.  
  DOI: [10.5551/jat.65238](https://doi.org/10.5551/jat.65238)
""")
