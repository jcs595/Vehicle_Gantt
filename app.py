import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta

# Path to the Excel file
file_path = r"Visor Archive.xlsx"

# Set the app to wide mode
st.set_page_config(layout="wide", page_title="Vehicle Assignment Gantt Chart", page_icon="📊")

# Streamlit app
st.title("Vehicle Assignment Gantt Chart")

# Load the data
try:
    df = pd.read_excel(file_path, engine="openpyxl")
    df['Checkout Date'] = pd.to_datetime(df['Checkout Date'])
    df['Return Date'] = pd.to_datetime(df['Return Date'])
    df["Unique ID"] = df.index  # Add a unique identifier for each row
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

# Full-screen Gantt chart
st.title("Interactive Vehicle Assignment Gantt Chart")
st.markdown("###")

# Add a button to toggle the legend
show_legend = st.checkbox("Show Legend", value=False)

# Calculate dynamic zoom range: past 2 weeks and next 4 weeks
today = datetime.today()
start_range = today - timedelta(weeks=2)  # 2 weeks ago
end_range = today + timedelta(weeks=4)    # 4 weeks from now

# Create the Gantt chart
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

# Limit the y-axis labels to three characters
fig.update_yaxes(
    ticktext=[label[:3] for label in df["Type"]],  # Truncated labels
    tickvals=df["Type"],
    title=None,  # Hide Y-axis title
)

# Add today's date as a vertical red line
fig.add_shape(
    type="line",
    x0=today,
    y0=0,
    x1=today,
    y1=1,
    xref="x",
    yref="paper",
    line=dict(color="red", width=2, dash="dot"),
    name="Today"
)

# Add weekly and daily grid lines
current_date = start_range
while current_date <= end_range:
    # Add weekly grid lines (thicker lines)
    if current_date.weekday() == 0:  # Monday
        fig.add_shape(
            type="line",
            x0=current_date,
            y0=0,
            x1=current_date,
            y1=1,
            xref="x",
            yref="paper",
            line=dict(color="gray", width=1.5, dash="solid"),
        )
    # Add daily grid lines (thinner lines)
    fig.add_shape(
        type="line",
        x0=current_date,
        y0=0,
        x1=current_date,
        y1=1,
        xref="x",
        yref="paper",
        line=dict(color="lightgray", width=0.5, dash="dot"),
    )
    current_date += timedelta(days=1)

# Add horizontal grid lines only for used rows
unique_y_values = df["Type"].unique()
for idx, label in enumerate(unique_y_values):
    fig.add_shape(
        type="line",
        x0=start_range,
        y0=idx - 0.5,  # Align with the row's center
        x1=end_range,
        y1=idx - 0.5,
        xref="x",
        yref="y",
        line=dict(color="lightgray", width=1, dash="dot"),
    )

# Update layout for dynamic zoom and better visualization
fig.update_layout(
    height=800,  # Adjust chart height to fit full screen
    title_font_size=20,
    margin=dict(l=0, r=0, t=40, b=0),  # Minimize margins
    showlegend=show_legend,  # Toggle legend based on the checkbox
    xaxis_range=[start_range, end_range]  # Set initial zoom range
)

# Display the Gantt chart full screen
st.plotly_chart(fig, use_container_width=True)

# Secure edit/delete section
with st.expander("Edit or Delete Entries (Protected)"):
    # Ask for the passcode
    passcode = st.text_input("Enter the 4-digit passcode:", type="password")

    # Check if the passcode is correct
    if passcode == "1234":  # Replace "1234" with your desired passcode
        st.success("Access granted!")

        # Allow the user to select an entry
        selected_id = st.selectbox(
            "Select an entry to edit/delete:",
            options=df["Unique ID"].values,
            format_func=lambda x: f"{df.loc[x, 'Assigned to']} ({df.loc[x, 'Checkout Date']} - {df.loc[x, 'Return Date']})",
        )

        # Show details of the selected entry
        st.write("Selected Entry Details:")
        st.write(df.loc[selected_id])

        # Edit the selected entry
        st.subheader("Edit Entry")
        edited_row = {}
        for column in df.columns[:-1]:  # Exclude Unique ID
            if pd.api.types.is_datetime64_any_dtype(df[column]):
                edited_row[column] = st.date_input(f"{column}:", value=df.loc[selected_id, column])
            elif pd.api.types.is_numeric_dtype(df[column]):
                edited_row[column] = st.number_input(f"{column}:", value=df.loc[selected_id, column])
            else:
                edited_row[column] = st.text_input(f"{column}:", value=df.loc[selected_id, column])

        if st.button("Update Entry"):
            for key, value in edited_row.items():
                df.at[selected_id, key] = value
            st.success("Entry updated successfully!")

        # Delete the selected row
        if st.button("Delete Entry"):
            df = df.drop(index=selected_id).reset_index(drop=True)
            st.success("Entry deleted successfully!")

        # Save changes to Excel
        if st.button("Save Changes"):
            df.to_excel(file_path, index=False, engine="openpyxl")
            st.success("Changes saved to the Excel file!")