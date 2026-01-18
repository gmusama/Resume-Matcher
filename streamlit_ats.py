import streamlit as st

from scripts.ats_tailor import build_outputs, read_text_from_upload

st.set_page_config(
    page_title="Resume Matcher - ATS Tailor",
    page_icon="Assets/img/favicon.ico",
    layout="centered",
)

st.title(":blue[ATS Resume Tailor]")
st.write(
    "Upload your resume and a job description to generate a tailored resume text file "
    "and a starter cover letter."
)

with st.sidebar:
    st.subheader("Quick tips")
    st.markdown("- Upload PDF or TXT files.")
    st.markdown("- Review the generated text before submitting anywhere.")
    st.markdown("- This tool does not auto-submit applications.")

resume_file = st.file_uploader(
    "Upload your resume (PDF or TXT)", type=["pdf", "txt"]
)
job_file = st.file_uploader(
    "Upload the job description (PDF or TXT)", type=["pdf", "txt"]
)

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Your name", value="Your Name")
    role = st.text_input("Target role", value="Target Role")
with col2:
    company = st.text_input("Company", value="Company Name")
    top_n = st.number_input("Keywords to extract", min_value=10, max_value=60, value=30)

max_keywords = st.slider("Keywords to include", min_value=5, max_value=30, value=20)

if st.button("Generate tailored files", type="primary"):
    if not resume_file or not job_file:
        st.error("Please upload both a resume and a job description.")
    else:
        resume_text = read_text_from_upload(resume_file.name, resume_file.getvalue())
        job_text = read_text_from_upload(job_file.name, job_file.getvalue())

        tailored_resume, cover_letter, matched, missing = build_outputs(
            resume_text,
            job_text,
            top_n=int(top_n),
            max_keywords=int(max_keywords),
            name=name,
            role=role,
            company=company,
        )

        st.success("Files generated. Review and download below.")

        st.subheader("Matched keywords")
        st.write(", ".join(matched) if matched else "None detected in the resume.")

        st.subheader("Missing keywords to consider")
        st.write(", ".join(missing) if missing else "None detected.")

        st.subheader("Tailored resume text")
        st.text_area("", tailored_resume, height=300)
        st.download_button(
            "Download tailored resume",
            data=tailored_resume,
            file_name="tailored_resume.txt",
        )

        st.subheader("Cover letter")
        st.text_area("", cover_letter, height=300)
        st.download_button(
            "Download cover letter",
            data=cover_letter,
            file_name="cover_letter.txt",
        )
