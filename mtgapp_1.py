import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="MTG Swiss Tracker", layout="wide")

# --- INITIALIZE DATA ---
if 'players' not in st.session_state:
    st.session_state.players = []
if 'matches' not in st.session_state:
    st.session_state.matches = []
if 'current_round' not in st.session_state:
    st.session_state.current_round = 0
if 'pairings' not in st.session_state:
    st.session_state.pairings = []

# --- DIALOGS ---
@st.dialog("Finalize Round Results?")
def confirm_results_dialog(results_to_save):
    st.write("Review scores below:")
    review_df = pd.DataFrame(results_to_save)[['p1', 'p1_w', 'p2_w', 'p2']]
    st.table(review_df)
    if st.button("Confirm and Finalize", type="primary"):
        st.session_state.matches.extend(results_to_save)
        st.session_state.pairings = [] 
        st.success("Results recorded!")
        st.rerun()

@st.dialog("Edit Match Result")
def edit_match_dialog(index):
    match = st.session_state.matches[index]
    st.write(f"Editing Round {match['round']}: **{match['p1']}** vs **{match['p2']}**")
    
    col1, col2, col3 = st.columns(3)
    new_p1w = col1.number_input(f"{match['p1']} Wins", 0, 3, value=int(match['p1_w']))
    new_draws = col2.number_input("Draws", 0, 3, value=int(match['d']))
    new_p2w = col3.number_input(f"{match['p2']} Wins", 0, 3, value=int(match['p2_w']))
    
    if st.button("Update Result"):
        st.session_state.matches[index]['p1_w'] = new_p1w
        st.session_state.matches[index]['p2_w'] = new_p2w
        st.session_state.matches[index]['d'] = new_draws
        st.success("Result Updated!")
        st.rerun()

# --- STANDINGS & SWISS PAIRING LOGIC ---
def get_standings():
    if not st.session_state.players:
        return pd.DataFrame(columns=['Player', 'Points', 'OMWP', 'GWP'])
    
    player_stats = {}
    
    # 1. Calculate Individual Match-Win % (MWP) and Game-Win % (GWP)
    for p in st.session_state.players:
        # Find all matches this player has participated in
        p_matches = [m for m in st.session_state.matches if m['p1'] == p or m['p2'] == p]
        m_pts, g_pts, total_games = 0, 0, 0
        rounds_played = len(p_matches)
        
        for m in p_matches:
            is_p1 = (m['p1'] == p)
            opp = m['p2'] if is_p1 else m['p1']
            w, l, d = (m['p1_w'], m['p2_w'], m['d']) if is_p1 else (m['p2_w'], m['p1_w'], m['d'])
            
            # --- MATCH POINTS ---
            # Win = 3, Draw = 1, Loss = 0 (Includes BYE wins)
            if w > l: 
                m_pts += 3
            elif w == l and (w > 0 or d > 0): 
                m_pts += 1
            
            # --- GAME WIN PERCENTAGE (GWP) ---
            # Per MTR: BYEs are ignored for GWP. Only count games against real opponents.
            if opp != "BYE":
                g_pts += (w * 3) + d
                total_games += (w + l + d)

        # Calculate MWP (Minimum 0.33 per MTR rules)
        mwp = max(0.33, m_pts / (rounds_played * 3)) if rounds_played > 0 else 0.33
        
        # Calculate GWP (Minimum 0.33 per MTR rules)
        # Only calculated based on non-BYE games
        gwp = max(0.33, g_pts / (total_games * 3)) if total_games > 0 else 0.33
        
        # Store for OMWP calculation in step 2
        opps = [m['p2'] if m['p1'] == p else m['p1'] for m in p_matches]
        player_stats[p] = {'points': m_pts, 'mwp': mwp, 'gwp': gwp, 'opponents': opps}

    # 2. Calculate Opponent Match-Win % (OMWP) and build the final list
    final_list = []
    for p, stats in player_stats.items():
        # Get the MWP of every opponent (excluding BYEs)
        opp_mwps = [player_stats[o]['mwp'] for o in stats['opponents'] if o != "BYE" and o in player_stats]
        
        # OMWP is the average of those MWPs
        omwp = sum(opp_mwps) / len(opp_mwps) if opp_mwps else 0.33
        
        # We return pure numbers (multiplied by 100) for numerical sorting
        final_list.append({
            'Player': p,
            'Points': stats['points'],
            'OMWP': max(0.33, omwp) * 100,
            'GWP': stats['gwp'] * 100
        })
    
    # Sort by Points (Primary), then OMWP (1st Tiebreaker), then GWP (2nd Tiebreaker)
    return pd.DataFrame(final_list).sort_values(
        by=['Points', 'OMWP', 'GWP'], 
        ascending=False
    )

# --- CALLBACK FOR RAPID ENTRY ---
def add_player_callback():
    # Use the 'player_input' key to get the text
    name = st.session_state.player_input
    if name and name not in st.session_state.players:
        st.session_state.players.append(name)
    # Clear the input box by resetting the key
    st.session_state.player_input = ""

# --- SIDEBAR ---
with st.sidebar:
    st.header("Tournament Overview")
    if st.session_state.current_round == 0:
        st.subheader("Registration")
        # Adding 'on_change' and 'key' makes hitting Enter work instantly
        st.text_input(
            "Enter Player Name:", 
            key="player_input", 
            on_change=add_player_callback,
            placeholder="Type name and hit Enter...",
            autocomplete="new-password"
        )
        
        st.write(f"**Total Players:** {len(st.session_state.players)}")
        if st.session_state.players:
            with st.expander("View/Remove Players"):
                for p in st.session_state.players:
                    cols = st.columns([4, 1])
                    cols[0].write(p)
                    if cols[1].button("❌", key=f"del_{p}"):
                        st.session_state.players.remove(p)
                        st.rerun()
    else:
        st.info(f"Tournament in Progress: Round {st.session_state.current_round}")

        st.divider()
        st.write(f"**Total Players:** {len(st.session_state.players)}")
        if st.session_state.players:
            with st.expander("View/Remove Players"):
                for p in st.session_state.players:
                    cols = st.columns([4, 1])
                    cols[0].write(p)
                    if cols[1].button("❌", key=f"del_{p}"):
                        st.session_state.players.remove(p)
                        st.rerun()


# --- MAIN UI ---
st.title("🔮 MTG Swiss Tournament")
tab1, tab2, tab3 = st.tabs(["📊 Standings", "⚔️ Active Round", "📖 Match History"])

with tab1:
    st.subheader("Leaderboard")
    standings_df = get_standings()
    
    st.dataframe(
        standings_df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            # "g" format means "General": it drops trailing zeros automatically
            # ".5" limits it to 5 significant figures/decimals
            "OMWP": st.column_config.NumberColumn("OMWP", format="%.5g%%"),
            "GWP": st.column_config.NumberColumn("GWP", format="%.5g%%")
        }
    )
    
    # Download Button
    csv = standings_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Standings to CSV",
        data=csv,
        file_name=f"Tournament_Results_Rd{st.session_state.current_round}.csv",
        mime='text/csv',
    )

with tab2:
    if not st.session_state.pairings:
        # Determine the correct button label
        label = "Start Tournament (Random Pairings)" if st.session_state.current_round == 0 else f"Generate Round {st.session_state.current_round + 1}"
        
        if st.button(label):
            # 1. Prepare candidates
            if st.session_state.current_round == 0:
                candidates = st.session_state.players.copy()
                random.shuffle(candidates) # True randomness for Round 1
            else:
                standings = get_standings()
                candidates = standings['Player'].tolist()
            
            new_pairings = []
            
            # 2. Handle BYE (Lowest ranked player who hasn't had one yet)
            if len(candidates) % 2 != 0:
                for i in range(len(candidates)-1, -1, -1):
                    p = candidates[i]
                    if not any(m['p2'] == "BYE" and m['p1'] == p for m in st.session_state.matches):
                        new_pairings.append({'p1': p, 'p2': 'BYE'})
                        candidates.remove(p)
                        break

            # 3. Swiss Pairing Loop (Matching by record + preventing rematches)
            while len(candidates) >= 2:
                p1 = candidates.pop(0)
                found = False
                for i in range(len(candidates)):
                    p2 = candidates[i]
                    # Check if they have played before
                    played_before = any((m['p1'] == p1 and m['p2'] == p2) or (m['p1'] == p2 and m['p2'] == p1) for m in st.session_state.matches)
                    
                    if not played_before or st.session_state.current_round == 0:
                        new_pairings.append({'p1': p1, 'p2': p2})
                        candidates.pop(i)
                        found = True
                        break
                
                # Fallback: if everyone left has played p1, just pair with the next person
                if not found:
                    p2 = candidates.pop(0)
                    new_pairings.append({'p1': p1, 'p2': p2})

            st.session_state.pairings = new_pairings
            st.session_state.current_round += 1
            st.rerun()
    
    else:
        # --- SCORE REPORTING UI ---
        st.subheader(f"Round {st.session_state.current_round} Score Reporting")
        
        # We widened the number columns slightly (from 1 to 1.2) to ensure buttons fit
        h_cols = st.columns([2.5, 2.5, 1.2, 1.2, 1.2])
        h_cols[0].markdown("**Player 1**")
        h_cols[1].markdown("**Player 2**")
        h_cols[2].markdown("**P1 Wins**")
        h_cols[3].markdown("**P2 Wins**")
        h_cols[4].markdown("**Draws**")
        st.divider()

        current_results = []
        for i, pair in enumerate(st.session_state.pairings):
            cols = st.columns([2.5, 2.5, 1.2, 1.2, 1.2])
            
            # Display Player Names
            cols[0].write(f"**{pair['p1']}**")
            cols[1].write(f"**{pair['p2']}**")
            
            # Scoring Inputs with Buttons restored
            if pair['p2'] == "BYE":
                p1_w, p2_w, draws = 2, 0, 0
                cols[2].number_input("P1W", 2, 2, key=f"p1w{i}", disabled=True, label_visibility="collapsed")
                cols[3].number_input("P2W", 0, 0, key=f"p2w{i}", disabled=True, label_visibility="collapsed")
                cols[4].number_input("D", 0, 0, key=f"d{i}", disabled=True, label_visibility="collapsed")
            else:
                # step=1 ensures the + and - buttons move by 1 game at a time
                p1_w = cols[2].number_input("P1W", 0, 2, step=1, key=f"p1w{i}", label_visibility="collapsed")
                p2_w = cols[3].number_input("P2W", 0, 2, step=1, key=f"p2w{i}", label_visibility="collapsed")
                draws = cols[4].number_input("D", 0, 3, step=1, key=f"d{i}", label_visibility="collapsed")
            
            current_results.append({
                'round': st.session_state.current_round, 
                'p1': pair['p1'], 
                'p2': pair['p2'], 
                'p1_w': p1_w, 
                'p2_w': p2_w, 
                'd': draws
            })
            st.divider()

        if st.button("Finalize Round Results", type="primary"):
            confirm_results_dialog(current_results)

with tab3:
    st.subheader("Match History")
    if not st.session_state.matches:
        st.write("No matches played yet.")
    else:
        # --- NEW: EXPORT HISTORY TO CSV ---
        history_df = pd.DataFrame(st.session_state.matches)
        
        # Reordering columns for better readability in the CSV
        history_df = history_df[['round', 'p1', 'p1_w', 'p2_w', 'p2', 'd']]
        
        csv_history = history_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Export Match History to CSV",
            data=csv_history,
            file_name=f"Tournament_History_Rd{st.session_state.current_round}.csv",
            mime='text/csv',
        )
        
        st.divider()
        # --- END EXPORT SECTION ---

        for idx, match in enumerate(st.session_state.matches):
            c = st.columns([1, 4, 1])
            c[0].write(f"**Rd {match['round']}**")
            c[1].write(f"{match['p1']} ({match['p1_w']}) vs {match['p2']} ({match['p2_w']}) - Draws: {match['d']}")
            if c[2].button("Edit", key=f"edit_{idx}"):
                edit_match_dialog(idx)








