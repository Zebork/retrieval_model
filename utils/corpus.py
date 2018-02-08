import os
import re


class Corpus:
    def __init__(self, filepath):
        root_path = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.normpath(os.path.join(root_path, filepath))

        re_split = re.compile("\s+")

        self.pos_doc_list = []
        self.neg_doc_list = []
        with open(filepath) as f:
            for line in f:
                splits = re_split.split(line.strip())
                if splits[0] == "pos":
                    self.pos_doc_list.append(splits[1:])
                elif splits[0] == "neg":
                    self.neg_doc_list.append(splits[1:])
                else:
                    print(splits)
                    raise ValueError("Corpus Error")

        self.pos_doc_length = len(self.pos_doc_list)
        self.neg_doc_length = len(self.neg_doc_list)
        #self.doc_length = len(self.pos_doc_list)
        #assert len(self.neg_doc_list) == self.doc_length

        self.train_num = 0
        self.test_num = 0

        '''
        runout_content = "You are using the corpus: %s.\n" % filepath
        #runout_content += "There are total %d positive and %d negative f_corpus." % \
        #                  (self.pos_doc_length, self.neg_doc_length)
        runout_content += "There are total %d positive and %d negative f_corpus." % \
                            (self.doc_length, self.doc_length)
        print(runout_content)
        '''

    def get_corpus(self, start=0, end=-1):
        #assert self.doc_length >= self.test_num + self.train_num

        if end == -1:
            end = 1

        pstart = int(start*self.pos_doc_length)
        nstart = int(start*self.neg_doc_length)
        pend = int(end*self.pos_doc_length)
        nend = int(end*self.neg_doc_length)

        data = self.pos_doc_list[pstart:pend] + self.neg_doc_list[nstart:nend]
        data_labels = [1] * (pend - pstart) + [0] * (nend - nstart)
        return data, data_labels

    def get_train_corpus(self, num):
        self.train_num = num
        return self.get_corpus(end=num)

    def get_test_corpus(self, num):
        self.test_num = num
        return self.get_corpus(start=self.train_num, end=self.train_num + num)

    def get_all_corpus(self):
        data = self.pos_doc_list[:] + self.neg_doc_list[:]
        data_labels = [1] * self.pos_doc_length + [0] * self.neg_doc_length
        return data, data_labels


class TencentCorpus(Corpus):
    def __init__(self):
        Corpus.__init__(self, "f_corpus/ch_tencent_corpus.txt")


class TencentCompleteCorpus(Corpus):
    def __init__(self):
        Corpus.__init__(self, "f_corpus/ch_tencent_comments_corpus_complete.txt")


if __name__ == "__main__":
    pass
    get_movie_corpus()
    # get_movie2_corpus()
    # get_hotel_corpus()
    # get_waimai_corpus()
    # test_corpus()
