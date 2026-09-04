import streamlit as st

def personal_screen_show2():
    
    if "data" not in st.session_state:
        st.warning(
            "ホーム画面でcsvを入力してください"
        )
        return
    
    df = st.session_state.data.copy()
    
    select_index = st.selectbox(
        '編集する社員を選択',
        df.index,
        format_func=lambda index: (
            f'{df.at[index, '社員ID']}'
            f'{df.at[index, '氏名']}'
        )
    )
    
    edit_df = st.data_editor(
        df.loc[[select_index]],
        hide_index=True,
        width="stretch",
        disabled=['氏名','社員ID'],
        key=f'editor_{select_index}'
    )
    
    if st.button('保存'):
        df.loc[select_index] = (edit_df.iloc[0])
        
        df.at[select_index,'差引支給額'] = df.at[select_index, "支給額"] - df.at[select_index, "控除額"]
    
        st.session_state.data = df
    
        st.success(
            '保存完了'
        )
