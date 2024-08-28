import streamlit as st
import pandas as pd

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.figure_factory as ff
import seaborn as sns

df = pd.read_csv("athlete_events.csv")
region_df = pd.read_csv("noc_regions.csv")

import preprocessor
import helper

df = preprocessor.preprocess(df, region_df)

st.sidebar.image("oo.jpeg", use_column_width=True)
st.sidebar.title("Olympics Analysis")

user_menu = st.sidebar.radio(
    'Select an Option',
    ('Dataset', 'Medal Tally', 'Overall Analysis', 'Athlete wise Analysis')
)

if user_menu == 'Dataset':
    st.title("120 years of Olympic history")
    st.dataframe(df)



if user_menu == 'Medal Tally':
    st.sidebar.header("Medal Tally")

    years,country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year",years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df,selected_year,selected_country)

    if selected_year == 'Overall' and selected_country == 'Overall':
        st.title("Overall Tally")
    if selected_year != 'Overall' and selected_country == 'Overall':
        st.title("Medal Tally in " + str(selected_year) + " Olympics")
    if selected_year == 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " overall performance")
    if selected_year != 'Overall' and selected_country != 'Overall':
        st.title(selected_country + " performance in " + str(selected_year) + " Olympics")

    st.table(medal_tally)


if user_menu == 'Overall Analysis':
    editions = df['Year'].unique().shape[0] - 1
    cities = df['City'].unique().shape[0]
    sports = df['Sport'].unique().shape[0]
    events = df['Event'].unique().shape[0]
    athletes = df['Name'].unique().shape[0]
    nations = df['region'].unique().shape[0]

    st.title("Top Statistics")
    col1,col2,col3 = st.columns(3)
    with col1:
        st.header("Editions")
        # st.title(editions)
        st.subheader(editions)
    with col2:
        st.header("Hosts")
        st.subheader(cities)
    with col3:
        st.header("Sports")
        st.subheader(sports)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.subheader(events)
    with col2:
        st.header("Nations")
        st.subheader(nations)
    with col3:
        st.header("Athletes")
        st.subheader(athletes)

    st.write("")
    st.write("")

    ############################################################

    nations_over_time = helper.participating_countries_over_time(df)
    fig = px.line(nations_over_time, x = 'Year', y = 'Number of countries')
    st.title("Participating Nations Over the Years")
    st.plotly_chart(fig)

    st.write("")
    st.write("")

    #############################################################

    st.title("Number of Events in every Sport")
    
    fig, ax = plt.subplots(figsize=(18,18))
    x = df.drop_duplicates(['Year', 'Sport', 'Event'])
    ax = sns.heatmap(x.pivot_table(index = 'Sport', columns = 'Year', values = 'Event', aggfunc='count').fillna(0).astype(int))

    st.pyplot(fig)

    st.write("")
    st.write("")

    ##############################################################

    st.title("Most Successful athletes")

    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    selected_sport = st.selectbox('Select sport', sport_list)

    x = helper.most_successful(df, selected_sport)
    st.dataframe(x)




if user_menu == 'Athlete wise Analysis':

    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()

    # Plot Distribution of Age by Medal Type
    ages_df = pd.DataFrame({
        'Age': pd.concat([x1, x2, x3, x4]),
        'Category': ['Overall Age'] * len(x1) + ['Gold Medalist'] * len(x2) + ['Silver Medalist'] * len(x3) + ['Bronze Medalist'] * len(x4)
    })

    fig = px.histogram(ages_df, x='Age', color='Category', barmode='overlay', labels={'Age': 'Age', 'Category': 'Medal Type'})
    fig.update_layout(title="Distribution of Age by Medal Type", autosize=False, width=1000, height=600)
    st.plotly_chart(fig)

    st.write("")
    st.write("")

    # Plot Distribution of Age by Sport for Gold Medalists
    sports = athlete_df['Sport'].unique()
    sports.sort()
    sports = list(sports)  # Convert numpy array to list
    sports.insert(0, 'Overall')

    x = []
    name = []
    for sport in sports[1:]:  # Skip 'Overall' for sport-specific analysis
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        if not temp_df[temp_df['Medal'] == 'Gold'].empty:
            x.append(temp_df[temp_df['Medal'] == 'Gold']['Age'].dropna())
            name.append(sport)

    if x:  # Ensure there is data to plot
        ages_sports_df = pd.DataFrame({
            'Age': np.concatenate(x),
            'Sport': np.concatenate([[n] * len(xi) for xi, n in zip(x, name)])
        })

        fig = px.histogram(ages_sports_df, x='Age', color='Sport', barmode='overlay', labels={'Age': 'Age', 'Sport': 'Sport'})
        fig.update_layout(title="Distribution of Age by Sport (Gold Medalists)", autosize=False, width=1000, height=600)
        st.plotly_chart(fig)

    st.write("")
    st.write("")

    # Height vs Weight
    sport_list = df['Sport'].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, 'Overall')

    st.title('Height Vs Weight')
    selected_sport = st.selectbox('Select a Sport', sport_list)
    temp_df = helper.weight_v_height(df, selected_sport)
    
    if not temp_df.empty:  # Ensure there is data to plot
        fig, ax = plt.subplots()
        ax = sns.scatterplot(x=temp_df['Weight'], y=temp_df['Height'], hue=temp_df['Medal'], style=temp_df['Sex'], s=60)
        ax.set_xlabel('Weight')
        ax.set_ylabel('Height')
        ax.set_title('Height vs Weight')
        st.pyplot(fig)
    else:
        st.write("No data available for the selected sport.")

    st.write("")
    st.write("")

    # Men vs Women Participation
    st.title("Men Vs Women Participation")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(title="Men vs Women Participation Over the Years", autosize=False, width=1000, height=600)
    st.plotly_chart(fig)
