#月次処理
import io
from datetime import date

import pandas as pd
import streamlit as st

def monthly_processing_screen_show():
    # ───────────────────────────── ページ設定 ─────────────────────────────
    st.set_page_config(
        page_title="月次処理 | 給与コパイロット",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ───────────────────────────── 定数（画像から逐語転記） ─────────────────────────────
    SIDEBAR_TITLE = "給与コパイロット"
    NAV_ITEMS = ["ホーム", "例外確認", "月次処理", "Q&A管理", "ナレッジ"]
    BREADCRUMB = "給与処理 > 月次処理"
    PAGE_TITLE = "月次処理"
    PAGE_DESC = "給与CSVから「月次」のレコードだけを抽出して、今月の処理状況を確認します。"

    # 想定CSVカラム名（給与ソフトの一般的な命名に合わせる）
    REQUIRED_COLUMNS = [
        "社員ID", "氏名", "区分", "対象月", "支給額", "控除額", "差引支給額", "処理日",
    ]
    CATEGORY_COLUMN = "区分"      # 区分列
    MONTHLY_VALUE = "月次"        # 月次処理のみを抽出する値
    MAX_MB = 200                  # 画像と同じ「200MB per file」

    # ───────────────────────────── データ読み込み ─────────────────────────────


    def normalize_category(value) -> str:
        """表記ゆれ吸収: 前後空白除去・全角スペース除去"""
        if pd.isna(value):
            return ""
        return str(value).replace("\u3000", "").strip()


    def filter_monthly(df: pd.DataFrame) -> pd.DataFrame:
        """区分列が『月次』に完全一致する行だけを返す"""
        if CATEGORY_COLUMN not in df.columns:
            return df.iloc[0:0]  # 空（列欠落のシグナル）
        mask = df[CATEGORY_COLUMN].map(normalize_category) == MONTHLY_VALUE
        return df.loc[mask].copy()


    # ───────────────────────────── UI: 当月の給与CSVを選択 ─────────────────────────────
    if "data" not in st.session_state:
            st.warning("先にホーム画面でcsvを読み込んでください。")
            return
        
    df_all = st.session_state.data.copy()
    source_label = "ホーム画面で読み込んだデータ"

    # ───────────────────────────── バリデーション ─────────────────────────────
    missing = [c for c in REQUIRED_COLUMNS if c not in df_all.columns]
    if missing:
        st.error(
            f"必要な列が不足しています: {', '.join(missing)}\n"
            f"最低限必要な列: {', '.join(REQUIRED_COLUMNS)}"
        )
        st.stop()

    # ───────────────────────────── サイドバーでの絞り込み ─────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown("**絞り込み**")
        months = sorted(
            df_all["対象月"].dropna().map(normalize_category).unique().tolist(),
            reverse=True,
        )
        default_month = months[0] if months else None
        selected_month = st.selectbox("対象月", months, index=0 if months else None)

    # ───────────────────────────── 月次のみ抽出 → 表示 ─────────────────────────────
    df_monthly = filter_monthly(df_all)
    df_view = df_monthly[df_monthly["対象月"].map(normalize_category) == normalize_category(selected_month)]

    st.caption(f"ソース: {source_label}　/　抽出区分: **月次**　/　対象月: **{selected_month}**")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("対象人数", f"{len(df_view):,} 名")
    c2.metric("支給額合計", f"¥{int(df_view['支給額'].sum()):,}")
    c3.metric("控除額合計", f"¥{int(df_view['控除額'].sum()):,}")
    c4.metric("差引支給額合計", f"¥{int(df_view['差引支給額'].sum()):,}")

    st.dataframe(
        df_view.reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
        column_config={
            "支給額":       st.column_config.NumberColumn(format="¥%d"),
            "控除額":       st.column_config.NumberColumn(format="¥%d"),
            "差引支給額":   st.column_config.NumberColumn(format="¥%d"),
            "処理日":       st.column_config.DateColumn(format="YYYY-MM-DD"),
        },
    )

    # ダウンロードボタン（月次のみを書き出したCSV）
    csv_buf = io.StringIO()
    df_view.to_csv(csv_buf, index=False)
    st.download_button(
        "月次処理結果をCSVでダウンロード",
        data=csv_buf.getvalue().encode("utf-8"),
        file_name=f"monthly_{selected_month}.csv",
        mime="text/csv",
    )

    # デバッグ用：抽出されなかった区分も小さく可視化（月次のみ表示である証拠）
    with st.expander("参考: 元データの区分別件数（月次以外は除外されていることを確認）"):
        st.dataframe(
            df_all.groupby(df_all[CATEGORY_COLUMN].map(normalize_category))
            .size().rename("件数").reset_index(),
            use_container_width=True,
            hide_index=True,
        )