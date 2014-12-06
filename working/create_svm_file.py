import sys

def get_word_counts(text):
	count = {}
	for word in text.split(" "):
		old_count = count.get(word, 0)
		count[word] = old_count + 1
	return count

def read_stoplist(stop_file):
	stoplist = open(stop_file, "r").readlines()
	stop = set()

	for line in stoplist:
		line = line.rstrip()
		stop.add(line)

	return stop


data_file = sys.argv[1]
stoplist = sys.argv[2]
out = sys.argv[3]


stop = read_stoplist(stoplist)
in_file = open(data_file, "r").readlines()
feature_file = open("feature_list1.txt", "w")
out_file = open(out, "w")


features = {}
feature_count = 1

for line in in_file:
	line = line.rstrip()

	label, text = line.split("\t")

	counts = get_word_counts(text)

	out_file.write(label)

	printme = {}

	for tok in counts.keys():
		if (tok not in stop):
			if (tok not in features):
				features[tok] = feature_count
				feature_file.write(str(feature_count) + "\t" + tok + "\n")

				feature_count+=1

			printme[features[tok]] = counts[tok]

	for fnum in sorted(printme):
		out_file.write(" " + str(fnum) + ":" + str(printme[fnum]))
	out_file.write("\n")



