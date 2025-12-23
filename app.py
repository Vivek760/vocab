import streamlit as st
import json
import pandas as pd

# -------------------------
# Page configuration
# -------------------------
st.set_page_config(
    page_title="Vocabulary Dashboard",
    layout="wide"
)

st.title("Vocab")

# -------------------------
# Load JSON data
# -------------------------
@st.cache_data
def load_data():
    with open("results.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # Convert list of synonyms to readable string
    df["synonyms"] = df["synonyms"].apply(lambda x: ", ".join(x))
    return df

df = load_data()

# -------------------------
# Sidebar filters
# -------------------------
# st.sidebar.header("Filters")

# search_word = st.sidebar.text_input("Search word")

# pos_filter = st.sidebar.multiselect(
#     "Part of Speech",
#     options=sorted(df["part_of_speech"].unique()),
#     default=sorted(df["part_of_speech"].unique())
# )

# -------------------------
# Apply filters
# -------------------------
# filtered_df = df[df["part_of_speech"].isin(pos_filter)]

# if search_word:
#     filtered_df = filtered_df[
#         filtered_df["word"].str.contains(search_word, case=False)
#     ]


# st.subheader("🔍 Search")

# search_query = st.text_input(
#     "Search across words, meanings, synonyms, examples",
#     placeholder="Type to filter…"
# )
search_query = st.text_input("Search", key="search", on_change=None)


filtered_df = df.copy()

if search_query:
    q = search_query.lower()

    filtered_df = filtered_df[
        df.apply(
            lambda row: (
                q in row["word"].lower()
                or q in row["meaning"].lower()
                or q in row["synonyms"].lower()
                or q in row["example_sentence"].lower()
            ),
            axis=1
        )
    ]

if st.button("Clear search"):
    st.rerun()

# -------------------------
# Main table view
# -------------------------
st.subheader("Word List")

# st.subheader("Word List")

all_columns = {
    "word": "Word",
    "meaning": "Meaning",
    "synonyms": "Synonyms",
    "part_of_speech": "Part of Speech",
    "hindi_transliteration": "Hindi Transliteration",
    "example_sentence": "Example Sentence",
}

selected_cols = st.multiselect(
    "Select columns to display",
    options=list(all_columns.keys()),
    default=["word", "meaning", "part_of_speech"],
    format_func=lambda x: all_columns[x]
)

# fallback if nothing selected
if not selected_cols:
    st.warning("Please select at least one column.")
else:
    st.dataframe(
        filtered_df[selected_cols],
        width='stretch',
        hide_index=True
    )


# -------------------------
# Word detail viewer
# -------------------------
# st.subheader("Word Details")
with st.expander("Word Details", expanded=False):
    selected_word = st.selectbox(
        "Select a word",
        filtered_df["word"].tolist()
    )

    if selected_word:
        row = filtered_df[filtered_df["word"] == selected_word].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**Meaning:** {row['meaning']}")
            st.markdown(f"**Part of Speech:** {row['part_of_speech']}")
            st.markdown(f"**Hindi Transliteration:** {row['hindi_transliteration']}")

        with col2:
            st.markdown(f"**Synonyms:** {row['synonyms']}")
            st.markdown(f"**Example Sentence:**")
            st.info(row["example_sentence"])


st.divider()

with st.expander("Word Browser", expanded=False):

    if "expanded_word" not in st.session_state:
        st.session_state.expanded_word = None

    words = filtered_df.to_dict("records")
    cols = st.columns(5)

    for idx, w in enumerate(words):
        col = cols[idx % 5]

        with col:
            if st.button(w["word"], key=f"grid_word_{idx}"):
                # toggle inline expansion
                if st.session_state.expanded_word == w["word"]:
                    st.session_state.expanded_word = None
                else:
                    st.session_state.expanded_word = w["word"]

            if st.session_state.expanded_word == w["word"]:
                st.markdown(
                    f"""
                    **Meaning:** {w['meaning']}  
                    **POS:** {w['part_of_speech']}  
                    **Synonyms:** {w['synonyms']}  
                    **Hindi:** {w['hindi_transliteration']}  
                    _{w['example_sentence']}_
                    """
                )


import random

st.divider()
with st.expander("Flashcards & Quiz", expanded=False):
# st.header("Flashcards & Quiz")

    mode = st.radio(
        "Select Mode",
        ["Flashcard", "Quiz"],
        horizontal=True
    )

    # ---------- Flashcard Mode ----------
    if mode == "Flashcard":
        if "flashcard_word" not in st.session_state:
            st.session_state.flashcard_word = df.sample(1).iloc[0]

        word = st.session_state.flashcard_word

        st.subheader(word["word"])

        if st.button("Reveal Meaning"):
            st.write(f"**Meaning:** {word['meaning']}")
            st.write(f"**Part of Speech:** {word['part_of_speech']}")
            st.write(f"**Synonyms:** {word['synonyms']}")
            st.write(f"**Example:** {word['example_sentence']}")

        if st.button("Next Word"):
            st.session_state.flashcard_word = df.sample(1).iloc[0]
            st.rerun()

    # ---------- Quiz Mode ----------
    if mode == "Quiz":
        if "quiz_word" not in st.session_state:
            st.session_state.quiz_word = df.sample(1).iloc[0]

        quiz_word = st.session_state.quiz_word

        correct = quiz_word["meaning"]
        options = df.sample(3)["meaning"].tolist()
        if correct not in options:
            options[random.randint(0, 2)] = correct
        random.shuffle(options)

        st.subheader(f"What is the meaning of **{quiz_word['word']}**?")

        answer = st.radio("Choose one:", options)

        if st.button("Submit"):
            if answer == correct:
                st.success("Correct!")
            else:
                st.error(f"Wrong. Correct answer: {correct}")

        if st.button("Next Question"):
            st.session_state.quiz_word = df.sample(1).iloc[0]
            st.rerun()
