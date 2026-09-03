#Q and A
import streamlit as st

def QandA_screen_show():
        # ページ設定
    st.set_page_config(
        page_title="Q&A（社員向け）",
        page_icon="💬",
        layout="wide"
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
        placeholder="例：今月の給与が先月より少ないのはなぜ？"
    )


    # 質問するボタン
    if st.button("質問する", type="primary"):

        if question.strip() == "":
            st.warning("質問を入力してください。")

        else:
            # 質問内容に応じて回答を作る
            if "給与" in question or "少ない" in question:

                answer = (
                    "今月の給与が先月より少ない理由として、"
                    "勤務日数や控除額の変更などが考えられます。"
                    "給与明細をご確認ください。"
                )

                reason = (
                    "給与規程 第○条および給与明細の情報を"
                    "もとにした回答です。"
                )

                faq = [
                    "給与明細の見方について",
                    "社会保険料が変わるのはなぜですか？",
                    "控除額について教えてください"
                ]

            elif "残業" in question:

                answer = (
                    "残業代は、所定の勤務時間を超えて勤務した"
                    "時間に応じて計算されます。"
                    "詳しい計算方法は給与規程をご確認ください。"
                )

                reason = (
                    "給与規程 第○条「時間外勤務手当」に"
                    "基づく回答です。"
                )

                faq = [
                    "残業代の計算方法について",
                    "休日出勤した場合の給与について",
                    "深夜勤務の割増について"
                ]

            elif "有給" in question:

                answer = (
                    "有給休暇を取得した場合の給与については、"
                    "就業規則および給与規程に定められています。"
                )

                reason = (
                    "就業規則および給与規程の有給休暇に関する"
                    "規定をもとにした回答です。"
                )

                faq = [
                    "有給休暇の取得方法について",
                    "有給休暇の日数について",
                    "休暇取得時の給与について"
                ]

            else:

                answer = (
                    "ご質問について確認しました。"
                    "詳しい内容については給与規程または"
                    "担当者にご確認ください。"
                )

                reason = (
                    "給与関連の規程および社内FAQを"
                    "もとにした回答です。"
                )

                faq = [
                    "給与明細の見方について",
                    "給与の支給日について",
                    "控除額について"
                ]


            # 回答を表示
            st.divider()

            st.subheader("回答")

            st.info(answer)


            # 根拠
            st.subheader("📖 回答の根拠")

            st.write(reason)


            # 関連FAQ
            st.subheader("🔎 関連FAQ")

            for item in faq:
                st.write(f"・{item}")


            # 次のアクション
            st.divider()

            st.subheader("回答で解決しましたか？")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("追加質問をする"):
                    st.info(
                        "上の質問入力欄から追加の質問を入力してください。"
                    )

            with col2:
                if st.button("担当者へ相談"):
                    st.warning(
                        "担当者への相談画面を準備しています。"
                    )