import streamlit as st
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

# Streamlit app setup
st.title("Social Network Analysis Dashboard")

# Upload edge list files for both datasets with timestamps
uploaded_file_1 = st.file_uploader("Upload 'Justin Bieber' edge list CSV with timestamps", type="csv", key="jb")
uploaded_file_2 = st.file_uploader("Upload 'One Direction' edge list CSV with timestamps", type="csv", key="od")

# Check if both files are uploaded
if uploaded_file_1 and uploaded_file_2:
    # Load the datasets
    df_bieber = pd.read_csv(uploaded_file_1)
    df_onedirection = pd.read_csv(uploaded_file_2)

    # Ensure both CSV files have the required columns
    required_columns = {'Node1', 'Node2', 'Timestamp'}
    if required_columns.issubset(df_bieber.columns) and required_columns.issubset(df_onedirection.columns):
        
        # Function to calculate and display centralities for a dataset
        def display_centralities(df, dataset_name):
            G_full = nx.from_pandas_edgelist(df, 'Node1', 'Node2', create_using=nx.Graph())
            st.subheader(f"{dataset_name} Network Analysis for the Entire Dataset")
            st.write(f"**Total Number of nodes:** {G_full.number_of_nodes()}")
            st.write(f"**Total Number of edges:** {G_full.number_of_edges()}")

            # Centrality Calculations
            st.subheader(f"Top 10 Nodes by Centrality Measures (for {dataset_name} entire dataset)")
            
            # Degree Centrality
            odc = nx.degree_centrality(G_full)
            top_odc = sorted(odc.items(), key=lambda item: item[1], reverse=True)[:10]
            df_odc = pd.DataFrame(top_odc, columns=['Node', 'Degree Centrality'])
            st.write("**Degree Centrality:**")
            st.dataframe(df_odc)

            # Closeness Centrality
            occ = nx.closeness_centrality(G_full)
            top_occ = sorted(occ.items(), key=lambda item: item[1], reverse=True)[:10]
            df_occ = pd.DataFrame(top_occ, columns=['Node', 'Closeness Centrality'])
            st.write("**Closeness Centrality:**")
            st.dataframe(df_occ)

            # Betweenness Centrality
            obc = nx.betweenness_centrality(G_full)
            top_obc = sorted(obc.items(), key=lambda item: item[1], reverse=True)[:10]
            df_obc = pd.DataFrame(top_obc, columns=['Node', 'Betweenness Centrality'])
            st.write("**Betweenness Centrality:**")
            st.dataframe(df_obc)

            # Eigenvector Centrality
            try:
                oec = nx.eigenvector_centrality(G_full, max_iter=1000, tol=1e-6)
                top_oec = sorted(oec.items(), key=lambda item: item[1], reverse=True)[:10]
                df_oec = pd.DataFrame(top_oec, columns=['Node', 'Eigenvector Centrality'])
                st.write("**Eigenvector Centrality:**")
                st.dataframe(df_oec)
            except nx.PowerIterationFailedConvergence:
                st.write("**Eigenvector Centrality:** Could not compute eigenvector centrality for this network.")

        # Display centralities for both datasets
        display_centralities(df_bieber, "Justin Bieber")
        display_centralities(df_onedirection, "One Direction")

        # Dataset selection for temporal analysis
        dataset_choice = st.selectbox("Select Dataset for Temporal Analysis", ["Justin Bieber", "One Direction"])
        df = df_bieber if dataset_choice == "Justin Bieber" else df_onedirection

        # Convert timestamp to datetime and group by week
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')
        df['year_week'] = df['Timestamp'].dt.to_period('W')
        
        # Group data by each week
        weekly_groups = df.groupby('year_week')

        # Plot each week's network in a single window
        st.subheader(f"Weekly Network Evolution for {dataset_choice}")
        fig, axes = plt.subplots(nrows=len(weekly_groups), figsize=(8, 4 * len(weekly_groups)))
        
        # Loop through each week's data and plot its network
        for i, (week, week_data) in enumerate(weekly_groups):
            G_week = nx.from_pandas_edgelist(week_data, 'Node1', 'Node2', create_using=nx.Graph())
            pos = nx.spring_layout(G_week)
            ax = axes[i] if len(weekly_groups) > 1 else axes  # Adjust if there's only one subplot
            nx.draw_networkx_nodes(G_week, pos, node_size=50, node_color='blue', alpha=0.7, ax=ax)
            nx.draw_networkx_edges(G_week, pos, edge_color='gray', alpha=0.5, ax=ax)
            ax.set_title(f'Network for Week: {week}')
            ax.axis('off')
        
        # Show all the weekly network plots
        st.pyplot(fig)
        
    else:
        st.error("Both CSV files must have 'Node1', 'Node2', and 'Timestamp' columns.")
else:
    st.info("Please upload both CSV files to start the analysis.")
