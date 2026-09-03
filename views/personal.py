#個人
import streamlit as st
import pandas as pd
import streamlit as st

def personal_screen_show():
    

    #=============ページ設定=========================
    st.set_page_config(
        page_title="個別詳細 | 給与コパイロット",
        page_icon="💴",
        layout="wide"
    )

    st.caption("例外確認 ＞ 個別詳細")
    st.title("個別詳細")

    #==============ページ上部=========================
    st.caption("例外確認 ＞ 個別詳細")
    st.title("個別詳細")


    #==============仮の社員データ=========================

    #CSVの代わりに仮の社員データを使用する
    #あとからCSVから取得した社員データに置き換える

    employee = {
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

    #退職日の年月が給与処理の対象年月と一致するか
    retired = (
        retire_date is not None
        and retire_date.to_period("M") == target
    )

    #対象年月中の入社で、かつ入社日が月初１日ではないか
    joined_midmonth = (
        joined
        and join_date.day > 1
    )

    # 対象年月中の退職で、かつ退職日が月末日ではないか
    retired_midmonth = (
        retired
        and retire_date.day < retire_date.days_in_month
    )

    # 月途中の入社または月途中の退職に該当し、基本給の日割り計算が必要か
    prorated = (
        joined_midmonth
        or retired_midmonth
    )

    # 検知理由をまとめる
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

    #「基本給÷20日×出勤日数」で基本給を計算
    if prorated:
        basic_pay = round(
            employee["基本給"]
            / WORK_DAYS
            * employee["出勤日数"]
        )

    #日割り対象でなければ、CSVから取得した基本給をそのまま使用
    else:
        basic_pay = employee["基本給"]


    #「残業時間×1500円」を計算して、基本給に加えて支給見込み額を計算
    estimated_pay = round(
        basic_pay
        + employee["残業時間"] * OVERTIME_PRICE
    )

    #==============通常額/今回計算額=========================

    st.subheader("通常額/今回計算額")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="基本給",
            value=f"{basic_pay:,}円",
            delta=f"{basic_pay - employee['基本給']:,}円"
        )

    with col2:
        st.metric(
            label="出勤日数",
            value=f"{employee['出勤日数']}日",
            delta=f"{employee['出勤日数'] - WORK_DAYS}日"
        )

    with col3:
        st.metric(
            label="支給見込額",
            value=f"{estimated_pay:,}円"
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
        f"= {employee['残業時間'] * OVERTIME_PRICE:,.0f}円"
    )

    #通常の基本給に残業代を加えた支給見込み額の表示
    st.write(
        "支給見込額："
        f"{basic_pay:,}円 + "
        f"{employee['残業時間'] * OVERTIME_PRICE:,.0f}円 "
        f"= {estimated_pay:,}円"
    )

    #==============確認ポイントと推奨対応=========================

    #例外の内容に応じて、給与担当者が確認すべき項目を格納
    check_points=[]

    #
    if joined:
        check_points.append(
            "入社日が正しく登録されているか"
        )

    # 退職日の年月が給与処理の対象年月と一致する場合、
    # CSVに登録されている退職日が正しいかを確認対象にする
    if retired:
        check_points.append(
            "退職日が正しく登録されているか"
        )

    # 月途中の入社または退職によって日割り対象となっている場合、
    # 日割り計算に使用する出勤日数と、日割り適用の妥当性を確認対象にする
    if prorated:
        check_points.append(
            "出勤日数が正しく登録されているか"
        )
        check_points.append(
            "日割り計算の対象として問題ないか"
        )

    # 残業時間が40時間以上の場合、
    # CSVに登録されている残業時間が正しいかを確認対象にする
    if employee["残業時間"] >= 40:
        check_points.append(
            "残業時間が正しく登録されているか"
        )


    # 検知された例外の種類に応じて、
    # 確認後に取ることを推奨する対応を決定する
    if prorated:
        recommendation = (
            "入退社日、出勤日数、日割り計算の適用に"
            "問題がなければ承認してください。"
        )

    elif employee["残業時間"] >= 40:
        recommendation = (
            "残業時間の入力値に問題がなければ"
            "承認してください。"
        )

    elif reasons:
        recommendation = (
            "検知された内容を確認し、"
            "問題がなければ承認してください。"
        )

    else:
        recommendation = (
            "要確認事項はありません。"
        )

    #==============判断支援情報の表示======================

    reason_col, check_col, recommendation_col = st.columns(3)


    with reason_col:
        st.subheader("検知理由")

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

        # 検知された例外に応じて生成した
        # 給与担当者の確認項目を1件ずつ表示する
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

        # 検知された例外の種類に基づいて生成した
        # 給与担当者向けの推奨対応を表示する
        st.write(
            recommendation
        )