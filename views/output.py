import streamlit as st

def output_screen_show():
    st.set_page_config(
    page_title="給与コパイロット",
    layout="wide"
)

    st.title("処理結果 / 出力確認です")

    st.write(
        "例外対応完了後、給与出力前の最終確認を行います。"
    )

    st.divider()

    st.subheader("処理状況")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("未処理件数", "0件")

    with col2:
        st.metric("保留件数", "0件")

    with col3:
        st.metric("確認済み", "120名")

    st.divider()

    st.subheader("最終確認")

    st.write("すべての給与データを確認してください。")