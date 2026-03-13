import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# --- PAGE CONFIG ---
st.set_page_config(page_title="PrepCo Interview Intel", page_icon="🎯", layout="centered")

# --- SIDEBAR: API KEY ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

st.title("🎯 PrepCo Interview Intel Agent")
st.markdown("Generate a 5-minute research dossier for your upcoming interview.")

# --- UI CONTROLS ---
col1, col2 = st.columns(2)
with col1:
    company_name = st.text_input("Company Name *", placeholder="e.g., McKinsey & Company")
with col2:
    job_role = st.text_input("Job Title / Role *", placeholder="e.g., Summer Associate")

website_url = st.text_input("Company Website URL (Optional but Recommended)", placeholder="e.g., https://www.mckinsey.com")

# --- WEBSCRAPER FUNCTION ---
def scrape_website(url):
    try:
        # We use a 'User-Agent' to pretend to be a normal web browser, preventing some blocks.
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text and clean it up
        text = soup.get_text(separator=' ', strip=True)
        # Return the first 10,000 characters to avoid overwhelming the AI
        return text[:10000] 
    except Exception as e:
        return None

if st.button("Generate Research Briefing", type="primary"):
    if not api_key:
        st.error("⚠️ Please enter your Gemini API Key in the sidebar.")
    elif not company_name or not job_role:
        st.warning("⚠️ Please enter both the Company Name and the Job Role.")
    else:
        try:
            with st.spinner(f"Deploying agents to research {company_name}..."):
                
                # 1. SCRAPE THE WEB (IF URL PROVIDED)
                live_context = ""
                if website_url:
                    st.toast("Scraping live website data...")
                    scraped_text = scrape_website(website_url)
                    if scraped_text:
                        live_context = f"\n\n--- LIVE WEBSITE DATA FROM {website_url} ---\n{scraped_text}\n-------------------------------------------\nUse the live data above to make your insights highly accurate and up-to-date."
                    else:
                        st.warning("⚠️ Could not read the website (it may be blocking bots). Proceeding with general AI knowledge.")

                # 2. SETUP MODEL
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

                # 3. THE 5-MINUTE DOSSIER PROMPT
                full_prompt = # 3. THE 5-MINUTE DOSSIER PROMPT (WITH ACCURACY GUARDRAILS)
                f"""
                Act as an elite corporate intelligence researcher and MBA Career Coach. Your task is to generate a comprehensive but highly scannable "5-Minute Interview Dossier" for a candidate interviewing at {company_name} for the {job_role} position.
                {live_context}
                
                CRITICAL ACCURACY & ENTITY CHECK:
                Before generating the dossier, you MUST verify the exact identity of '{company_name}'. 
                - If multiple companies share this name, use the '{job_role}' context and the provided website data to identify the correct corporate entity.
                - Ground ALL facts (revenue, competitors, news) strictly in reality. Do NOT hallucinate or guess financial metrics.
                - If a specific metric or news item is unknown, state "Data not publicly disclosed" rather than making it up.
                
                STRICT FORMATTING RULES:
                - Target length: Detailed enough for a 5-minute read (approx. 600-800 words).
                - Use bullet points with bolded keywords for easy scanning.
                - NO long, blocky paragraphs. 
                - Focus on MBA-level strategic insights rather than generic surface-level facts.
                
                STRUCTURE THE DOSSIER EXACTLY AS FOLLOWS:
                
                ### 🏢 1. The Executive Brief (Company DNA)
                * **Verified Entity:** [State the full legal name, industry, and HQ location of the company you are profiling to prove you selected the right one]
                * **Mission & Vision:** [2-3 sentences explaining their core purpose and long-term goal]
                * **Culture & Values:** [3 detailed bullet points on their management style and what behaviors they actually reward]
                
                ### 💰 2. The Economic Engine (Business Model)
                * **Revenue Streams:** [Break down exactly how they make money in 3-4 detailed bullets. Mention core products/services and target demographics.]
                * **Financial Posture:** [Explain their current financial narrative in 2 bullets. Are they prioritizing growth, profitability, cutting costs, or expanding?]
                
                ### ⚔️ 3. The Competitive Moat (Market Landscape)
                * **Key Competitors:** [List top 3-4 competitors and exactly how {company_name} differentiates itself from them]
                * **Unique Value Proposition:** [Detail their 'unfair advantage'—e.g., distribution network, proprietary tech, brand loyalty]
                
                ### 📰 4. Strategic Imperatives (Recent News & Headwinds)
                * **Recent Wins:** [2-3 bullet points on major launches, acquisitions, or positive news from the last 12-18 months]
                * **Current Challenges/Headwinds:** [2-3 bullet points on their biggest threats right now—e.g., regulatory hurdles, supply chain, new entrants, AI disruption]
                
                ### 🎯 5. The {job_role} Playbook
                * **Core Competencies:** [3 specific technical or soft skills they will heavily test for this specific role]
                * **How to Add Value:** [2 concrete ways a person in this role can help solve the company's current challenges mentioned above]
                
                ### 🎤 6. "Drop the Mic" Questions (To ask the Interviewer)
                Provide 3 highly strategic, MBA-level questions for the candidate to ask at the end of the interview. For each, include a brief rationale.
                * **Question 1:** [Strategic question about company direction or market shifts]
                  * *Why this works:* [Brief rationale on why this impresses the panel]
                * **Question 2:** [Role-specific or operational question]
                  * *Why this works:* [Brief rationale]
                * **Question 3:** [Culture, team-dynamics, or success-metric question]
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
            st.error(f"Error: {e}")
