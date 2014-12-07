import math
import sys

class SvmInput:
  
  def __init__(self, in_file, feature_file, out_file, stop_file):
    self.in_file = open(in_file, "r").readlines()
    self.feature_file = open(feature_file, "w")
    self.out_file = open(out_file, "w")
    self.stop = self.read_stoplist(stop_file)

    self.features = {}
    
    # info for Mutual Information
    self.num_objective = 0
    self.num_subjective = 0
    self.word_frequency = {}

    self.selected_features = []
    # calculate idf
    self.idf = {}
    for text in self.in_file:
      label, line = text.split("\t")

      if label == "1":
        self.num_objective += 1
      else:
        self.num_subjective += 1

      if label not in self.word_frequency:
        self.word_frequency[label] = {}

      words_seen = set()
      for word in line.split(" "):
        word = word.rstrip()

        if word not in words_seen and word not in self.stop:
          previous_count = self.word_frequency[label].get(word, 0)
          self.word_frequency[label][word] = previous_count + 1

          self.idf[word] = self.idf.get(word, 0) + 1
          words_seen.add(word)

    for word in self.idf.keys():
      self.idf[word] = math.log10(len(self.in_file) / self.idf[word])

  def read_stoplist(self, stop_file):
    stoplist = open(stop_file, "r").readlines()
    stop = set()

    for line in stoplist:
      line = line.rstrip()
      stop.add(line)

    return stop
	
  def get_word_counts(self, text):
  	count = {}
  	for word in text.split(" "):
  		old_count = count.get(word, 0)
  		count[word] = old_count + 1
  	return count

  def get_tf(self, text):
    count = {}
    words = text.split(" ")
    for word in words:
      word = word.rstrip()
      old_count = count.get(word, 0)
      count[word] = old_count + 1

    # normalize by length of text
    for word in count:
      count[word] = count[word] / float(len(words))

    return count


  def get_tfidf(self, text):
    tf = self.get_word_counts(text)
    
    for word in tf.keys():
      tf[word] = tf[word] * self.idf[word]

    return tf

  def create_bow_file(self, feature_type):
    self.features = {}
    feature_count = 1

    for line in self.in_file:
      line = line.rstrip()
      label, text = line.split("\t")

      counts = feature_type(text)
      
      self.out_file.write(label)

      printme = {}
      for word in counts.keys():
        if (word not in self.stop):
          if (word not in self.features):
            self.features[word] = feature_count
            self.feature_file.write(str(feature_count) + "\t" + word + "\n")

            feature_count+=1

          printme[self.features[word]] = counts[word]
      self.create_svm_file(printme)

  def create_svm_file(self, print_info):
    for fnum in sorted(print_info):
      if not self.selected_features or fnum in self.selected_features:
        self.out_file.write(" " + str(fnum) + ":" + str(print_info[fnum]))
    self.out_file.write("\n")

  def create_word_count_file(self):
    self.create_bow_file(self.get_word_counts)

  def create_tf_file(self):
    self.create_bow_file(self.get_tf)

  def create_tfidf_file(self):
    self.create_bow_file(self.get_word_counts)

  def feature_selection(self, num_features = None):
    num_documents = float(self.num_objective + self.num_subjective)

    mutual_information = {}
    
    # compute mutual information
    for word in self.features:
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
      self.selected_features = [self.features[x[0]] for x in mutual_info_tuple[:num_features]]
    else:
      self.selected_features = [self.features[x[0]] for x in mutual_info_tuple]
    print self.selected_features
# data_file = sys.argv[1]
# stoplist = sys.argv[2]
# out = sys.argv[3]

svm_factory = SvmInput("data/data.txt", "test_feature.txt", "model.svm", "stop.txt")
# svm_factory.create_tf_file()
svm_factory.create_word_count_file()
svm_factory.feature_selection(10)
svm_factory.create()
