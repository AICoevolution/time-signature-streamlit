import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter, defaultdict
import re
import plotly.express as px
import plotly.graph_objects as go
from matplotlib.colors import LinearSegmentedColormap

# Set page configuration
st.set_page_config(
    page_title="Classical Time Signature Analysis",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better appearance
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 1rem;
        color: #555;
    }
    .st-emotion-cache-16txtl3 h1 {
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Functions for data manipulation
def load_json_file(file):
    try:
        if isinstance(file, str):
            # Load from file path
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Load from uploaded file
            return json.load(file)
    except Exception as e:
        st.error(f"Error loading JSON file: {e}")
        return None

def extract_time_signatures(data):
    """Extract time signatures with relevant metadata from the database"""
    signatures = []
    
    for composer, works in data.items():
        for work_title, movements in works.items():
            for i, movement in enumerate(movements):
                # Extract time signature
                time_sig = movement.get('time_signature')
                if time_sig:
                    # Add metadata
                    signatures.append({
                        'composer': composer,
                        'work': work_title,
                        'movement': movement.get('movement', f"Movement {i+1}"),
                        'time_signature': time_sig
                    })
    
    return signatures

def normalize_time_signature(time_sig):
    """Normalize time signature format"""
    # Handle common time (C) and cut time (C|)
    if time_sig == 'C':
        return '4/4'
    elif time_sig == 'C|':
        return '2/2'
    
    # Handle fraction format
    if '/' in time_sig:
        return time_sig
    
    return time_sig

def parse_time_signature(time_sig):
    """Parse time signature into numerator and denominator"""
    if '/' in time_sig:
        try:
            num, denom = map(int, time_sig.split('/'))
            return num, denom
        except:
            return None, None
    return None, None

def get_time_signature_category(time_sig):
    """Categorize time signatures into groups"""
    if time_sig in ['2/4', '2/2', '2/8']:
        return 'Duple'
    elif time_sig in ['3/4', '3/8', '3/2']:
        return 'Triple'
    elif time_sig in ['4/4', '4/8', '4/2']:
        return 'Quadruple'
    elif time_sig in ['6/8', '6/4']:
        return 'Compound Duple'
    elif time_sig in ['9/8', '9/4']:
        return 'Compound Triple'
    elif time_sig in ['12/8', '12/4']:
        return 'Compound Quadruple'
    elif time_sig in ['5/4', '5/8', '7/8', '7/4']:
        return 'Irregular'
    else:
        return 'Other'

def get_composer_era(composer):
    """Determine a composer's musical era"""
    eras = {
        'Johann Sebastian Bach': 'Baroque',
        'George Frideric Handel': 'Baroque',
        'Antonio Vivaldi': 'Baroque',
        'Wolfgang Amadeus Mozart': 'Classical',
        'Ludwig van Beethoven': 'Classical',
        'Joseph Haydn': 'Classical',
        'Franz Schubert': 'Romantic',
        'Frédéric Chopin': 'Romantic',
        'Felix Mendelssohn': 'Romantic',
        'Johannes Brahms': 'Romantic',
        'Richard Wagner': 'Romantic',
        'Pyotr Ilyich Tchaikovsky': 'Romantic',
        'Claude Debussy': 'Impressionist',
        'Maurice Ravel': 'Impressionist',
        'Sergei Rachmaninoff': 'Late Romantic',
        'Igor Stravinsky': 'Modern',
        'Béla Bartók': 'Modern',
        'Giacomo Puccini': 'Romantic',
        'Gustav Mahler': 'Late Romantic',
        'Robert Schumann': 'Romantic',
        'Franz Liszt': 'Romantic',
        'Edvard Grieg': 'Romantic'
    }
    
    # Try exact match
    if composer in eras:
        return eras[composer]
    
    # Try partial match
    for known_composer, era in eras.items():
        if known_composer in composer or composer in known_composer:
            return era
    
    return 'Unknown'

def analyze_time_signatures(signatures):
    """Comprehensive analysis of time signatures"""
    # Count occurrences of each time signature
    time_sig_counts = Counter()
    composer_time_sigs = defaultdict(Counter)
    era_time_sigs = defaultdict(Counter)
    
    # Create dataframe for more detailed analysis
    if not signatures:
        return {
            'total_movements': 0,
            'unique_time_signatures': 0,
            'time_signature_counts': {},
            'composer_time_signatures': {},
            'era_time_signatures': {}
        }
    
    df = pd.DataFrame(signatures)
    
    # Add era information
    df['era'] = df['composer'].apply(get_composer_era)
    
    # Normalize time signatures
    df['normalized_time_signature'] = df['time_signature'].apply(normalize_time_signature)
    
    # Add time signature category
    df['category'] = df['normalized_time_signature'].apply(get_time_signature_category)
    
    # Extract numerator and denominator
    df['numerator'], df['denominator'] = zip(*df['normalized_time_signature'].apply(parse_time_signature))
    
    # Count occurrences
    for sig in signatures:
        time_sig = normalize_time_signature(sig['time_signature'])
        
        # Count overall
        time_sig_counts[time_sig] += 1
        
        # Count by composer
        composer_time_sigs[sig['composer']][time_sig] += 1
        
        # Count by era
        era = get_composer_era(sig['composer'])
        era_time_sigs[era][time_sig] += 1
    
    return {
        'total_movements': len(signatures),
        'unique_time_signatures': len(time_sig_counts),
        'time_signature_counts': dict(time_sig_counts.most_common()),
        'composer_time_signatures': {comp: dict(sigs) for comp, sigs in composer_time_sigs.items()},
        'era_time_signatures': {era: dict(sigs) for era, sigs in era_time_sigs.items()},
        'dataframe': df
    }

# Visualization functions
def create_time_signature_distribution_chart(analysis):
    """Create a bar chart of time signature distribution"""
    if not analysis['time_signature_counts']:
        return None
    
    # Get top 15 time signatures
    top_sigs = dict(sorted(analysis['time_signature_counts'].items(), 
                          key=lambda x: x[1], reverse=True)[:15])
    
    fig = px.bar(
        x=list(top_sigs.keys()),
        y=list(top_sigs.values()),
        labels={'x': 'Time Signature', 'y': 'Count'},
        title='Most Common Time Signatures',
        color=list(top_sigs.values()),
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title='Time Signature',
        yaxis_title='Number of Movements',
        coloraxis_showscale=False
    )
    
    return fig

def create_time_signature_by_era_chart(analysis):
    """Create a stacked bar chart of time signatures by era"""
    if 'dataframe' not in analysis or analysis['dataframe'].empty:
        return None
    
    df = analysis['dataframe']
    
    # Get top 6 time signatures
    top_sigs = list(dict(sorted(analysis['time_signature_counts'].items(), 
                               key=lambda x: x[1], reverse=True)[:6]).keys())
    
    # Filter to just these time signatures
    filtered_df = df[df['normalized_time_signature'].isin(top_sigs)]
    
    # Group by era and time signature
    era_counts = filtered_df.groupby(['era', 'normalized_time_signature']).size().reset_index(name='count')
    
    # Sort eras chronologically
    era_order = ['Baroque', 'Classical', 'Romantic', 'Late Romantic', 'Impressionist', 'Modern', 'Unknown']
    era_counts['era'] = pd.Categorical(era_counts['era'], categories=era_order, ordered=True)
    era_counts = era_counts.sort_values('era')
    
    fig = px.bar(
        era_counts,
        x='era',
        y='count',
        color='normalized_time_signature',
        title='Time Signatures by Musical Era',
        labels={'normalized_time_signature': 'Time Signature'},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        xaxis_title='Musical Era',
        yaxis_title='Number of Movements',
        legend_title='Time Signature'
    )
    
    return fig

def create_composer_heatmap(analysis, selected_composers=None):
    """Create a heatmap of time signatures used by composers"""
    if 'dataframe' not in analysis or analysis['dataframe'].empty:
        return None
    
    df = analysis['dataframe']
    
    # Filter to selected composers if provided
    if selected_composers and len(selected_composers) > 0:
        df = df[df['composer'].isin(selected_composers)]
    
    # Get top 10 composers by movement count
    top_composers = df['composer'].value_counts().nlargest(10).index.tolist()
    
    # Get top 10 time signatures
    top_sigs = df['normalized_time_signature'].value_counts().nlargest(10).index.tolist()
    
    # Create pivot table
    pivot_data = df[df['composer'].isin(top_composers) & 
                   df['normalized_time_signature'].isin(top_sigs)]
    
    pivot = pivot_data.pivot_table(
        index='composer',
        columns='normalized_time_signature',
        aggfunc='size',
        fill_value=0
    )
    
    # Sort composers by era and name
    composer_era = {composer: get_composer_era(composer) for composer in pivot.index}
    era_order = {'Baroque': 0, 'Classical': 1, 'Romantic': 2, 'Late Romantic': 3, 
                'Impressionist': 4, 'Modern': 5, 'Unknown': 6}
    
    pivot = pivot.reset_index()
    pivot['era'] = pivot['composer'].map(composer_era)
    pivot['era_order'] = pivot['era'].map(era_order)
    pivot = pivot.sort_values(['era_order', 'composer']).drop(['era', 'era_order'], axis=1)
    pivot = pivot.set_index('composer')
    
    # Create heatmap
    fig = px.imshow(
        pivot,
        labels=dict(x="Time Signature", y="Composer", color="Movement Count"),
        x=pivot.columns,
        y=pivot.index,
        color_continuous_scale='Viridis',
        aspect='auto',
        title='Time Signature Usage by Composer'
    )
    
    fig.update_layout(
        xaxis_title='Time Signature',
        yaxis_title='Composer'
    )
    
    return fig

def create_time_signature_categories_chart(analysis):
    """Create a pie chart of time signature categories"""
    if 'dataframe' not in analysis or analysis['dataframe'].empty:
        return None
    
    df = analysis['dataframe']
    
    # Count categories
    category_counts = df['category'].value_counts()
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title='Time Signature Categories',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    
    fig.update_layout(
        legend_title='Category'
    )
    
    return fig

def create_time_signature_correlations(analysis):
    """Create a visualization of correlations between time signatures"""
    if 'dataframe' not in analysis or analysis['dataframe'].empty:
        return None
    
    df = analysis['dataframe']
    
    # Get top 10 time signatures
    top_sigs = list(dict(sorted(analysis['time_signature_counts'].items(), 
                               key=lambda x: x[1], reverse=True)[:10]).keys())
    
    # For each composer, which time signatures do they use?
    composer_time_sigs = df.groupby('composer')['normalized_time_signature'].apply(set)
    
    # Create correlation matrix
    matrix = np.zeros((len(top_sigs), len(top_sigs)))
    
    for i, sig1 in enumerate(top_sigs):
        for j, sig2 in enumerate(top_sigs):
            # Count composers using both time signatures
            count = sum(1 for sigs in composer_time_sigs if sig1 in sigs and sig2 in sigs)
            matrix[i, j] = count
    
    # Normalize by dividing by diagonal values
    for i in range(len(top_sigs)):
        if matrix[i, i] > 0:
            matrix[:, i] = matrix[:, i] / matrix[i, i]
    
    # Create heatmap
    fig = px.imshow(
        matrix,
        labels=dict(x="Time Signature", y="Time Signature", color="Correlation"),
        x=top_sigs,
        y=top_sigs,
        color_continuous_scale='RdBu_r',
        zmin=0,
        zmax=1,
        title='Time Signature Co-occurrence (How often time signatures appear together in a composer\'s works)'
    )
    
    return fig

# Main application
def main():
    st.title("🎵 Classical Music Time Signature Analyzer")
    
    st.markdown("""
    This application analyzes time signatures in classical music compositions. 
    Upload your JSON database to explore patterns and distributions across composers and musical eras.
    """)

    # File uploader
    st.sidebar.header("Data Upload")
    uploaded_file = st.sidebar.file_uploader(
        "Upload JSON database of time signatures",
        type="json",
        help="Upload a JSON file in the format of imslp_scores_corrected.json"
    )
    
    use_example_data = st.sidebar.checkbox("Use example data", value=not uploaded_file)
    
    data = None
    
    if use_example_data:
        # Provide a path to the example JSON file
        example_path = 'imslp_scores_corrected.json'
        try:
            data = load_json_file(example_path)
            st.sidebar.success("Loaded example data")
        except:
            st.sidebar.error(f"Example data not found at {example_path}")
    elif uploaded_file:
        data = load_json_file(uploaded_file)
        if data:
            st.sidebar.success("Data loaded successfully")
    
    if not data:
        st.info("Please upload a JSON file with time signature data to begin analysis.")
        
        st.markdown("""
        ## Expected JSON Format
        
        The analyzer expects data in the following format:
        
        ```json
        {
          "Composer Name": {
            "Work Title": [
              {
                "movement": "Movement Title",
                "time_signature": "4/4"
              },
              ...
            ],
            ...
          },
          ...
        }
        ```
        """)
        return
    
    # Extract and analyze time signatures
    signatures = extract_time_signatures(data)
    analysis = analyze_time_signatures(signatures)
    
    if not signatures:
        st.error("No time signature data found in the uploaded file.")
        return
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "👩‍🎨 Composers", 
        "🕰️ Time Signatures",
        "🔍 Advanced Analysis"
    ])
    
    with tab1:
        st.header("Overview")
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{analysis['total_movements']:,}</div>
                <div class="metric-label">Total Movements</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{len(analysis['composer_time_signatures']):,}</div>
                <div class="metric-label">Composers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{analysis['unique_time_signatures']:,}</div>
                <div class="metric-label">Unique Time Signatures</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            most_common = max(analysis['time_signature_counts'].items(), key=lambda x: x[1])[0]
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-value">{most_common}</div>
                <div class="metric-label">Most Common</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.subheader("Time Signature Distribution")
        
        # Display time signature distribution chart
        fig1 = create_time_signature_distribution_chart(analysis)
        if fig1:
            st.plotly_chart(fig1, use_container_width=True)
        
        st.subheader("Time Signatures by Musical Era")
        
        # Display time signature by era chart
        fig2 = create_time_signature_by_era_chart(analysis)
        if fig2:
            st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("Time Signature Categories")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            fig3 = create_time_signature_categories_chart(analysis)
            if fig3:
                st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            if 'dataframe' in analysis:
                df = analysis['dataframe']
                category_desc = {
                    'Duple': 'Time signatures with 2 beats per measure (2/4, 2/2, 2/8)',
                    'Triple': 'Time signatures with 3 beats per measure (3/4, 3/8, 3/2)',
                    'Quadruple': 'Time signatures with 4 beats per measure (4/4, 4/8, 4/2)',
                    'Compound Duple': 'Time signatures with 2 groups of 3 beats (6/8, 6/4)',
                    'Compound Triple': 'Time signatures with 3 groups of 3 beats (9/8, 9/4)',
                    'Compound Quadruple': 'Time signatures with 4 groups of 3 beats (12/8, 12/4)',
                    'Irregular': 'Time signatures with irregular groupings (5/4, 7/8, etc.)',
                    'Other': 'Other unusual time signatures'
                }
                
                st.markdown("### Understanding Time Signature Categories")
                
                for category, desc in category_desc.items():
                    count = df[df['category'] == category].shape[0]
                    if count > 0:
                        percent = (count / len(df) * 100)
                        st.markdown(f"**{category}** ({count:,} movements, {percent:.1f}%): {desc}")
    
    with tab2:
        st.header("Composer Analysis")
        
        # Select composers to analyze
        all_composers = list(analysis['composer_time_signatures'].keys())
        default_composers = all_composers[:5] if len(all_composers) > 5 else all_composers
        
        selected_composers = st.multiselect(
            "Select composers to analyze",
            options=sorted(all_composers),
            default=default_composers
        )
        
        # Heatmap of composer time signature usage
        st.subheader("Time Signature Usage by Composer")
        fig4 = create_composer_heatmap(analysis, selected_composers if selected_composers else None)
        if fig4:
            st.plotly_chart(fig4, use_container_width=True)
        
        # Individual composer analysis
        if selected_composers:
            st.subheader("Individual Composer Analysis")
            
            composer_to_analyze = st.selectbox(
                "Select a composer for detailed analysis",
                options=selected_composers
            )
            
            if composer_to_analyze and 'dataframe' in analysis:
                df = analysis['dataframe']
                composer_df = df[df['composer'] == composer_to_analyze]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Composer's favorite time signatures
                    time_sig_counts = composer_df['normalized_time_signature'].value_counts()
                    
                    fig = px.pie(
                        values=time_sig_counts.values,
                        names=time_sig_counts.index,
                        title=f"Time Signatures Used by {composer_to_analyze}",
                        color_discrete_sequence=px.colors.qualitative.Bold
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Composer's time signature categories
                    category_counts = composer_df['category'].value_counts()
                    
                    fig = px.bar(
                        x=category_counts.index,
                        y=category_counts.values,
                        title=f"Time Signature Categories Used by {composer_to_analyze}",
                        color=category_counts.values,
                        color_continuous_scale='Viridis'
                    )
                    
                    fig.update_layout(
                        xaxis_title='Category',
                        yaxis_title='Count',
                        coloraxis_showscale=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # List of works by this composer
                st.subheader(f"Works by {composer_to_analyze}")
                
                works_df = composer_df.groupby('work').apply(
                    lambda x: pd.Series({
                        'Movements': len(x),
                        'Time Signatures': ', '.join(sorted(x['normalized_time_signature'].unique()))
                    })
                ).reset_index()
                
                st.dataframe(
                    works_df,
                    column_config={
                        "work": "Work Title",
                        "Movements": st.column_config.NumberColumn("Movements"),
                        "Time Signatures": "Time Signatures Used"
                    },
                    hide_index=True
                )
    
    with tab3:
        st.header("Time Signature Analysis")
        
        # Select time signatures to analyze
        all_time_sigs = list(analysis['time_signature_counts'].keys())
        top_sigs = sorted(all_time_sigs, key=lambda x: analysis['time_signature_counts'][x], reverse=True)[:5]
        
        selected_time_sigs = st.multiselect(
            "Select time signatures to analyze",
            options=sorted(all_time_sigs, key=lambda x: (len(x), x)),
            default=top_sigs
        )
        
        if selected_time_sigs and 'dataframe' in analysis:
            df = analysis['dataframe']
            
            # Compare selected time signatures
            st.subheader("Comparison of Selected Time Signatures")
            
            # Prepare data for comparison
            compare_data = []
            
            for sig in selected_time_sigs:
                sig_df = df[df['normalized_time_signature'] == sig]
                
                # Count by era
                era_counts = sig_df['era'].value_counts().to_dict()
                
                # Count by composer (top 3)
                composer_counts = sig_df['composer'].value_counts().nlargest(3).to_dict()
                top_composers = ", ".join(f"{c} ({n})" for c, n in composer_counts.items())
                
                compare_data.append({
                    'Time Signature': sig,
                    'Category': sig_df['category'].iloc[0] if not sig_df.empty else "Unknown",
                    'Movement Count': len(sig_df),
                    'Top Composers': top_composers,
                    'Baroque': era_counts.get('Baroque', 0),
                    'Classical': era_counts.get('Classical', 0),
                    'Romantic': era_counts.get('Romantic', 0),
                    'Late Romantic': era_counts.get('Late Romantic', 0),
                    'Impressionist': era_counts.get('Impressionist', 0),
                    'Modern': era_counts.get('Modern', 0)
                })
            
            compare_df = pd.DataFrame(compare_data)
            
            st.dataframe(
                compare_df,
                column_config={
                    "Time Signature": st.column_config.TextColumn("Time Signature"),
                    "Category": st.column_config.TextColumn("Category"),
                    "Movement Count": st.column_config.NumberColumn("Total Movements"),
                    "Top Composers": st.column_config.TextColumn("Top Composers"),
                    "Baroque": st.column_config.ProgressColumn("Baroque", format="%d", min_value=0),
                    "Classical": st.column_config.ProgressColumn("Classical", format="%d", min_value=0), 
                    "Romantic": st.column_config.ProgressColumn("Romantic", format="%d", min_value=0),
                    "Late Romantic": st.column_config.ProgressColumn("Late Romantic", format="%d", min_value=0),
                    "Impressionist": st.column_config.ProgressColumn("Impressionist", format="%d", min_value=0),
                    "Modern": st.column_config.ProgressColumn("Modern", format="%d", min_value=0)
                },
                hide_index=True
            )
            
            # Individual time signature analysis
            time_sig_to_analyze = st.selectbox(
                "Select a time signature for detailed analysis",
                options=selected_time_sigs
            )
            
            if time_sig_to_analyze:
                st.subheader(f"Analysis of {time_sig_to_analyze} Time Signature")
                
                sig_df = df[df['normalized_time_signature'] == time_sig_to_analyze]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Composers using this time signature
                    composer_counts = sig_df['composer'].value_counts().nlargest(10)
                    
                    fig = px.bar(
                        x=composer_counts.index,
                        y=composer_counts.values,
                        title=f"Top Composers Using {time_sig_to_analyze}",
                        color=composer_counts.values,
                        color_continuous_scale='Viridis'
                    )
                    
                    fig.update_layout(
                        xaxis_title='Composer',
                        yaxis_title='Count',
                        coloraxis_showscale=False,
                        xaxis_tickangle=-45
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Usage by era
                    era_counts = sig_df['era'].value_counts()
                    
                    # Sort eras chronologically
                    era_order = ['Baroque', 'Classical', 'Romantic', 'Late Romantic', 'Impressionist', 'Modern', 'Unknown']
                    era_counts = era_counts.reindex(era_order, fill_value=0)
                    
                    fig = px.pie(
                        values=era_counts.values,
                        names=era_counts.index,
                        title=f"Usage of {time_sig_to_analyze} by Era",
                        color_discrete_sequence=px.colors.qualitative.Bold
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # List of works using this time signature
                st.subheader(f"Works using {time_sig_to_analyze}")
                
                works_df = sig_df.groupby(['composer', 'work']).size().reset_index(name='movement_count')
                works_df = works_df.sort_values(['composer', 'movement_count'], ascending=[True, False])
                
                st.dataframe(
                    works_df,
                    column_config={
                        "composer": "Composer",
                        "work": "Work Title",
                        "movement_count": st.column_config.NumberColumn("Movements with this Time Signature")
                    },
                    hide_index=True
                )
    
    with tab4:
        st.header("Advanced Analysis")
        
        st.subheader("Time Signature Co-occurrence")
        st.markdown("""
        This heatmap shows how often different time signatures appear together in a composer's works.
        Higher values (darker colors) indicate time signatures that frequently co-occur.
        """)
        
        fig5 = create_time_signature_correlations(analysis)
        if fig5:
            st.plotly_chart(fig5, use_container_width=True)
        
        st.subheader("Time Signature Complexity by Era")
        
        if 'dataframe' in analysis:
            df = analysis['dataframe']
            
            # Calculate complexity scores
            def complexity_score(row):
                # Simple metric: higher numerator and denominator = more complex
                if pd.isna(row['numerator']) or pd.isna(row['denominator']):
                    return None
                
                # Base score from numerator
                num_score = 0
                if row['numerator'] in [2, 4]:
                    num_score = 1  # Common
                elif row['numerator'] in [3]:
                    num_score = 2  # Also common but slightly less so
                elif row['numerator'] in [6, 9, 12]:
                    num_score = 3  # Compound meters
                else:
                    num_score = 4  # Irregular meters
                
                # Modifier from denominator
                denom_score = 0
                if row['denominator'] in [4]:
                    denom_score = 1  # Common
                elif row['denominator'] in [2, 8]:
                    denom_score = 2  # Less common
                else:
                    denom_score = 3  # Unusual
                
                return num_score + denom_score
            
            df['complexity'] = df.apply(complexity_score, axis=1)
            
            # Group by era and calculate average complexity
            era_complexity = df.groupby('era')['complexity'].mean().reset_index()
            
            # Sort eras chronologically
            era_order = ['Baroque', 'Classical', 'Romantic', 'Late Romantic', 'Impressionist', 'Modern', 'Unknown']
            era_complexity['era'] = pd.Categorical(era_complexity['era'], categories=era_order, ordered=True)
            era_complexity = era_complexity.sort_values('era')
            
            # Create chart
            fig = px.bar(
                era_complexity,
                x='era',
                y='complexity',
                title='Average Time Signature Complexity by Era',
                color='complexity',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(
                xaxis_title='Musical Era',
                yaxis_title='Complexity Score',
                coloraxis_showscale=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **Complexity Score Explanation:**
            - Lower scores (1-2) indicate common time signatures like 2/4, 3/4, 4/4
            - Medium scores (3-4) indicate compound meters like 6/8, 9/8
            - Higher scores (5+) indicate irregular or unusual time signatures
            """)
        
        # Time signature evolution over time
        st.subheader("Time Signature Evolution")
        
        if 'dataframe' in analysis:
            df = analysis['dataframe']
            
            # Define rough time periods for each era
            era_periods = {
                'Baroque': (1600, 1750),
                'Classical': (1750, 1820),
                'Romantic': (1820, 1900),
                'Late Romantic': (1880, 1915),
                'Impressionist': (1875, 1925),
                'Modern': (1900, 1975),
                'Unknown': (1800, 1900)  # Default for unknown
            }
            
            # Assign midpoint year to each era
            df['period_midpoint'] = df['era'].map(lambda x: sum(era_periods[x])/2)
            
            # Get top 6 time signatures
            top_sigs = list(dict(sorted(analysis['time_signature_counts'].items(), 
                                      key=lambda x: x[1], reverse=True)[:6]).keys())
            
            # Filter to just these time signatures
            sig_df = df[df['normalized_time_signature'].isin(top_sigs)]
            
            # Group by era and time signature
            era_sig_counts = sig_df.groupby(['era', 'normalized_time_signature']).size().reset_index(name='count')
            
            # Add era midpoint
            era_sig_counts['period_midpoint'] = era_sig_counts['era'].map(lambda x: sum(era_periods[x])/2)
            
            # Create chart
            fig = px.line(
                era_sig_counts,
                x='period_midpoint',
                y='count',
                color='normalized_time_signature',
                title='Time Signature Usage Evolution',
                labels={'period_midpoint': 'Time Period', 'count': 'Number of Movements'},
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            
            fig.update_layout(
                xaxis_title='Time Period',
                yaxis_title='Number of Movements',
                legend_title='Time Signature',
                xaxis=dict(
                    tickmode='array',
                    tickvals=[1675, 1785, 1860, 1895, 1900, 1940],
                    ticktext=['Baroque', 'Classical', 'Romantic', 'Late Romantic', 'Impressionist', 'Modern']
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
            **Note:** The time periods are approximate and based on commonly accepted era boundaries.
            This is a simplified visualization of time signature evolution.
            """)
            
            # Custom query section
            st.subheader("Custom Query")
            
            st.markdown("""
            Explore the dataset with custom filters to find specific patterns or examples.
            """)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_composer = st.multiselect(
                    "Composer",
                    options=["All"] + sorted(df['composer'].unique().tolist()),
                    default=["All"]
                )
            
            with col2:
                filter_era = st.multiselect(
                    "Era",
                    options=["All"] + sorted(df['era'].unique().tolist()),
                    default=["All"]
                )
            
            with col3:
                filter_time_sig = st.multiselect(
                    "Time Signature",
                    options=["All"] + sorted(df['normalized_time_signature'].unique().tolist()),
                    default=["All"]
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if "All" not in filter_composer:
                filtered_df = filtered_df[filtered_df['composer'].isin(filter_composer)]
            
            if "All" not in filter_era:
                filtered_df = filtered_df[filtered_df['era'].isin(filter_era)]
            
            if "All" not in filter_time_sig:
                filtered_df = filtered_df[filtered_df['normalized_time_signature'].isin(filter_time_sig)]
            
            # Display results
            st.write(f"Found {len(filtered_df)} movements matching your criteria")
            
            if not filtered_df.empty:
                st.dataframe(
                    filtered_df[['composer', 'work', 'movement', 'normalized_time_signature', 'era']],
                    column_config={
                        "composer": "Composer",
                        "work": "Work Title",
                        "movement": "Movement",
                        "normalized_time_signature": "Time Signature",
                        "era": "Musical Era"
                    },
                    hide_index=True
                )

if __name__ == "__main__":
    main()
