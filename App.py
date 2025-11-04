from flask import Flask, request, render_template_string
import nltk
import numpy as np
import networkx as nx
import urllib.request
import bs4 as BeautifulSoup
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance

nltk.download("stopwords")

app = Flask(__name__)

# Core functions
def sentence_similarity(S1, S2, stop_words=None):
    if stop_words is None:
        stop_words = []
    S1 = [w.lower() for w in S1]
    S2 = [w.lower() for w in S2]
    all_words = list(set(S1 + S2))
    v1 = [0] * len(all_words)
    v2 = [0] * len(all_words)
    for w in S1:
        if w not in stop_words:
            v1[all_words.index(w)] += 1
    for w in S2:
        if w not in stop_words:
            v2[all_words.index(w)] += 1
    return 1 - cosine_distance(v1, v2)


def build_similarity_matrix(sentences, stop_words):
    sim_matrix = np.zeros((len(sentences), len(sentences)))
    for i in range(len(sentences)):
        for j in range(len(sentences)):
            if i != j:
                sim_matrix[i][j] = sentence_similarity(sentences[i], sentences[j], stop_words)
    return sim_matrix


def fetch_article(url):
    article = urllib.request.urlopen(url)
    text = article.read()
    parsed = BeautifulSoup.BeautifulSoup(text, "lxml")
    paragraphs = parsed.find_all("p")
    content = " ".join([p.text for p in paragraphs])
    article = content.split(".")
    sentences = [s.replace("[^a-zA-Z]", " ").split(" ") for s in article if s.strip()]
    return sentences


def summarize(url):
    stop_words = stopwords.words("english")
    sentences = fetch_article(url)
    sim_matrix = build_similarity_matrix(sentences, stop_words)
    graph = nx.from_numpy_array(sim_matrix)
    scores = nx.pagerank(graph)
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    summary = ". ".join([" ".join(r[1]) for r in ranked_sentences[:5]])  # top 5 sentences
    return summary


# HTML template
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Text Summarizer</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 700px; margin: auto; padding: 40px; }
    input, button { padding: 10px; width: 100%; margin-top: 10px; }
    .summary { background: #f7f7f7; padding: 15px; border-radius: 8px; margin-top: 20px; }
  </style>
</head>
<body>
  <h1>Web Article Summarizer</h1>
  <form method="POST">
    <input name="url" placeholder="Enter article URL" required />
    <button type="submit">Summarize</button>
  </form>
  {% if summary %}
  <div class="summary">
    <h3>Summary:</h3>
    <p>{{ summary }}</p>
  </div>
  {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    summary = None
    if request.method == "POST":
        url = request.form["url"]
        try:
            summary = summarize(url)
        except Exception as e:
            summary = f"Error: {str(e)}"
    return render_template_string(TEMPLATE, summary=summary)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)￼Enter
