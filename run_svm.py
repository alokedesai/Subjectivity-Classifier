"""
Main file to create feature set from our corpus.
Feature set is written to an svm file in the proper format for running SVM Light
We then run SVM Light and print out results

authors: Aloke Desai and Garrett Wells
"""

import math
import sys
import subprocess
from nltk.stem.porter import *
import random

class FeatureMaker:
    def __init__(self, documents):
        """
        set up variables
        :param documents: list of documents
            formatted as a list of tuples [(label, body)]
            where the body is a list of words stripped of stopwords
        """
        self.document_list = documents

        self.feature_count = 1
        self.features = {}
        self.feature_mapping = {}
        self.idf = {}
        self.label_mapping = {}
        self.objective_features = {}
        self.subjective_features = {}
        self.num_objective = 0
        self.num_subjective = 0
        self.selected_features = []

        self.calculate_idf()

    def calculate_idf(self):
        """Calculate idf for corpus."""
        for document in self.document_list:
            label, text = document
            words_in_text = set()  # used for keeping track of words already seen in the document
            for word in text:
                if word not in words_in_text:
                    self.idf[word] = self.idf.get(word,0) +1
                    words_in_text.add(word)

            # calculate num objective or subjective
            if label == "1":
                self.num_objective += 1
            else:
                self.num_subjective += 1

        # update idf dictionary to be idf
        for word in self.idf.keys():
            self.idf[word] = math.log10(len(self.document_list) / float(self.idf[word]))

    def tf_idf(self, text):
        """
        Calculates tf-idf values for an article
        text: article body as list of words
        returns: tf-idf values in a dictionary
        """
        counts = unigram_counts(text)
        for word in counts:
            counts[word] *= self.idf[word]
        normalize(counts)
        return counts

    def add_feature(self, feature_function):
        """
        Adds a new feature to the feature dictioanry
        :param feature_function: a function to calculate a feature, such as
            tf-idf or unigram counts
        :return: void
        """
        document_id = 0
        for document in self.document_list:
            label, text = document
            self.label_mapping[document_id] = label
            feature_vector = feature_function(text)

            for key in feature_vector.keys():

                # get feature number
                if key not in self.feature_mapping:
                    self.feature_mapping[key] = self.feature_count
                    feature_number = self.feature_count
                    self.feature_count += 1
                else:
                    feature_number = self.feature_mapping[key]

                # add feature to dictionary
                document_features = self.features.get(document_id, {})
                document_features[feature_number] = feature_vector[key]
                self.features[document_id] = document_features

                # mutual information bullshit
                if label == "1":
                    self.objective_features[key] = self.objective_features.get(key, 0) + 1
                else:
                    self.subjective_features[key] = self.subjective_features.get(key, 0) + 1

            document_id += 1

    def print_feature_mapping(self, feature_file_path):
        """
        writes feature mapping dictionary to file
        :param feature_file_path: filepath
        :return: void
        """
        feature_file = open(feature_file_path, "w")
        for feature, feature_number in sorted(self.feature_mapping.items(), key=lambda f:f[1]):
            out_string = "%d\t%s\n" % (feature_number, str(feature))
            feature_file.write(out_string)
        feature_file.close()

    def print_svm_file(self, svm_file_path):
        """
        writes feature dictionary to an svm file, formatted properly
        :param svm_file_path: filepath of svm file
        :return: void
        """
        svm_file = open(svm_file_path, "w")
        for document_id in self.features.keys():
            label = self.label_mapping[document_id]
            output_string = str(label)
            sorted_features = self.features[document_id].items()
            sorted_features.sort(key=lambda f: f[0])
            for feature_number, feature_weight in sorted_features:
                if not self.selected_features or feature_number in self.selected_features:
                    if int(feature_weight) == float(feature_weight):
                        output_string += " %d:%d" % (feature_number, feature_weight)
                    else:
                        output_string += " %d:%.4f" % (feature_number, feature_weight)
            svm_file.write(output_string)
            svm_file.write("\n")
        svm_file.close()

    def feature_selection(self, num_features = None, print_features = False):
        """
        Calculates mutual information for a feature and performs feature selection on the best features
        :param num_features: how many top features to select
        :param print_features: whether to print out top features
        :return: void
        """
        self.word_frequency = {"1": self.objective_features, "-1": self.subjective_features}
        num_documents = float(self.num_objective + self.num_subjective)

        mutual_information = {}

        # compute mutual information
        for word in self.feature_mapping:
            objective_count = self.word_frequency["1"].get(word, 0)
            objective_count = objective_count if objective_count != 0 else 1

            subjective_count = self.word_frequency["-1"].get(word, 0)
            subjective_count = subjective_count if subjective_count != 0 else 1

            docs_with_word = subjective_count + objective_count
            docs_without_word = num_documents - docs_with_word

            first = (objective_count / num_documents) * math.log(((num_documents * objective_count)/ float(docs_with_word*self.num_objective)),2)
            second = ((self.num_objective - objective_count) / num_documents) * math.log(((num_documents * (self.num_objective - objective_count)) / float(docs_without_word*self.num_objective)), 2)

            third = (subjective_count / num_documents) * math.log(((num_documents * subjective_count) / float(docs_with_word * self.num_subjective)), 2)
            fourth = ((self.num_subjective - subjective_count) / num_documents) * math.log(((num_documents * (self.num_subjective - subjective_count)) / float(docs_without_word * self.num_subjective)), 2)

            mutual_information[word] = first + second + third + fourth

        # convert mutual info to tuple list and sort
        mutual_info_tuple = [(k,v) for k,v in mutual_information.iteritems()]
        mutual_info_tuple = sorted(mutual_info_tuple, key= lambda x: x[1], reverse=True)

        if num_features:
            self.selected_features = [self.feature_mapping[x[0]] for x in mutual_info_tuple[:num_features]]
        else:
            self.selected_features = [self.feature_mapping[x[0]] for x in mutual_info_tuple]

        # prints out top 100 features
        if print_features:
            for feature, prob in mutual_info_tuple[:30]:
                print "%s\t%.4f" % (feature, prob)


stemmer = PorterStemmer()


def unigram_counts(text):
    """
    Calcualtes unigram counts for a document
    :param text: document
    :return: dictionary of counts
    """
    counts = {}
    for word in text:
        counts[word] = counts.get(word,0) + 1
    return counts


def unigram_present(text):
    """
    Calcualtes unigram occurrence counts for a document
    :param text: document
    :return: dictionary of counts
    """
    counts = {}
    for word in text:
        counts[word] = 1
    return counts


def unigram_probs(text):
    """
    Calculates unigram probabilities for a document
    :param text: document
    :return: dictionary of probabilities
    """
    counts = unigram_counts(text)
    for word in counts:
        counts[word] /= float(len(text))
    return counts


def bigram_prob(text):
    """
    Calculates bigram probabilities for a document
    :param text: document
    :return: dictionary of probabilities
    """
    counts = bigram_counts(text)
    num_bigrams = sum(counts.values())

    for word in counts:
        counts[word] /= float(num_bigrams)
    return counts


def bigram_counts(text):
    """
    Calculates bigram counts for a document
    :param text: document
    :return: dictionary of counts
    """
    counts = {}
    for i in xrange(len(text)-1):
        current = text[i]
        next = text[i+1]
        tpl = (current, next)
        counts[tpl] = counts.get(tpl, 0) + 1
    return counts


def trigram_counts(text):
    """
    Calculates trigram counts for a document
    :param text: document
    :return: dictionary of counts
    """
    counts = {}
    for i in range(len(text) - 2):
        first = text[i]
        second = text[i+1]
        third = text[i+2]
        tpl = (first, second, third)
        counts[tpl] = counts.get(tpl, 0) + 1
    return counts


def bigram_present(text):
    """
    Calculates bigram occurrence counts for a document
    :param text: document
    :return: dictionary of counts
    """
    counts = {}
    for i in xrange(len(text)-1):
        current = text[i]
        next = text[i+1]
        tpl = (current, next)
        counts[tpl] = 1
    return counts


def trigram_present(text):
    """
    Calculates trigram occurrence counts for a document
    :param text: document
    :return: dictionary of counts
    """
    counts = {}
    for i in range(len(text) - 2):
        first = text[i]
        second = text[i+1]
        third = text[i+2]
        tpl = (first, second, third)
        counts[tpl] = 1
    return counts


def divide(svm_file):
    """
    divides an svm file into training and testing files
    :param svm_file: filepath to svm file
    :return:
    """
    in_file = open(svm_file, "r").readlines()

    test = len(in_file)/10
    train = 9*test

    test_lines = in_file[:test]
    train_lines = in_file[-train:]

    test_file = open("test.svm", "w")
    train_file = open("train.svm", "w")

    test_file.writelines(test_lines)
    train_file.writelines(train_lines)


def normalize(vector):
    """
    length normalize a feature vector
    :param vector: dictionary of features
    :return: void
    """
    total = 0
    for key in vector:
        total += vector[key]**2
    for key in vector:
        vector[key] /= float(total)


def run_svm_light(svm_file):
    """
    run svm light on our training and testing data
    :param svm_file: filepath of svm file
    :return: accuracy, precision and recall as a string
    """
    divide(svm_file)
    subprocess.check_output(["./svm_learn", "train.svm", "model.txt"])
    result = subprocess.check_output(["./svm_classify", "test.svm", "model.txt", "result.out"])
    return "\n".join(result.split("\n")[3:5])


def stem(text):
    """
    run porter stemmer on a text
    :param text: text
    :return: stemmed text
    """
    return [stemmer.stem(word) for word in text]


def shuffle(svm_file):
    """
    randomly shuffle svm fie
    :param svm_file: svm filepath
    :return: void
    """
    with open(svm_file, "r") as source:
        data = [(random.random(), line) for line in source]
    data.sort()
    with open(svm_file, "w") as target:
        for _, line in data:
            target.write(line)


def main():
    to_stem = False
    #read stoplist
    stop_list = open("stop.txt").readlines()
    stop_list = [e.strip() for e in stop_list]

    # read and preprocess data
    data = []
    data_file = open("data/data.txt", "r")

    for line in data_file:
        label, text = line.split("\t")
        split_text = text.strip().split(" ")
        split_text = [word for word in split_text if word not in stop_list]
        if to_stem:
            split_text = stem(split_text)

        data.append((label, split_text))
    classifier = FeatureMaker(data)
    
    # classifier.add_feature(unigram_counts)
    # classifier.add_feature(bigram_counts)
    # classifier.add_feature(trigram_counts)
    # classifier.add_feature(classifier.tf_idf)
    # classifier.add_feature(unigram_probs)
    # classifier.add_feature(unigram_present)
    # classifier.add_feature(bigram_present)
    classifier.add_feature(bigram_prob)
    # classifier.add_feature(trigram_present)

    # classifier.feature_selection(2700)

    classifier.print_feature_mapping("feature_mapping.txt")
    classifier.print_svm_file("all_data.svm")

    # shuffle("all_data.svm")

    # print run_svm_light("all_data.svm")

    # code that calculates the top n features that maximizes accuracy
    for i in xrange(100, 10000, 100):
        classifier.feature_selection(i)
        classifier.print_svm_file("all_data.svm")
        
        accuracy = 0
        num_iterations = 10
        for num in xrange(num_iterations):
            shuffle("all_data.svm")
            result = run_svm_light("all_data.svm")
            accuracy += float(result.split("\n")[0][22:27])
        accuracy = "{0:.2f}".format(accuracy / float(num_iterations))
        print str(i) + "\t" + accuracy + "%"

if __name__ == "__main__": main()