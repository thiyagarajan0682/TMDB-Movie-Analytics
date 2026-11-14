import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("TMDB Movie Analytics")


from sqlalchemy import create_engine
engine = create_engine("sqlite:///data/movies.db")

from streamlit_option_menu import option_menu

with st.sidebar:
    selected = option_menu("Main Menu", ["Filters", 'Dashboard',"Query Explorer"], 
        icons=['funnel', 'bar-chart','search'], menu_icon="cast", default_index=1)
    selected

if selected == "Query Explorer": 
    option = st.selectbox(
    "Select a query",
    ("List all movies in the Action genre released after 2015, showing title and release date",
     "Find the top 10 highest-grossing movies along with the genre(s) each belongs to",
     "Calculate the average budget and average revenue for each genre, sorted byaverage revenue descending",
     "List the top 10 actors who have appeared in the most movies in the dataset",
     "Find all directors who have directed more than 3 movies, along with their movie count",
     "List the top 10 most frequently used keywords across all movies",
     "Find movies where the budget was above the overall average budget but the revenue was below the overall average revenue",
     "List all actors who have appeared in a movie directed by a specific director(e.g., Christopher Nolan)",
     "Find the genre with the highest average rating, considering only genres with atleast 20 movies",
     "List the top 10 movies with the highest number of keywords tagged to them"),
    )

    q1 = """SELECT m.title, m.release_date FROM movies m
JOIN movie_genres mg ON m.movie_id = mg.movie_id
JOIN genres g ON mg.genre_id = g.genre_id 
WHERE g.genre_name='Action' AND m.release_date >= "2016-01-01"
"""

    q2 = """SELECT m.title, m.revenue, GROUP_CONCAT(g.genre_name,", ") AS genres FROM movies m
JOIN movie_genres mg ON m.movie_id = mg.movie_id
JOIN genres g ON mg.genre_id = g.genre_id
GROUP BY m.movie_id, m.title, m.revenue
ORDER BY m.revenue DESC
LIMIT 10
"""
    q3 = """SELECT g.genre_name, ROUND(AVG(m.budget),0) budgetAvrg, ROUND(AVG(m.revenue),0) revenueAvrg FROM movies m
JOIN  movie_genres mg ON m.movie_id = mg.movie_id
JOIN genres g ON mg.genre_id = g.genre_id
WHERE m.budget > 0 AND m.revenue > 0
GROUP BY g.genre_name
ORDER BY revenueAvrg DESC
"""
    q4 = """SELECT actor_name, COUNT(DISTINCT movie_id) movieCount FROM cast
GROUP BY person_id, actor_name
ORDER BY movieCount DESC
LIMIT 10
"""
    q5 = """SELECT person_name AS director, COUNT(DISTINCT movie_id) AS movieCount FROM crew
WHERE job = 'Director'
GROUP BY person_id, person_name
HAVING COUNT(DISTINCT movie_id) > 3
ORDER BY movieCount DESC
"""
    q6 = """SELECT keyword_name AS keyword, COUNT(DISTINCT movie_id) AS usageCount FROM movie_keywords
GROUP BY keyword_id, keyword_name
ORDER BY usageCount DESC
LIMIT 10
"""
    q7 = """ SELECT title, budget, revenue FROM movies
WHERE budget > (SELECT AVG(budget) FROM movies WHERE budget > 0)
AND revenue < (SELECT AVG(revenue) FROM movies WHERE revenue > 0)
AND revenue > 0
ORDER BY budget DESC
"""
    q8 = """ SELECT DISTINCT ca.actor_name FROM cast AS ca
JOIN crew AS cr ON ca.movie_id = cr.movie_id
WHERE cr.person_name = 'Christopher Nolan'
AND cr.job = 'Director'
ORDER BY ca.actor_name
"""
    q9 = """ SELECT g.genre_name, ROUND(AVG(m.vote_average),2) AS averageRating, COUNT(DISTINCT m.movie_id) AS movieCount
FROM genres g
JOIN movie_genres mg ON g.genre_id = mg.genre_id
JOIN movies m ON mg.movie_id = m.movie_id
GROUP BY g.genre_id, g.genre_name
HAVING COUNT(DISTINCT m.movie_id) >= 20
ORDER BY averageRating DESC
"""
    q10 = """ SELECT m.title, COUNT(DISTINCT mk.keyword_id) AS keywordCount FROM movies m
JOIN movie_keywords mk ON m.movie_id = mk.movie_id
GROUP BY m.movie_id, m.title
ORDER BY keywordCount DESC
LIMIT 10
"""

    if option == "List all movies in the Action genre released after 2015, showing title and release date":
        df = pd.read_sql(q1,engine)
        st.dataframe(df)

        st.subheader("Visualization")
        st.bar_chart(df["release_date"].str[:4].value_counts().sort_index())

        st.subheader("Insight")
        st.info("268 Action movies were released from 1 January 2016 onwards, so Action is a regularly produced genre in recent years.")



    if option == "Find the top 10 highest-grossing movies along with the genre(s) each belongs to":
        df = pd.read_sql(q2,engine)
        st.dataframe(df)

        st.subheader("Visualization")
        st.bar_chart(df.set_index("title")["revenue"])

        st.subheader("Insight")
        st.info("A small number of movies contribute a significant share of total revenue, indicating the impact of blockbuster films.")


    if option == "Calculate the average budget and average revenue for each genre, sorted byaverage revenue descending":
        df = pd.read_sql(q3,engine)
        st.dataframe(df)

        st.subheader("Visualization")
        st.bar_chart(df.set_index("genre_name")[["budgetAvrg", "revenueAvrg"]])

        st.subheader("Insight")
        st.info("Some genres generate much higher average revenue than others, showing that financial performance varies across genres.")

    if option == "List the top 10 actors who have appeared in the most movies in the dataset":
            df = pd.read_sql(q4,engine)
            st.dataframe(df)

            st.subheader("Visualization")
            st.bar_chart(df.set_index("actor_name")["movieCount"])

            st.subheader("Insight")
            st.info("A few actors appear in a large number of movies, suggesting a strong and consistent presence in the industry.")



    if option == "Find all directors who have directed more than 3 movies, along with their movie count":
            df = pd.read_sql(q5,engine)
            st.dataframe(df)

            st.subheader("Visualization")
            st.bar_chart(df.set_index("director")["movieCount"])

            st.subheader("Insight")
            st.info("Only a limited number of directors have directed multiple movies, indicating sustained contribution over time.")


    if option == "List the top 10 most frequently used keywords across all movies":
            df = pd.read_sql(q6,engine)
            st.dataframe(df)

            st.subheader("Visualization")
            st.bar_chart(df.set_index("keyword")["usageCount"])

            st.subheader("Insight")
            st.info("Frequently used keywords reveal common themes and topics that appear across many movies.")


    if option == "Find movies where the budget was above the overall average budget but the revenue was below the overall average revenue":
            df = pd.read_sql(q7,engine)
            st.dataframe(df)

            st.subheader("Visualization")
            st.bar_chart(df.set_index("title")[["budget", "revenue"]])

            st.subheader("Insight")
            st.info("Higher spending does not always guarantee higher revenue, as several high-budget movies performed below average.")


    if option == "List all actors who have appeared in a movie directed by a specific director(e.g., Christopher Nolan)":
            df = pd.read_sql(q8,engine)
            st.dataframe(df)

            st.subheader("Visualization")
            st.write("Total Actors:", len(df))

            st.subheader("Insight")
            st.info("The result highlights recurring actor collaborations within movies directed by Christopher Nolan.")


    if option == "Find the genre with the highest average rating, considering only genres with atleast 20 movies":
            df = pd.read_sql(q9,engine)
            st.dataframe(df)

            st.subheader("Visualization")
            st.bar_chart(df.set_index("genre_name")["averageRating"])

            st.subheader("Insight")
            st.info("Certain genres consistently receive better audience ratings, showing differences in audience preference.")


    if option == "List the top 10 movies with the highest number of keywords tagged to them":
            df = pd.read_sql(q10,engine)
            st.dataframe(df)

            st.subheader("Visualization")
            st.bar_chart(df.set_index("title")["keywordCount"])

            st.subheader("Insight")
            st.info("Smile 2 has the most keywords (98), far ahead of Taken 3 (70), which is 28 keywords lower. Silent Hill is third with 63.")



    st.write("You selected:", option)




elif selected == "Dashboard":
    st.header("Dashboard")
    movies_df = pd.read_sql("SELECT * FROM movies", engine)
    genres_df = pd.read_sql("SELECT * FROM genres", engine)
    cast_df = pd.read_sql("SELECT * FROM cast", engine)

    movies_df["release_year"] = pd.to_datetime(movies_df["release_date"]).dt.year

    if "year_range" in st.session_state:
        movies_df = movies_df[
        (movies_df["release_year"] >= st.session_state["year_range"][0])
        &
        (movies_df["release_year"] <= st.session_state["year_range"][1])
    ]
    if "rating" in st.session_state:
        movies_df = movies_df[
        movies_df["vote_average"] >= st.session_state["rating"]
    ]
    if "language" in st.session_state and st.session_state["language"] != "All":
        movies_df = movies_df[
        movies_df["original_language"] == st.session_state["language"]
    ]


    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Total Movies", len(movies_df))
    with c2:
            st.metric("Total Genres", len(genres_df))
    with c3:
            st.metric("Total Actors", cast_df["person_id"].nunique())
    with c4:
            st.metric(
            "Average Rating",
            round(movies_df["vote_average"].mean(), 2)
        )


    st.subheader("Top 10 Movies by Revenue")
    top10 = (movies_df[["title", "revenue"]].sort_values("revenue", ascending=False).head(10))
    st.bar_chart(
        top10.set_index("title")["revenue"]
    )

    st.subheader("Genre Distribution")
    genre_count = pd.read_sql("""
    SELECT g.genre_name,
           COUNT(*) AS movie_count
    FROM movie_genres mg
    JOIN genres g
    ON mg.genre_id = g.genre_id
    GROUP BY g.genre_name
    ORDER BY movie_count DESC
    """, engine)
    st.bar_chart(
        genre_count.set_index("genre_name")["movie_count"]
    )

    st.subheader("Budget vs Revenue")
    fig, ax = plt.subplots(figsize=(8,5))
    sns.scatterplot(
        data=movies_df,
        x="budget",
        y="revenue",
        ax=ax
    )
    st.pyplot(fig)

    st.subheader("Insight")
    st.info("Most movies are concentrated in a few popular genres. Higher budget movies generally tend to generate higher revenue, although there are several exceptions.")





elif selected == "Filters":
    st.header("Filters")
    movies_df = pd.read_sql("SELECT * FROM movies", engine)
    genres_df = pd.read_sql("""
    SELECT DISTINCT g.genre_name
    FROM genres g
    ORDER BY g.genre_name
    """, engine)
    movies_df["release_year"] = pd.to_datetime(
        movies_df["release_date"]
    ).dt.year
    st.session_state["genre"] = st.multiselect(
        "Select Genre",
        genres_df["genre_name"].tolist()
    )
    st.session_state["year_range"] = st.slider(
        "Release Year Range",
        int(movies_df["release_year"].min()),
        int(movies_df["release_year"].max()),
        (
            int(movies_df["release_year"].min()),
            int(movies_df["release_year"].max())
        )
    )
    st.session_state["rating"] = st.slider(
        "Minimum Rating",
        0.0,
        10.0,
        5.0
    )
    st.session_state["language"] = st.selectbox(
        "Language",
        ["All"] + sorted(
            movies_df["original_language"]
            .dropna()
            .unique()
            .tolist()
        )
    )
    filtered_df = movies_df.copy()
    filtered_df = filtered_df[
        (filtered_df["release_year"] >= st.session_state["year_range"][0])
        &
        (filtered_df["release_year"] <= st.session_state["year_range"][1])
    ]
    filtered_df = filtered_df[
        filtered_df["vote_average"] >= st.session_state["rating"]
    ]
    if st.session_state["language"] != "All":
        filtered_df = filtered_df[
            filtered_df["original_language"]
            ==
            st.session_state["language"]
        ]
    st.metric(
        "Matching Movies",
        len(filtered_df)
    )

