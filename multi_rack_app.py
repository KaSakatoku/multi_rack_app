import streamlit as st
import json
from github import Github

# GitHub連携情報
REPO_NAME = "KaSakatoku/antibody-multi-rack-app"  # ← あなたの新リポジトリ名に変更
FILE_PATH = "rack.json"
g = Github(st.secrets["GITHUB_TOKEN"])
repo = g.get_repo(REPO_NAME)

# ラック定義（No1〜4：5x16、Stock Box：10x10）
RACKS = {
    "No1": (5, 16),
    "No2": (5, 16),
    "No3": (5, 16),
    "No4": (5, 16),
    "Stock Box": (10, 10),
}

# 初期データ取得
try:
    file = repo.get_contents(FILE_PATH, ref="heads/main")
    data = json.loads(file.decoded_content)
except:
    data = {name: {} for name in RACKS}

# UI表示
st.set_page_config(layout="wide")
st.title("🧪 抗体ラック管理アプリ（GitHub JSON形式・複数ラック）")

if "selected" not in st.session_state:
    st.session_state.selected = None

for rack_name, (ROWS, COLS) in RACKS.items():
    st.subheader(f"🧊 {rack_name}")
    rack = data.get(rack_name, {})
    positions = [f"{chr(65+i)}{j+1}" for i in range(ROWS) for j in range(COLS)]

    for i in range(ROWS):
        cols = st.columns(COLS)
        for j in range(COLS):
            pos = f"{chr(65+i)}{j+1}"
            ab = rack.get(pos, {"name": "", "clone": "", "fluor": ""})
            label = ab["name"] if ab["name"] else pos
            if cols[j].button(label, key=f"{rack_name}_{pos}"):
                st.session_state.selected = (rack_name, pos)

# 編集フォーム
if st.session_state.selected:
    rack_name, pos = st.session_state.selected
    st.divider()
    st.subheader(f"✏️ 編集: {rack_name} - {pos}")
    ab = data[rack_name].get(pos, {"name": "", "clone": "", "fluor": ""})

    ab["name"] = st.text_input("抗体名", ab["name"])
    ab["clone"] = st.text_input("クローン", ab["clone"])
    ab["fluor"] = st.text_input("蛍光色素", ab["fluor"])

    if st.button("保存"):
        data[rack_name][pos] = ab
        try:
            file = repo.get_contents(FILE_PATH, ref="heads/main")
            repo.update_file(
                path=FILE_PATH,
                message=f"update {rack_name} {pos}",
                content=json.dumps(data, indent=2),
                sha=file.sha
            )
        except Exception as e:
            repo.create_file(
                path=FILE_PATH,
                message=f"create {rack_name} {pos}",
                content=json.dumps(data, indent=2)
            )
        st.success("保存しました。リロードで反映されます。")
