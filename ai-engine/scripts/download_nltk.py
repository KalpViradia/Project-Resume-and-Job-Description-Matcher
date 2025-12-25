import nltk
try:
    nltk.download('punkt')
    nltk.download('punkt_tab')
    print("NLTK data downloaded successfully.")
except Exception as e:
    print(f"Error downloading NLTK data: {e}")
