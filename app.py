import streamlit as st
from instagram_scraper import scrape_instagram, save_to_csv

st.title("Instagram Hashtag Scraper")

# Pre-fill the email and password fields
email = "username"  # Your Instagram email
password = "password"  # Your Instagram password

hashtag = st.text_input("Hashtag to Search for:")

if st.button("Scrape"):
    if hashtag:
        with st.spinner("Scraping data..."):
            try:
                data = scrape_instagram(email, password, hashtag.strip("#"))
                save_to_csv(data)
                st.success("Scraping completed successfully!")
                st.write(data)
                st.download_button(
                    label="Download CSV",
                    data=open('scraped_data.csv').read(),
                    file_name='scraped_data.csv',
                    mime='text/csv'
                )
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a hashtag to search for.")
