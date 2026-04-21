import streamlit as st
import pandas as pd
import requests
import json
import time
from datetime import datetime
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

# ---------- 页面配置 ----------
st.set_page_config(
    page_title="智鉴 · AI内容检测",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- 自定义CSS（专业深色科技风）----------
st.markdown("""
<style>
    /* 全局深色基调 */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', 'Microsoft YaHei', sans-serif;
        background-color: #0f1117;
        color: #e6e9f0;
    }
    
    /* 主内容区域背景 */
    .main > div {
        background-color: #0f1117;
    }
    
    /* 侧边栏 - 半透明毛玻璃效果 */
    section[data-testid="stSidebar"] {
        background: rgba(20, 25, 35, 0.75) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: 1px solid rgba(0, 194, 255, 0.15);
    }
    section[data-testid="stSidebar"] * {
        color: #e0e4f0 !important;
    }
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea {
        background: rgba(10, 15, 22, 0.7) !important;
        border: 1px solid #2a3345 !important;
        color: #fff !important;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #00c2ff, #7b61ff) !important;
        border: none !important;
        color: #000 !important;
        font-weight: 600 !important;
        border-radius: 30px !important;
        transition: all 0.2s !important;
    }
    section[data-testid="stSidebar"] button:hover {
        box-shadow: 0 0 15px #00c2ff80 !important;
        transform: scale(1.02) !important;
    }
    
    /* 顶部主标题 - 科技感渐变 */
    .main-header {
        background: linear-gradient(145deg, #151e2c 0%, #0f1722 100%);
        padding: 1.5rem 2.2rem;
        border-radius: 28px;
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 194, 255, 0.2);
        box-shadow: 0 20px 35px -8px rgba(0,0,0,0.7), 0 0 0 1px rgba(0,194,255,0.1) inset;
    }
    .main-header h1 {
        background: linear-gradient(135deg, #ffffff 0%, #a0c8ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .main-header p {
        color: #aab3cf !important;
        margin: 0.4rem 0 0 0;
        font-size: 1rem;
        font-weight: 400;
    }
    
    /* 卡片 - 暗色微光 */
    .card {
        background: rgba(20, 28, 40, 0.7);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        border-radius: 24px;
        padding: 1.8rem 1.8rem;
        border: 1px solid rgba(0, 194, 255, 0.18);
        box-shadow: 0 15px 30px -10px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.02) inset;
        transition: border 0.2s;
        height: 100%;
    }
    .card:hover {
        border-color: rgba(0, 194, 255, 0.4);
    }
    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #e0e9ff;
        margin-bottom: 1.5rem;
        letter-spacing: -0.01em;
        border-left: 5px solid #00c2ff;
        padding-left: 1.2rem;
        text-shadow: 0 2px 5px rgba(0,0,0,0.3);
    }
    
    /* 指标卡片（用于AI概率等） */
    .metric-card {
        background: rgba(12, 18, 28, 0.7);
        border-radius: 20px;
        padding: 1.2rem 0.8rem;
        text-align: center;
        border: 1px solid #253040;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        backdrop-filter: blur(4px);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #8d9bb5;
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* 按钮 */
    .stButton > button {
        background: linear-gradient(135deg, #1e2b44 0%, #0f1a2b 100%);
        color: #ccd9ff !important;
        border: 1px solid #2e4b70 !important;
        border-radius: 40px !important;
        padding: 0.5rem 2rem !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #00c2ff20, #7b61ff20) !important;
        border-color: #00c2ff !important;
        color: #ffffff !important;
        box-shadow: 0 0 12px #00c2ff40 !important;
    }
    
    /* 文本输入框 */
    .stTextArea textarea {
        background: #0f1722 !important;
        border: 1.5px solid #253545 !important;
        border-radius: 20px !important;
        color: #eef2fb !important;
        font-size: 1rem;
    }
    .stTextArea textarea:focus {
        border-color: #00c2ff !important;
        box-shadow: 0 0 10px #00c2ff30 !important;
    }
    
    /* 选项卡 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        border-bottom: 1px solid #253545;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 16px 16px 0 0;
        padding: 0.7rem 1.8rem;
        font-weight: 500;
        color: #9aabca;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1e3350, #0f1a2b);
        color: #00c2ff !important;
        border-bottom: 3px solid #00c2ff;
    }
    
    /* 提示信息 */
    .stAlert {
        background: #1a2536;
        border-left: 6px solid #00c2ff;
        border-radius: 14px;
        color: #d3defa;
    }
    
    /* 数据表格 */
    .stDataFrame {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid #253545;
    }
    
    /* 展开器 */
    .streamlit-expanderHeader {
        background: #141e2c;
        border-radius: 16px;
        border: 1px solid #2a3a50;
    }
</style>
""", unsafe_allow_html=True)

# ---------- 主标题 ----------
st.markdown("""
<div class="main-header">
    <h1>🛡️ 智鉴 · AI生成内容智能检测与溯源平台</h1>
    <p>多模态AI文本鉴别 · 工具指纹溯源 · 风险量化评估</p>
</div>
""", unsafe_allow_html=True)

# ---------- 侧边栏（毛玻璃优化）----------
# ---------- 侧边栏 API 配置 ----------
with st.sidebar:
    st.markdown("## ⚙️ 控制中心")
    st.markdown("---")
    st.markdown("#### 🔑 API 配置")
    
    # 优先从 secrets 读取密钥（线上环境），否则使用默认空值
    default_key = ""
    if "api_key" in st.secrets:
        default_key = st.secrets["api_key"]
    
    api_key = st.text_input("API密钥", type="password", value=default_key, help="输入你的大模型API密钥")
    api_url = st.text_input("API地址", value="https://open.bigmodel.cn/api/paas/v4/chat/completions")
    model = st.text_input("模型名称", value="glm-3-turbo")
    
    # 测试连接按钮
    if st.button("🔌 测试连接", use_container_width=True):
        if not api_key:
            st.error("请输入API密钥")
        else:
            with st.spinner("正在验证..."):
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                data = {"model": model, "messages": [{"role": "user", "content": "hi"}], "temperature": 0.1}
                try:
                    response = requests.post(api_url, headers=headers, json=data, timeout=10)
                    if response.status_code == 200:
                        st.success("✅ 连接成功")
                        st.session_state.api_configured = True
                        st.session_state.api_key = api_key
                        st.session_state.api_url = api_url
                        st.session_state.model = model
                    else:
                        st.error(f"连接失败，状态码：{response.status_code}")
                except Exception as e:
                    st.error(f"连接异常：{e}")
    
    st.markdown("---")
    st.markdown("#### 🔎 数据筛选")
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    if st.session_state.history:
        dates = []
        for rec in st.session_state.history:
            if "时间" in rec:
                try:
                    d = datetime.strptime(rec["时间"], "%Y-%m-%d %H:%M:%S").date()
                    dates.append(d)
                except:
                    continue
        if dates:
            date_range = st.date_input("日期范围", [min(dates), max(dates)])
        else:
            date_range = None
    else:
        date_range = None
    
    all_labels = set()
    for rec in st.session_state.history:
        if "分析结果" in rec and isinstance(rec["分析结果"], dict):
            label = rec["分析结果"].get("ai_label", "未知")
            all_labels.add(label)
    label_options = sorted(list(all_labels)) if all_labels else ["高概率AI生成", "疑似AI生成", "大概率真人"]
    selected_labels = st.multiselect("判定标签", label_options, default=label_options)
    
    st.markdown("---")
    if st.button("🗑️ 清空历史", use_container_width=True):
        st.session_state.history = []
        st.rerun()
    st.caption("🔐 密钥仅保存在当前会话")

# ---------- 初始化 ----------
if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False
if 'history' not in st.session_state:
    st.session_state.history = []

def call_llm(prompt, retries=2):
    # 优先从 secrets 获取，否则从 session_state 获取
    api_key = st.secrets.get("api_key") or st.session_state.get("api_key")
    api_url = st.secrets.get("api_url") or st.session_state.get("api_url")
    model = st.secrets.get("model") or st.session_state.get("model")
    
    if not api_key or not api_url or not model:
        return "错误：API配置不完整"
    
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
    for attempt in range(retries + 1):
        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=30)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                if attempt < retries:
                    time.sleep(1)
                    continue
                else:
                    return f"API错误：{response.status_code}"
        except Exception as e:
            if attempt < retries:
                time.sleep(1)
                continue
            else:
                return f"请求异常：{e}"
    return "调用失败"

def extract_ai_info(text):
    prompt = f"""
你是一位专业的AI生成内容鉴定与数字取证专家。请仔细分析以下文本，判断它是否由AI生成，并尝试溯源可能的生成工具。

文本内容：“{text}”

请严格按照以下JSON格式输出分析结果，不要包含任何其他文字：
{{
    "ai_probability": 0.0-1.0之间的浮点数，表示AI生成的概率,
    "tool_fingerprint": "推测的生成工具或模型名称",
    "reason": "简要分析理由",
    "confidence_level": "高/中/低"
}}
"""
    result_str = call_llm(prompt)
    try:
        import re
        match = re.search(r'\{.*\}', result_str, re.DOTALL)
        if match:
            parsed = json.loads(match.group())
            prob = parsed.get("ai_probability", 0.5)
            if prob >= 0.7:
                parsed["ai_label"] = "高概率AI生成"
            elif prob >= 0.4:
                parsed["ai_label"] = "疑似AI生成"
            else:
                parsed["ai_label"] = "大概率真人"
            return parsed
        else:
            return {"ai_probability": 0.5, "tool_fingerprint": "解析失败", "reason": "无法解析", "confidence_level": "低", "ai_label": "解析失败"}
    except:
        return {"ai_probability": 0.5, "tool_fingerprint": "解析异常", "reason": "JSON错误", "confidence_level": "低", "ai_label": "解析异常"}

def generate_structured_brief(result_dict, trend_data):
    prompt = f"""
你是一位AI安全与内容合规顾问。基于以下检测结果撰写结构化风险简报。

检测结果：{json.dumps(result_dict, ensure_ascii=False)}
历史趋势：近7天类似内容出现 {trend_data.get('similar_count', 0)} 次，周增长 {trend_data.get('growth_rate', 0)}%。

输出JSON格式：
{{
    "summary": "检测结论摘要",
    "impact": "影响评估",
    "actions": ["建议1", "建议2", "建议3"],
    "risk_level": "低/中/高"
}}
"""
    response = call_llm(prompt)
    try:
        import re
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            return json.loads(match.group())
        else:
            return {"summary": "无法解析", "impact": "请重试", "actions": [], "risk_level": "未知"}
    except:
        return {"summary": "生成失败", "impact": "", "actions": [], "risk_level": "未知"}

def get_trend_data_for_comment(result_dict):
    fingerprint = result_dict.get("tool_fingerprint", "")
    if not fingerprint or fingerprint == "解析失败":
        return {"similar_count": 0, "growth_rate": 0}
    similar = []
    for rec in st.session_state.history:
        if "分析结果" in rec and isinstance(rec["分析结果"], dict):
            if rec["分析结果"].get("tool_fingerprint") == fingerprint:
                similar.append(rec)
    now = datetime.now()
    last_7d = [rec for rec in similar if (now - datetime.strptime(rec["时间"], "%Y-%m-%d %H:%M:%S")).days <= 7]
    prev_7d = [rec for rec in similar if 7 < (now - datetime.strptime(rec["时间"], "%Y-%m-%d %H:%M:%S")).days <= 14]
    count_last = len(last_7d)
    count_prev = len(prev_7d)
    growth = 100 if count_last > 0 and count_prev == 0 else (round((count_last - count_prev) / count_prev * 100, 1) if count_prev > 0 else 0)
    return {"similar_count": count_last, "growth_rate": growth}

def get_filtered_history(date_range, selected_labels):
    filtered = []
    for rec in st.session_state.history:
        if date_range and len(date_range) == 2:
            try:
                rec_date = datetime.strptime(rec["时间"], "%Y-%m-%d %H:%M:%S").date()
                if rec_date < date_range[0] or rec_date > date_range[1]:
                    continue
            except:
                pass
        if selected_labels:
            label = rec.get("分析结果", {}).get("ai_label", "")
            if label not in selected_labels:
                continue
        filtered.append(rec)
    return filtered

def generate_wordcloud(text):
    if not text:
        return None
    try:
        wordcloud = WordCloud(width=500, height=240, background_color='#0f1117',
                              font_path='simhei.ttf', collocations=False,
                              colormap='cool', color_func=lambda *args, **kwargs: (0, 194, 255)).generate(text)
        plt.figure(figsize=(5, 2.4), facecolor='#0f1117')
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=150, facecolor='#0f1117')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.getvalue()).decode()
        plt.close()
        return f"data:image/png;base64,{img_base64}"
    except:
        return None

# ---------- 主界面 ----------
if not st.session_state.get('api_configured', False):
    st.warning("⚠️ 请先在左侧控制中心配置并测试API连接")
    st.stop()

tab1, tab2, tab3 = st.tabs(["🔍 智能检测", "📊 分析看板", "📁 批量检测"])

# ---------- 选项卡1 ----------
with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")
    with col_left:
        st.markdown('<div class="card-title">📝 输入待检测文本</div>', unsafe_allow_html=True)
        input_text = st.text_area("待检测文本", placeholder="在此粘贴社交媒体帖子、评论、文章段落...", height=220, label_visibility="collapsed")
        detect_btn = st.button("🚀 开始智能检测", use_container_width=True)
        with st.expander("📋 示例文本"):
            examples = [
                "这款手机的续航真的不太行，用半天就没电了，而且发热严重。",
                "我认为人工智能的发展将深刻改变人类社会的生产方式和生活方式。",
                "哈哈哈哈笑死我了，今天在路上看到一只猫追着狗跑，太搞笑了！"
            ]
            for i, ex in enumerate(examples):
                if st.button(ex[:35]+"...", key=f"ex_{i}"):
                    input_text = ex
                    st.rerun()
    
    with col_right:
        if detect_btn and input_text:
            with st.spinner("🤖 AI模型分析中..."):
                result = extract_ai_info(input_text)
                trend = get_trend_data_for_comment(result)
                brief = generate_structured_brief(result, trend)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.history.append({
                    "时间": timestamp,
                    "文本摘要": input_text[:50] + "..." if len(input_text) > 50 else input_text,
                    "完整文本": input_text,
                    "分析结果": result,
                    "简报": brief
                })
            
            st.markdown('<div class="card-title">📊 检测结果</div>', unsafe_allow_html=True)
            prob = result.get('ai_probability', 0.5)
            prob_color = '#ff6b6b' if prob >= 0.7 else '#f39c12' if prob >= 0.4 else '#2ecc71'
            
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color:{prob_color};">{prob*100:.1f}%</div>
                    <div class="metric-label">AI生成概率</div>
                </div>
                """, unsafe_allow_html=True)
            with col_m2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color:#a0b0ff;">{result.get('confidence_level', '—')}</div>
                    <div class="metric-label">置信水平</div>
                </div>
                """, unsafe_allow_html=True)
            with col_m3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color:#c0d0ff;">{result.get('ai_label', '—')}</div>
                    <div class="metric-label">判定标签</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"**🔬 工具指纹** · {result.get('tool_fingerprint', '未知')}")
            st.markdown(f"**📝 分析理由** · {result.get('reason', '无')}")
            
            st.markdown("---")
            st.markdown("#### 🛡️ 风险简报")
            col_b1, col_b2 = st.columns([3,1])
            with col_b1:
                st.markdown(f"**摘要**：{brief.get('summary', '')}")
                st.markdown(f"**影响**：{brief.get('impact', '')}")
                st.markdown("**建议**：")
                for act in brief.get('actions', []):
                    st.markdown(f"- {act}")
            with col_b2:
                risk = brief.get('risk_level', '未知')
                risk_color = {'低':'#2ecc71', '中':'#f39c12', '高':'#ff6b6b'}.get(risk, '#7f8c8d')
                st.markdown(f"""
                <div style="background:{risk_color}20; border-radius:40px; padding:0.8rem; text-align:center; border-left:5px solid {risk_color};">
                    <div style="font-size:0.9rem; color:#b0c0e0;">风险等级</div>
                    <div style="font-size:2rem; font-weight:700; color:{risk_color};">{risk}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="card-title">📊 检测结果</div>', unsafe_allow_html=True)
            st.info("👆 输入文本并点击检测，查看分析结果")

# ---------- 选项卡2：分析看板 ----------
with tab2:
    filtered = get_filtered_history(date_range, selected_labels)
    if filtered:
        total = len(filtered)
        high_risk = sum(1 for r in filtered if r.get("简报", {}).get("risk_level") == "高")
        avg_prob = sum(r["分析结果"].get("ai_probability", 0.5) for r in filtered) / total
        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        col_k1.metric("总检测数", total)
        col_k2.metric("高风险数", high_risk)
        col_k3.metric("平均AI概率", f"{avg_prob*100:.1f}%")
        col_k4.metric("活跃指纹数", len(set(r["分析结果"].get("tool_fingerprint","") for r in filtered)))
        st.markdown("---")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown('<div class="card-title">📈 判定趋势（近7天）</div>', unsafe_allow_html=True)
            data = []
            for rec in filtered:
                try:
                    dt = datetime.strptime(rec["时间"], "%Y-%m-%d %H:%M:%S")
                    label = rec["分析结果"].get("ai_label", "未知")
                    data.append({"日期": dt.date(), "判定": label})
                except: continue
            if data:
                df = pd.DataFrame(data)
                trend_df = df.groupby(['日期', '判定']).size().reset_index(name='数量')
                fig = px.line(trend_df, x='日期', y='数量', color='判定',
                              color_discrete_map={'高概率AI生成':'#ff6b6b', '疑似AI生成':'#f39c12', '大概率真人':'#2ecc71'})
                fig.update_layout(template='plotly_dark', paper_bgcolor='#0f1117', plot_bgcolor='#0f1117', font=dict(color='#e0e4f0'))
                st.plotly_chart(fig, use_container_width=True)
        with col_v2:
            st.markdown('<div class="card-title">🥧 标签分布</div>', unsafe_allow_html=True)
            labels = [r["分析结果"].get("ai_label", "未知") for r in filtered]
            if labels:
                pie_df = pd.DataFrame(labels, columns=["标签"]).value_counts().reset_index(name='数量')
                fig_pie = px.pie(pie_df, values='数量', names='标签', hole=0.4, color_discrete_map={'高概率AI生成':'#ff6b6b', '疑似AI生成':'#f39c12', '大概率真人':'#2ecc71'})
                fig_pie.update_layout(template='plotly_dark', paper_bgcolor='#0f1117', font=dict(color='#e0e4f0'))
                st.plotly_chart(fig_pie, use_container_width=True)
        
        col_w1, col_w2 = st.columns([1.2, 1])
        with col_w1:
            st.markdown('<div class="card-title">☁️ 热点词云</div>', unsafe_allow_html=True)
            all_text = " ".join([r.get("完整文本", "") for r in filtered])
            if all_text.strip():
                img = generate_wordcloud(all_text)
                if img:
                    st.image(img, use_container_width=True)
        with col_w2:
            st.markdown('<div class="card-title">🔍 高频工具指纹</div>', unsafe_allow_html=True)
            fingerprints = [r["分析结果"].get("tool_fingerprint", "未知") for r in filtered]
            if fingerprints:
                fp_df = pd.DataFrame(fingerprints, columns=["指纹"]).value_counts().head(5).reset_index(name='次数')
                fig_bar = px.bar(fp_df, x='次数', y='指纹', orientation='h', color_discrete_sequence=['#00c2ff'])
                fig_bar.update_layout(template='plotly_dark', paper_bgcolor='#0f1117', plot_bgcolor='#0f1117', font=dict(color='#e0e4f0'))
                st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("暂无数据，请先进行智能检测")

# ---------- 选项卡3：批量检测 ----------
with tab3:
    st.markdown('<div class="card-title">📁 批量文本检测</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("上传CSV文件", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.dataframe(df.head(), use_container_width=True)
        text_column = st.selectbox("选择文本所在列", df.columns.tolist())
        if st.button("开始批量检测", use_container_width=True):
            progress_bar = st.progress(0)
            results = []
            total = len(df)
            for i, row in df.iterrows():
                text = str(row[text_column])
                res = extract_ai_info(text)
                brief_prompt = f"基于检测结果撰写风险提示：{json.dumps(res, ensure_ascii=False)}"
                brief = call_llm(brief_prompt)
                results.append({
                    "原始文本": text[:100] + "..." if len(text) > 100 else text,
                    "AI概率": res.get("ai_probability", 0.5),
                    "工具指纹": res.get("tool_fingerprint", ""),
                    "理由": res.get("reason", ""),
                    "置信度": res.get("confidence_level", ""),
                    "简报": brief
                })
                progress_bar.progress((i+1)/total)
            result_df = pd.DataFrame(results)
            st.dataframe(result_df, use_container_width=True)
            csv = result_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 下载检测报告", csv, f"AI检测结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            # 存入历史
            for res in results:
                st.session_state.history.append({
                    "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "文本摘要": res["原始文本"],
                    "完整文本": res["原始文本"],
                    "分析结果": {
                        "ai_probability": res["AI概率"],
                        "tool_fingerprint": res["工具指纹"],
                        "reason": res["理由"],
                        "confidence_level": res["置信度"],
                        "ai_label": "高概率AI生成" if res["AI概率"] >= 0.7 else ("疑似AI生成" if res["AI概率"] >= 0.4 else "大概率真人")
                    },
                    "简报": res["简报"]
                })
    else:
        st.info("📂 请上传包含文本数据的CSV文件")

# 历史记录折叠
with st.expander("📜 查看历史检测记录", expanded=False):
    if not st.session_state.history:
        st.info("暂无记录")
    else:
        for rec in reversed(st.session_state.history[-20:]):
            st.markdown(f"**🕒 {rec['时间']}** — {rec['文本摘要']}")
            col_a, col_b = st.columns(2)
            with col_a:
                st.json(rec["分析结果"])
            with col_b:
                st.info(rec["简报"])
            st.markdown("---")
