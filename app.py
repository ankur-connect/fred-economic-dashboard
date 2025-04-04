import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fredapi import Fred
from logger_config import setup_logging

# Set up logging
logger = setup_logging()

# Load environment variables
load_dotenv()
fred_api_key = os.getenv("FRED_API_KEY")

def initialize_fred():
    """Initialize FRED API client."""
    try:
        logger.info("Initializing FRED API client")
        if not fred_api_key:
            logger.error("FRED API key not found in environment variables")
            st.error("FRED API key not found. Please check your .env file.")
            return None
        return Fred(api_key=fred_api_key)
    except Exception as e:
        logger.error(f"Error initializing FRED API client: {str(e)}", exc_info=True)
        st.error(f"Error initializing FRED API: {str(e)}")
        return None

def get_economic_data(fred, series_id, title, units="", quarters=8):
    """Fetch economic data from FRED API."""
    try:
        logger.info(f"Fetching {title} data with series ID: {series_id}")
        
        # Calculate start date (8 quarters back from today)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=quarters * 91)  # Approximate quarters
        
        # Get data from FRED
        data = fred.get_series(series_id, start_date, end_date)
        
        if data.empty:
            logger.warning(f"No data returned for series {series_id}")
            return None
            
        # Convert to DataFrame and format
        df = pd.DataFrame(data)
        df.reset_index(inplace=True)
        df.columns = ['Date', 'Value']
        
        # Format date to quarters
        df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
        
        logger.info(f"Successfully retrieved {len(df)} data points for {title}")
        return {
            'data': df,
            'title': title,
            'units': units
        }
    except Exception as e:
        logger.error(f"Error fetching data for {series_id}: {str(e)}", exc_info=True)
        st.error(f"Error fetching {title} data: {str(e)}")
        return None

def create_chart(data_dict, chart_type):
    """Create chart based on the selected type."""
    try:
        logger.info(f"Creating {chart_type} chart for {data_dict['title']}")
        df = data_dict['data']
        title = data_dict['title']
        units = data_dict['units']
        
        if chart_type == 'Line':
            fig = px.line(
                df, 
                x='Quarter', 
                y='Value',
                title=f"{title} - Last {len(df)} Quarters",
                labels={'Value': f"{title} ({units})", 'Quarter': ''},
                markers=True
            )
        elif chart_type == 'Bar':
            fig = px.bar(
                df, 
                x='Quarter', 
                y='Value',
                title=f"{title} - Last {len(df)} Quarters",
                labels={'Value': f"{title} ({units})", 'Quarter': ''},
                color_discrete_sequence=['#1E88E5']
            )
        elif chart_type == 'Area':
            fig = px.area(
                df, 
                x='Quarter', 
                y='Value',
                title=f"{title} - Last {len(df)} Quarters",
                labels={'Value': f"{title} ({units})", 'Quarter': ''},
                color_discrete_sequence=['#1E88E5']
            )
        else:  # Default to line
            fig = px.line(
                df, 
                x='Quarter', 
                y='Value',
                title=f"{title} - Last {len(df)} Quarters",
                labels={'Value': f"{title} ({units})", 'Quarter': ''}
            )
            
        # Update layout
        fig.update_layout(
            xaxis_title="",
            yaxis_title=f"{title} ({units})",
            template="plotly_white",
            height=500
        )
        
        return fig
    except Exception as e:
        logger.error(f"Error creating chart: {str(e)}", exc_info=True)
        st.error(f"Error creating chart: {str(e)}")
        return None

def calculate_change(data_dict):
    """Calculate percentage change from oldest to newest data point."""
    try:
        df = data_dict['data']
        if len(df) >= 2:
            oldest = df['Value'].iloc[0]
            newest = df['Value'].iloc[-1]
            pct_change = ((newest - oldest) / oldest) * 100
            return pct_change
        return None
    except Exception as e:
        logger.error(f"Error calculating change: {str(e)}")
        return None

def main():
    try:
        # Page config
        st.set_page_config(
            page_title="Economic Data Dashboard",
            page_icon="📊",
            layout="wide"
        )
        
        # Header
        st.title("📊 U.S. Economic Data Dashboard")
        st.markdown("This dashboard shows key economic indicators from the Federal Reserve Economic Data (FRED).")
        
        # Initialize FRED client
        fred = initialize_fred()
        if not fred:
            st.stop()
        
        # Sidebar options
        st.sidebar.header("Options")
        
        # Economic indicators selection
        st.sidebar.subheader("Economic Indicators")
        
        indicators = {
            "Gross Domestic Product (GDP)": {
                "series_id": "GDP",
                "units": "Billions of Dollars"
            },
            "Real GDP": {
                "series_id": "GDPC1", 
                "units": "Billions of Chained 2017 Dollars"
            },
            "GDP Growth Rate": {
                "series_id": "A191RL1Q225SBEA", 
                "units": "Percent Change from Preceding Period"
            },
            "Personal Consumption Expenditures": {
                "series_id": "PCE", 
                "units": "Billions of Dollars"
            },
            "Unemployment Rate": {
                "series_id": "UNRATE", 
                "units": "Percent"
            },
            "Consumer Price Index (CPI)": {
                "series_id": "CPIAUCSL", 
                "units": "Index 1982-1984=100"
            },
            "Federal Funds Rate": {
                "series_id": "FEDFUNDS", 
                "units": "Percent"
            }
        }
        
        selected_indicator = st.sidebar.selectbox(
            "Select Economic Indicator", 
            list(indicators.keys()),
            index=0
        )
        
        # Chart type selection
        chart_type = st.sidebar.selectbox(
            "Select Chart Type",
            ["Line", "Bar", "Area"],
            index=0
        )
        
        # Number of quarters
        quarters = st.sidebar.slider(
            "Number of quarters to display",
            min_value=4,
            max_value=20,
            value=8
        )
        
        # Get selected indicator details
        indicator_details = indicators[selected_indicator]
        series_id = indicator_details["series_id"]
        units = indicator_details["units"]
        
        # Get data
        data_dict = get_economic_data(fred, series_id, selected_indicator, units, quarters)
        #Log everytime the data is pulled
        if data_dict:
            logger.info(f"Successfully pulled {len(data_dict['data'])} data points for {selected_indicator}")
        else:
            logger.warning(f"No data returned for {selected_indicator}")
        
        if data_dict and not data_dict['data'].empty:
            # Main content area
            col1, col2 = st.columns([7, 3])
            
            with col1:
                # Display chart
                fig = create_chart(data_dict, chart_type)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Data table with toggle
                    with st.expander("Show Raw Data"):
                        st.dataframe(
                            data_dict['data'][['Quarter', 'Value']].sort_values('Quarter', ascending=False),
                            use_container_width=True
                        )
            
            with col2:
                # Key statistics
                st.subheader("Key Statistics")
                
                df = data_dict['data']
                latest_value = df['Value'].iloc[-1]
                latest_quarter = df['Quarter'].iloc[-1]
                
                # Calculate change
                pct_change = calculate_change(data_dict)
                
                # Metrics
                st.metric(
                    label=f"Latest Value ({latest_quarter})",
                    value=f"{latest_value:,.2f} {units}",
                    delta=f"{pct_change:.2f}%" if pct_change is not None else None
                )
                
                # Min, max, average
                col_min, col_max = st.columns(2)
                with col_min:
                    min_val = df['Value'].min()
                    min_quarter = df.loc[df['Value'].idxmin(), 'Quarter']
                    st.metric("Minimum", f"{min_val:,.2f}")
                    st.caption(f"Quarter: {min_quarter}")
                
                with col_max:
                    max_val = df['Value'].max()
                    max_quarter = df.loc[df['Value'].idxmax(), 'Quarter']
                    st.metric("Maximum", f"{max_val:,.2f}")
                    st.caption(f"Quarter: {max_quarter}")
                
                st.metric("Average", f"{df['Value'].mean():,.2f}")
                
                # Description of indicator
                st.subheader("About this Indicator")
                descriptions = {
                    "Gross Domestic Product (GDP)": "GDP is the total monetary or market value of all finished goods and services produced within a country's borders in a specific time period.",
                    "Real GDP": "Real GDP is a macroeconomic measure of the value of economic output adjusted for price changes (inflation or deflation).",
                    "GDP Growth Rate": "This measures the annualized percentage change in GDP from the previous quarter.",
                    "Personal Consumption Expenditures": "PCE measures consumer spending on goods and services in the U.S. economy.",
                    "Unemployment Rate": "The unemployment rate represents the number of unemployed as a percentage of the labor force.",
                    "Consumer Price Index (CPI)": "CPI measures the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services.",
                    "Federal Funds Rate": "The federal funds rate is the interest rate at which depository institutions trade federal funds with each other overnight."
                }
                st.markdown(descriptions.get(selected_indicator, "No description available."))
                
        else:
            st.error(f"No data available for {selected_indicator}. Please try another indicator.")
        
        # Footer
        st.sidebar.markdown("---")
        st.sidebar.caption("Data source: Federal Reserve Economic Data (FRED)")
        st.sidebar.caption("St. Louis Federal Reserve Bank")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
