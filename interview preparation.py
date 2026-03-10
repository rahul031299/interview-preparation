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
                Act as an elite corporate intelligence researcher. Create a highly precise, actionable, and scannable "Interview Cheat Sheet" for a candidate interviewing at {company_name} for the {job_role} position.
                
                STRICT CONSTRAINTS:
                - ZERO fluff, filler words, or generic advice.
                - Use punchy, data-backed bullet points.
                - Maximum 2-3 bullets per section.
                - Keep sentences under 15 words.
                
                STRUCTURE THE OUTPUT EXACTLY LIKE THIS:
                
                ### 🏢 1. The DNA (Company Overview)
                * **What they actually do:** [1 sentence summary]
                * **Core Values:** [Just the keywords, e.g., "Bias for Action, Frugality"]
                
                ### 💰 2. The Engine (Business Model & Health)
                * **How they make money:** [Revenue streams in 1 bullet]
                * **Market Position:** [Current financial health or market share]
                
                ### ⚔️ 3. The Moat (Competitors & Advantage)
                * **Top 3 Competitors:** [Names only]
                * **The Unique Advantage:** [Why they win against competitors in 1 sentence]
                
                ### 📰 4. The "Right Now" (Recent News & Challenges)
                * **Recent Win:** [Biggest news/launch in the last 6 months]
                * **Biggest Pain Point:** [Current strategic challenge they are facing]
                
                ### 🎯 5. The Interview Angle (For a {job_role})
                * **What they want:** [The core competency needed for this specific role]
                * **Cultural Fit:** [Top 2 soft skills to emphasize]
                
                ### 🎤 6. The "Drop the Mic" Questions (To ask the interviewer)
                Provide exactly 2 highly strategic, role-specific questions the candidate should ask to prove they did deep research. (Do not give generic questions).
                1. [Question 1]
                2. [Question 2]
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
