import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini

st.set_page_config(
    page_title="AI 健康与健身计划助手",
    page_icon="🏋️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0fff4;
        border: 1px solid #9ae6b4;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fffaf0;
        border: 1px solid #fbd38d;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.1rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

def display_dietary_plan(plan_content):
    with st.expander("📋 你的个性化饮食方案", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 饮食方案说明")
            st.info(plan_content.get("why_this_plan_works", "暂无说明"))
            st.markdown("### 🍽️ 一日饮食建议")
            st.write(plan_content.get("meal_plan", "暂无内容"))
        
        with col2:
            st.markdown("### ⚠️ 注意事项")
            considerations = plan_content.get("important_considerations", "").split('\n')
            for c in considerations:
                if c.strip():
                    st.warning(c)

def display_fitness_plan(plan_content):
    with st.expander("💪 你的个性化健身计划", expanded=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 健身目标")
            st.success(plan_content.get("goals", "未指定目标"))
            st.markdown("### 🏋️‍♂️ 锻炼内容")
            st.write(plan_content.get("routine", "暂无内容"))
        
        with col2:
            st.markdown("### 💡 实用建议")
            tips = plan_content.get("tips", "").split('\n')
            for t in tips:
                if t.strip():
                    st.info(t)

def main():
    if 'dietary_plan' not in st.session_state:
        st.session_state.dietary_plan = {}
        st.session_state.fitness_plan = {}
        st.session_state.qa_pairs = []
        st.session_state.plans_generated = False

    st.title("🏋️‍♂️ AI 健康与健身计划助手")
    st.markdown("""
        <div style='background-color: #00008B; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem; color: white;'>
        输入你的基本信息，我们将为你生成科学合理的饮食与锻炼计划，助你实现健康目标 💪
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.header("🔑 API 设置")
        gemini_api_key = st.text_input("请输入 Gemini API 密钥", type="password", help="从 Google 获取你的 Gemini API 密钥")

        if not gemini_api_key:
            st.warning("⚠️ 请先填写 Gemini API Key 才能生成计划")
            st.markdown("[点击这里获取 API Key](https://aistudio.google.com/apikey)")
            return
        else:
            st.success("✅ 已接收 API 密钥")

    try:
        gemini_model = Gemini(id="gemini-2.5-flash-preview-05-20", api_key=gemini_api_key)
    except Exception as e:
        st.error(f"❌ 初始化 Gemini 模型失败：{e}")
        return

    st.header("👤 用户基本信息")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("年龄", min_value=10, max_value=100, step=1)
        height = st.number_input("身高（厘米）", min_value=100.0, max_value=250.0, step=0.1)
        activity_level = st.selectbox("日常活动水平", ["久坐", "轻度活动", "中度活动", "高度活动", "非常活跃"])
        dietary_preferences = st.selectbox("饮食偏好", ["无特殊限制", "素食", "生酮", "低碳水", "无麸质", "不含乳制品"])

    with col2:
        weight = st.number_input("体重（公斤）", min_value=20.0, max_value=300.0, step=0.1)
        sex = st.selectbox("性别", ["男", "女", "其他"])
        fitness_goals = st.selectbox("健身目标", ["减脂", "增肌", "增强耐力", "保持健康", "力量训练"])

    if st.button("🎯 生成我的健康计划", use_container_width=True):
        with st.spinner("AI 正在为你定制专属健康方案，请稍候..."):
            try:
                dietary_agent = Agent(
                    name="饮食专家",
                    role="根据用户信息生成个性化饮食建议",
                    model=gemini_model,
                    instructions=[
                        "你是一位专业的营养师。",
                        "根据用户的年龄、性别、身高、体重、活动水平、饮食偏好和健身目标，生成个性化饮食建议。",
                        "请输出三餐建议（早餐、午餐、晚餐）及加餐内容。",
                        "内容实用，清晰，适合普通用户阅读。",
                        "请用中文回答。"
                    ]
                )

                fitness_agent = Agent(
                    name="健身教练",
                    role="根据用户信息生成个性化锻炼计划",
                    model=gemini_model,
                    instructions=[
                        "你是一位经验丰富的私人健身教练。",
                        "根据用户的性别、年龄、体重、身高、目标等信息，提供个性化健身建议。",
                        "计划应包括热身、主训练、拉伸环节，列出动作、次数、组数。",
                        "语言清晰，用中文输出，适合初学者执行。"
                    ]
                )

                user_profile = f"""
                年龄：{age}岁
                性别：{sex}
                身高：{height} cm
                体重：{weight} kg
                活动水平：{activity_level}
                饮食偏好：{dietary_preferences}
                健身目标：{fitness_goals}
                """

                dietary_response = dietary_agent.run(user_profile)
                fitness_response = fitness_agent.run(user_profile)

                dietary_plan = {
                    "why_this_plan_works": "根据用户目标匹配蛋白质、碳水与脂肪比例，兼顾饮食偏好与营养均衡",
                    "meal_plan": dietary_response.content,
                    "important_considerations": """
                    - 多喝水，保持水分充足
                    - 注意食物新鲜与均衡
                    - 每天摄入适量的膳食纤维
                    - 根据身体反应灵活调整
                    """
                }

                fitness_plan = {
                    "goals": "提升身体素质，助力达成健康目标",
                    "routine": fitness_response.content,
                    "tips": """
                    - 保持良好作息
                    - 保证锻炼后拉伸放松
                    - 持之以恒才是关键
                    - 重视姿势规范，避免受伤
                    """
                }

                st.session_state.dietary_plan = dietary_plan
                st.session_state.fitness_plan = fitness_plan
                st.session_state.plans_generated = True
                st.session_state.qa_pairs = []

                display_dietary_plan(dietary_plan)
                display_fitness_plan(fitness_plan)

            except Exception as e:
                st.error(f"❌ 生成计划出错：{e}")

    if st.session_state.plans_generated:
        st.header("❓ 有什么问题想问 AI 吗？")
        question_input = st.text_input("请输入你对健身/饮食计划的疑问")

        if st.button("🤖 提问"):
            if question_input.strip():
                with st.spinner("AI 正在思考中..."):
                    try:
                        context = f"""
                        饮食计划：{st.session_state.dietary_plan.get('meal_plan', '')}
                        健身计划：{st.session_state.fitness_plan.get('routine', '')}
                        用户提问：{question_input}
                        """

                        agent = Agent(model=gemini_model, show_tool_calls=True, markdown=True)
                        response = agent.run(context)

                        answer = getattr(response, 'content', "很抱歉，目前无法回答该问题。")
                        st.session_state.qa_pairs.append((question_input, answer))
                    except Exception as e:
                        st.error(f"❌ 回答失败：{e}")

        if st.session_state.qa_pairs:
            st.header("📚 问答记录")
            for q, a in st.session_state.qa_pairs:
                st.markdown(f"**Q:** {q}")
                st.markdown(f"**A:** {a}")

if __name__ == "__main__":
    main()
