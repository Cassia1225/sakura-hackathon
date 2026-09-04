import pandas as pd
import streamlit as st
import views.irregular_screen as ir
import views.monthly_processing_screen as mo
import views.output as ou
import views.personal as pe
import views.QandA_screen as qa
import views.FAQ_screen as fa
import views.personal2 as pe2


WORK_DAYS = 20 #仮の１ヶ月の所定労働日数
OVERTIME_LIMIT = 40 #残業時間が40以上かどうかを調べるための定数


st.set_page_config(
    page_title="ジェット計算システム",
    page_icon="",
    layout="wide"
)

def home_screen():
    st.title("おはようございます")
    st.write(
        "給与CSVを読み込み、"
        "今月の処理状況を確認しましょう。"
    )

    file = st.file_uploader(
        "当月の給与CSVを選択",
        type="csv"
    )

    if file is not None:#もし新しいcsvが選ばれたら

        try:
            df = pd.read_csv(
                file,
                dtype={"社員ID": "string"} #文字列として社員IDを扱って、形を保つ
            )

        except:
            st.error("CSVを入れてください")
            return
        
    elif "data" in st.session_state:
        df = st.session_state.data.copy()
    
    else:
        st.info('csvを選択してください')
        return


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
    
    missing = []
    
    for col in required:
        if col not in df.columns:
            missing.append(col)

    if missing: #赤文字エラーで出力する。
        st.error(
            "不足している列：" + "、".join(missing)
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
        "前月支給額",
        "残業単価",
        "残業代",
        "手当額",
        "支給額",
        "控除額",
        "差引支給額",
    ]
    
    #文字列を数値に変換しておく
    for column in number_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )
    #他の画面でcsvデータを共有するために、整形したデータを保存
    st.session_state.data = df.copy()
    print(st.session_state.data)
    


    # 日割り計算と例外判定
    target_month = str(
        df["対象年月"].iloc[0]
    )

    target = pd.Period(
        target_month,
        freq="M"
    )

    results = [] #社員ごとの計算結果を保存する

    for _, employee in df.iterrows():
        reasons = [] #要確認の理由

        # 当月入社か否か
        joined = (
            employee["入社日"].to_period("M") == target
        )

        # 当月退職か
        retired = (
            #notnaで空欄じゃないか。　その上で退職年月と対象年月を比較する。
            pd.notna(employee["退職日"]) and employee["退職日"].to_period("M") == target
        )

        # 月途中の入社か
        joined_midmonth = (
            #当月入社かつ入社日が1日より後
            joined and employee["入社日"].day > 1
        )

        # 月途中の退職か
        retired_midmonth = (
            #employee['退職日'].days_in_monthは、その月の最終日で、退職日が20なら、 20 < 30　になる
            retired and employee["退職日"].day < employee["退職日"].days_in_month
        )

        # 日割り対象か
        prorated = (
            #月途中の入社 or 月途中の退職なら
            joined_midmonth or retired_midmonth
        )

        if joined:
            #もし当月入社なら、確認理由に追加
            reasons.append("当月入社")

        if retired:
            reasons.append("当月退職")

        if prorated:
            reasons.append("日割り計算")

        if employee["残業時間"] >= OVERTIME_LIMIT:
            reasons.append("残業40時間以上")

        # 日割り基本給 基本給 ÷ 20日 × 出勤日数
        if prorated:
            basic_pay = round(
                employee["基本給"] / WORK_DAYS * employee["出勤日数"]
            )

        else:
            basic_pay = int(employee["基本給"])

        results.append({
            #現在の社員の計算結果をresultに入れる
            "社員ID": employee["社員ID"],
            "氏名": employee["氏名"],
            "部門": employee["部門"],
            "日割り": (#日割り対象か否か
                "対象" if prorated else "対象外"
            ),
            "基本給計算額": basic_pay,
            "検知理由": "／".join(reasons),
        })


    result_df = pd.DataFrame(results)

    # 例外がある社員だけを抽出（検知理由が空でない社員のみを抽出する。）
    exception_df = result_df[result_df["検知理由"] != ""]
    
    st.session_state["exception_df"] = exception_df


    # ホーム画面に表示する数字
    total = len(df)#csvに入っている社員の総数
    exceptions = len(exception_df)#要確認の社員の総数


    st.success(
        f"{total}名分を読み込みました。"
        f"対象年月：{target_month}"
    )


    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric(#大きく数字を表示するコンポーネントの描画をする。
        "要確認",
        f"{exceptions}名"
    )

    left, right = st.columns([1.5, 1])

    with right:
        st.subheader("要確認の内訳")

        #検知理由に当月入社が含まれている社員数を計算
        joined_count = (
            exception_df["検知理由"].str.contains("当月入社").sum()
            )

        retired_count = (
            exception_df["検知理由"].str.contains("当月退職").sum()
        )

        prorated_count = (#日割りの人数を数える
            exception_df["検知理由"].str.contains("日割り計算").sum()
        )

        overtime_count = (
            exception_df["検知理由"].str.contains("残業40時間以上").sum()
        )

        st.write("当月入社：", joined_count, "名")

        st.write("当月退職：", retired_count, "名")

        st.write("日割り計算：", prorated_count, "名")

        st.write("残業40時間以上：", overtime_count, "名")


    # 今やるべきこと
    st.subheader("今やるべきこと")

    st.write(
        f"要確認社員"
        f"{exceptions}名を確認する"
    )

    # 要確認社員一覧の見出し
    st.subheader("要確認社員")

    st.warning(
        "日割りは「基本給 ÷ 20日 × 出勤日数」で仮計算しています。"
    )
    
    #ここで、要確認者を表として出力する
    st.dataframe(
        exception_df,#表示する表
        width="stretch",#画面幅に合わせている
        hide_index=True#左端にある行番号を隠している
    )

#ここから下が、ホーム画面を描画するための土台。一番最初はサイドバーだけが表示されている状態になる。
with st.sidebar:
    st.title("ジェット計算システム")
    
    menu = st.radio(
        "メニュー",
        [
            "ホーム",
            "個別",
            "月次処理",
            "Q&A",
        ]
    )

if menu == 'ホーム':
    home_screen()
elif menu == '月次処理':
    mo.monthly_processing_screen_show()
elif menu == "個別":
    pe2.personal_screen_show2()
elif menu == "Q&A":
    qa.QandA_screen_show()
elif menu == "FAQ":
    fa.faq_screen_show()
else:
    home_screen()
    