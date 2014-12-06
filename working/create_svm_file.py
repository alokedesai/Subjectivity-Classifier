import sys

class SvmInput:
  
  def __init__(self, in_file, feature_file, out_file, stop_file):
    self.in_file = open(in_file, "r").readlines()
    self.feature_file = open(feature_file, "w")
    self.out_file = open(out_file, "w")
    self.stop = self.read_stoplist(stop_file)

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

  def create_word_count_file(self):
  	features = {}
  	feature_count = 1

  	for line in self.in_file:
  		line = line.rstrip()
  		label, text = line.split("\t")

  		counts = self.get_word_counts(text)
  		self.out_file.write(label)

  		printme = {}
  		for tok in counts.keys():
  			if (tok not in self.stop):
  				if (tok not in features):
  					features[tok] = feature_count
  					self.feature_file.write(str(feature_count) + "\t" + tok + "\n")

  					feature_count+=1

  				printme[features[tok]] = counts[tok]

  		for fnum in sorted(printme):
  			self.out_file.write(" " + str(fnum) + ":" + str(printme[fnum]))
  		self.out_file.write("\n")

# data_file = sys.argv[1]
# stoplist = sys.argv[2]
# out = sys.argv[3]

svm_factory = SvmInput("data/data.txt", "test_feature.txt", "test2.model", "stop.txt")
svm_factory.create_word_count_file()
