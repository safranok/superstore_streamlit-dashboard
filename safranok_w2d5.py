import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(
    page_title="Superstore Dashboard",
    page_icon="📊",
    layout="wide"
)

df = pd.read_csv(r"cleaned_superstore.csv")
df['order_date'] = pd.to_datetime(df['order_date'])

with st.sidebar:
    st.header("Filters")

    regions =st.multiselect(
        "Region",
        options=df['region'].unique(),
        default=df['region'].unique()
    )
    order_year=df["order_date"].dt.year
    years=st.multiselect(
        "Year",
        options=sorted(order_year.unique()),
        default=sorted(order_year.unique())
    )
    shipping_mode=st.multiselect(
        "Shipping Mode",
        options=df['ship_mode'].unique(),
        default=df['ship_mode'].unique()
    )
    segment=st.multiselect(
        "Segment",
        options=df['segment'].unique(),
        default=df['segment'].unique()
    )

filtered=df[
    (df["region"].isin(regions))
    & (order_year.isin(years))
    & (df["ship_mode"].isin(shipping_mode))
    & (df["segment"].isin(segment))
]

st.title("📊 Superstore Sales Dashboard")
col1,col2,col3,col4=st.columns(4)

with col1:
    st.metric(
        "Total Sales",
        f"${filtered['sales_price'].sum():,.0f}"
    )
with col2:
    st.metric(
        "Total Profit",
        f"${filtered['profit'].sum():,.0f}"
    )
with col3:
    st.metric(
        "Average Discount",
        f"{filtered['discount(%)'].mean() *100}"
    )
with col4:
    st.metric(
        "Total Orders",
        f"{filtered['order_id'].nunique():,}"
    )



tab1,tab2,tab3,tab4 =st.tabs(
    ["Overview","BY Category","By Region","Quality Alert"]
)

with tab1:
    st.subheader("Filtered Data Sample")

    st.dataframe(
        filtered.head(20),
        use_container_width=True
    )
    
    st.subheader("Monthly Sales by Year")
    filtered['order_year']=filtered['order_date'].dt.year
    filtered['month']=filtered.order_date.dt.to_period('M').astype(str)
    monthly_yr=filtered.groupby(['month','order_year'])['sales_price'].sum().reset_index()
    monthly_yr_fig=px.line(monthly_yr,x='month',y='sales_price',color='order_year')
    st.plotly_chart(monthly_yr_fig)

with tab2:
    col1,col2=st.columns(2)
    with col1:
        st.subheader("Top_10_Sub_Category")
        top_10_subcategory_by_sales_price=filtered.groupby('sub_category')['sales_price'].sum().nlargest(10).reset_index()
        cat_plot=top_10_subcategory_by_sales_price.plot(x='sub_category', y='sales_price', kind='barh')
        st.pyplot(cat_plot.figure)
    with col2:
        st.subheader('Sales vs Profit')
        scatter_fig=px.scatter(filtered,x='sales_price',y='profit',color='category')
        st.plotly_chart(scatter_fig)

with tab3:
    st.subheader("Profit share by Region")
    region_by_profit = filtered.groupby('region')['profit'].sum().reset_index()

    donut_region = px.pie(
    region_by_profit,
    names='region',
    values='profit',
    hole=0.5,
    title='Profit by Region'
)
    st.plotly_chart(donut_region, use_container_width=True)

disc_arr = filtered['discount(%)'].values
sales_arr = filtered['sales_price'].values
margin_arr = filtered['profit'].values

high_disc_pct = np.percentile(disc_arr,75)
high_disc_n = int(np.sum(disc_arr > high_disc_pct))

z_score =(
    sales_arr - np.mean(sales_arr)
    / np.std(sales_arr)
)

outlier_n= int(np.sum(np.abs(z_score) > 2))
mean_margin =float(np.mean(margin_arr))

with tab4:
    st.header("Quality Alert")
    if mean_margin <10:
        st.error(
            f"🛑Low profit margin:"
            f"{mean_margin:.if}% -investigate discounts"
        )
    elif mean_margin < 20:
        st.warning(
            f"🟡Moderate profit margin: "
            f"{mean_margin:.if}%- monitor discount"
        )  
    else:
        st.success(
            f"Healthy profit margin: "
            f"{mean_margin:.1f}%"
        )
   
    st.info(
        f"ℹ️{high_disc_n} order above the"
        f"75th-precentile discount"
    )

    if outlier_n >0:
        st.warning(
            f" {outlier_n} sales outliers"
            f"detected (|z| >2)"
        )
    else:
        st.success(
            "✅ No sales outliers detected"
        )

with st.expander ("View Outlet Rows"):
        mask=np.abs(z_score) >2

        st.dataframe(
            filtered[mask][
            [
                "order_id",
                "order_date",
                "sales_price",
                "profit",
                "region"
            ]
        ],
        use_container_width=True
    )