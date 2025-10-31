import streamlit as st
import pandas as pd
import numpy as np


st.set_page_config(page_title="Transaction Data Analysis", layout="wide")
st.title("Transaction Data Analysis")


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
		# Coerce to datetime; invalid parsed as NaT
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


# File uploader
uploaded_file = st.file_uploader("Upload transactions CSV", type=["csv"]) 

if uploaded_file is None:
	st.info("👆 Please upload a CSV file to continue.")
else:
	df = read_csv_file(uploaded_file)
	if df.empty:
		st.stop()

	st.success("✅ File uploaded successfully!")
	df = ensure_datetime_and_derived_columns(df)

	st.subheader("🔍 Data Preview")
	st.dataframe(df.head(50), use_container_width=True)

	# Available reports mapped to callables
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

	selected = st.selectbox("Choose a report to generate:", reports)

	if selected == "Select Report":
		st.stop()

	if selected == "Total Sales":
		if has_columns(df, ["t_amt"]):
			total_sales = pd.to_numeric(df["t_amt"], errors="coerce").sum()
			st.metric("Total Sales Amount", f"{total_sales:,.2f}")

	elif selected == "Month With Highest Sales":
		if has_columns(df, ["t_amt", "month"]):
			month_total = df.groupby("month")["t_amt"].sum().sort_values(ascending=False)
			st.write(month_total)
			st.bar_chart(month_total)
			st.info(f"Top month: {month_total.idxmax()}")

	elif selected == "Average Transaction Amount Per Customer":
		if has_columns(df, ["cust_id", "t_amt"]):
			avg_txn = df.groupby("cust_id")["t_amt"].mean().sort_values(ascending=False)
			st.dataframe(avg_txn.rename("avg_t_amt"))

	elif selected == "Highest Single Transaction":
		if has_columns(df, ["t_amt"]):
			st.metric("Highest Transaction", f"{pd.to_numeric(df['t_amt'], errors='coerce').max():,.2f}")

	elif selected == "Revenue By Service":
		if has_columns(df, ["services", "t_amt"]):
			service_total = df.groupby("services")["t_amt"].sum().sort_values(ascending=False)
			st.write(service_total)
			st.bar_chart(service_total)
			st.info(f"Top service: {service_total.idxmax()}")

	elif selected == "Revenue By Product":
		if has_columns(df, ["products_used", "t_amt"]):
			product_total = df.groupby("products_used")["t_amt"].sum().sort_values(ascending=False)
			st.write(product_total)
			st.bar_chart(product_total.head(30))
			st.info(f"Top product: {product_total.idxmax()}")

	elif selected == "Average Amount Per Service":
		if has_columns(df, ["services", "t_amt"]):
			avg_service = df.groupby("services")["t_amt"].mean().sort_values(ascending=False)
			st.write(avg_service)
			st.bar_chart(avg_service)

	elif selected == "Unique Customers":
		if has_columns(df, ["cust_id"]):
			st.metric("Unique Customers", int(df["cust_id"].nunique()))

	elif selected == "Top Customers By Spend":
		if has_columns(df, ["cust_id", "t_amt"]):
			top_n = st.slider("Top N", min_value=5, max_value=50, value=10)
			cust_total = df.groupby("cust_id")["t_amt"].sum().sort_values(ascending=False).head(top_n)
			st.dataframe(cust_total.rename("total_spend"))

	elif selected == "Average Transactions Per Customer":
		if has_columns(df, ["cust_id"]):
			txn_count = df.groupby("cust_id").size()
			st.metric("Average Transactions per Customer", f"{txn_count.mean():.3f}")

	elif selected == "Customers Purchasing Multiple Services":
		if has_columns(df, ["cust_id", "services"]):
			multi = df.groupby("cust_id")["services"].nunique()
			st.write(multi[multi > 1])

	elif selected == "Percentage Of Repeat Buyers":
		if has_columns(df, ["cust_id"]):
			cust_count = df["cust_id"].value_counts()
			repeat_pct = (cust_count[cust_count > 1].count() / cust_count.count()) * 100
			st.metric("Repeat Buyers (%)", f"{repeat_pct:.2f}%")

	elif selected == "Popular Services By Count":
		if has_columns(df, ["services"]):
			popular = df["services"].value_counts()
			st.write(popular)
			st.bar_chart(popular)

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
			st.write(state_total)
			st.bar_chart(state_total.head(20))
			st.info(f"Top state: {state_total.idxmax()}")

	elif selected == "City With Highest Number Of Transactions":
		if has_columns(df, ["city"]):
			city_count = df["city"].value_counts()
			st.write(city_count)
			st.bar_chart(city_count.head(20))
			st.info(f"Top city: {city_count.idxmax()}")

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
			st.bar_chart(outdoor_by_state.head(20))

	elif selected == "Compare Average Spending: California vs Texas":
		if has_columns(df, ["state", "t_amt"]):
			ca_avg = df[df["state"] == "California"]["t_amt"].mean()
			tx_avg = df[df["state"] == "Texas"]["t_amt"].mean()
			col1, col2 = st.columns(2)
			col1.metric("California Avg", f"{ca_avg:,.3f}")
			col2.metric("Texas Avg", f"{tx_avg:,.3f}")

	elif selected == "Quarter With Highest Sales":
		if has_columns(df, ["quarter", "t_amt"]):
			quarter_total = df.groupby("quarter")["t_amt"].sum().sort_values(ascending=False)
			st.write(quarter_total)
			st.bar_chart(quarter_total)
			st.info(f"Top quarter: {quarter_total.idxmax()}")

	elif selected == "Total Sales By Month":
		if has_columns(df, ["month", "t_amt"]):
			month_total = df.groupby("month")["t_amt"].sum()
			st.write(month_total)
			st.bar_chart(month_total)

	elif selected == "Team Sports Sales By Month":
		if has_columns(df, ["services", "month", "t_amt"]):
			sports = df[df["services"] == "Team Sports"]
			monthly = sports.groupby("month")["t_amt"].sum()
			st.write(monthly)
			st.line_chart(monthly)

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

	elif selected == "Cities By Average Transaction":
		if has_columns(df, ["city", "t_amt"]):
			city_avg = df.groupby("city")["t_amt"].mean().sort_values(ascending=False)
			st.write(city_avg.head(50))

	elif selected == "Exercise & Fitness: Top Products":
		if has_columns(df, ["services", "products_used", "t_amt"]):
			fitness = df[df["services"] == "Exercise & Fitness"]
			product_sales = fitness.groupby("products_used")["t_amt"].sum().sort_values(ascending=False)
			st.write(product_sales.head(20))
			st.bar_chart(product_sales.head(20))

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

	# Footer
	st.caption("Built with Streamlit • Upload your own transactions.csv to explore insights")


