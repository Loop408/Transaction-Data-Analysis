import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configure page
st.set_page_config(page_title="Transaction Data Analysis", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    /* Selectbox styling - ensure selected option is visible */
    .stSelectbox label {
        color: #262730 !important;
        font-weight: 500 !important;
    }
    /* BaseWeb select component - make selected value visible */
    div[data-baseweb="select"] {
        background-color: white !important;
    }
    /* Selected option display area */
    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 1) !important;
        border: 1px solid #d0d0d0 !important;
        color: #262730 !important;
    }
    /* Selected value text */
    div[data-baseweb="select"] > div > div {
        color: #262730 !important;
        font-weight: 500 !important;
        background-color: transparent !important;
    }
    /* Selected value when dropdown is open */
    div[data-baseweb="select"] > div[aria-expanded="true"] {
        background-color: white !important;
        border: 2px solid #1f77b4 !important;
    }
    /* Dropdown menu items */
    ul[role="listbox"] {
        background-color: white !important;
    }
    ul[role="listbox"] li {
        background-color: white !important;
        color: #262730 !important;
    }
    ul[role="listbox"] li:hover {
        background-color: #f0f2f6 !important;
    }
    /* Highlight selected option in dropdown */
    ul[role="listbox"] li[aria-selected="true"] {
        background-color: #e0f2fe !important;
        color: #1f77b4 !important;
        font-weight: 600 !important;
    }
    /* Ensure the selectbox container is visible */
    .stSelectbox {
        background-color: transparent !important;
    }
    .stSelectbox > div {
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header"> Transaction Data Analysis Dashboard</p>', unsafe_allow_html=True)
st.markdown("---")

@st.cache_data(show_spinner=False)
def read_csv_file(file) -> pd.DataFrame:
	try:
		df = pd.read_csv(file)
		return df
	except Exception as exc:
		st.error(f"Failed to read CSV: {exc}")
		return pd.DataFrame()

def ensure_datetime_and_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
	if "t_date" in df.columns:
		df["t_date"] = pd.to_datetime(df["t_date"], errors="coerce")
		if "month" not in df.columns:
			df["month"] = df["t_date"].dt.month_name()
		if "quarter" not in df.columns:
			df["quarter"] = df["t_date"].dt.to_period("Q").astype(str)
	return df

def has_columns(df: pd.DataFrame, cols: list[str]) -> bool:
	missing = [c for c in cols if c not in df.columns]
	if missing:
		st.error(f"Missing required columns: {', '.join(missing)}")
		return False
	return True

def create_figure():
	"""Helper function to create matplotlib figure"""
	fig, ax = plt.subplots(figsize=(6, 4))
	return fig, ax

# File upload at the top
st.markdown("### Upload Your Transaction Data")
uploaded_file = st.file_uploader("Upload transactions CSV", type=["csv"], help="Upload your transactions.csv file here", label_visibility="collapsed")

if uploaded_file is None:
	st.info(" Please upload a CSV file to continue.")

else:
	st.success(f"File loaded: **{uploaded_file.name}**")
	df = read_csv_file(uploaded_file)
	if df.empty:
		st.stop()
	
	df = ensure_datetime_and_derived_columns(df)
	
	# Main content area - Detailed Analysis Reports first
	# Detailed Analysis Reports section
	st.header("Detailed Analysis Reports")
	
	reports = [
		"Select Report",
		"Total Sales",
		"Month With Highest Sales",
		"Average Transaction Amount Per Customer",
		"Highest Single Transaction",
		"Revenue By Service",
		"Revenue By Product",
		"Average Amount Per Service",
		"Unique Customers",
		"Top Customers By Spend",
		"Average Transactions Per Customer",
		"Customers Purchasing Multiple Services",
		"Percentage Of Repeat Buyers",
		"Popular Services By Count",
		"Most Purchased Product Per Service",
		"Average Amount Per Product",
		"State With Highest Total Sales",
		"City With Highest Number Of Transactions",
		"Average Spending Per State",
		"Services Popularity By State (Counts)",
		"Outdoor Recreation Revenue By State",
		"Compare Average Spending: California vs Texas",
		"Quarter With Highest Sales",
		"Total Sales By Month",
		"Team Sports Sales By Month",
		"Credit vs Debit: Counts, Revenue, Averages",
		"Cities By Average Transaction",
		"Exercise & Fitness: Top Products",
		"High Total, Low Avg Products",
		"Underperforming Services",
	]
	selected = st.selectbox("Choose a report to generate:", reports, key="report_selector")
	
	if selected == "Select Report":
		st.info("Please select a report from the dropdown above to view detailed analysis.")
	elif selected == "Total Sales":
		if has_columns(df, ["t_amt"]):
			total_sales = pd.to_numeric(df["t_amt"], errors="coerce").sum()
			st.metric("Total Sales Amount", f"${total_sales:,.2f}")
	elif selected == "Month With Highest Sales":
		if has_columns(df, ["t_amt", "month"]):
			month_total = df.groupby("month")["t_amt"].sum().sort_values(ascending=False)
			st.write(month_total)
			st.success(f"Top Month: {month_total.idxmax()}")
	elif selected == "Average Transaction Amount Per Customer":
		if has_columns(df, ["cust_id", "t_amt"]):
			avg_txn = df.groupby("cust_id")["t_amt"].mean().sort_values(ascending=False)
			st.dataframe(avg_txn.rename("avg_t_amt"))
	elif selected == "Highest Single Transaction":
		if has_columns(df, ["t_amt"]):
			max_amount = pd.to_numeric(df["t_amt"], errors="coerce").max()
			st.metric("Highest Transaction", f"${max_amount:,.2f}")
	elif selected == "Revenue By Service":
		if has_columns(df, ["services", "t_amt"]):
			service_total = df.groupby("services")["t_amt"].sum().sort_values(ascending=False)
			col1, col2 = st.columns([1, 1])
			with col1:
				st.dataframe(service_total.to_frame("Total Revenue"))
				st.success(f"Top Service: {service_total.idxmax()}")
			with col2:
				fig, ax = create_figure()
				service_total.plot(kind='bar', ax=ax)
				ax.set_title('Total Revenue by Service Category', fontsize=12, fontweight='bold')
				ax.set_xlabel('Service', fontsize=10)
				ax.set_ylabel('Total Revenue', fontsize=10)
				plt.xticks(rotation=45, ha='right', fontsize=9)
				plt.tight_layout()
				st.pyplot(fig)
	elif selected == "Revenue By Product":
		if has_columns(df, ["products_used", "t_amt"]):
			product_total = df.groupby("products_used")["t_amt"].sum().sort_values(ascending=False)
			col1, col2 = st.columns([1, 1])
			with col1:
				st.dataframe(product_total.head(10).to_frame("Total Revenue"))
				st.success(f"Top Product: {product_total.idxmax()}")
			with col2:
				fig, ax = create_figure()
				product_total.head(10).plot(kind='bar', ax=ax)
				ax.set_title('Top 10 Products by Revenue', fontsize=12, fontweight='bold')
				ax.set_xlabel('Products', fontsize=10)
				ax.set_ylabel('Revenue', fontsize=10)
				plt.xticks(rotation=45, ha='right', fontsize=8)
				plt.tight_layout()
				st.pyplot(fig)
	elif selected == "Average Amount Per Service":
		if has_columns(df, ["services", "t_amt"]):
			avg_service = df.groupby("services")["t_amt"].mean().sort_values(ascending=False)
			col1, col2 = st.columns([1, 1])
			with col1:
				st.dataframe(avg_service.to_frame("Avg Amount"))
			with col2:
				fig, ax = create_figure()
				avg_service.plot(kind='bar', ax=ax)
				ax.set_title('Average Transaction Amount per Service', fontsize=12, fontweight='bold')
				ax.set_xlabel('Service', fontsize=10)
				ax.set_ylabel('Average Amount', fontsize=10)
				plt.xticks(rotation=45, ha='right', fontsize=9)
				plt.tight_layout()
				st.pyplot(fig)
	elif selected == "Unique Customers":
		if has_columns(df, ["cust_id"]):
			unique_cust = int(df["cust_id"].nunique())
			st.metric("Unique Customers", f"{unique_cust:,}")
	elif selected == "Top Customers By Spend":
		if has_columns(df, ["cust_id", "t_amt"]):
			cust_total = df.groupby("cust_id")["t_amt"].sum().sort_values(ascending=False).head(10)
			st.write(cust_total.head())
	elif selected == "Average Transactions Per Customer":
		if has_columns(df, ["cust_id"]):
			txn_count = df.groupby("cust_id").size()
			st.metric("Average Transactions per Customer", f"{txn_count.mean():.3f}")
	elif selected == "Customers Purchasing Multiple Services":
		if has_columns(df, ["cust_id", "services"]):
			multi = df.groupby("cust_id")["services"].nunique()
			multi_cust = multi[multi > 1]
			st.write(multi_cust)
	elif selected == "Percentage Of Repeat Buyers":
		if has_columns(df, ["cust_id"]):
			cust_count = df["cust_id"].value_counts()
			repeat = cust_count[cust_count > 1].count()
			total = cust_count.count()
			repeat_pct = (repeat / total) * 100 if total > 0 else 0
			st.metric("Repeat Buyers (%)", f"{repeat_pct:.2f}%")
	elif selected == "Popular Services By Count":
		if has_columns(df, ["services"]):
			popular = df["services"].value_counts()
			col1, col2 = st.columns([1, 1])
			with col1:
				st.dataframe(popular.to_frame("Count"))
				st.success(f"Most Popular: {popular.idxmax()}")
			with col2:
				fig, ax = create_figure()
				popular.plot(kind='bar', ax=ax)
				ax.set_title('Most Popular Services by Transaction Count', fontsize=12, fontweight='bold')
				ax.set_xlabel('Service', fontsize=10)
				ax.set_ylabel('Number of Transactions', fontsize=10)
				plt.xticks(rotation=45, ha='right', fontsize=9)
				plt.tight_layout()
				st.pyplot(fig)
	elif selected == "Most Purchased Product Per Service":
		if has_columns(df, ["services", "products_used"]):
			prod_count = df.groupby(["services", "products_used"]).size()
			most_per_service = prod_count.groupby(level=0).idxmax()
			st.write(most_per_service)
	elif selected == "Average Amount Per Product":
		if has_columns(df, ["products_used", "t_amt"]):
			avg_per_product = df.groupby("products_used")["t_amt"].mean().sort_values(ascending=False)
			st.write(avg_per_product)
	elif selected == "State With Highest Total Sales":
		if has_columns(df, ["state", "t_amt"]):
			state_total = df.groupby("state")["t_amt"].sum().sort_values(ascending=False)
			col1, col2 = st.columns([1, 1])
			with col1:
				st.dataframe(state_total.head(10).to_frame("Total Sales"))
				st.success(f"Top State: {state_total.idxmax()}")
			with col2:
				fig, ax = create_figure()
				state_total.head(10).plot(kind='bar', ax=ax)
				ax.set_title('Top 10 States by Total Sales', fontsize=12, fontweight='bold')
				ax.set_xlabel('State', fontsize=10)
				ax.set_ylabel('Total Sales', fontsize=10)
				plt.xticks(rotation=45, ha='right', fontsize=9)
				plt.tight_layout()
				st.pyplot(fig)
	elif selected == "City With Highest Number Of Transactions":
		if has_columns(df, ["city"]):
			city_count = df["city"].value_counts().sort_values(ascending=False)
			col1, col2 = st.columns([1, 1])
			with col1:
				st.dataframe(city_count.head(10).to_frame("Count"))
				st.success(f"Top City: {city_count.idxmax()}")
			with col2:
				fig, ax = create_figure()
				city_count.head(10).plot(kind='bar', ax=ax)
				ax.set_title('Top 10 Cities by Number of Transactions', fontsize=12, fontweight='bold')
				ax.set_xlabel('City', fontsize=10)
				ax.set_ylabel('Transaction Count', fontsize=10)
				plt.xticks(rotation=45, ha='right', fontsize=9)
				plt.tight_layout()
				st.pyplot(fig)
	elif selected == "Average Spending Per State":
		if has_columns(df, ["state", "t_amt"]):
			avg_state = df.groupby("state")["t_amt"].mean().sort_values(ascending=False)
			st.write(avg_state)
	elif selected == "Services Popularity By State (Counts)":
		if has_columns(df, ["state", "services"]):
			pivot = df.groupby(["state", "services"]).size().unstack(fill_value=0)
			st.dataframe(pivot, use_container_width=True)
	elif selected == "Outdoor Recreation Revenue By State":
		if has_columns(df, ["services", "state", "t_amt"]):
			outdoor = df[df["services"] == "Outdoor Recreation"]
			outdoor_by_state = outdoor.groupby("state")["t_amt"].sum().sort_values(ascending=False)
			st.write(outdoor_by_state)
	elif selected == "Compare Average Spending: California vs Texas":
		if has_columns(df, ["state", "t_amt"]):
			ca_avg = df[df["state"] == "California"]["t_amt"].mean()
			tx_avg = df[df["state"] == "Texas"]["t_amt"].mean()
			col1, col2 = st.columns(2)
			col1.metric("California Avg", f"${ca_avg:,.3f}")
			col2.metric("Texas Avg", f"${tx_avg:,.3f}")
	elif selected == "Quarter With Highest Sales":
		if has_columns(df, ["quarter", "t_amt"]):
			quarter_total = df.groupby("quarter")["t_amt"].sum().sort_values(ascending=False)
			col1, col2 = st.columns([1, 1])
			with col1:
				st.dataframe(quarter_total.to_frame("Total Sales"))
				st.success(f"Top Quarter: {quarter_total.idxmax()}")
			with col2:
				fig, ax = create_figure()
				quarter_total.plot(kind='bar', ax=ax)
				ax.set_title('Total Sales by Quarter', fontsize=12, fontweight='bold')
				ax.set_xlabel('Quarter', fontsize=10)
				ax.set_ylabel('Total Sales', fontsize=10)
				plt.xticks(rotation=45, ha='right', fontsize=9)
				plt.tight_layout()
				st.pyplot(fig)
	elif selected == "Total Sales By Month":
		if has_columns(df, ["month", "t_amt"]):
			month_total = df.groupby("month")["t_amt"].sum()
			col1, col2 = st.columns([1, 1])
			with col1:
				st.dataframe(month_total.to_frame("Total Sales"))
			with col2:
				fig, ax = create_figure()
				month_total.plot(kind='bar', ax=ax)
				ax.set_title('Total Sales by Month', fontsize=12, fontweight='bold')
				ax.set_xlabel('Month', fontsize=10)
				ax.set_ylabel('Total Sales', fontsize=10)
				plt.xticks(rotation=45, ha='right', fontsize=9)
				plt.tight_layout()
				st.pyplot(fig)
	elif selected == "Team Sports Sales By Month":
		if has_columns(df, ["services", "month", "t_amt"]):
			sports = df[df["services"] == "Team Sports"]
			monthly = sports.groupby("month")["t_amt"].sum()
			col1, col2 = st.columns([1, 1])
			with col1:
				st.dataframe(monthly.to_frame("Sales"))
			with col2:
				fig, ax = create_figure()
				monthly.plot(kind='line', ax=ax)
				ax.set_title('Sports Equipment Sales by Month', fontsize=12, fontweight='bold')
				ax.set_xlabel('Month', fontsize=10)
				ax.set_ylabel('Total Sales', fontsize=10)
				plt.xticks(rotation=45, ha='right', fontsize=9)
				plt.tight_layout()
				st.pyplot(fig)
	elif selected == "Credit vs Debit: Counts, Revenue, Averages":
		if has_columns(df, ["t_details", "t_amt"]):
			details = df.copy()
			details["t_details_lower"] = details["t_details"].astype(str).str.lower()
			credit = details[details["t_details_lower"] == "credit"]
			cash = details[details["t_details_lower"] == "cash"]
			c1, c2, c3 = st.columns(3)
			c1.metric("Credit Count", int(credit.shape[0]))
			c2.metric("Credit Revenue", f"{credit['t_amt'].sum():,.2f}")
			c3.metric("Avg Credit Amount", f"{credit['t_amt'].mean():,.2f}")
			c1, c2 = st.columns(2)
			c1.metric("Cash Count", int(cash.shape[0]))
			c2.metric("Avg Cash Amount", f"{cash['t_amt'].mean():,.2f}")
			avg_by_pay = df.groupby(df["t_details"].astype(str).str.lower())["t_amt"].mean()
			st.write(avg_by_pay)
	elif selected == "Cities By Average Transaction":
		if has_columns(df, ["city", "t_amt"]):
			city_avg = df.groupby("city")["t_amt"].mean().sort_values(ascending=False)
			st.write(city_avg.head(10))
	elif selected == "Exercise & Fitness: Top Products":
		if has_columns(df, ["services", "products_used", "t_amt"]):
			fitness = df[df["services"] == "Exercise & Fitness"]
			product_sales = fitness.groupby("products_used")["t_amt"].sum().sort_values(ascending=False)
			col1, col2 = st.columns([1, 1])
			with col1:
				st.dataframe(product_sales.head(10).to_frame("Revenue"))
			with col2:
				fig, ax = create_figure()
				product_sales.head(10).plot(kind='bar', ax=ax)
				ax.set_title('Exercise & Fitness Product Popularity', fontsize=12, fontweight='bold')
				ax.set_xlabel('Products', fontsize=10)
				ax.set_ylabel('Total Sales', fontsize=10)
				plt.xticks(rotation=45, ha='right', fontsize=8)
				plt.tight_layout()
				st.pyplot(fig)
	elif selected == "High Total, Low Avg Products":
		if has_columns(df, ["products_used", "t_amt"]):
			prod_total = df.groupby("products_used")["t_amt"].sum()
			prod_avg = df.groupby("products_used")["t_amt"].mean()
			prod_df = pd.DataFrame({"total": prod_total, "avg": prod_avg})
			threshold = prod_df["total"].quantile(0.75)
			candidates = prod_df[(prod_df["total"] >= threshold) & (prod_df["avg"] <= prod_df["avg"].median())].sort_values("total", ascending=False)
			st.write(candidates)
	elif selected == "Underperforming Services":
		if has_columns(df, ["services", "t_amt"]):
			svc_total = df.groupby("services")["t_amt"].sum()
			svc_avg = df.groupby("services")["t_amt"].mean()
			svc_df = pd.DataFrame({"total": svc_total, "avg": svc_avg})
			low_threshold = svc_df["total"].quantile(0.25)
			underperform = svc_df[(svc_df["total"] <= low_threshold) & (svc_df["avg"] <= svc_df["avg"].median())].sort_values("total")
			st.write(underperform)
	
	st.markdown("---")
	
	# Data Explorer section - moved down
	st.header("Data Explorer")
	st.subheader("Raw Data Preview")
	
	col1, col2 = st.columns([1, 1])
	with col1:
		rows_to_show = st.slider("Number of rows to display", min_value=10, max_value=500, value=100, step=10)
	with col2:
		if "cust_id" in df.columns:
			filter_cust = st.selectbox("Filter by Customer ID (optional)", ["All"] + sorted(df["cust_id"].unique().tolist())[:100])
	
	# Display filtered data
	display_df = df.head(rows_to_show)
	if "cust_id" in df.columns and filter_cust != "All":
		display_df = df[df["cust_id"] == filter_cust].head(rows_to_show)
	
	st.dataframe(display_df, use_container_width=True)

	# Footer
	st.markdown("---")
	st.caption("Built with Streamlit • Upload your own transactions.csv to explore insights")


