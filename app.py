import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from src.services.job_analyzer import analyze_job_skills
from src.config import LLM_API_KEY, LLM_PROVIDER

st.set_page_config(page_title="SkillPulse AI", layout="wide")

st.title("🎯 SkillPulse AI")
st.markdown("Discover the most in-demand technical skills for your desired job role in India using real-time market data.")

col1, col2 = st.columns(2)
with col1:
    role = st.text_input("Job Role", placeholder="e.g., Backend Developer, Data Scientist")
with col2:
    experience = st.selectbox("Experience Level", ["0-2 years", "2-4 years", "4-7 years", "8+ years"])

if st.button("Analyze Market", type="primary"):
    if not role:
        st.warning("Please enter a Job Role.")
    elif not LLM_API_KEY or LLM_API_KEY == "your_llm_api_key_here":
        st.error(f"LLM API Key is missing. Please configure your .env file with your preferred LLM provider's key (e.g. {LLM_PROVIDER}).")
    else:
        with st.spinner(f"Fetching job listings for '{role}' and analyzing technical skills..."):
            try:
                top_skills = analyze_job_skills(role, experience)
                
                if not top_skills:
                    st.warning("No jobs found or no technical skills could be extracted for this query.")
                else:
                    st.success("Analysis Complete!")
                    
                    df = pd.DataFrame(top_skills, columns=["Skill", "Frequency"])
                    
                    chart_col, table_col = st.columns([2, 1])
                    
                    with chart_col:
                        st.subheader("Skill Cloud")
                        skill_dict = dict(top_skills)
                        wordcloud = WordCloud(
                            width=800, 
                            height=400, 
                            background_color="white", 
                            colormap="viridis"
                        ).generate_from_frequencies(skill_dict)
                        
                        fig, ax = plt.subplots(figsize=(10, 5))
                        ax.imshow(wordcloud, interpolation="bilinear")
                        ax.axis("off")
                        st.pyplot(fig)
                        
                    with table_col:
                        st.subheader("Top 15 Skills")
                        st.dataframe(df, use_container_width=True)
                        
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Data as CSV",
                            data=csv,
                            file_name=f"{role.replace(' ', '_')}_{experience.replace(' ', '_')}_skills.csv",
                            mime="text/csv"
                        )
                        
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
