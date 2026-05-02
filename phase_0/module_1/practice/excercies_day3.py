# Exercise 5 — Dictionaries (Grouping)
words = ["apple", "ant", "banana", "bat", "cat"]
grouped_words = {}
for word in words:
    grouped_words.setdefault(word[0], []).append(word)
print(grouped_words)
