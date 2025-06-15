import streamlit as st

st.title("Lp(a) 換算アプリ")

# キットの選択
kit = st.selectbox("使った検査キットをえらんでね", 
                   ["Sekisui", "Denka-1", "Denka-2", "Shino-test", "Nittobo", "Roche"])

# 単位の自動切り替え
input_unit = "nmol/L" if kit == "Roche" else "mg/dL"
value = st.number_input(f"{kit}で測った Lp(a) の値を入力してね（{input_unit}）", min_value=0.0)

# 各キットごとの換算式（nmol/Lに変換）
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

# 参考：nmol/L → mg/dL（目安として 1 mg/dL ≈ 2.4 nmol/L）
def to_mg_dl(nmol_val):
    return nmol_val / 2.4

# 計算
nmol = to_ifcc_nmol(kit, value)
mg_dl = to_mg_dl(nmol) if nmol is not None else None

# 結果表示
if nmol is not None and mg_dl is not None:
    st.markdown("### ✅ 結果")
    st.markdown(f"- IFCC準拠の Lp(a)： **{nmol:.2f} nmol/L**")
    st.markdown(f"- おおよその換算値： **{mg_dl:.2f} mg/dL（目安）**")
    st.caption("※ mg/dLへの換算は目安です。分子の大きさによって正確な換算は変わります。")
