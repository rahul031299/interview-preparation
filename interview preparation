import streamlit as st
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="PrepCo Interview Intel", page_icon="🎯", layout="centered")

# --- SIDEBAR: API KEY ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

st.title("🎯 PrepCo Interview Intel Agent")
st.markdown("Generate a highly detailed, comprehensive research briefing for your upcoming interview.")

# --- UI CONTROLS ---
col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input("Company Name", placeholder="e.g., McKinsey & Company")
with col2:
    job_role = st.text_input("Job Title / Role", placeholder="e.g., Summer Associate")

if st.button("Generate Research Briefing", type="primary"):
    if not api_key:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar.")
    elif not company_name or not job_role:
        st.warning("⚠️ Please enter both the Company Name and the Job Role.")
    else:
        try:
            with st.spinner(f"Agents are researching {company_name} for the {job_role} role. This may take a few seconds..."):
                
                # 1. SETUP MODEL (Universal Fix)
                genai.configure(api_key=api_key)
                active_model = "models/gemini-1.5-flash" 
                try:
                    all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if 'models/gemini-1.5-flash' in all_models:
                        active_model = 'models/gemini-1.5-flash'
                    elif 'models/gemini-pro' in all_models:
                        active_model = 'models/gemini-pro'
                    elif all_models:
                        active_model = all_models[0]
                except Exception:
                    pass 
                
                model = genai.GenerativeModel(active_model)

                # 2. THE MASTER PROMPT
                full_prompt = f"""
                Role: You are an elite career coach and corporate intelligence researcher.
                
                Task: I am preparing a student for a job interview at {company_name} for the {job_role} position. 
                Please generate a highly detailed, comprehensive research briefing to give them a competitive edge.
                
                Please structure the briefing strictly using the following sections. Use markdown for readability:
                
                1. Company Overview & DNA:
                - Founding history, mission statement, and core company values.
                - Key executives and current leadership structure.
                
                2. Business Model & Financial Health:
                - How does the company make money? (Core products, services, target audience, and revenue streams).
                - Recent financial performance, funding rounds, or overall market position.
                
                3. Industry Landscape & Competitors:
                - Who are their top 3 to 5 direct competitors?
                - What is {company_name}'s unique value proposition or competitive advantage in the market?
                
                4. Recent News & Strategic Initiatives:
                - Major announcements, product launches, acquisitions, or news events from the last 6 to 12 months.
                - Current challenges, industry shifts, or pain points the company might be trying to solve.
                
                5. Work Culture & Employee Experience:
                - Known workplace culture, management style, and work environment (synthesize general insights typically found on company review sites).
                - Notable initiatives regarding employee growth or social responsibility.
                
                6. Interview Strategy & Application for {job_role}:
                - How the student can connect their role to the company's broader mission.
                - Specific soft skills or behavioral traits the company historically values (e.g., bias for action, collaboration, adaptability).
                - 3 highly tailored, strategic questions the student should ask the interviewer at the end of the conversation to demonstrate deep research.
                """

                # 3. GENERATE
                response = model.generate_content(full_prompt)
                
                # 4. DISPLAY
                st.success("✅ Briefing Generated Successfully!")
                st.markdown("---")
                st.markdown(response.text)
                
                # Add a copy button logic (Streamlit native code block or text area)
                with st.expander("Show Raw Text (for easy copying)"):
                    st.text_area("Copy your briefing here:", response.text, height=300)

        except Exception as e:
            st.error(f"Error: {e}")
            st.warning("If this fails, ensure your API key has correct permissions and quotas.")
