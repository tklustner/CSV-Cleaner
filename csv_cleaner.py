import pandas as pd
import streamlit as st
import base64
import io


# Cleaning function
def clean_dataframe(df, drop_duplicates=False, drop_empty_rows=False):
    if drop_duplicates:
        df.drop_duplicates(inplace=True)
    if drop_empty_rows:
        df.dropna(inplace=True)
    return df


# Streamlit formatting
st.set_page_config(
    page_title="CSV Data Cleaning App", page_icon="🧼", layout="centered"
)

st.markdown(
    """<style>#MainMenu, footer {visibility: hidden;}</style>""", unsafe_allow_html=True
)

st.title("CSV Data Cleaning App")

st.markdown(" ## Upload one or more CSV files to merge, clean or modify.")

# Reading files
upload = st.file_uploader(
    "Upload CSV files",
    type="csv",
    accept_multiple_files=True,
)

dataframes = []

if upload:
    try:
        dataframes = [pd.read_csv(file) for file in upload]
    except UnicodeDecodeError:
        st.error(
            "Error: Encountered characters outside valid range for encoding. \
                Please ensure the CSV file uses UTF-8 encoding."
        )
    except pd.errors.ParserError as e:  # type: ignore
        dataframes = [pd.read_csv(file, sep=";") for file in upload]

# For single upload
if len(dataframes) == 1:
    df = dataframes[0]
    drop_first_row = st.selectbox("Remove first row", ["Yes", "No"])
    drop_duplicate_rows = st.selectbox("Remove duplicate rows", ["Yes", "No"])
    drop_empty_rows = st.selectbox("Remove all empty rows", ["Yes", "No"])

    # removing first row
    if drop_first_row == "Yes":
        df = df.iloc[1:,]

    df = clean_dataframe(
        df.copy(),
        drop_duplicate_rows == "Yes",
        drop_empty_rows == "Yes",
    )
    dataframes = [df]

    show_df = st.checkbox("Show Data", value=True)
    if show_df:
        for i, df in enumerate(dataframes):
            st.write(f"File {i + 1}")
            st.dataframe(df)

    if st.button("Download Cleaned Data") and dataframes:
        for i, df in enumerate(dataframes):
            csv = df.to_csv(index=False)
        if csv:
            href = f'<a href="data:file/csv;base64, {base64.b64encode(csv.encode()).decode()}" \
            download= "cleaned_data_{i + 1}.csv"> Download cleaned_data_{i + 1}.csv </a>'
            st.markdown(href, unsafe_allow_html=True)

# Merge multiple dataframes
elif len(dataframes) > 1:
    merge = st.checkbox("Merge CSV files")
    if merge:
        keep_header = st.selectbox(
            "Make first row of first file the header", ["Yes", "No"]
        )
        drop_duplicate_rows = st.selectbox("Remove duplicate rows", ["Yes", "No"])
        drop_empty_rows = st.selectbox("Remove all empty rows", ["Yes", "No"])

        try:
            dataframes = [
                (df.set_axis(df.iloc[0], axis=1) if keep_header == "Yes" else df)
                for df in dataframes
            ]

            merged_df = pd.concat(
                [df.reset_index(drop=True) for df in dataframes],
                ignore_index=True,
                join="outer",
            )

            merged_df = clean_dataframe(
                merged_df,
                drop_duplicate_rows == "Yes",
                drop_empty_rows == "Yes",
            )

            dataframes = [merged_df]

        except Exception as e:
            st.error(
                f"An error occurred during merging: {e}; Please ensure at least one column matches"
            )
    # Display dataframes
    show_df = st.checkbox("Show Data", value=True)

    if show_df:
        for i, df in enumerate(dataframes):
            st.write(f"File {i + 1}")
            st.dataframe(df)

    # download cleaned CSVs
    if st.button("Download Cleaned Data") and dataframes:
        for i, df in enumerate(dataframes):
            csv = df.to_csv(index=False)
        if csv:
            href = f'<a href="data:file/csv;base64, {base64.b64encode(csv.encode()).decode()}" \
            download= "cleaned_data_{i + 1}.csv"> Download cleaned_data_{i + 1}.csv </a>'
            st.markdown(href, unsafe_allow_html=True)

    if not dataframes:
        st.warning("Please upload CSV files")
        st.stop()

st.markdown("")
st.markdown("---")
st.markdown(
    "<p style= 'text-align: center'><a href='https://github.com/tklustner'>Github</a></p>",
    unsafe_allow_html=True,
)
