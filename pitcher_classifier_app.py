import streamlit as st
import pandas as pd
import joblib

model = joblib.load('pitcher_classifier_model.joblib')

def calculate_muscle_fatigue(total_pitches, pace, games_played):
    return (0.10963 + 0.032 * total_pitches - 0.0023 * pace) / games_played

def calculate_fatigue_units(whip, bb_ip, k_ip, batters_ip, ip, starting, relieving):
    return 0.18*whip + 0.14*bb_ip + 0.34*k_ip - 0.16*batters_ip + 0.08*ip + 0.3*starting + 0.14*relieving

# Title of the app
st.title("Pitcher Cluster Prediction")

# Section for calculating muscle fatigue
st.sidebar.header("Average Muscle Fatigue Calculator")
total_pitches = st.number_input("Total Pitches")
pace = st.number_input("Average Pace")
games_played = st.number_input("Games Played")
muscle_fatigue = calculate_muscle_fatigue(total_pitches, pace, games_played)
st.write(f"Calculated Muscle Fatigue: {muscle_fatigue:.2f}")

# Section for calculating fatigue units
st.sidebar.header("Fatigue Units Calculator")
whip = st.number_input("WHIP")
bb_ip = st.number_input("Walks per Inning Pitched")
k_ip = st.number_input("Strikeouts per Inning Pitched")
batters_ip = st.number_input("Batters Faced per Inning Pitched")
ip = st.number_input("Innings Pitched")
starting = st.number_input("Games Started")
relieving = st.number_input("Games Relieved")
fatigue_units = calculate_fatigue_units(whip, bb_ip, k_ip, batters_ip, ip, starting, relieving)
st.write(f"Calculated Fatigue Units: {fatigue_units:.2f}")

# Section for predicting the cluster
st.header("Predict Pitcher Cluster")

# Collect user input for the prediction model
average_rest_days = st.number_input("Average Rest Days")
fatigue_units = st.number_input("Fatigue Units")
muscle_fatigue = st.number_input("Muscle Fatigue")
games_played = st.number_input("Games Played")
total_pitches = st.number_input("Total Pitches")


# Predict button
if st.button("Predict Cluster"):
    # Create a DataFrame from the input
    input_data = pd.DataFrame({
        'average_rest_days': [average_rest_days],
        'fatigue_units': [fatigue_units],
        'average_muscle_fatigue': [muscle_fatigue],
        'games_played': [games_played],
        'total_pitches': [total_pitches]
    })
    cluster_description = {
        0: "Versatile Pitcher",
        1: "Middle Reliever",
        2: "Starting Pitcher",
        3: "Closer"
    }

    # Predict the cluster
    cluster = model.predict(input_data)[0]
    st.write(f"The predicted cluster is: {cluster}")

# Additional information or descriptions about clusters can be added here
