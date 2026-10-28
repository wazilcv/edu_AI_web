import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download VADER lexicon if not already installed
nltk.download('vader_lexicon')


def classify_with_vader(text):
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(text)
    print("Scr : ", scores)

    # Compound score ranges from -1 (most negative) to 1 (most positive)
    # compound = scores['compound']
    #
    # if compound >= 0.05:
    #     return "positive"
    # elif compound <= -0.05:
    #     return "negative"
    # else:
    #     return "neutral"

    if scores['pos'] > scores['neg']  and scores['pos'] > scores['neu']:
        return "positive"
    elif scores['neg'] > scores['pos']  and scores['neg'] > scores['neu']:
        return "negative"
    else:
        if scores['pos'] > scores['neg']:
            return "positive"
        else:
            return 'negative'


# Example usage
# texts = [
#     "I was not able to understand this unit. ",
#     "The way you taught this portion was great. I understood the whole portion",
#     "It was very helpful that you provided with short notes which helped me a lot for the exams"
# ]
#
# for text in texts:
#     sentiment = classify_with_vader(text)
#     print(f"Text: {text}")
#     print(f"Sentiment: {sentiment}\n")