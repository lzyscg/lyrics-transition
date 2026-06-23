from __future__ import annotations

import json
from datetime import datetime

import streamlit as st

from lyrics_converter.core import convert_text
from lyrics_converter.registry import get_converter, list_converters
from lyrics_converter.utils import parse_json_dict


st.set_page_config(page_title="歌词转换工作台", page_icon="♪", layout="wide")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }
    .app-title {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        gap: 1rem;
        border-bottom: 1px solid #d8dee8;
        padding-bottom: .75rem;
        margin-bottom: 1rem;
    }
    .app-title h1 {
        font-size: 1.7rem;
        line-height: 1.2;
        margin: 0;
        letter-spacing: 0;
    }
    .app-title span {
        color: #5f6b7a;
        font-size: .88rem;
    }
    .converter-note {
        border: 1px solid #d8dee8;
        border-radius: 8px;
        padding: .75rem .9rem;
        background: #f7f9fc;
        color: #253044;
        font-size: .92rem;
        min-height: 74px;
    }
    .status-row {
        color: #5f6b7a;
        font-size: .85rem;
        margin-top: -.35rem;
        margin-bottom: .5rem;
    }
    div[data-testid="stTextArea"] textarea {
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        line-height: 1.55;
    }
    div[data-testid="stButton"] button,
    div[data-testid="stDownloadButton"] button {
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def decode_upload(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    raw = uploaded_file.getvalue()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def parse_uploaded_custom_dict(uploaded_file) -> dict[str, list[str] | str]:
    if uploaded_file is None:
        return {}
    raw = uploaded_file.getvalue().decode("utf-8-sig")
    return parse_json_dict(raw)


def build_options(converter_id: str) -> dict:
    converter = get_converter(converter_id)
    options = {}
    select_labels = {
        "tailo_format": {
            "mark": "调号符号：lâng",
            "number": "数字声调：lang5",
            "strip": "无声调：lang",
        },
        "tailo_dialect": {
            "south": "南部 / 漳州偏向",
            "north": "北部 / 泉州偏向",
            "singapore": "新加坡",
        },
    }
    for option in converter.metadata.options:
        if option.kind == "checkbox":
            options[option.key] = st.checkbox(
                option.label,
                value=bool(option.default),
                help=option.help or None,
            )
        elif option.kind == "select":
            labels = select_labels.get(option.key, {})
            values = list(labels.keys()) or [str(option.default)]
            default_index = values.index(option.default) if option.default in values else 0
            selected_label = st.selectbox(
                option.label,
                options=[labels.get(value, value) for value in values],
                index=default_index,
                help=option.help or None,
            )
            reverse_labels = {label: value for value, label in labels.items()}
            options[option.key] = reverse_labels.get(selected_label, selected_label)
        elif option.kind == "number":
            options[option.key] = st.number_input(
                option.label,
                min_value=1,
                max_value=64,
                value=int(option.default or 12),
                step=1,
                help=option.help or None,
            )
    return options


ready_converters = list_converters(include_unimplemented=False)
all_converters = list_converters(include_unimplemented=True)
converter_names = {converter.metadata.name: converter.metadata.id for converter in all_converters}

st.markdown(
    """
    <div class="app-title">
      <h1>歌词转换工作台</h1>
      <span>模块化转换 / 文件上传 / 结果下载</span>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([0.95, 1.25], gap="large")

with left:
    st.subheader("输入")
    selected_name = st.selectbox(
        "转换类型",
        options=list(converter_names.keys()),
        index=0,
    )
    converter_id = converter_names[selected_name]
    converter = get_converter(converter_id)

    status = "可用" if converter.metadata.implemented else "待实现"
    st.markdown(
        f"""
        <div class="converter-note">
          <strong>{converter.metadata.name}</strong> · {status}<br>
          {converter.metadata.description}
        </div>
        """,
        unsafe_allow_html=True,
    )

    options = build_options(converter_id)
    uploaded_text_file = st.file_uploader("上传歌词 .txt", type=["txt"], key="lyrics_file")
    uploaded_text = decode_upload(uploaded_text_file)

    default_text = uploaded_text or st.session_state.get("source_text", "")
    source_text = st.text_area(
        "原歌词",
        value=default_text,
        height=430,
        placeholder="在这里粘贴歌词，或上传 txt 文件。",
    )
    st.session_state["source_text"] = source_text

    uploaded_dict = st.file_uploader("自定义词典 JSON（可选）", type=["json"], key="custom_dict")

with right:
    st.subheader("输出")
    custom_dict: dict[str, list[str] | str] = {}
    dict_error = ""
    try:
        custom_dict = parse_uploaded_custom_dict(uploaded_dict)
    except Exception as exc:  # noqa: BLE001
        dict_error = str(exc)

    if dict_error:
        st.error(f"自定义词典读取失败：{dict_error}")

    can_convert = bool(source_text.strip()) and converter.metadata.implemented and not dict_error
    convert_clicked = st.button("转换歌词", type="primary", disabled=not can_convert, use_container_width=True)

    if not converter.metadata.implemented:
        st.warning("这个转换器已经预留接口，但还没有接入正式算法。")
    elif not source_text.strip():
        st.info("请先输入或上传歌词。")

    output_text = st.session_state.get("output_text", "")
    if convert_clicked:
        try:
            output_text = convert_text(converter_id, source_text, custom_dict=custom_dict, options=options)
            st.session_state["output_text"] = output_text
            st.session_state["last_mode"] = converter_id
            st.session_state["last_converted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception as exc:  # noqa: BLE001
            st.error(f"转换失败：{exc}")
            output_text = ""

    line_count = len(output_text.splitlines()) if output_text else 0
    converted_at = st.session_state.get("last_converted_at", "尚未转换")
    st.markdown(
        f'<div class="status-row">行数：{line_count} · 最近转换：{converted_at}</div>',
        unsafe_allow_html=True,
    )

    st.text_area(
        "转换后歌词",
        value=output_text,
        height=530,
        placeholder="转换结果会显示在这里。",
    )

    download_name = f"{converter_id}_converted.txt"
    st.download_button(
        "下载转换结果",
        data=output_text.encode("utf-8"),
        file_name=download_name,
        mime="text/plain",
        disabled=not bool(output_text),
        use_container_width=True,
    )

with st.expander("自定义词典格式"):
    st.code(
        json.dumps({"不了": "bù le", "through": "throo"}, ensure_ascii=False, indent=2),
        language="json",
    )
    st.caption("国语/粤语按短语覆盖读音；英语按单词覆盖音译。")
