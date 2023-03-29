import numpy as np
import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
#nltk.download('punkt') #need these for nltk to work
#nltk.download('stopwords')
#nltk.download('tagsets') #need for parts of speech tagging
#nltk.download('averaged_perceptron_tagger')
#nltk.download('wordnet')
#nltk.download('maxent_ne_chunker')
#nltk.download('words')

from summary_generation import get_summ_from_pretrained


#reads input text and returns lists of contained sentences and words
def read_data(input_text):
    data_sentences_tokenized = sent_tokenize(input_text) #split text into sentences
    data_words_tokenized = word_tokenize(input_text) #split text into words
    return data_sentences_tokenized, data_words_tokenized

#implementation of patent methodology, currently only returns a single sentence
def algo_1(input_text, sentence_resolution):
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
    weights_df = weights_df.T #transpose weights to match indexing of sentences dataframe
    '''maximize the weights to pick the sentence with the highest euclidean distance'''
    summary = [] #stores summary sentences
    '''calc distances of each sentence in sentences df using weights'''
    distances = []
    for sentence in weights_df:
        euclidean_distance = np.sqrt(np.sum(sentence**2))
        distances.append(euclidean_distance)
    '''get title for summary for storing in database'''
    title = np.asarray(sentence_df['sen_0'])
    title = title[title != np.array(None)]
    title = " ".join(title)
    '''calculate the best sentence i number of times where i = sentence_resolution'''
    for i in range(sentence_resolution): #get i number of sentences for the summary
        if len(summary) < len(distances): #check that there are enough sentence to populate i number of sentences
            max_distance = np.max(distances)
            index_max_dist = distances.index(max_distance)
            #select the sentence with the largest distance
            best_pick = np.asarray(sentence_df['sen_' + str(index_max_dist)])
            #remove any trailing None's for any sentence that isn't the longest
            best_pick = best_pick[best_pick != np.array(None)]
            best_pick = " ".join(best_pick)
            print(best_pick)
            summary.append(best_pick)
            #remove the best sentence to continue finding i best summary sentences
            distances[index_max_dist] = 0
    #use the first sentence in the text as a title

    return title, summary

#place holder for the next algorithm
def algo_2(input_text, sentence_resolution):
    '''determine which sentences are most relevant by using bags of words.
    This will create a dictionary of every meaningful word in the text and rate each sentence by how similar it is to the overall text.
    For example, a sentence containing "pancakes" is likely a better summary to a text about making pancakes than a sentence without the word "pancakes".'''
    sentences, words = read_data(input_text) #break text into sentences and total words
    sentences_word_tokenized = [word_tokenize(sentence) for sentence in sentences] #split each sentence into individual words

    stemmer = nltk.stem.SnowballStemmer('english', ignore_stopwords=True) #stemming attempts to remove tense and differentiate between words that may have the same root, but different meanings

    sentences_stemmed = [[stemmer.stem(word) for word in sentence] for sentence in sentences_word_tokenized] #stem each sentence in text
    words_stemmed = [stemmer.stem(word) for word in words] #stem each word in text

    #remove punctuation from stemmed words and sentences
    punctuation = ['.', ',', '!', '?', '...']
    for char in punctuation:
        while char in words_stemmed:
            words_stemmed.remove(char)
        for sentence in sentences_stemmed:
            while char in sentence:
                sentence.remove(char)

    total_bow = gen_bag_of_words(words_stemmed) #create histogram of each word in the entire text
    sentence_bows = [gen_bag_of_words(sentence) for sentence in sentences_stemmed] #create histogram for each word in each sentence
    print(total_bow, sentence_bows)
    title = sentences[0] #use first sentence for title used to store the summary in database

    bag_distances = [sum([total_bow[key] - sentence[key] if key in sentence.keys() else total_bow[key] for key in total_bow.keys()]) for sentence in sentence_bows] #calculate basic distance between histograms
    print(bag_distances)
    summary = [] #stores each sentence used in the summary
    for i in range(sentence_resolution):
        if len(bag_distances) > 0:
            best_sentence = bag_distances.index(min(bag_distances)) #calc index of best sentence
            summary.append(sentences[best_sentence])
            del bag_distances[best_sentence]
            del sentences[best_sentence]
    

    return title, summary

#generate bag of words for algo_2
def gen_bag_of_words(words: list):
    bow_dict = {} #bag of words for input; bag of words is a histogram that counts each occurance of a word in the text
    #print('words: ', words)

    for word in words: #loop through each word

        if word in bow_dict.keys(): #if the key exists iterate count by 1
            bow_dict[word] += 1
        else: #if key doesn't exist, add key to dict
            bow_dict[word] = 1

    return bow_dict


#controller for which algorithm to use
def generate_summary(input_text, algorithm_choice, sentence_resolution):
    if algorithm_choice == 0:
        title, total_summary = algo_1(input_text, sentence_resolution)
        best_summary = convert_summary(total_summary)
        return title, best_summary
    elif algorithm_choice == 1:
        title, best_summary = algo_2(input_text, sentence_resolution)
        best_summary = convert_summary(best_summary)
        return title, best_summary
    elif algorithm_choice == 2:
        #set title to be first sentence
        title = sent_tokenize(input_text)[0]
        #generate summary using pre-trained model
        best_summary = get_summ_from_pretrained("t5-large", input_text)
        #split into sentences and convert summary
        best_summary = convert_summary(sent_tokenize(best_summary))
        return title, best_summary

#converts the summary list into a single string
def convert_summary(best_summary):
    summary_string = ''
    for sentence in best_summary:
        summary_string += ('splitmehere' + sentence) #cat the summary into something easily splittable for use in show_summary.html
    return summary_string

#used for testing
def main():
    #test_text = """Muad'Dib learned rapidly because his first training was in how to learn. And the first lesson of all was the basic trust that he could learn. It's shocking to find how many people do not believe they can learn, and how many more believe learning to be difficult."""
    #test_text = "This This This, This This This. This This This, This, This This."
    test_text = "sentence one sentence. sentence two and. The third sentence sentence."
    title, best_summary = generate_summary(test_text, 1, 3)
    print(title, best_summary)


if __name__ == "__main__":
    main()