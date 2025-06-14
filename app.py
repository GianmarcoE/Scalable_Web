import streamlit as st
import pandas as pd
import io
from utilities import operations
from st_keyup import st_keyup


# Page title
st.set_page_config(page_title="Scalable Calculator", layout="centered")

# Header
st.title("Examine your Scalable report")

# --- Upload file ---
uploaded_file = st.file_uploader("Upload your Scalable report", type=["csv"])

if uploaded_file is not None:
    # Convert the binary file to a text stream
    text_io = io.StringIO(uploaded_file.read().decode("utf-8"))

    if uploaded_file.name.endswith(".csv"):
        ranges, capital, stock_list, interests = operations.input_file_prep(text_io)
        st.subheader(f"Capital invested: {'{0:.2f}'.format(capital)}€")
        st.subheader(f"Interest: {interests}€ ({round(interests * 100 / capital, 2)}%)")
        df = pd.DataFrame([vars(stock) for stock in stock_list])

        # Slider di esempio
        selected_date = st.slider("Select date range", ranges[0], ranges[1], (ranges[0], ranges[1]),
                                  format="DD/MM/YYYY")

        # filter the DataFrame based on stock name
        search_query = st_keyup("Find Stock", key="0")

        # Filter the DataFrame based on date
        filtered_df = df[(pd.to_datetime(df['closing_date']) >= selected_date[0]) & (pd.to_datetime(df['closing_date'])
                                                                                     <= selected_date[1])]

        if search_query:
            filtered_df = filtered_df[filtered_df["name"].str.contains(search_query, case=False, na=False)]

        # Show filtered data
        with st.expander("Show tab", expanded=True):
            st.dataframe(filtered_df[['name', 'time_open', 'price_diff', 'percentage']], hide_index=True, column_config=
                {
                    "name": st.column_config.TextColumn("Stock"),
                    "time_open": st.column_config.NumberColumn("Days Open"),
                    "price_diff": st.column_config.NumberColumn("Earnings", format="%.2f €"),
                    "percentage": st.column_config.NumberColumn("+/-", format="%.2f%%")
                }
                         )

        # Calcola guadagni netti cumulati
        filtered_df["net_income"] = filtered_df["price_diff"].cumsum()

        # Group by date (if you have multiple transactions in one day)
        daily = filtered_df.groupby("closing_date")["price_diff"].sum().cumsum().reset_index()

        # Line chart
        st.line_chart(daily.rename(columns={"closing_date": "Date", "price_diff": "Earnings"}).set_index("Date"))

    else:
        st.warning("Format unsupported.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ for Coccia")
