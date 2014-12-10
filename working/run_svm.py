import math
import sys
import subprocess

class FeatureMaker:
    def __init__(self, documents):
        # document_list is a list of tuples [(lable, [word, word])]
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
        counts = unigram_counts(text)
        for word in counts:
            counts[word] *= self.idf[word]
        normalize(counts)
        return counts

    def add_feature(self, feature_function):
        """
        adds new feature
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
        feature_file = open(feature_file_path, "w")
        for feature, feature_number in sorted(self.feature_mapping.items(), key=lambda f:f[1]):
            out_string = "%d\t%s\n" % (feature_number, str(feature))
            feature_file.write(out_string)
        feature_file.close()

    def print_svm_file(self, svm_file_path):
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

    def mutual_information(self, feature):
        self.objective_features = {"export": 49}
        self.subjective_features = {"export": 27652}
        self.num_objective = 190
        self.num_subjective = 801758
        # number_of_documents = len(self.document_list)
        number_of_documents = self.num_subjective + self.num_objective
        info_score = 0
        for label in range(0,2):
            for present in range(0,2):

                # get dictionary
                if label == 0:
                    dict_type = self.objective_features
                    num_of_type = self.num_objective
                else:
                    dict_type = self.subjective_features
                    num_of_type = self.num_subjective

                if present == 1:
                    prob_of_feature_and_label = dict_type[feature] / float(num_of_type)
                else:
                    prob_of_feature_and_label = (num_of_type - dict_type[feature]) / float(num_of_type)

                prob_of_label = num_of_type / float(number_of_documents)
                prob_of_feature = (self.objective_features[feature] + self.subjective_features[feature]) / float(number_of_documents)

                total_prob = prob_of_feature_and_label * math.log(prob_of_feature_and_label / (prob_of_label * prob_of_feature), 2)
                info_score += total_prob
        return info_score

    # returns the top n features using feature_selection


    def feature_selection(self, num_features = None):
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

        for feature, prob in mutual_info_tuple[:100]:
            print "%s\t%.4f" % (feature, prob)


strip_list = ["'s"]

def unigram_counts_stripped(text):
    counts = {}
    for word in text:
        if word not in strip_list:
            counts[word] = counts.get(word, 0) +1
    return counts

def unigram_counts(text):
    """get word counts in a single document"""
    counts = {}
    for word in text:
        counts[word] = counts.get(word,0) + 1
    return counts

def unigram_present(text):
    counts = {}
    for word in text:
        counts[word] = 1
    return counts


def unigram_probs(text):
    """normalize counts by length of text"""
    counts = unigram_counts(text)
    for word in counts:
        counts[word] /= float(len(text))
    return counts

def bigram_counts(text):
    counts = {}
    for i in xrange(len(text)-1):
        current = text[i]
        next = text[i+1]
        tpl = (current, next)
        counts[tpl] = counts.get(tpl, 0) + 1
    return counts


def trigram_counts(text):
    counts = {}
    for i in range(len(text) - 2):
        first = text[i]
        second = text[i+1]
        third = text[i+2]
        tpl = (first, second, third)
        counts[tpl] = counts.get(tpl, 0) + 1
    return counts


def divide(svm_file):
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
    total = 0
    for key in vector:
        total += vector[key]**2
    for key in vector:
        vector[key] /= float(total)


def run_svm_light(svm_file):
    divide(svm_file)
    subprocess.check_output(["../svm_learn", "train.svm", "model.txt"])
    result = subprocess.check_output(["../svm_classify", "test.svm", "model.txt"])
    return "\n".join(result.split("\n")[3:5])


def main():
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
        data.append((label, split_text))
    classifier = FeatureMaker(data)
    classifier.add_feature(unigram_counts)
    # classifier.add_feature(bigram_counts)
    # classifier.add_feature(trigram_counts)
    # classifier.add_feature(classifier.tf_idf)
    # classifier.add_feature(unigram_probs)
    # classifier.add_feature(unigram_present)
    classifier.feature_selection(1500)

    classifier.print_feature_mapping("feature_mapping.txt")
    classifier.print_svm_file("all_data.svm")

    # print run_svm_light("all_data.svm")


if __name__ == "__main__": main()