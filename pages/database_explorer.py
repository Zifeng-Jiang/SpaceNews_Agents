import streamlit as st
import pandas as pd
from db_manager import NewsDatabase
import os

st.set_page_config(page_icon="📰", page_title="SpaceNews Database")
st.title('📰 SpaceNews Database Explorer')

# Initialize database connection
try:
    db = NewsDatabase()
    if db.connect():
        st.success("✅ Connected to MySQL database")
        
        # Sidebar for filtering
        st.sidebar.header("Filters")
        data_type = st.sidebar.radio("Select data type:", ["Articles", "Events"])
        
        if data_type == "Articles":
            # First check if we have any articles at all
            db.cursor.execute("SELECT COUNT(*) as count FROM articles")
            total_articles = db.cursor.fetchone()['count']
            st.sidebar.write(f"Total articles in database: {total_articles}")
            
            if total_articles > 0:
                # Fetch unique regions for filtering
                db.cursor.execute("SELECT DISTINCT region FROM articles WHERE region IS NOT NULL AND region != ''")
                region_results = db.cursor.fetchall()
                regions = [r['region'] for r in region_results]
                regions.insert(0, "All Regions")
                
                # Fetch unique tags for filtering
                db.cursor.execute("SELECT DISTINCT tag FROM articles WHERE tag IS NOT NULL AND tag != ''")
                tag_results = db.cursor.fetchall()
                tags = [t['tag'] for t in tag_results]
                tags.insert(0, "All Tags")
                
                # Region and tag filters
                selected_region = st.sidebar.selectbox("Filter by Region:", regions)
                selected_tag = st.sidebar.selectbox("Filter by Tag:", tags)
                
                # Build query with filters
                query = "SELECT * FROM articles WHERE 1=1"
                params = []
                
                if selected_region != "All Regions":
                    query += " AND region = %s"
                    params.append(selected_region)
                
                if selected_tag != "All Tags":
                    query += " AND tag = %s"
                    params.append(selected_tag)
                
                query += " ORDER BY created_at DESC LIMIT 100"
                
                # Execute query
                db.cursor.execute(query, params)
                articles = db.cursor.fetchall()
                
                # Display articles
                st.header(f"Articles ({len(articles)} results)")
                
                if articles:
                    # Convert to DataFrame for better display
                    df = pd.DataFrame(articles)
                    # Limit content display length for table view
                    df_display = df.copy()
                    if 'content' in df_display.columns:
                        df_display['content'] = df_display['content'].apply(lambda x: x[:200] + '...' if x and len(str(x)) > 200 else x)
                    if 'abstract' in df_display.columns:
                        df_display['abstract'] = df_display['abstract'].apply(lambda x: x[:200] + '...' if x and len(str(x)) > 200 else x)
                    
                    # Allow user to select which columns to display
                    all_columns = df_display.columns.tolist()
                    default_columns = ['id', 'title', 'date', 'region', 'tag', 'created_at']
                    default_columns = [col for col in default_columns if col in all_columns]
                    
                    selected_columns = st.multiselect(
                        "Select columns to display:",
                        all_columns,
                        default=default_columns
                    )
                    
                    if selected_columns:
                        st.dataframe(df_display[selected_columns], use_container_width=True)
                    else:
                        st.dataframe(df_display, use_container_width=True)
                    
                    # Download as CSV
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download data as CSV",
                        csv,
                        "articles.csv",
                        "text/csv",
                        key='download-csv'
                    )
                    
                    # Show detailed view of selected article
                    st.subheader("Article Details")
                    if len(df) > 0:
                        article_ids = df['id'].tolist()
                        selected_id = st.selectbox("Select an article to view details:", article_ids)
                        
                        if selected_id:
                            # Get full article details
                            db.cursor.execute("SELECT * FROM articles WHERE id = %s", (selected_id,))
                            article = db.cursor.fetchone()
                            
                            if article:
                                st.markdown(f"### {article['title']}")
                                st.markdown(f"**Region:** {article['region']}")
                                st.markdown(f"**Date:** {article['date']}")
                                st.markdown(f"**Tag:** {article['tag']}")
                                st.markdown(f"**Link:** [{article['link']}]({article['link']})")
                                
                                with st.expander("Abstract"):
                                    st.markdown(article['abstract'] or "No abstract available")
                                
                                with st.expander("Full Content"):
                                    st.markdown(article['content'] or "No content available")
                else:
                    st.info("No articles found with the selected filters.")
            else:
                st.warning("No articles found in the database yet. Run the news collector first!")
            
        else:  # Events section
            # First check if we have any events
            db.cursor.execute("SELECT COUNT(*) as count FROM events")
            total_events = db.cursor.fetchone()['count']
            st.sidebar.write(f"Total events in database: {total_events}")
            
            if total_events > 0:
                # Build query for events
                query = "SELECT * FROM events ORDER BY created_at DESC LIMIT 100"
                
                # Execute query
                db.cursor.execute(query)
                events = db.cursor.fetchall()
                
                # Display events
                st.header(f"Events ({len(events)} results)")
                
                if events:
                    # Convert to DataFrame for better display
                    df = pd.DataFrame(events)
                    df_display = df.copy()
                    # Limit summary display length
                    if 'summary' in df_display.columns:
                        df_display['summary'] = df_display['summary'].apply(lambda x: x[:200] + '...' if x and len(str(x)) > 200 else x)
                    
                    # Allow user to select which columns to display
                    all_columns = df_display.columns.tolist()
                    default_columns = ['id', 'title', 'date', 'address', 'created_at']
                    default_columns = [col for col in default_columns if col in all_columns]
                    
                    selected_columns = st.multiselect(
                        "Select columns to display:",
                        all_columns,
                        default=default_columns,
                        key='events_columns'
                    )
                    
                    if selected_columns:
                        st.dataframe(df_display[selected_columns], use_container_width=True)
                    else:
                        st.dataframe(df_display, use_container_width=True)
                    
                    # Download as CSV
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download data as CSV",
                        csv,
                        "events.csv",
                        "text/csv",
                        key='download-events-csv'
                    )
                    
                    # Show detailed view of selected event
                    st.subheader("Event Details")
                    if len(df) > 0:
                        event_ids = df['id'].tolist()
                        selected_id = st.selectbox("Select an event to view details:", event_ids, key='event_selector')
                        
                        if selected_id:
                            # Get full event details
                            db.cursor.execute("SELECT * FROM events WHERE id = %s", (selected_id,))
                            event = db.cursor.fetchone()
                            
                            if event:
                                st.markdown(f"### {event['title']}")
                                st.markdown(f"**Date:** {event['date']}")
                                st.markdown(f"**Address:** {event['address']}")
                                st.markdown(f"**Link:** [{event['link']}]({event['link']})")
                                
                                with st.expander("Full Summary"):
                                    st.markdown(event['summary'] or "No summary available")
                else:
                    st.info("No events found.")
            else:
                st.warning("No events found in the database yet. Run the news collector first!")
        
        # Close database connection
        db.close()
    else:
        st.error("❌ Failed to connect to MySQL database")
except Exception as e:
    st.error(f"❌ Database error: {str(e)}")
    import traceback
    st.error(f"Error details: {traceback.format_exc()}")
