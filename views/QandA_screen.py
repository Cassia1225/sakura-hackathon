#Q and A
import streamlit as st
import pandas as pd

def QandA_screen_show():
    # ページ設定
    st.set_page_config(
        page_title="Q&A（社員向け）",
        page_icon="💬",
        layout="wide"
    )


    # FAQデータを読み込む
    faq_df = pd.read_csv(
        "data/faq.csv"
    )


    # タイトル
    st.title("Q&A（社員向け）")

    st.write(
        "給与に関する疑問を入力してください。"
        "給与コパイロットが回答します。"
    )

    st.divider()


    # 質問入力
    st.subheader("質問する")

    question = st.text_input(
        "給与について質問してください",
        placeholder="例：残業代はどのように計算されますか？"
    )


    # 質問するボタン
    if st.button("質問する", type="primary"):

        if question.strip() == "":
            st.warning("質問を入力してください。")

        else:

            # --------------------------------
            # 質問に含まれているキーワードを探す
            # --------------------------------

            matched_faq = None

            for _, faq in faq_df.iterrows():

                # FAQの質問文・カテゴリを検索対象にする
                search_text = (
                    str(faq["question"])
                    + str(faq["category"])
                )

                # 入力された単語のいずれかが含まれているか確認
                if any(
                    word in search_text
                    for word in question.split()
                ):
                    matched_faq = faq
                    break


            # --------------------------------
            # 回答表示
            # --------------------------------

            st.divider()

            st.subheader("回答")

            if matched_faq is not None:

                # 回答
                st.info(
                    matched_faq["answer"]
                )


                # --------------------------------
                # 回答の根拠
                # --------------------------------

                st.subheader("回答の根拠")

                st.write(
                    matched_faq["source"]
                )


                # --------------------------------
                # 関連FAQ
                # --------------------------------

                st.subheader("関連FAQ")

                related_ids = str(
                    matched_faq["related_faq"]
                )

                # 「;」で区切られたFAQ IDを分割
                related_id_list = [
                    faq_id.strip()
                    for faq_id in related_ids.split(";")
                    if faq_id.strip()
                ]


                # 関連FAQを取得
                related_faq = faq_df[
                    faq_df["faq_id"].isin(
                        related_id_list
                    )
                ]


                if not related_faq.empty:

                    # 関連FAQをリスト表示
                    for _, related in related_faq.iterrows():

                        st.markdown(
                            f"・**{related['question']}**"
                        )

                else:

                    st.write(
                        "関連FAQはありません。"
                    )


            else:

                st.warning(
                    "該当するFAQが見つかりませんでした。"
                )

                st.write(
                    "担当者への相談をご利用ください。"
                )


            # --------------------------------
            # 次のアクション
            # --------------------------------

            st.divider()

            st.subheader(
                "回答で解決しましたか？"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button("追加質問をする"):

                    st.info(
                        "上の質問入力欄から"
                        "追加の質問を入力してください。"
                    )

            with col2:

                if st.button("担当者へ相談"):

                    st.warning(
                        "担当者への相談画面を準備しています。"
                    )