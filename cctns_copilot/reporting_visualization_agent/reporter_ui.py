import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import base64
import time # For unique filenames

# --- Helper Functions ---

def dataframe_to_pdf(df: pd.DataFrame, title="Report"):
    """Converts a Pandas DataFrame to a PDF string."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=title, ln=1, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 10)
    # Table Header
    for col in df.columns:
        pdf.cell(max(35, pdf.get_string_width(col) + 6) , 10, col, border=1) # Adjust width
    pdf.ln()

    # Table Rows
    pdf.set_font("Arial", "", 8)
    for index, row in df.iterrows():
        for col in df.columns:
            pdf.cell(max(35, pdf.get_string_width(str(row[col])) + 6), 10, str(row[col]), border=1) # Adjust width
        pdf.ln()

    return pdf.output(dest='S').encode('latin-1') # 'S' returns as string, encode for bytes

def fig_to_base64(fig):
    """Converts a Matplotlib or Plotly figure to a base64 encoded image for PDF embedding."""
    img_bytes = BytesIO()
    if hasattr(fig, 'savefig'): # Matplotlib
        fig.savefig(img_bytes, format='png', bbox_inches='tight')
    elif hasattr(fig, 'to_image'): # Plotly
        img_bytes.write(fig.to_image(format="png"))
    img_bytes.seek(0)
    return base64.b64encode(img_bytes.read()).decode()

# --- Streamlit App ---

st.set_page_config(layout="wide", page_title="CCTNS Copilot - Reporting")

st.title("CCTNS Query Results & Reporting")

# Initialize session state variables if they don't exist
if 'query_results_df' not in st.session_state:
    st.session_state.query_results_df = None # To store the DataFrame from DB agent
if 'dataset_name' not in st.session_state:
    st.session_state.dataset_name = ""
if 'dataset_tags' not in st.session_state:
    st.session_state.dataset_tags = []
if 'generated_sql' not in st.session_state:
    st.session_state.generated_sql = ""
if 'charts' not in st.session_state:
    st.session_state.charts = [] # List to store chart configurations/figures

# --- Placeholder for receiving data from other agents ---
# In a real multi-agent setup, this data would be passed programmatically.
# For now, we can use a simple uploader or text input for testing.

st.sidebar.header("Data Input (Placeholder)")
uploaded_file = st.sidebar.file_uploader("Upload CSV with Query Results", type="csv")
if uploaded_file:
    try:
        st.session_state.query_results_df = pd.read_csv(uploaded_file)
        st.session_state.generated_sql = "SQL from uploaded CSV (if available in metadata)"
        st.session_state.dataset_name = uploaded_file.name.split('.')[0]
        st.session_state.charts = [] # Reset charts on new data
    except Exception as e:
        st.sidebar.error(f"Error reading CSV: {e}")
        st.session_state.query_results_df = None

# --- Display Query Results and Metadata ---
if st.session_state.query_results_df is not None:
    st.header("Query Results")

    # Display SQL Query (if available)
    if st.session_state.generated_sql:
        st.subheader("Generated SQL Query")
        st.code(st.session_state.generated_sql, language="sql")

    # Dataset Labeling & Metadata
    st.subheader("Dataset Metadata")
    st.session_state.dataset_name = st.text_input("Dataset Name", value=st.session_state.dataset_name)
    # Using st.multiselect for tags, can also use text_input and split by comma
    st.session_state.dataset_tags = st.multiselect("Tags",
                                                   options=["crime", "fir", "arrest", "officer", "district", "guntur"],
                                                   default=st.session_state.dataset_tags)

    st.subheader("Data Table")
    # Simple pagination idea (can be enhanced with AgGrid or other components)
    page_size = st.slider("Rows per page", 5, 100, 10)
    total_pages = (len(st.session_state.query_results_df) - 1) // page_size + 1
    current_page = st.number_input("Page", min_value=1, max_value=total_pages, value=1, step=1)
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    st.dataframe(st.session_state.query_results_df.iloc[start_idx:end_idx])
    st.caption(f"Showing rows {start_idx+1}-{min(end_idx, len(st.session_state.query_results_df))} of {len(st.session_state.query_results_df)}")


    # --- Charting Section ---
    st.header("Graph Agent: Create Visualizations")
    if not st.session_state.query_results_df.empty:
        chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Pie Chart", "Scatter Plot"])

        columns = st.session_state.query_results_df.columns.tolist()

        if chart_type in ["Bar Chart", "Line Chart", "Scatter Plot"]:
            x_axis = st.selectbox("Select X-axis", options=columns, index=0 if columns else None)
            y_axis = st.selectbox("Select Y-axis", options=columns, index=1 if len(columns)>1 else 0 if columns else None)
            color_by = st.selectbox("Color by (Optional)", options=[None] + columns)

            if x_axis and y_axis:
                try:
                    if chart_type == "Bar Chart":
                        fig = px.bar(st.session_state.query_results_df, x=x_axis, y=y_axis, color=color_by, title=f"Bar Chart: {y_axis} by {x_axis}")
                    elif chart_type == "Line Chart":
                        fig = px.line(st.session_state.query_results_df, x=x_axis, y=y_axis, color=color_by, title=f"Line Chart: {y_axis} over {x_axis}")
                    elif chart_type == "Scatter Plot":
                        fig = px.scatter(st.session_state.query_results_df, x=x_axis, y=y_axis, color=color_by, title=f"Scatter Plot: {y_axis} vs {x_axis}")

                    st.plotly_chart(fig, use_container_width=True)
                    if st.button("Add this chart to report", key=f"add_{chart_type.lower().replace(' ','_')}_{x_axis}_{y_axis}"):
                        st.session_state.charts.append({"type": chart_type, "fig": fig, "title": fig.layout.title.text})
                        st.success(f"{chart_type} added to report queue.")
                except Exception as e:
                    st.error(f"Error generating {chart_type}: {e}")

        elif chart_type == "Pie Chart":
            names_column = st.selectbox("Select Column for Pie Chart Labels (Names)", options=columns)
            values_column = st.selectbox("Select Column for Pie Chart Values", options=columns)
            if names_column and values_column:
                try:
                    fig = px.pie(st.session_state.query_results_df, names=names_column, values=values_column, title=f"Pie Chart: {values_column} by {names_column}")
                    st.plotly_chart(fig, use_container_width=True)
                    if st.button("Add this chart to report", key=f"add_pie_{names_column}_{values_column}"):
                        st.session_state.charts.append({"type": chart_type, "fig": fig, "title": fig.layout.title.text})
                        st.success(f"{chart_type} added to report queue.")
                except Exception as e:
                    st.error(f"Error generating Pie Chart: {e}")

        if st.session_state.charts:
            st.subheader("Charts Queued for Report:")
            for i, chart_info in enumerate(st.session_state.charts):
                st.write(f"{i+1}. {chart_info['title']}")
            if st.button("Clear Queued Charts"):
                st.session_state.charts = []
                st.experimental_rerun()


    # --- Export Options ---
    st.header("Export Options")

    # CSV Export
    csv_export_data = st.session_state.query_results_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Data as CSV",
        data=csv_export_data,
        file_name=f"{st.session_state.dataset_name or 'query_results'}_{int(time.time())}.csv",
        mime="text/csv",
    )

    # PDF Export
    if st.button("Generate and Download PDF Report"):
        with st.spinner("Generating PDF... This may take a moment."):
            try:
                pdf = FPDF()
                pdf.add_page(orientation='L') # Landscape for wider tables/charts

                # Report Title
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, f"Report: {st.session_state.dataset_name or 'Query Results'}", ln=1, align="C")
                pdf.ln(5)

                # SQL Query
                if st.session_state.generated_sql:
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, "Generated SQL Query:", ln=1)
                    pdf.set_font("Courier", "", 8) # Courier for SQL
                    # MultiCell for longer SQL queries
                    pdf.multi_cell(0, 5, st.session_state.generated_sql)
                    pdf.ln(5)

                # Data Table
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 10, "Data Table:", ln=1)
                pdf.ln(2)

                # Simplified table for PDF to avoid complex width calculations for now
                # Using fpdf.html.HTMLMixin could be an option for better tables from HTML
                pdf.set_font("Arial", "", 7) # Smaller font for table data

                # Column Headers
                # Calculate available width and distribute
                page_width = pdf.w - 2 * pdf.l_margin
                num_cols = len(st.session_state.query_results_df.columns)
                col_width = page_width / num_cols if num_cols > 0 else page_width

                for col_header in st.session_state.query_results_df.columns:
                    pdf.cell(col_width, 7, str(col_header)[:20], border=1, align='C') # Truncate long headers
                pdf.ln()

                # Data Rows (limit rows for PDF to prevent excessive size)
                max_rows_in_pdf = 50
                for i, row in st.session_state.query_results_df.head(max_rows_in_pdf).iterrows():
                    for item in row:
                        pdf.cell(col_width, 7, str(item)[:20], border=1) # Truncate long cell content
                    pdf.ln()
                if len(st.session_state.query_results_df) > max_rows_in_pdf:
                    pdf.set_font("Arial", "I", 8)
                    pdf.cell(0,10, f"... and {len(st.session_state.query_results_df) - max_rows_in_pdf} more rows (table truncated in PDF).", ln=1)
                pdf.ln(5)

                # Charts
                if st.session_state.charts:
                    pdf.set_font("Arial", "B", 12)
                    pdf.add_page(orientation='P') # New page for charts, portrait often better
                    pdf.cell(0, 10, "Visualizations:", ln=1)
                    pdf.ln(5)

                    for chart_info in st.session_state.charts:
                        try:
                            chart_title = chart_info.get("title", "Chart")
                            pdf.set_font("Arial", "B", 10)
                            pdf.cell(0, 10, chart_title, ln=1)

                            img_bytes = BytesIO()
                            chart_fig = chart_info["fig"]
                            if hasattr(chart_fig, 'savefig'): # Matplotlib
                                chart_fig.savefig(img_bytes, format='png', bbox_inches='tight', dpi=150)
                            elif hasattr(chart_fig, 'to_image'): # Plotly
                                img_bytes.write(chart_fig.to_image(format="png", scale=2)) # scale for better resolution
                            img_bytes.seek(0)

                            # Calculate position and size
                            # Max width: page_width - margins. Max height: similar.
                            img_w, img_h = 0, 0
                            if pdf.w - pdf.l_margin - pdf.r_margin < 180 : # Arbitrary check for landscape vs portrait needs
                                img_w = 180 # mm, adjust as needed
                            else:
                                img_w = 250

                            # Add image to PDF, ensuring it's a unique name for fpdf
                            img_name = f"chart_{int(time.time()*1000)}.png"
                            pdf.image(img_bytes, w=img_w, type='PNG', link='', title=chart_title)
                            pdf.ln(5) # Space after chart
                        except Exception as e_chart:
                            st.error(f"Could not add chart '{chart_title}' to PDF: {e_chart}")
                            pdf.set_font("Arial", "I", 8)
                            pdf.cell(0,10, f"[Error embedding chart: {chart_title} - {e_chart}]", ln=1)


                pdf_data = pdf.output(dest='S').encode('latin-1')
                st.download_button(
                    label="Download PDF Report (Click again if first was generation)",
                    data=pdf_data,
                    file_name=f"{st.session_state.dataset_name or 'report'}_{int(time.time())}.pdf",
                    mime="application/pdf",
                    key="pdf_download_final" # Unique key for the actual download button
                )
                st.success("PDF report generated! Click the download button that appeared.")
            except Exception as e:
                st.error(f"Failed to generate PDF: {e}")
                import traceback
                st.error(traceback.format_exc())

else:
    st.info("Upload a CSV file or provide data through agent integration to see results and reporting options.")

st.sidebar.info(
    """
    **How to Use:**
    1.  (Placeholder) Upload query results as a CSV. In the full app, data will come from the Database Agent.
    2.  View the data table. Use pagination to navigate.
    3.  Set a name and tags for your dataset.
    4.  Create charts using the Graph Agent section. Add desired charts to the report.
    5.  Export the raw data as CSV or generate a PDF report with data and selected charts.
    """
)

# To run this Streamlit app:
# Save as reporter_ui.py
# In your terminal, navigate to the directory and run:
# streamlit run cctns_copilot/reporting_visualization_agent/reporter_ui.py
