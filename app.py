import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import tempfile
import os
from utils.audio_processor import AudioProcessor
from utils.sentiment_analyzer import SentimentAnalyzer
from utils.wellness_generator import WellnessGenerator
import json

# Audio recording is optional - we'll use text input as primary method
AUDIO_RECORDER_AVAILABLE = False

# Page config
st.set_page_config(
    page_title="SereneDesk - AI Workspace Mood Optimizer",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'mood_history' not in st.session_state:
    st.session_state.mood_history = []
if 'stress_triggers' not in st.session_state:
    st.session_state.stress_triggers = {}
if 'wellness_log' not in st.session_state:
    st.session_state.wellness_log = []

# Initialize processors
@st.cache_resource
def load_processors():
    audio_processor = AudioProcessor()
    sentiment_analyzer = SentimentAnalyzer()
    wellness_generator = WellnessGenerator()
    return audio_processor, sentiment_analyzer, wellness_generator

def main():
    st.title("🧘 SereneDesk: AI Workspace Mood Optimizer")
    st.markdown("*Transform your workspace into a sanctuary of productivity and wellness*")
    
    audio_processor, sentiment_analyzer, wellness_generator = load_processors()
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox("Choose a feature:", [
            "💭 Mood Check-in",
            "📊 Mood Analytics", 
            "🎵 Ambient Soundscapes",
            "📝 Wellness Journal",
            "⚙️ Settings"
        ])
        
        st.markdown("---")
        st.markdown("### Quick Stats")
        if st.session_state.mood_history:
            avg_mood = np.mean([entry['mood_score'] for entry in st.session_state.mood_history])
            st.metric("Average Mood", f"{avg_mood:.1f}/10")
            st.metric("Check-ins Today", len([e for e in st.session_state.mood_history 
                                            if e['timestamp'].date() == datetime.now().date()]))
    
    if page == "💭 Mood Check-in":
        voice_checkin_page(audio_processor, sentiment_analyzer, wellness_generator)
    elif page == "📊 Mood Analytics":
        analytics_page()
    elif page == "🎵 Ambient Soundscapes":
        soundscapes_page()
    elif page == "📝 Wellness Journal":
        journal_page()
    elif page == "⚙️ Settings":
        settings_page()

def voice_checkin_page(audio_processor, sentiment_analyzer, wellness_generator):
    st.header("💭 Mood Check-in")
    st.markdown("Share how you're feeling and get personalized wellness recommendations")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Tell Us How You're Feeling")
        
        # Text input for mood check-in
        st.info("💡 Describe your current mood, energy level, and any workplace stress you're experiencing.")
        
        text_input = st.text_area(
            "Your check-in:", 
            height=120, 
            placeholder="Example: I'm feeling a bit overwhelmed today with the project deadline coming up. I'm tired but trying to stay motivated. The constant meetings are making it hard to focus on deep work..."
        )
        
        # Quick mood selector as additional input
        col_a, col_b = st.columns(2)
        with col_a:
            quick_mood = st.selectbox("Quick mood rating:", 
                                     ["Select...", "😊 Great", "🙂 Good", "😐 Okay", "😟 Stressed", "😫 Overwhelmed"])
        with col_b:
            energy_quick = st.selectbox("Energy level:", 
                                       ["Select...", "⚡ High", "🔋 Medium", "🪫 Low", "😴 Exhausted"])
        
        # Combine inputs
        if st.button("✨ Get Wellness Insights", type="primary") and text_input.strip():
            # Enhance text with quick selections
            enhanced_text = text_input.strip()
            if quick_mood != "Select...":
                enhanced_text += f" My mood right now is {quick_mood}."
            if energy_quick != "Select...":
                enhanced_text += f" My energy level is {energy_quick}."
            
            transcript = enhanced_text
            st.subheader("Your Check-in")
            st.write(transcript)
            
            with st.spinner("Analyzing your check-in..."):
                try:
                    # Analyze sentiment
                    sentiment_result = sentiment_analyzer.analyze_sentiment(transcript)
                    
                    # Generate wellness recommendations
                    wellness_suggestions = wellness_generator.generate_suggestions(
                        transcript, sentiment_result
                    )
                    
                    # Display results
                    display_analysis_results(sentiment_result, wellness_suggestions)
                    
                    # Save to history
                    save_checkin(transcript, sentiment_result, wellness_suggestions)
                    
                except Exception as e:
                    st.error(f"Sorry, there was an issue analyzing your check-in: {e}")
                    st.info("Please make sure you have set up your OpenAI API key in the .env file.")
        
        elif st.button("✨ Get Wellness Insights", type="primary", key="insights_button_empty"):
            st.warning("Please share how you're feeling before getting insights!")
    
    with col2:
        st.subheader("Recent Mood Trend")
        if st.session_state.mood_history:
            recent_moods = st.session_state.mood_history[-7:]  # Last 7 entries
            df = pd.DataFrame(recent_moods)
            fig = px.line(df, x='timestamp', y='mood_score', 
                         title="Mood Score Trend",
                         range_y=[0, 10])
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Start with check-ins to see your mood trend!")
            
        # Sample prompts to help users
        st.subheader("Need inspiration?")
        sample_prompts = [
            "I'm feeling productive today but worried about tomorrow's presentation.",
            "Overwhelmed with emails and back-to-back meetings. Need a break.",
            "Great morning! Accomplished a lot and feeling motivated.",
            "Tired from staying up late. Struggling to focus on important tasks."
        ]
        
        for i, prompt in enumerate(sample_prompts):
            if st.button(f"Use this example", key=f"sample_{i}", help=prompt):
                st.session_state.sample_text = prompt

def display_analysis_results(sentiment_result, wellness_suggestions):
    st.subheader("Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mood_score = sentiment_result.get('mood_score', 5)
        st.metric("Mood Score", f"{mood_score}/10")
    
    with col2:
        stress_level = sentiment_result.get('stress_level', 'Moderate')
        st.metric("Stress Level", stress_level)
    
    with col3:
        energy_level = sentiment_result.get('energy_level', 'Medium')
        st.metric("Energy Level", energy_level)
    
    # Wellness recommendations
    st.subheader("🌟 Personalized Recommendations")
    
    if wellness_suggestions.get('break_suggestion'):
        st.info(f"💡 **Break Suggestion**: {wellness_suggestions['break_suggestion']}")
    
    if wellness_suggestions.get('focus_tips'):
        st.success(f"🎯 **Focus Tip**: {wellness_suggestions['focus_tips']}")
    
    if wellness_suggestions.get('journaling_prompt'):
        st.write("📝 **Journaling Prompt**:")
        st.write(wellness_suggestions['journaling_prompt'])

def save_checkin(transcript, sentiment_result, wellness_suggestions):
    entry = {
        'timestamp': datetime.now(),
        'transcript': transcript,
        'mood_score': sentiment_result.get('mood_score', 5),
        'stress_level': sentiment_result.get('stress_level', 'Moderate'),
        'energy_level': sentiment_result.get('energy_level', 'Medium'),
        'wellness_suggestions': wellness_suggestions
    }
    st.session_state.mood_history.append(entry)
    
    # Update stress triggers
    triggers = sentiment_result.get('stress_triggers', [])
    for trigger in triggers:
        if trigger in st.session_state.stress_triggers:
            st.session_state.stress_triggers[trigger] += 1
        else:
            st.session_state.stress_triggers[trigger] = 1

def analytics_page():
    st.header("📊 Mood Analytics Dashboard")
    
    if not st.session_state.mood_history:
        st.info("Start recording voice check-ins to see your analytics!")
        return
    
    df = pd.DataFrame(st.session_state.mood_history)
    
    # Time period selector
    col1, col2 = st.columns([3, 1])
    with col2:
        period = st.selectbox("Time Period", ["Last 7 days", "Last 30 days", "All time"])
    
    # Filter data based on period
    if period == "Last 7 days":
        cutoff = datetime.now() - timedelta(days=7)
        df_filtered = df[df['timestamp'] >= cutoff]
    elif period == "Last 30 days":
        cutoff = datetime.now() - timedelta(days=30)
        df_filtered = df[df['timestamp'] >= cutoff]
    else:
        df_filtered = df
    
    if df_filtered.empty:
        st.warning(f"No data available for {period.lower()}")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_mood = df_filtered['mood_score'].mean()
        st.metric("Average Mood", f"{avg_mood:.1f}/10")
    
    with col2:
        total_checkins = len(df_filtered)
        st.metric("Total Check-ins", total_checkins)
    
    with col3:
        stress_counts = df_filtered['stress_level'].value_counts()
        high_stress = stress_counts.get('High', 0)
        stress_percentage = (high_stress / total_checkins) * 100
        st.metric("High Stress %", f"{stress_percentage:.1f}%")
    
    with col4:
        energy_counts = df_filtered['energy_level'].value_counts()
        high_energy = energy_counts.get('High', 0)
        energy_percentage = (high_energy / total_checkins) * 100
        st.metric("High Energy %", f"{energy_percentage:.1f}%")
    
    # Mood trend chart
    st.subheader("Mood Trend Over Time")
    fig_mood = px.line(df_filtered, x='timestamp', y='mood_score',
                       title="Mood Score Trend", range_y=[0, 10])
    fig_mood.add_hline(y=7, line_dash="dash", line_color="green", 
                       annotation_text="Good Mood Threshold")
    fig_mood.add_hline(y=4, line_dash="dash", line_color="red", 
                       annotation_text="Low Mood Alert")
    st.plotly_chart(fig_mood, use_container_width=True)
    
    # Stress and energy distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Stress Level Distribution")
        stress_counts = df_filtered['stress_level'].value_counts()
        fig_stress = px.pie(values=stress_counts.values, names=stress_counts.index,
                           title="Stress Levels")
        st.plotly_chart(fig_stress, use_container_width=True)
    
    with col2:
        st.subheader("Energy Level Distribution")
        energy_counts = df_filtered['energy_level'].value_counts()
        fig_energy = px.pie(values=energy_counts.values, names=energy_counts.index,
                           title="Energy Levels")
        st.plotly_chart(fig_energy, use_container_width=True)
    
    # Stress triggers
    if st.session_state.stress_triggers:
        st.subheader("Top Stress Triggers")
        triggers_df = pd.DataFrame(list(st.session_state.stress_triggers.items()),
                                  columns=['Trigger', 'Frequency'])
        triggers_df = triggers_df.sort_values('Frequency', ascending=False).head(10)
        
        fig_triggers = px.bar(triggers_df, x='Frequency', y='Trigger', 
                             orientation='h', title="Most Common Stress Triggers")
        st.plotly_chart(fig_triggers, use_container_width=True)

def soundscapes_page():
    st.header("🎵 Ambient Soundscapes")
    st.markdown("Choose from curated soundscapes to enhance your workspace environment")
    
    soundscapes = {
        "🌧️ Rain & Thunder": {
            "description": "Gentle rain with distant thunder for deep focus",
            "benefits": "Masks distracting noises, promotes concentration"
        },
        "🌊 Ocean Waves": {
            "description": "Rhythmic ocean waves for relaxation",
            "benefits": "Reduces stress, promotes calm thinking"
        },
        "🏔️ Mountain Stream": {
            "description": "Flowing water over rocks",
            "benefits": "Natural white noise, enhances creativity"
        },
        "🌲 Forest Ambience": {
            "description": "Birds chirping with rustling leaves",
            "benefits": "Reduces mental fatigue, improves mood"
        },
        "☕ Coffee Shop": {
            "description": "Busy café atmosphere with gentle chatter",
            "benefits": "Optimal background noise for productivity"
        },
        "🔥 Crackling Fireplace": {
            "description": "Warm fireplace with gentle crackling",
            "benefits": "Creates cozy atmosphere, reduces anxiety"
        }
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        for name, details in soundscapes.items():
            with st.expander(name):
                st.write(f"**Description:** {details['description']}")
                st.write(f"**Benefits:** {details['benefits']}")
                
                col_a, col_b, col_c = st.columns([1, 1, 2])
                with col_a:
                    if st.button(f"▶️ Play", key=f"play_{name}"):
                        st.success(f"Playing {name}")
                with col_b:
                    if st.button(f"⏸️ Stop", key=f"stop_{name}"):
                        st.info("Stopped")
                with col_c:
                    volume = st.slider("Volume", 0, 100, 50, key=f"vol_{name}")
    
    with col2:
        st.subheader("Personalized Recommendations")
        
        if st.session_state.mood_history:
            latest_mood = st.session_state.mood_history[-1]
            mood_score = latest_mood['mood_score']
            stress_level = latest_mood['stress_level']
            
            if stress_level == 'High':
                st.info("🌧️ **Recommended**: Rain & Thunder for stress relief")
            elif mood_score < 5:
                st.info("🌊 **Recommended**: Ocean Waves for mood boost")
            elif stress_level == 'Low':
                st.info("☕ **Recommended**: Coffee Shop for productivity")
            else:
                st.info("🌲 **Recommended**: Forest Ambience for balance")
        else:
            st.info("Complete a mood check-in to get personalized soundscape recommendations!")
        
        st.subheader("Custom Timer")
        duration = st.selectbox("Focus Session Duration", 
                               ["15 minutes", "25 minutes", "45 minutes", "1 hour", "2 hours"])
        
        if st.button("Start Focus Session"):
            st.success(f"Focus session started for {duration}!")
            st.balloons()

def journal_page():
    st.header("📝 Wellness Journal")
    st.markdown("Reflect on your experiences and track your wellness journey")
    
    tab1, tab2 = st.tabs(["✍️ New Entry", "📖 Journal History"])
    
    with tab1:
        st.subheader("Create New Journal Entry")
        
        # Suggested prompts based on recent mood
        if st.session_state.mood_history:
            latest_entry = st.session_state.mood_history[-1]
            if 'wellness_suggestions' in latest_entry and 'journaling_prompt' in latest_entry['wellness_suggestions']:
                st.info(f"💡 **Suggested Prompt**: {latest_entry['wellness_suggestions']['journaling_prompt']}")
        
        journal_prompt = st.selectbox("Choose a prompt or write freely:", [
            "Free writing",
            "What am I grateful for today?",
            "What challenges did I face and how did I overcome them?",
            "What would make tomorrow better than today?",
            "How did I practice self-care today?",
            "What patterns do I notice in my mood and energy?"
        ])
        
        journal_entry = st.text_area("Your thoughts...", height=200, 
                                   placeholder="Express your thoughts freely...")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("💾 Save Entry"):
                if journal_entry.strip():
                    entry = {
                        'timestamp': datetime.now(),
                        'prompt': journal_prompt,
                        'content': journal_entry,
                        'word_count': len(journal_entry.split())
                    }
                    st.session_state.wellness_log.append(entry)
                    st.success("Journal entry saved!")
                    st.balloons()
                else:
                    st.warning("Please write something before saving.")
        
        with col2:
            if journal_entry.strip():
                word_count = len(journal_entry.split())
                st.metric("Word Count", word_count)
    
    with tab2:
        st.subheader("Your Journal History")
        
        if not st.session_state.wellness_log:
            st.info("Start journaling to see your entries here!")
            return
        
        # Journal statistics
        total_entries = len(st.session_state.wellness_log)
        total_words = sum(entry['word_count'] for entry in st.session_state.wellness_log)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Entries", total_entries)
        with col2:
            st.metric("Total Words", total_words)
        with col3:
            avg_words = total_words / total_entries if total_entries > 0 else 0
            st.metric("Avg Words/Entry", f"{avg_words:.0f}")
        
        # Display entries
        for i, entry in enumerate(reversed(st.session_state.wellness_log)):
            with st.expander(f"📝 {entry['timestamp'].strftime('%B %d, %Y at %I:%M %p')} - {entry['word_count']} words"):
                if entry['prompt'] != "Free writing":
                    st.write(f"**Prompt**: {entry['prompt']}")
                st.write(entry['content'])
                
                col1, col2 = st.columns([3, 1])
                with col2:
                    if st.button("🗑️ Delete", key=f"delete_{i}"):
                        st.session_state.wellness_log.remove(entry)
                        st.rerun()

def settings_page():
    st.header("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["🔔 Notifications", "📊 Data", "ℹ️ About"])
    
    with tab1:
        st.subheader("Notification Preferences")
        
        reminder_enabled = st.checkbox("Enable mood check-in reminders", value=True)
        if reminder_enabled:
            reminder_frequency = st.selectbox("Reminder frequency", 
                                            ["Every 2 hours", "Every 4 hours", "Twice daily", "Daily"])
        
        wellness_alerts = st.checkbox("Enable wellness alerts", value=True)
        stress_notifications = st.checkbox("Notify when stress levels are high", value=True)
        
        st.subheader("Focus Session Settings")
        default_session = st.selectbox("Default focus session length", 
                                     ["15 minutes", "25 minutes", "45 minutes", "1 hour"])
        break_reminders = st.checkbox("Remind me to take breaks", value=True)
    
    with tab2:
        st.subheader("Data Management")
        
        st.write(f"**Total mood check-ins**: {len(st.session_state.mood_history)}")
        st.write(f"**Total journal entries**: {len(st.session_state.wellness_log)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Export Data"):
                # Create export data
                export_data = {
                    'mood_history': st.session_state.mood_history,
                    'wellness_log': st.session_state.wellness_log,
                    'stress_triggers': st.session_state.stress_triggers
                }
                
                # Convert datetime objects to strings for JSON serialization
                for entry in export_data['mood_history']:
                    entry['timestamp'] = entry['timestamp'].isoformat()
                for entry in export_data['wellness_log']:
                    entry['timestamp'] = entry['timestamp'].isoformat()
                
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(export_data, indent=2),
                    file_name=f"serenedesk_data_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("🗑️ Clear All Data", type="secondary"):
                if st.button("⚠️ Confirm Delete", type="secondary"):
                    st.session_state.mood_history = []
                    st.session_state.wellness_log = []
                    st.session_state.stress_triggers = {}
                    st.success("All data cleared!")
                    st.rerun()
    
    with tab3:
        st.subheader("About SereneDesk")
        st.markdown("""
        **SereneDesk v1.0**
        
        An AI-powered workspace mood optimizer that helps you:
        - Monitor your emotional well-being through text check-ins
        - Identify stress triggers and patterns
        - Receive personalized wellness recommendations
        - Create a more intentional and focused work environment
        
        **Technology Stack:**
        - Streamlit for the web interface
        - GPT-4 for sentiment analysis and recommendations
        - Plotly for data visualization
        
        **Privacy Note:**
        Your data is stored locally in your browser session and is not transmitted to external servers.
        """)
        
        st.markdown("---")
        st.markdown("Made with ❤️ for better workplace wellness")

if __name__ == "__main__":
    main()