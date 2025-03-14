# Import necessary libraries
import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Set page configuration
st.set_page_config(
    page_title="Library Management System",
    page_icon=":books:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS styling
st.markdown(
    """
    <style>
        .main-header {
            font-size: 3rem !important;
            color: #1E3A8A;
            font-weight: 700;
            margin-bottom: 1rem;
            text-align: center;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }
        .sub-header {
            font-size: 1.8rem !important;
            color: #3B82F6;
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        .success-message {
            padding: 1rem;
            background-color: #ECFDF3;
            border-left: 5px solid #10B981;
            border-radius: 0.375rem;
        }
        .warning-message {
            padding: 1rem;
            background-color: #FEF3E2;
            border-left: 5px solid #F59E0B;
            border-radius: 0.375rem;
        }
        .book-card {
            background-color: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 5px solid #3B82F6;
            transition: transform 0.3s ease-in-out;
        }
        .book-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        }
        .read-badge {
            background-color: #ECFDF3;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .unread-badge {
            background-color: #FEF3E2;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .action-button {
            margin-right: 0.5rem;
        }
        .stButton>button {
            border-radius: 0.375rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Function to load Lottie animations from URL
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state variables
if "Library" not in st.session_state:
    st.session_state.Library = []

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "book_added" not in st.session_state:
    st.session_state.book_added = False

if "book_removed" not in st.session_state:
    st.session_state.book_removed = False

if "current_view" not in st.session_state:
    st.session_state.current_view = "library"

# Function to load the library data
def load_library():
    try:
        if os.path.exists("library.json"):
            with open("library.json", "r") as file:
                st.session_state.Library = json.load(file)
            return True
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

# save library data
def save_library():
    try:
        with open("library.json", "w") as file:
            json.dump(st.session_state.Library, file)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

#read book data
def read_book(title, author, publication_year, read_status):
    book = {
        "title": title,
        "author": author,
        "publication_year": publication_year,
        "read_status": read_status,
        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    st.session_state.Library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

# remove book
def remove_book(index):
    if 0 <= index < len(st.session_state.Library):
        del st.session_state.Library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

#search book
def search_book(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.Library:
        if search_by == "Title" and search_term in book["title"].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book["author"].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book["genre"].lower():
            results.append(book)
    st.session_state.search_results = results

#calculate library stats
def get_library_stats():
    total_books = len(st.session_state.Library)
    read_books = sum(1 for book in st.session_state.Library if book["read_status"])
    percent_read = round((read_books / total_books) * 100) if total_books > 0 else 0

    genres = {}
    authors = {}
    decades = {}

    for book in st.session_state.Library:
        if book["genre"] in genres:
            genres[book["genre"]] += 1
        else:
            genres[book["genre"]] = 1

        if book["author"] in authors:
            authors[book["author"]] += 1
        else:
            authors[book["author"]] = 1

        decade = (book["publication_year"] // 10) * 10
        if decade in decades:
            decades[decade] += 1
        else:
            decades[decade] = 1
    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))

    return {
        "total_books": total_books,
        "read_books": read_books,
        "percent_read": percent_read,
        "genres": genres,
        "authors": authors,
        "decades": decades,
    }

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
# Display the library
def display_library():
    if not st.session_state.Library:
        st.info("Your library is empty.")
        return
    
    for index, book in enumerate(st.session_state.Library):
        st.markdown(
            f"""
            <div class="book-card">
                <h3>{book['title']}</h3>
                <p><b>Author:</b> {book['author']}</p>
                <p><b>Published:</b> {book['publication_year']}</p>
                <p><b>Status:</b> {'Read' if book['read_status'] else 'Unread'}</p>
                <button class="read-badge">{'Read' if book['read_status'] else 'Unread'}</button>
                <button class="action-button" onclick="remove_book({index})">Remove</button>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Visualize library stats with Plotly
def visualize_library_stats():
    stats = get_library_stats()
    
    # Total books visualization
    st.subheader("Total Books and Read Percentage")
    fig1 = px.pie(
        names=["Read", "Unread"],
        values=[stats["read_books"], stats["total_books"] - stats["read_books"]],
        title="Read vs Unread Books",
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Genres visualization
    st.subheader("Books by Genre")
    if stats["genres"]:
        fig2 = px.bar(
            x=list(stats["genres"].keys()),
            y=list(stats["genres"].values()),
            title="Books by Genre",
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No genres to display.")

    # Decades visualization
    st.subheader("Books by Decade")
    if stats["decades"]:
        fig3 = go.Figure(data=[
            go.Bar(
                x=list(stats["decades"].keys()),
                y=list(stats["decades"].values()),
                marker=dict(color="purple"),
            )
        ])
        fig3.update_layout(
            title="Books by Decade",
            xaxis_title="Decade",
            yaxis_title="Number of Books",
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No decade data to display.")

# Main application view
def main():
    st.title(":books: Library Management System")
    st.write("Manage your book collection effortlessly!")
    
    # Navigation buttons
    if st.button("View Library"):
        st.session_state.current_view = "library"
    elif st.button("Add Book"):
        st.session_state.current_view = "add"
    elif st.button("Search Library"):
        st.session_state.current_view = "search"
    elif st.button("Library Stats"):
        st.session_state.current_view = "stats"

    # Render the selected view
    if st.session_state.current_view == "library":
        st.header("Your Library")
        display_library()
    elif st.session_state.current_view == "add":
        st.header("Add a New Book")
        with st.form(key="add_book_form"):
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            publication_year = st.number_input("Publication Year", min_value=0, step=1)
            genre = st.text_input("Genre")
            read_status = st.radio("Read Status", options=[True, False], format_func=lambda x: "Read" if x else "Unread")
            submit = st.form_submit_button("Add Book")
        if submit:
            read_book(title, author, publication_year, read_status)
            st.success("Book added successfully!")
    elif st.session_state.current_view == "search":
        st.header("Search the Library")
        search_term = st.text_input("Search Term")
        search_by = st.radio("Search By", options=["Title", "Author", "Genre"])
        if st.button("Search"):
            search_book(search_term, search_by)
        if st.session_state.search_results:
            for book in st.session_state.search_results:
                st.markdown(
                    f"""
                    <div class="book-card">
                        <h3>{book['title']}</h3>
                        <p><b>Author:</b> {book['author']}</p>
                        <p><b>Published:</b> {book['publication_year']}</p>
                        <p><b>Status:</b> {'Read' if book['read_status'] else 'Unread'}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    elif st.session_state.current_view == "stats":
        st.header("Library Statistics")
        visualize_library_stats()

if __name__ == "__main__":
    load_library()
    main()








