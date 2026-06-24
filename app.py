import streamlit as st
import pandas as pd
import joblib
from textblob import TextBlob
import plotly.express as px
from prophet import Prophet

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Smart Community AI",
    page_icon="🏙️",
    layout="wide"
)

# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------

model = joblib.load("model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🏙️ Smart Community AI")
st.markdown(
    "### AI-Powered Decision Intelligence Platform for Smarter Communities"
)

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

menu = st.sidebar.selectbox(
    "Select Module",
    [
        "Complaint Analysis",
        "Dashboard",
        "Insights",
        "Forecast"
    ],
    key="main_menu"
)

# ==================================================
# COMPLAINT ANALYSIS
# ==================================================

if menu == "Complaint Analysis":

    st.subheader("📝 Citizen Complaint Analyzer")

    complaint = st.text_area(
        "Enter Citizen Complaint",
        key="complaint_input"
    )

    if st.button(
        "Analyze Complaint",
        key="analyze_button"
    ):

        if complaint.strip():

            transformed = vectorizer.transform(
                [complaint]
            )

            category = model.predict(
                transformed
            )[0]

            sentiment_score = TextBlob(
                complaint
            ).sentiment.polarity

            if sentiment_score > 0:
                sentiment = "Positive"
            elif sentiment_score < 0:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"

            recommendations = {
                "Waste":
                "Increase waste collection frequency and deploy sanitation teams.",

                "Water":
                "Inspect pipelines and repair leakages immediately.",

                "Traffic":
                "Deploy traffic officers and optimize signal timing.",

                "Infrastructure":
                "Schedule maintenance and infrastructure inspection.",

                "Environment":
                "Initiate environmental monitoring and cleanup action.",

                "Public Safety":
                "Increase surveillance and emergency response presence.",

                "Healthcare":
                "Allocate additional healthcare resources."
            }

            priority_map = {
                "Public Safety": "High",
                "Healthcare": "High",
                "Traffic": "Medium",
                "Water": "Medium",
                "Waste": "Medium",
                "Infrastructure": "Low",
                "Environment": "Low"
            }

            priority = priority_map.get(
                category,
                "Medium"
            )

            st.success(
                f"Predicted Category: {category}"
            )

            st.info(
                f"Sentiment: {sentiment}"
            )

            st.error(
                f"Priority Level: {priority}"
            )

            st.warning(
                recommendations.get(
                    category,
                    "Investigate issue further."
                )
            )

# ==================================================
# DASHBOARD
# ==================================================

elif menu == "Dashboard":

    df = pd.read_csv(
        "complaints.csv"
    )

    st.subheader(
        "📊 Community Dashboard"
    )

    category_counts = (
        df["category"]
        .value_counts()
        .reset_index()
    )

    category_counts.columns = [
        "Category",
        "Count"
    ]

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            category_counts,
            x="Category",
            y="Count",
            title="Complaint Categories"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        fig2 = px.pie(
            category_counts,
            names="Category",
            values="Count",
            title="Category Distribution"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    st.subheader("Dataset Preview")

    st.dataframe(
        df,
        use_container_width=True
    )

# ==================================================
# INSIGHTS
# ==================================================

elif menu == "Insights":

    df = pd.read_csv(
        "complaints.csv"
    )

    st.subheader(
        "🤖 AI Community Insights"
    )

    total = len(df)

    top_issue = (
        df["category"]
        .value_counts()
        .idxmax()
    )

    count = (
        df["category"]
        .value_counts()
        .max()
    )

    health_score = max(
        0,
        100 - total
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Complaints",
            total
        )

    with col2:
        st.metric(
            "Top Issue",
            top_issue
        )

    with col3:
        st.metric(
            "Occurrences",
            count
        )

    with col4:
        st.metric(
            "Community Score",
            health_score
        )

    st.markdown(
        "### Suggested Actions"
    )

    st.write(
        f"""
        • Prioritize resources for **{top_issue}**

        • Monitor high-frequency complaints

        • Improve response time

        • Use AI forecasting for future planning

        • Increase citizen engagement

        • Track category-wise trends

        • Implement preventive maintenance
        """
    )

# ==================================================
# FORECAST
# ==================================================

elif menu == "Forecast":

    st.subheader(
        "📈 Complaint Forecast"
    )

    try:

        df = pd.read_csv(
            "complaints.csv"
        )

        df["date"] = pd.to_datetime(
            df["date"]
        )

        daily_data = (
            df.groupby("date")
            .size()
            .reset_index(name="count")
        )

        forecast_df = daily_data.rename(
            columns={
                "date": "ds",
                "count": "y"
            }
        )

        prophet_model = Prophet()

        prophet_model.fit(
            forecast_df
        )

        future = (
            prophet_model
            .make_future_dataframe(
                periods=30
            )
        )

        forecast = (
            prophet_model
            .predict(future)
        )

        predicted_total = int(
            forecast.tail(30)["yhat"].sum()
        )

        st.metric(
            "Predicted Complaints Next Month",
            predicted_total
        )

        fig = px.line(
            forecast,
            x="ds",
            y="yhat",
            title="Next 30-Day Complaint Forecast"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.subheader(
            "Forecast Details"
        )

        st.dataframe(
            forecast[
                [
                    "ds",
                    "yhat",
                    "yhat_lower",
                    "yhat_upper"
                ]
            ].tail(30),
            use_container_width=True
        )

    except Exception as e:

        st.error(
            f"Forecast Error: {e}"
        )