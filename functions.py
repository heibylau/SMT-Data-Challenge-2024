import pandas as pd
import pyarrow.dataset as pads
from SMT_data_starter import readDataSubset

PITCH = 1
HIT_IN_PLAY = 4
HOMERUN = 11

def get_game_events(level):
    game_events_subset = readDataSubset('game_events', '2024_SMT_Data_Challenge')
    game_events = game_events_subset.to_table(filter = (pads.field('Season') == 'Season_1884') & (pads.field('HomeTeam') == f'Home{level}')).to_pandas()
    return game_events

def get_hits(game_info, game_events):
    at_bat_list = game_info['at_bat'].unique().tolist()
    hits = 0
    for at_bat in at_bat_list:
        at_bat_events = game_events[game_events['at_bat'] == at_bat]['event_code'].tolist()
        if HOMERUN in at_bat_events:
            hits += 1
        if HIT_IN_PLAY in at_bat_events:
            next_at_bat = at_bat + 1
            current_batter = game_info[game_info['at_bat'] == at_bat]['batter'].values[0]
            if current_batter in game_info[game_info['at_bat'] == next_at_bat][['first_baserunner', 'second_baserunner', 'third_baserunner']].values:
                hits += 1
    return hits

def get_walks(game_info, game_events):
    at_bat_list = game_info['at_bat'].unique().tolist()
    walks = 0
    for at_bat in at_bat_list:
        at_bat_events = game_events[game_events['at_bat'] == at_bat]['event_code'].tolist()
        if HIT_IN_PLAY not in at_bat_events:
            next_at_bat = at_bat + 1
            current_batter = game_info[game_info['at_bat'] == at_bat]['batter'].values[0]
            if current_batter in game_info[game_info['at_bat'] == next_at_bat][['first_baserunner', 'second_baserunner', 'third_baserunner']].values:
                walks += 1
    return walks

def get_strikeouts(game_info, game_events):
    at_bat_list = game_info['at_bat'].unique().tolist()
    strikeouts = 0
    for at_bat in at_bat_list:
        at_bat_events = game_events[game_events['at_bat'] == at_bat]['event_code'].tolist()
        if HOMERUN not in at_bat_events and HIT_IN_PLAY not in at_bat_events:
            next_at_bat = at_bat + 1
            current_batter = game_info[game_info['at_bat'] == at_bat]['batter'].values[0]
            if current_batter not in game_info[game_info['at_bat'] == next_at_bat][['first_baserunner', 'second_baserunner', 'third_baserunner']].values:
                strikeouts += 1
    return strikeouts

def get_batters_faced(game_info):
    return game_info['batter'].nunique()

def get_pitching_metrics(game_info, level):
    hits_list = []
    walks_list = []
    strikeout_list = []
    batters_faced_list = []
    innings_pitched_list = []
    is_starter_list = []
    game_str_list = game_info['game_str'].unique().tolist()
    for game_str in game_str_list:
        pitchers_list = game_info[game_info['game_str'] == game_str]['pitcher'].unique().tolist()
        for pitcher in pitchers_list:
            game_info_subset = game_info[(game_info['pitcher'] == pitcher) & (game_info['game_str'] == game_str)]
            inning_list = game_info_subset['inning'].unique().tolist()
            game_events = get_game_events(level)[get_game_events(level)['game_str'] == game_str]
            hits = get_hits(game_info_subset, game_events)
            walks = get_walks(game_info_subset, game_events)
            strikeouts = get_strikeouts(game_info_subset, game_events)
            batters_faced = get_batters_faced(game_info_subset)
            hits_list.append(hits)
            walks_list.append(walks)
            strikeout_list.append(strikeouts)
            batters_faced_list.append(batters_faced)
            innings_pitched_list.append(game_info_subset['inning'].nunique())
            if inning_list[0] == 1:
                is_starter_list.append(1)
            else:
                is_starter_list.append(0)
    return hits_list, walks_list, strikeout_list, batters_faced_list, innings_pitched_list, is_starter_list


def create_pitching_metrics_df(game_info, hits_list, walks_list, strikeout_list, batters_faced_list, innings_pitched_list, is_starter_list):
    pitching_metrics = game_info[['pitcher', 'game_str']].drop_duplicates().reset_index(drop = True)
    pitching_metrics['hits'] = hits_list
    pitching_metrics['walks'] = walks_list
    pitching_metrics['strikeouts'] = strikeout_list
    pitching_metrics['batters_faced'] = batters_faced_list
    pitching_metrics['innings_pitched'] = innings_pitched_list
    pitching_metrics['is_starter'] = is_starter_list
    pitching_metrics['is_reliever'] = pitching_metrics['is_starter'].apply(lambda x: 1 if x == 0 else 0)
    pitching_metrics['BB/IP'] = pitching_metrics['walks'] / pitching_metrics['innings_pitched']
    pitching_metrics['K/IP'] = pitching_metrics['strikeouts'] / pitching_metrics['innings_pitched']
    pitching_metrics['Batters/IP'] = pitching_metrics['batters_faced'] / pitching_metrics['innings_pitched']
    pitching_metrics['WHIP'] = (pitching_metrics['hits'] + pitching_metrics['walks']) / pitching_metrics['innings_pitched']
    return pitching_metrics

def calculate_pace(game_info, level):
    pace_list = []
    total_pitches_list = []
    game_str_list = game_info['game_str'].unique().tolist()
    for game_str in game_str_list:
        pitchers_list = game_info[game_info['game_str'] == game_str]['pitcher'].unique().tolist()
        for pitcher in pitchers_list:
            time = 0
            num_pitches = 0
            game_info_subset = game_info[(game_info['pitcher'] == pitcher) & (game_info['game_str'] == game_str)]
            game_events_subset = get_game_events(level)[get_game_events(level)['game_str'] == game_str]
            if game_str == '1884_143_Vis4BE_Home4A':
                game_events_subset['timestamp'] = game_events_subset['timestamp'] + 500  # Timestamps are systematically off by 500ms for this game
            at_bats = game_info_subset['at_bat'].unique().tolist()
            for at_bat in at_bats:
                pitches_df = game_events_subset[(game_events_subset['at_bat'] == at_bat) & (game_events_subset['event_code'] == PITCH)]
                total_pitches = pitches_df['event_code'].count()
                num_pitches += total_pitches
                if total_pitches > 0:
                    first_pitch = pitches_df.iloc[0]['timestamp']
                    last_pitch = pitches_df.iloc[-1]['timestamp']
                    time += ((last_pitch - first_pitch) / total_pitches) / 1000
            average_pace = time / len(at_bats)
            pace_list.append(average_pace)
            total_pitches_list.append(num_pitches)
    return total_pitches_list, pace_list

def calculate_rest_days(cumulative_metrics):
    game_str = cumulative_metrics['game_str'].tolist()
    game_day = []
    rest_days = []
    pitchers_list = cumulative_metrics['pitcher'].unique().tolist()
    for games in game_str:
        day = int(games[5:8])
        game_day.append(day)
    cumulative_metrics['game_day'] = game_day
    for pitcher in pitchers_list:
        df = cumulative_metrics[cumulative_metrics['pitcher'] == pitcher]
        days = df['game_day'].tolist()
        for i in range(len(days)):
            if i == 0:
                rest_days.append(0)
            else:
                rest_days.append(days[i] - days[i-1] - 1)
    return rest_days

def create_cumulative_pitching_metrics_df(pitching_metrics):
    info = pitching_metrics[['pitcher', 'game_str']]
    cumulative_pitching_metrics = pitching_metrics.groupby('pitcher')[['hits', 'walks', 'strikeouts', 'batters_faced', 'innings_pitched', 'is_starter', 'is_reliever', 'total_pitches', 'pace']].cumsum()
    cumulative_pitching_metrics = pd.concat([info, cumulative_pitching_metrics], axis=1)
    cumulative_pitching_metrics['games_played'] = pitching_metrics.groupby('pitcher')['game_str'].cumcount() + 1
    cumulative_pitching_metrics['BB/IP'] = cumulative_pitching_metrics['walks'] / cumulative_pitching_metrics['innings_pitched']
    cumulative_pitching_metrics['K/IP'] = cumulative_pitching_metrics['strikeouts'] / cumulative_pitching_metrics['innings_pitched']
    cumulative_pitching_metrics['Batters/IP'] = cumulative_pitching_metrics['batters_faced'] / cumulative_pitching_metrics['innings_pitched']
    cumulative_pitching_metrics['WHIP'] = (cumulative_pitching_metrics['walks'] + cumulative_pitching_metrics['hits']) / cumulative_pitching_metrics['innings_pitched']
    cumulative_pitching_metrics['average_pace'] = cumulative_pitching_metrics['pace'] / cumulative_pitching_metrics['games_played']
    cumulative_pitching_metrics.rename(columns={'is_starter': 'games_started', 'is_reliever': 'games_relieved'}, inplace=True)
    return cumulative_pitching_metrics

def apply_fatigue_unit_equation(cumulative_pitching_metrics):
    whip = cumulative_pitching_metrics['WHIP']
    bb_ip = cumulative_pitching_metrics['BB/IP']
    k_ip = cumulative_pitching_metrics['K/IP']
    batters_ip = cumulative_pitching_metrics['Batters/IP']
    ip = cumulative_pitching_metrics['innings_pitched']
    starting = cumulative_pitching_metrics['games_started']
    relieving = cumulative_pitching_metrics['games_relieved']
    fatigue_units_list = (0.18*whip + 0.14*bb_ip + 0.34*k_ip - 0.16*batters_ip + 0.08*ip + 0.3*starting + 0.14*relieving).tolist()
    return fatigue_units_list

def apply_muscle_fatigue_equation(pitching_metrics):
    total_pitches = pitching_metrics['total_pitches']
    pace = pitching_metrics['pace']
    muscle_fatigue_list = (0.10963 + 0.032 * total_pitches - 0.0023 * pace).tolist()
    return muscle_fatigue_list

def get_season_metrics_df(cumulative_pitching_metrics):
    df = pd.DataFrame()
    level = int(cumulative_pitching_metrics['game_str'][0][-2])
    pitchers_list = cumulative_pitching_metrics['pitcher'].unique().tolist()
    for pitcher in pitchers_list:
        rest_day_sum = cumulative_pitching_metrics[cumulative_pitching_metrics['pitcher'] == pitcher]['rest_days'].sum()
        pitcher_last_row = cumulative_pitching_metrics[cumulative_pitching_metrics['pitcher'] == pitcher].iloc[-1]
        pitcher_last_row['average_rest_days'] = rest_day_sum / pitcher_last_row['games_played']
        df = pd.concat([df, pitcher_last_row.to_frame().transpose()], axis=0, ignore_index=True)
    df.drop(columns=['game_str'], inplace=True)
    df['level'] = level
    return df