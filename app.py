import pandas as pd
import plotly.express as px
import streamlit as st

# Path to the Excel file
file_path = r"S:\FOR\Adm_EquipmentManager\Visor Archive.xlsx"

# Streamlit app
st.title("Vehicle Assignment Gantt Chart")

try:
    # Load the Excel file
    df = pd.read_excel(file_path, engine="openpyxl")

    # Ensure date columns are properly converted
    df['Checkout Date'] = pd.to_datetime(df['Checkout Date'])
    df['Return Date'] = pd.to_datetime(df['Return Date'])

    # Add a unique identifier for each row
    df["Unique ID"] = df.index

    # Gantt chart panel
    st.subheader("Interactive Gantt Chart")
    fig = px.timeline(
        df,
        x_start="Checkout Date",
        x_end="Return Date",
        y="Type",
        color="Assigned to",
        title="Vehicle Assignments",
        hover_data=["Unique ID", "Assigned to", "Status", "Type", "Checkout Date", "Return Date"],
        labels={"Assigned to": "Vehicle"}
    )

    # Update layout for better visualization
    fig.update_yaxes(categoryorder="total ascending")

    # Display the Gantt chart
    st.plotly_chart(fig, use_container_width=True)

    # User selects an entry by its unique ID
    st.subheader("Manage Selected Entry")
    selected_id = st.number_input(
        "Enter the Unique ID of the entry to edit/delete:",
        min_value=0,
        max_value=len(df) - 1,
        step=1
    )

    if selected_id in df["Unique ID"].values:
        # Display details of the selected entry
        st.write("Selected Entry Details:")
        st.write(df.loc[df["Unique ID"] == selected_id])

        # Edit the selected entry
        st.subheader("Edit Entry")
        edited_row = {}
        for column in df.columns[:-1]:  # Exclude the "Unique ID" column
            if pd.api.types.is_datetime64_any_dtype(df[column]):
                edited_row[column] = st.date_input(f"{column}:", value=df.loc[selected_id, column])
            elif pd.api.types.is_numeric_dtype(df[column]):
                edited_row[column] = st.number_input(f"{column}:", value=df.loc[selected_id, column])
            else:
                edited_row[column] = st.text_input(f"{column}:", value=df.loc[selected_id, column])

        if st.button("Update Entry"):
            # Update the DataFrame with edited values
            for key, value in edited_row.items():
                df.at[selected_id, key] = value
            st.success("Entry updated successfully!")

        # Delete the selected row
        if st.button("Delete Entry"):
            df = df.drop(index=selected_id).reset_index(drop=True)
            st.success("Entry deleted successfully!")

    # Save changes to Excel (optional)
    if st.button("Save Changes"):
        df.to_excel(file_path, index=False, engine="openpyxl")
        st.success("Changes saved to the Excel file!")

except Exception as e:
    st.error(f"Error reading or processing the file: {e}")
