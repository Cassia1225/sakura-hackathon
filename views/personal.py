#個人
import streamlit as st
import pandas as pd
import streamlit as st

def personal_screen_show():
    #=============ページ設定=========================
    st.set_page_config(
        page_title="個別詳細 | 給与コパイロット",
        page_icon="",
        layout="stretch"
    )

    #==============ページ上部=========================
    st.caption("例外確認 ＞ 個別詳細")
    st.title("個別詳細")

    #==============仮の社員データ=========================

    #CSVの代わりに仮の社員データを使用する
    #あとからCSVから取得した社員データに置き換える

    initial_employee = {
        "社員ID": "00021",
        "氏名": "山田 太郎",
        "部門": "営業部",
        "入社日": "2026-09-15",
        "退職日": None,
        "基本給": 300000,
        "出勤日数": 10,
        "残業時間": 5,
        "対象年月": "2026-09",
    }

    #修正した社員データを画面の再実行後も保持する
    if "employee" not in st.session_state:
        st.session_state.employee = initial_employee.copy()

    #以降の給与計算で使用する社員データ
    employee = st.session_state.employee

    #==============社員基本情報=========================

    #氏名を表示
    st.subheader(employee["氏名"])

    #社員IDと所属部門を表示
    st.write(
        f"社員ID：{employee['社員ID']}　｜　"
        f"部門：{employee['部門']}"
    )

    #入社日と給与の対象年月を表示
    st.write(
        f"入社日：{employee['入社日']}　｜　"
        f"対象年月：{employee['対象年月']}"
    )

    #==============例外判定=========================

    #対象年月を比較できる形に変換
    target = pd.Period(
        employee["対象年月"],
        freq="M"
    )

    #入社日を日付型に変換
    join_date = pd.to_datetime(
        employee["入社日"]
    )

    #退職日が存在する場合日付型に変換
    retire_date = pd.to_datetime(
        employee["退職日"]
    ) if employee["退職日"] else None

    #入社日の年月が給与処理の対象年月と一致するか
    joined = (
        join_date.to_period("M")
        == target
    )

    #退職日が存在し、その年月が給与処理の対象年月と一致するか
    retired = (
        retire_date is not None
        and retire_date.to_period("M") == target
    )

    #対象年月中の入社で、かつ入社日が月初1日ではないか
    joined_midmonth = (
        joined
        and join_date.day > 1
    )

    #対象年月中の退職で、かつ退職日が月末日ではないか
    retired_midmonth = (
        retired
        and retire_date.day < retire_date.days_in_month
    )

    #月途中の入社または月途中の退職に該当し、基本給の日割り計算が必要か
    prorated = (
        joined_midmonth
        or retired_midmonth
    )

    #検知理由をまとめる
    reasons = []

    if joined:
        reasons.append("当月入社")

    if retired:
        reasons.append("当月退職")

    if prorated:
        reasons.append("日割り計算")

    if employee["残業時間"] >= 40:
        reasons.append("残業40時間以上")

    #==============給与計算=========================

    #日割り計算で使用する仮ルール
    WORK_DAYS = 20
    OVERTIME_PRICE = 1500

    #日割り対象の場合、「基本給÷20日×出勤日数」で基本給を計算
    if prorated:
        basic_pay = round(
            employee["基本給"]
            / WORK_DAYS
            * employee["出勤日数"]
        )

    #日割り対象でなければ、CSVから取得した基本給をそのまま使用
    else:
        basic_pay = employee["基本給"]

    #「残業時間×1500円」で残業代を計算
    overtime_pay = round(
        employee["残業時間"]
        * OVERTIME_PRICE
    )

    #今回計算した基本給に残業代を加えて支給見込額を計算
    estimated_pay = round(
        basic_pay
        + overtime_pay
    )

    #==============通常勤務の場合の給与計算=========================

    #日割り計算を行わなかった場合の基本給
    normal_basic_pay = employee["基本給"]

    #通常勤務の場合の出勤日数を20日とする
    normal_work_days = WORK_DAYS

    #通常勤務の場合も今回と同じ残業時間だったとして支給見込額を計算
    normal_estimated_pay = round(
        normal_basic_pay
        + overtime_pay
    )

    #==============通常勤務の場合/今回の計算=========================

    st.subheader("通常勤務の場合 / 今回の計算")

    #比較基準となる「通常勤務の場合」の意味を表示
    st.info(
        f"通常勤務の場合とは、所定労働日数を{WORK_DAYS}日とし、"
        "基本給の日割り計算を行わなかった場合です。"
    )

    #通常勤務の場合と今回の計算結果を比較する表を作成
    comparison_df = pd.DataFrame(
        {
            "項目": [
                "基本給",
                "出勤日数",
                "残業時間",
                "支給見込額",
            ],
            "通常勤務の場合": [
                f"{normal_basic_pay:,}円",
                f"{normal_work_days}日",
                f"{employee['残業時間']}時間",
                f"{normal_estimated_pay:,}円",
            ],
            "今回の計算": [
                f"{basic_pay:,}円",
                f"{employee['出勤日数']}日",
                f"{employee['残業時間']}時間",
                f"{estimated_pay:,}円",
            ],
            "差": [
                f"{basic_pay - normal_basic_pay:+,}円",
                f"{employee['出勤日数'] - normal_work_days:+}日",
                f"{0:+}時間",
                f"{estimated_pay - normal_estimated_pay:+,}円",
            ],
        }
    )

    #比較表を表示
    st.dataframe(
        comparison_df,
        hide_index=True,
        use_container_width=True
    )

    #==============計算根拠=========================

    st.subheader("計算根拠")

    #日割り対象となっている場合、日割り計算式を表示する
    if prorated:
        st.write(
            "日割り計算："
            f"{employee['基本給']:,}円 ÷ "
            f"{WORK_DAYS}日 × "
            f"{employee['出勤日数']}日 "
            f"= {basic_pay:,}円"
        )

    #日割り対象でない場合は、CSVから取得した基本給をそのまま使用している旨を表示
    else:
        st.write(
            "日割り対象ではないため、"
            f"基本給 {employee['基本給']:,}円をそのまま使用しています。"
        )

    #残業代の計算式を表示する
    st.write(
        "残業代："
        f"{employee['残業時間']}時間 × "
        f"{OVERTIME_PRICE:,}円 "
        f"= {overtime_pay:,}円"
    )

    #今回計算した基本給に残業代を加えた支給見込額を表示
    st.write(
        "支給見込額："
        f"{basic_pay:,}円 + "
        f"{overtime_pay:,}円 "
        f"= {estimated_pay:,}円"
    )

    #==============確認ポイントと推奨対応=========================

    #例外の内容に応じて、給与担当者が確認すべき項目を格納
    check_points = []

    #当月入社の場合、入社日の登録内容を確認対象にする
    if joined:
        check_points.append(
            "入社日が正しく登録されているか"
        )

    #当月退職の場合、退職日の登録内容を確認対象にする
    if retired:
        check_points.append(
            "退職日が正しく登録されているか"
        )

    #日割り対象の場合、出勤日数と日割り適用の妥当性を確認対象にする
    if prorated:
        check_points.append(
            "出勤日数が正しく登録されているか"
        )
        check_points.append(
            "日割り計算の対象として問題ないか"
        )

    #残業時間が40時間以上の場合、残業時間の登録内容を確認対象にする
    if employee["残業時間"] >= 40:
        check_points.append(
            "残業時間が正しく登録されているか"
        )

    #日割り対象の場合の推奨対応
    if prorated:
        recommendation = (
            "入退社日、出勤日数、日割り計算の適用に"
            "問題がなければ承認してください。"
        )

    #残業時間が40時間以上の場合の推奨対応
    elif employee["残業時間"] >= 40:
        recommendation = (
            "残業時間の入力値に問題がなければ"
            "承認してください。"
        )

    #その他の検知理由が存在する場合の推奨対応
    elif reasons:
        recommendation = (
            "検知された内容を確認し、"
            "問題がなければ承認してください。"
        )

    #検知理由が存在しない場合
    else:
        recommendation = (
            "要確認事項はありません。"
        )

    #==============判断支援情報の表示======================

    reason_col, check_col, recommendation_col = st.columns(3)

    with reason_col:
        st.subheader("検知理由")

        #検知された理由を1件ずつ表示
        if reasons:
            for reason in reasons:
                st.markdown(
                    f"- {reason}"
                )

        else:
            st.write(
                "検知された例外はありません。"
            )

    with check_col:
        st.subheader("確認ポイント")

        #検知された内容に応じた確認項目を1件ずつ表示
        if check_points:
            for point in check_points:
                st.markdown(
                    f"- {point}"
                )

        else:
            st.write(
                "確認が必要な項目はありません。"
            )

    with recommendation_col:
        st.subheader("推奨対応")

        #検知内容に応じて生成した推奨対応を表示
        st.write(
            recommendation
        )

    #==============修正操作=========================

    st.subheader("給与データの修正")

    #修正フォームを開くかどうかを保持する
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    #修正ボタンを押した場合、修正フォームを表示する
    if st.button("修正する"):
        st.session_state.edit_mode = True


    #修正モードの場合のみ入力フォームを表示する
    if st.session_state.edit_mode:

        with st.form("edit_employee_form"):

            st.write("修正する項目を入力してください。")

            #現在登録されている入社日を初期値として表示
            edited_join_date = st.date_input(
                "入社日",
                value=pd.to_datetime(
                    employee["入社日"]
                ).date()
            )

            #退職日が登録されている場合は現在の日付を表示し、
            #登録されていない場合は空欄の代わりに入力有無を選択する
            has_retire_date = st.checkbox(
                "退職日を入力する",
                value=employee["退職日"] is not None
            )

            edited_retire_date = None

            if has_retire_date:

                retire_default = (
                    pd.to_datetime(employee["退職日"]).date()
                    if employee["退職日"] is not None
                    else pd.to_datetime(employee["対象年月"] + "-01").date()
                )

                edited_retire_date = st.date_input(
                    "退職日",
                    value=retire_default
                )

            #現在登録されている基本給を初期値として表示
            edited_basic_salary = st.number_input(
                "基本給",
                min_value=0,
                value=int(employee["基本給"]),
                step=1000
            )

            #現在登録されている出勤日数を初期値として表示
            edited_work_days = st.number_input(
                "出勤日数",
                min_value=0,
                max_value=31,
                value=int(employee["出勤日数"]),
                step=1
            )

            #現在登録されている残業時間を初期値として表示
            edited_overtime = st.number_input(
                "残業時間",
                min_value=0.0,
                value=float(employee["残業時間"]),
                step=0.5
            )

            save_col, cancel_col = st.columns(2)

            with save_col:

                #入力した内容を社員データへ反映する
                save_edit = st.form_submit_button(
                    "修正内容を保存",
                    use_container_width=True
                )

            with cancel_col:

                #入力内容を保存せず修正画面を閉じる
                cancel_edit = st.form_submit_button(
                    "キャンセル",
                    use_container_width=True
                )


            #修正内容を保存した場合、
            #session_state内の社員データを更新して給与計算を再実行する
            if save_edit:

                st.session_state.employee["入社日"] = str(
                    edited_join_date
                )

                st.session_state.employee["退職日"] = (
                    str(edited_retire_date)
                    if edited_retire_date is not None
                    else None
                )

                st.session_state.employee["基本給"] = (
                    edited_basic_salary
                )

                st.session_state.employee["出勤日数"] = (
                    edited_work_days
                )

                st.session_state.employee["残業時間"] = (
                    edited_overtime
                )

                st.session_state.edit_mode = False

                st.rerun()


            #キャンセルした場合は社員データを変更せず修正画面を閉じる
            if cancel_edit:

                st.session_state.edit_mode = False

                st.rerun()

    #==============対応状態の初期化=========================

    #現在の社員に対する対応状態を保持する
    if "detail_status" not in st.session_state:
        st.session_state.detail_status = "未対応"

    #保留理由を保持する
    if "hold_reason" not in st.session_state:
        st.session_state.hold_reason = ""


    #==============現在の対応状態=========================

    st.subheader("対応状況")

    #現在の対応状態を表示
    st.write(
        f"現在の状態：{st.session_state.detail_status}"
    )

    #保留中の場合は、登録されている保留理由も表示
    if (
        st.session_state.detail_status == "保留"
        and st.session_state.hold_reason
    ):
        st.write(
            f"保留理由：{st.session_state.hold_reason}"
        )


    #==============承認・保留操作=========================

    st.subheader("対応")

    hold_col, approve_col = st.columns(2)

    with hold_col:

        #保留理由を入力する
        hold_reason = st.text_input(
            "保留理由",
            value=st.session_state.hold_reason,
            placeholder="例：出勤日数を人事部へ確認中"
        )

        #すぐに判断できない場合、社員の対応状態を保留にする
        if st.button(
            "保留する",
            use_container_width=True
        ):
            st.session_state.detail_status = "保留"
            st.session_state.hold_reason = hold_reason
            st.rerun()


    with approve_col:

        st.write("内容に問題がなければ承認してください。")

        #検知内容・計算内容・確認ポイントに問題がないと判断した場合、
        #社員の対応状態を承認済みにする
        if st.button(
            "承認する",
            type="primary",
            use_container_width=True
        ):
            st.session_state.detail_status = "承認済み"
            st.session_state.hold_reason = ""
            st.rerun()