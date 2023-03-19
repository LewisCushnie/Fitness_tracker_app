import streamlit as st

def show_cardio_summary_stats(df, day_diff):

        line = '---'
        st.header(f'Summary stats for {day_diff}-day time period')

        col1, col2, col3, col4 = st.columns(4)

        # total gym visits over time period
        with col1: 
            count_tokei_start = df['start_location'].str.count("Tokei").sum()
            count_tokei_end = df['end_location'].str.count("Tokei").sum()
            total_gym_visits = max(count_tokei_start, count_tokei_end)
            st.metric('Total gym visits', int(total_gym_visits))

        with col2:
            # total number of days I cycled
            count_cycle = df['type'].str.count("Ride").sum()
            st.metric('Total cycle rides', count_cycle)

        with col3:
            # total distance cycled
            ride_mask = (df['type'] == 'Ride')
            ride_distance = df['distance (km)'][ride_mask].sum()
            st.metric('Total distance riden (km)', round(ride_distance, 1))

        with col4:
            # total distance cycled
            run_mask = (df['type'] == 'Run')
            run_distance = df['distance (km)'][run_mask].sum()
            st.metric('Total distance run (km)', round(run_distance, 1))