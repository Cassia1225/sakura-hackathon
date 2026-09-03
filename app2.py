import pandas as pd
import streamlit as st
import views.irregular_screen as ir
import views.monthly_processing_screen as mo


# 一旦のルール
WORK_DAYS = 20
OVERTIME_LIMIT = 40


st.set_page_config(
    page_title="給与コパイロット",
    page_icon="",
    layout="wide"
)

def home_screen():
    #st.caption("給与処理 ＞ ホーム")
    st.title("おはようございます")
    st.write(
        "給与CSVを読み込み、"
        "今月の処理状況を確認しましょう。"
    )

    file = st.file_uploader(
        "当月の給与CSVを選択",
        type="csv"
    )

    if file is None:
        st.info("CSVを選択してください。")
        st.stop()

    try:
        df = pd.read_csv(
            file,
            dtype={"社員ID": "string"}
        )

    except pd.errors.EmptyDataError:
        st.error("CSVが空です。")
        st.stop()


    required = [
        "対象年月",
        "社員ID",
        "氏名",
        "部門",
        "入社日",
        "退職日",
        "基本給",
        "出勤日数",
        "残業時間",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        st.error(
            "不足している列："
            + "、".join(missing)
        )
        st.stop()


    # 日付と数字を変換する
    df["入社日"] = pd.to_datetime(
        df["入社日"],
        errors="coerce"
    )

    df["退職日"] = pd.to_datetime(
        df["退職日"],
        errors="coerce"
    )

    number_columns = [
        "基本給",
        "出勤日数",
        "残業時間",
    ]

    for column in number_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


    # 日割り計算と例外判定
    target_month = str(
        df["対象年月"].iloc[0]
    )

    target = pd.Period(
        target_month,
        freq="M"
    )

    results = []

    for _, employee in df.iterrows():
        reasons = []

        # 当月入社か
        joined = (
            employee["入社日"].to_period("M")
            == target
        )

        # 当月退職か
        retired = (
            pd.notna(employee["退職日"])
            and employee["退職日"].to_period("M")
            == target
        )

        # 月途中の入社か
        joined_midmonth = (
            joined
            and employee["入社日"].day > 1
        )

        # 月途中の退職か
        retired_midmonth = (
            retired
            and employee["退職日"].day
            < employee["退職日"].days_in_month
        )

        # 日割り対象か
        prorated = (
            joined_midmonth
            or retired_midmonth
        )

        if joined:
            reasons.append("当月入社")

        if retired:
            reasons.append("当月退職")

        if prorated:
            reasons.append("日割り計算")

        if (
            employee["残業時間"]
            >= OVERTIME_LIMIT
        ):
            reasons.append(
                "残業40時間以上"
            )

        # 日割り基本給
        # 基本給 ÷ 20日 × 出勤日数
        if prorated:
            basic_pay = round(
                employee["基本給"]
                / WORK_DAYS
                * employee["出勤日数"]
            )

        else:
            basic_pay = int(
                employee["基本給"]
            )

        results.append({
            "社員ID": employee["社員ID"],
            "氏名": employee["氏名"],
            "部門": employee["部門"],
            "日割り": (
                "対象"
                if prorated
                else "対象外"
            ),
            "基本給計算額": basic_pay,
            "検知理由": "／".join(reasons),
        })


    result_df = pd.DataFrame(results)

    # 例外がある社員だけを抽出
    exception_df = result_df[
        result_df["検知理由"] != ""
    ]


    # ホーム画面に表示する数字
    total = len(df)
    exceptions = len(exception_df)


    st.success(
        f"{total}名分を読み込みました。"
        f"対象年月：{target_month}"
    )


    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric(
        "⚠ 要確認",
        f"{exceptions}名"
    )

    left, right = st.columns(
        [1.5, 1]
    )

    with right:
        st.subheader(
            "要確認の内訳"
        )

        joined_count = (
            exception_df["検知理由"]
            .str.contains("当月入社")
            .sum()
        )

        retired_count = (
            exception_df["検知理由"]
            .str.contains("当月退職")
            .sum()
        )

        prorated_count = (
            exception_df["検知理由"]
            .str.contains("日割り計算")
            .sum()
        )

        overtime_count = (
            exception_df["検知理由"]
            .str.contains("残業40時間以上")
            .sum()
        )

        st.write(
            "当月入社：",
            joined_count,
            "名"
        )

        st.write(
            "当月退職：",
            retired_count,
            "名"
        )

        st.write(
            "日割り計算：",
            prorated_count,
            "名"
        )

        st.write(
            "残業40時間以上：",
            overtime_count,
            "名"
        )


    # 今やるべきこと
    st.subheader(
        "今やるべきこと"
    )

    st.write(
        f"要確認社員"
        f"{exceptions}名を確認する"
    )


    # 要確認社員一覧
    st.subheader(
        "要確認社員"
    )

    st.warning(
        "日割りは"
        "「基本給 ÷ 20日 × 出勤日数」"
        "で仮計算しています。"
    )

    st.dataframe(
        exception_df,
        width="stretch",
        hide_index=True
    )
    
with st.sidebar:
    st.title("給与コパイロット")
    
    menu = st.radio(
        "メニュー",
        [
            "ホーム",
            "例外確認",
            "月次処理",
            "Q&A",
        ]
    )
    
if menu == 'ホーム':
    home_screen()
elif menu == '例外確認':
    ir.iregure_screen_show()
elif menu == '月次処理':
    mo.monthly_processing_screen_show()