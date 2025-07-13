import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.express as px
from faker import Faker
from datetime import datetime

# Page config and custom CSS
st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide", page_icon="📊")

st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Sample data generation
fake = Faker()
np.random.seed(42)
random.seed(42)

n_rows = 10000

categories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Books', 'Toys', 'Sports']
regions = ['North', 'South', 'East', 'West']
payment_methods = ['Credit Card', 'PayPal', 'Bank Transfer', 'Cash on Delivery']
customer_segments = ['Consumer', 'Corporate', 'Home Office']
shipping_types = ['Standard Class', 'Second Class', 'First Class', 'Same Day']

def skewed_sales():
    return round(np.random.exponential(scale=100), 2)

def skewed_profit():
    profit = round(np.random.normal(loc=10, scale=20), 2)
    return max(profit, 0) 

data = {
    'Order ID': [fake.uuid4() for _ in range(n_rows)],
    'Order Date': [fake.date_between(start_date='-2y', end_date='today') for _ in range(n_rows)],
    'Customer ID': [fake.uuid4() for _ in range(n_rows)],
    'Customer Name': [fake.name() for _ in range(n_rows)],
    'Region': [random.choice(regions) for _ in range(n_rows)],
    'Category': [random.choice(categories) for _ in range(n_rows)],
    'Sub-Category': [fake.word() for _ in range(n_rows)],
    'Sales': [skewed_sales() for _ in range(n_rows)],
    'Quantity': [random.randint(1, 10) for _ in range(n_rows)],
    'Discount': [round(random.choice([0, 0.1, 0.2, 0.3]), 2) for _ in range(n_rows)],
    'Profit': [skewed_profit() for _ in range(n_rows)],
    'Payment Method': [random.choice(payment_methods) for _ in range(n_rows)],
    'Customer Segment': [random.choice(customer_segments) for _ in range(n_rows)],
    'Shipping Type': [random.choice(shipping_types) for _ in range(n_rows)],
    'Product ID': [fake.uuid4() for _ in range(n_rows)],
    'Product Name': [fake.word().capitalize() + ' ' + fake.word().capitalize() for _ in range(n_rows)],
}

df = pd.DataFrame(data)
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['YearMonth'] = df['Order Date'].dt.to_period('M')

# Streamlit page setup
st.title("Sales Analytics Dashboard")

# Sidebar filters
def apply_filters(df):
    st.sidebar.header("🔧 Filter Options")
    
    region_options = ['All'] + sorted(df['Region'].unique().tolist())
    selected_region = st.sidebar.multiselect("Region:", options=region_options, default=['All'])
    
    category_options = ['All'] + sorted(df['Category'].unique().tolist())
    selected_category = st.sidebar.multiselect("Category:", options=category_options, default=['All'])
    
    payment_options = ['All'] + sorted(df['Payment Method'].unique().tolist())
    selected_payment = st.sidebar.multiselect("Payment Method:", options=payment_options, default=['All'])
    
    segment_options = ['All'] + sorted(df['Customer Segment'].unique().tolist())
    selected_segment = st.sidebar.multiselect("Customer Segment:", options=segment_options, default=['All'])
    
    # Apply filters
    filtered_df = df.copy()
    
    if 'All' not in selected_region:
        filtered_df = filtered_df[filtered_df['Region'].isin(selected_region)]
    
    if 'All' not in selected_category:
        filtered_df = filtered_df[filtered_df['Category'].isin(selected_category)]
    
    if 'All' not in selected_payment:
        filtered_df = filtered_df[filtered_df['Payment Method'].isin(selected_payment)]
    
    if 'All' not in selected_segment:
        filtered_df = filtered_df[filtered_df['Customer Segment'].isin(selected_segment)]
    
    return filtered_df

# KPI calculation
def calculate_kpis(df):
    if len(df) == 0:
        return dict.fromkeys(['total_sales', 'average_profit', 'average_quantity', 'total_orders'], 0)
    
    kpis = {
        'total_sales': df['Sales'].sum(),
        'average_profit': df['Profit'].mean(),
        'average_quantity': df['Quantity'].mean(),
        'total_orders': len(df)
    }
    return kpis

# KPI display
def display_kpis(kpis):
    st.markdown("### 📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Sales", f"${kpis['total_sales']:,.2f}")
    with col2:
        st.metric("📊 Avg Profit", f"${kpis['average_profit']:,.2f}")
    with col3:
        st.metric("📦 Avg Quantity", f"{kpis['average_quantity']:,}")
    with col4:
        st.metric("🛒 Total Orders", f"{kpis['total_orders']:,}")

# Visualization function
def create_visualizations(df):
    st.markdown("---")
    st.markdown("### 📊 Data Visualizations")
    
    # Plot 1: Monthly Sales Trend (Plotly Line Plot)
    monthly_sales = df.groupby('YearMonth')['Sales'].sum().reset_index()
    monthly_sales['YearMonth'] = monthly_sales['YearMonth'].astype(str)
    fig1 = px.line(monthly_sales, x='YearMonth', y='Sales', title='Monthly Sales Trend', markers=True)
    fig1.update_layout(
        xaxis_title='Month',
        yaxis_title='Total Sales',
        template="plotly_dark"  # Dark theme for the plot
    )
    st.plotly_chart(fig1)
    
    # Plot 2: Total Sales by Region (Plotly Bar Plot)
    sales_by_region = df.groupby('Region')['Sales'].sum().sort_values(ascending=False)
    fig2 = px.bar(sales_by_region, 
                  x=sales_by_region.index, 
                  y=sales_by_region.values, 
                  title='Total Sales by Region',
                  labels={'x': 'Region', 'y': 'Total Sales'},
                  color=sales_by_region.index)
    fig2.update_layout(
        xaxis_title='Region',
        yaxis_title='Total Sales',
        template="plotly_dark"
    )
    st.plotly_chart(fig2)

    # Plot 3: Profit Distribution by Category (Plotly Box Plot)
    fig3 = px.box(df, x='Category', y='Profit', title='Profit Distribution by Product Category', color='Category')
    st.plotly_chart(fig3)

    # Plot 4: Distribution of Order Quantities (Plotly Histogram)
    fig4 = px.histogram(df, x='Quantity', nbins=10, title='Distribution of Order Quantities', histnorm='probability density')
    fig4.update_layout(
        xaxis_title='Quantity Ordered',
        yaxis_title='Number of Orders'
    )
    st.plotly_chart(fig4)

    # Plot 5: Sales vs Profit (Plotly Scatter Plot)
    fig5 = px.scatter(df, x='Sales', y='Profit', title='Sales vs. Profit', labels={'Sales': 'Sales Amount', 'Profit': 'Profit'})
    st.plotly_chart(fig5)

    # Plot 6: Total Profit by Customer Segment (Plotly Bar Plot)
    profit_by_segment = df.groupby('Customer Segment')['Profit'].sum().sort_values(ascending=False).reset_index()
    fig6 = px.bar(profit_by_segment, x='Customer Segment', y='Profit', title='Total Profit by Customer Segment')
    fig6.update_layout(
        xaxis_title='Customer Segment',
        yaxis_title='Total Profit',
        template="plotly_dark"
    )
    st.plotly_chart(fig6)

    # Plot 7: Order Distribution by Payment Method (Plotly Pie Chart)
    payment_counts = df['Payment Method'].value_counts().reset_index()
    payment_counts.columns = ['Payment Method', 'Order Count']
    fig7 = px.pie(payment_counts, values='Order Count', names='Payment Method', title='Order Distribution by Payment Method')
    st.plotly_chart(fig7)

    # Plot 8: Order Count by Customer Segment and Shipping Type (Plotly Bar Plot)
    order_counts = df.groupby(['Customer Segment', 'Shipping Type']).size().unstack(fill_value=0)
    fig8 = px.bar(order_counts, barmode='stack', title='Order Count by Customer Segment and Shipping Type')
    fig8.update_layout(
        xaxis_title='Customer Segment',
        yaxis_title='Number of Orders',
        template="plotly_dark"
    )
    st.plotly_chart(fig8)

    # Plot 9: Average Profit by Shipping Type (Plotly Bar Plot)
    avg_profit_by_shipping = df.groupby('Shipping Type')['Profit'].mean().sort_values(ascending=False).reset_index()
    fig9 = px.bar(avg_profit_by_shipping, x='Shipping Type', y='Profit', title='Average Profit by Shipping Type', color='Shipping Type')
    fig9.update_layout(
        xaxis_title='Shipping Type',
        yaxis_title='Average Profit',
        template="plotly_dark"
    )
    st.plotly_chart(fig9)

    # Plot 10: Sales Distribution by Product Category (Plotly Box Plot)
    fig10 = px.box(df, x='Category', y='Sales', title='Sales Distribution by Product Category', color='Category')
    st.plotly_chart(fig10)

# Main function
def main():
    st.markdown("""
    <div class="main-header">
        <h1>Sales Analytics Dashboard</h1>
        <p>Analyze sales trends, customer behavior, and transaction insights.</p>
    </div>
    """, unsafe_allow_html=True)

    filtered_df = apply_filters(df)  # Applying filters to the data
    st.success(f"📋 Showing {len(filtered_df):,} orders out of {len(df):,} total orders")

    kpis = calculate_kpis(filtered_df)  # Calculating key performance indicators
    display_kpis(kpis)  # Displaying KPIs

    st.markdown("---")
    
    # Download options for filtered and full datasets
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if len(filtered_df) > 0:
            st.download_button("📥 Download Filtered Data", filtered_df.to_csv(index=False).encode('utf-8'),
                               file_name=f'sales_data_filtered_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', mime='text/csv')
    with col2:
        st.download_button("📥 Download Full Dataset", df.to_csv(index=False).encode('utf-8'),
                           file_name=f'sales_data_full_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv', mime='text/csv')

    # Displaying raw data option
    if st.sidebar.checkbox("Show Raw Data"):
        st.markdown("### 📄 Raw Data Preview")
        if len(filtered_df) > 0:
            st.dataframe(filtered_df, use_container_width=True, height=300)
        else:
            st.info("No data to display with current filters")

    # Visualizations based on filtered data
    if len(filtered_df) > 0:
        create_visualizations(filtered_df)  # Creating visualizations
    else:
        st.warning("⚠️ No data available with current filters.")

    st.markdown("---")
    st.markdown("### 📊 Dataset Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Total Records:** {len(filtered_df):,}")
    with col2:
        st.info(f"**Total Columns:** {len(filtered_df.columns)}")
    with col3:
        st.info(f"**Memory Usage:** {filtered_df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; margin-top: 2rem;">
        <p>Sales Analytics Dashboard v1.0</p>
    </div>
    """, unsafe_allow_html=True)

# Run
if __name__ == "__main__":
    main()
