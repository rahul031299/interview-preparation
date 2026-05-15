import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import PyPDF2
import docx
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Interview Preparation", page_icon="🎯", layout="centered")

# --- SIDEBAR: API KEY ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

st.title("🎯 PrepCo Interview Intel Agent")
st.markdown("Generate a 5-minute research dossier tailored to the exact JD and past interviews.")

# --- UI CONTROLS ---
col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input("Company Name *", placeholder="e.g., Company name")
with col2:
    job_role = st.text_input("Job Title / Role *", placeholder="e.g., Summer Associate")

website_url = st.text_input("Company Website URL (Optional)", placeholder="e.g., https://www.TATA.com")

st.markdown("### 📄 Context Documents (Optional but Recommended)")
col3, col4 = st.columns(2)
with col3:
    jd_file = st.file_uploader("Upload Job Description", type=["pdf", "docx", "txt"])
with col4:
    exp_file = st.file_uploader("Upload Past Experiences", type=["pdf", "docx", "txt"])

# --- HELPER FUNCTIONS ---
def scrape_website(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text(separator=' ', strip=True)[:10000] 
    except Exception:
        return None

def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    try:
        text = ""
        if uploaded_file.name.endswith('.pdf'):
            reader = PyPDF2.PdfReader(uploaded_file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        elif uploaded_file.name.endswith('.txt'):
            text = uploaded_file.read().decode('utf-8')
        return text[:10000] # Limit to 10k characters to stay focused
    except Exception as e:
        return f"[Error reading file: {e}]"

# --- MAIN GENERATION ---
if st.button("Generate Research Briefing", type="primary"):
    if not api_key:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar.")
    elif not company_name or not job_role:
        st.warning("⚠️ Please enter both the Company Name and the Job Role.")
    else:
        try:
            with st.spinner(f"Analyzing documents & researching {company_name}..."):
                
                # 1. GATHER ALL CONTEXT
                live_context = ""
                if website_url:
                    scraped_text = scrape_website(website_url)
                    if scraped_text:
                        live_context += f"\n\n--- LIVE WEBSITE DATA ---\n{scraped_text}\n"

                jd_context = extract_text_from_file(jd_file)
                if jd_context:
                    live_context += f"\n\n--- OFFICIAL JOB DESCRIPTION ---\n{jd_context}\n"
                    
                exp_context = extract_text_from_file(exp_file)
                if exp_context:
                    live_context += f"\n\n--- PAST INTERVIEW EXPERIENCES ---\n{exp_context}\n"

                # 2. SETUP MODEL
                genai.configure(api_key=api_key)
                active_model = "models/gemini-3-flash" 
                try:
                    all_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    if 'models/gemini-3-flash' in all_models:
                        active_model = 'models/gemini-3-flash'
                    elif 'models/gemini-3.1-flash-lite' in all_models:
                        active_model = 'models/gemini-3.1-flash-lite'
                    elif all_models:
                        active_model = all_models[0]
                except Exception:
                    pass 
                
                model = genai.GenerativeModel(active_model)

                # 3. THE HYPER-TARGETED PROMPT
                full_prompt = f"""
                Act as an elite corporate intelligence researcher and MBA Career Coach. Your task is to generate a highly scannable "5-Minute Interview Dossier" for a candidate interviewing at {company_name} for the {job_role} position.
                
                Here is the provided context (Website data, JD, and/or Past Interviews). Use this to hyper-personalize your advice:
                {live_context}
                
                CRITICAL INSTRUCTIONS:
                - If a Job Description is provided, map the "Core Competencies" directly to what the JD emphasizes.
                - If Past Interview Experiences are provided, tailor the insights and questions to address patterns, traps, or themes seen in those past interviews.
                - Verify the entity of '{company_name}' to avoid hallucinations.
                
                STRICT FORMATTING RULES:
                - Target length: 610-800 words.
                - Use bullet points with bolded keywords. NO blocky paragraphs.
                
                STRUCTURE THE DOSSIER EXACTLY AS FOLLOWS:
                
                ### 🏢 1. The Executive Brief (Company DNA)
                * **Verified Entity:** [Legal name, industry, and HQ]
                * **Mission & Vision:** [2-3 sentences on core purpose]
                * **Culture & Values:** [3 detailed bullets on management style]
                
                ### 💰 2. The Economic Engine (Business Model)
                * **Revenue Streams:** [3-4 detailed bullets on how they make money]
                * **Financial Posture:** [Current financial narrative]
                
                ### ⚔️ 3. The Competitive Moat
                * **Key Competitors:** [Top 3-4 competitors and differentiators]
                * **Unique Value Proposition:** [Their 'unfair advantage']
                
                ### 🎯 4. The {job_role} book (Tailored to JD)
                * **Core Competencies Tested:** [Extract 3 hard/soft skills prioritized in the JD or role standard]
                * **Past Interview Patterns:** [If past experiences were provided, summarize the 2 biggest themes/types of questions asked previously. If not provided, state "No past data provided - expect standard behavioral/case questions."]
                * **How to Add Value:** [2 concrete ways this role solves their current challenges]
                
                ### 🎤 5. Questions To ask the Interviewer
                Provide 3 highly strategic questions for the candidate to ask. Ensure they do not overlap with what was asked in past interviews.
                * **Question 1:** [Strategic question]
                  * *Why this works:* [Brief rationale]
                * **Question 2:** [Role-specific/JD-related question]
                  * *Why this works:* [Brief rationale]
                * **Question 3:** [Culture/Team question]
                  * *Why this works:* [Brief rationale]
                """

                # 4. GENERATE
                response = model.generate_content(full_prompt)
                
                # 5. DISPLAY
                st.success("✅ Briefing Generated Successfully!")
                st.markdown("---")
                st.markdown(response.text)
                
                with st.expander("Show Raw Text (for easy copying)"):
                    st.text_area("Copy your briefing here:", response.text, height=300)

        except Exception as e:
            st.error(f"Error processing request: {e}")
            st.warning("If uploading large PDFs, try extracting just the text into a txt file first.")
