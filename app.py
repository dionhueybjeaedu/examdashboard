import pandas as pd
import streamlit as st

# Helper function to normalize scores (percentages or whole numbers)
def normalize_score(value):
    try:
        if pd.isna(value):
            return None
        value = float(value)
        if 0 < value <= 1:
            return round(value * 100)
        return round(value)
    except:
        return None

# File uploader
uploaded_file = st.file_uploader("Upload your AP Exam Excel Sheet", type=["xlsx"])

if uploaded_file:
    df_raw = pd.read_excel(uploaded_file, header=None)

    # Extract metadata and student data
    student_rows = df_raw.iloc[14:54]
    question_numbers = [
        f"Q{idx+1}" if pd.isna(q) or str(q).strip() == "" else str(q)
        for idx, q in enumerate(df_raw.iloc[11, 13:73])
    ]
    correct_answers = df_raw.iloc[12, 13:73].tolist()
    mc_topics = df_raw.iloc[9, 13:73].tolist()
    mc_skills = df_raw.iloc[10, 13:73].tolist()
    frq_topics = df_raw.iloc[9, 73:76].tolist()
    frq_skills = df_raw.iloc[10, 73:76].tolist()
    st.write("DEBUG: Total MCQs pulled =", len(question_numbers))

    # Process each student row
    summary_data = []
    for _, row in student_rows.iterrows():
        student_id = row[1]
        first_name = row[2]
        last_name = row[3]
        english_name = row[4]

        mc_score = normalize_score(row[6])
        frq_total = normalize_score(row[7])
        frq1 = normalize_score(row[8])
        frq2 = normalize_score(row[9])
        frq3 = normalize_score(row[10])
        predicted_ap = row[11]  # Column L

        incorrect_mc = []
        weak_topics = set()

for idx, question_number in enumerate(question_numbers):
    if pd.isna(question_number) or str(question_number).strip() == "":
        continue  # skip blank question numbers

    col = 13 + idx # match to the column index
    answer = row[col]
    correct_answer = correct_answers[idx]
    topic = mc_topics[idx]
    skill = mc_skills[idx]

    if pd.notna(answer) and answer != correct_answer:
        weak_topics.add(topic)
        incorrect_mc.append({
            "Q": question_number,
            "Topic": topic,
            "Skill": skill,
            "Answer": answer,
            "Correct": correct_answer
        })

        summary_data.append({
            "ID": student_id,
            "Name": " ".join(str(x) for x in [first_name, last_name] if pd.notna(x)),
            "MC Score": mc_score,
            "FRQ Total": frq_total,
            "FRQ1": frq1,
            "FRQ2": frq2,
            "FRQ3": frq3,
            "Predicted AP Score": predicted_ap,
            "Incorrect Count": len(incorrect_mc),
            "Weak Topics": ", ".join(str(t) for t in weak_topics if pd.notna(t)),
            "Incorrect Details": incorrect_mc,
        })

    # Display dashboard
    st.title("Student Performance Dashboard")
    df_summary = pd.DataFrame(summary_data).reset_index(drop=True)
    st.dataframe(df_summary[["ID", "Name", "Predicted AP Score", "MC Score", "FRQ Total", "Incorrect Count", "Weak Topics"]])

    # Individual student view
    selected_student = st.selectbox("Select a student to view details", df_summary["Name"])
    student_info = next(s for s in summary_data if s["Name"] == selected_student)

    st.subheader("Individual Performance")
    st.write(f"**MC Score:** {student_info['MC Score']}")
    st.write(f"**FRQ Total:** {student_info['FRQ Total']} (FRQ1: {student_info['FRQ1']}, FRQ2: {student_info['FRQ2']}, FRQ3: {student_info['FRQ3']})")
    st.write("**Weak Topics:**", student_info['Weak Topics'])

    # Incorrect details
    st.subheader("Incorrect MC Questions")
    st.dataframe(pd.DataFrame(student_info["Incorrect Details"]))

    # Recommendations
    st.subheader("AI Recommendations")
    for topic in student_info['Weak Topics'].split(", "):
        st.markdown(f"- Review **{topic}**. Consider redoing practice questions and revisiting core concepts.")
