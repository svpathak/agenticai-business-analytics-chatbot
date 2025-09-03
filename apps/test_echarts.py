from streamlit_echarts import st_echarts
import streamlit as st
import json


op = """```json [ { "title": { "text": "HDFC Bank Financial Performance - This Quarter (June 2025)", "left": "center" }, "tooltip": { "trigger": "axis", "axisPointer": { "type": "shadow" }, "formatter": "{b}: {c} Crores" }, "grid": { "left": "3%", "right": "4%", "bottom": "3%", "containLabel": true }, "xAxis": { "type": "category", "data": [ "Net Profit", "Revenue", "Interest Income", "Net Interest Income (NII)" ], "axisLabel": { "interval": 0, "rotate": 30 } }, "yAxis": { "type": "value", "name": "Amount (INR Crores)" }, "series": [ { "name": "Amount", "type": "bar", "data": [ 18155, 99200, 77470, 31440 ], "itemStyle": { "color": "#5470C6" }, "label": { "show": true, "position": "top", "formatter": "{c}" } } ] } ] ```"""
option = json.loads(op.strip().removeprefix("```json").removesuffix("```").strip())
st.write(option[0])
col1, col2 = st.columns(2)

# Plot the first chart in the first column
with col1:
    st_echarts(options=option[0], height="300px")

# Plot the second chart in the second column
with col2:
    st_echarts(options=option[1], height="300px")