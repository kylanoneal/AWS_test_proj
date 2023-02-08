import numpy as np
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

#reads input text and returns lists of contained sentences and words
def read_data(input_text):
    data_sentences_tokenized = sent_tokenize(input_text) #split text into sentences
    data_words_tokenized = word_tokenize(input_text) #split text into words
    return data_sentences_tokenized, data_words_tokenized

#implementation of patent methodology, currently only returns a single sentence
def algo_1(input_text):
    '''create a dataframe of the sentences in input_text
       Columns are sentences, rows are words'''
    sentences, words = read_data(input_text)
    col_names = ["sen_" + str(i) for i in range(len(sentences))]
    words = [sentence.strip().split(" ") for sentence in sentences]
    sentence_df = pd.DataFrame(data=words)
    sentence_df = sentence_df.T
    sentence_df.columns = col_names
    '''weight dataframe used to grade each sentence'''
    weights_df = sentence_df.copy().values
    for column in range(len(weights_df)):
        for row in range(len(weights_df[column])):
            if weights_df[column,row] == None:
                weights_df[column,row] = 0
            else:
                weights_df[column,row] = np.exp(-1 * column)
    '''maximize the weights to pick the sentence with the highest euclidean distance'''
    distances = []
    for sentence in weights_df.T:
        euclidean_distance = np.sqrt(np.sum(sentence**2))
        distances.append(euclidean_distance)
    max_distance = np.max(distances)
    index_max_dist = distances.index(max_distance)
    #select the sentence with the largest distance
    best_pick = " ".join(np.asarray(sentence_df['sen_' + str(index_max_dist)]))
    #use the first sentence in the text as a title
    title = np.asarray(sentence_df['sen_0'])
    title = title[title != np.array(None)]
    title = " ".join(title)
    return title, best_pick

#used for testing
'''def main():
    test_text = """
 Muad'Dib learned rapidly because his first training was in how to learn. And the first lesson of all was the basic trust that he could learn. It's shocking to find how many people do not believe they can learn, and how many more believe learning to be difficult."""
    algo_1(test_text)

if __name__ == "__main__":
    main()'''