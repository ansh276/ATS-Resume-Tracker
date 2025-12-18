import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import os
from dotenv import load_dotenv

from helper import (
    configure_openai,
    get_openai_response,
    extract_pdf_text,
    extract_docx_text,
    prepare_prompt
)


def init_session_state():
    if "processing" not in st.session_state:
        st.session_state.processing = False


def main():
    load_dotenv()
    init_session_state()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error(" Please set the OPENAI_API_KEY in your .env file.")
        return

    # Create OpenAI client
    try:
        client = configure_openai(api_key)
    except Exception as e:
        st.error(f" Failed to configure OpenAI API: {str(e)}")
        return


    with st.sidebar:
        st.title("🎯 Smart ATS")
        st.subheader("About")
        st.write(
            """
            This Smart ATS helps you:
            - Evaluate resume vs job description match
            - Identify missing ATS keywords
            - Get personalized resume improvement suggestions
            """
        )
        add_vertical_space(2)


    st.title("📄 Smart ATS Resume Analyzer")
    st.subheader("Optimize Your Resume for ATS Screening")

    jd = st.text_area(
        "Job Description",
        placeholder="Paste the complete job description here...",
        help="Provide the full job description for accurate ATS evaluation",
    )

    uploaded_file = st.file_uploader(
        "Upload Resume (PDF or DOCX)",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX"
    )

    

    if st.button(" Analyze Resume", disabled=st.session_state.processing):

        if not jd.strip():
            st.warning(" Please enter a job description.")
            return

        if not uploaded_file:
            st.warning(" Please upload your resume.")
            return

        st.session_state.processing = True

        try:
            with st.spinner("📊 Analyzing your resume using ATS logic..."):

                file_ext = uploaded_file.name.split(".")[-1].lower()

                # Extract resume text
                if file_ext == "pdf":
                    resume_text = extract_pdf_text(uploaded_file)
                elif file_ext == "docx":
                    resume_text = extract_docx_text(uploaded_file)
                else:
                    st.error("Unsupported file format.")
                    return

                # Prepare prompt
                input_prompt = prepare_prompt(resume_text, jd)

                # Call OpenAI
                response_json = get_openai_response(client, input_prompt)

                

                st.success("✅ Analysis Complete!")

                # Match Score
                st.metric(
                    label="ATS Match Score",
                    value=response_json.get("JD Match", "N/A")
                )

                # Missing Keywords
                st.subheader(" Missing Keywords")
                missing_keywords = response_json.get("Missing Keywords", [])

                if missing_keywords:
                    st.write(", ".join(missing_keywords))
                else:
                    st.write(" No critical keywords missing!")

                # Profile Summary
                st.subheader(" Profile Summary")
                st.write(
                    response_json.get(
                        "Profile Summary",
                        "No summary available."
                    )
                )

        except Exception as e:
            st.error(f" An error occurred: {str(e)}")

        finally:
            st.session_state.processing = False


if __name__ == "__main__":
    main()
