# -*- coding:utf-8 -*-
import MySQLdb
import math
from datetime import datetime,date,timedelta
class db_connecter:

    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.passwd = ''
        self.charset = 'utf8'
        self.database = 'retrieval'
        # self.file_table = "files_2018_01_07"
        # self.invert_table = "inverted_2018_01_07"
        self.file_table = 'files_' + date.today().strftime('%Y_%m_%d')
        self.invert_table = 'inverted_' + date.today().strftime('%Y_%m_%d')
        self.connected = False
        self.connect()
        self.create_by_date()
    def connect(self):
        self.connecter =  MySQLdb.connect(self.host,\
            self.user,self.passwd,self.database,charset=self.charset)
        self.connected = self.database
    def close(self):
        self.connecter.close()
        self.connected = False

    def check_null(self):
        if self.connected == False:
            self.connect()
        for i in range(10):
            try:
                cursor = self.connecter.cursor()
                yesterday = (date.today() - timedelta(i)).strftime('%Y_%m_%d')
                sql_order = "SELECT count(term) from inverted_{}".format(date.today().strftime('%Y_%m_%d'))
                cursor.execute(sql_order)
                num = cursor.fetchall()
                num = num[0][0]
                if num == 0:
                    self.file_table = "inverted_{}".format(yesterday)
                    self.invert_table = "files_{}".format(yesterday)
                else:
                    break
            except:
                self.create_by_date()
                print 'wrong'
    def check_not_null(self):
        if self.connected == False:
            self.connect()
        for i in range(3):
            try:
                cursor = self.connecter.cursor()
                # yesterday = (date.today() - timedelta(i)).strftime('%Y_%m_%d')
                sql_order = "SELECT count(term) from inverted_{}".format(date.today().strftime('%Y_%m_%d'))
                cursor.execute(sql_order)
                num = cursor.fetchall()
                num = num[0][0]
                if num == 0:
                    return False
                else:
                    return True
            except:
                print 'No'
                return False
    def delete_inverted(self):
        if not self.connected:
            self.connect()
        try:
            cursor = self.connecter.cursor()
            sql_order = "DELETE from {} where df > 0".format(self.invert_table)
            cursor.execute(sql_order)
            sql_order = "DELETE from {} where id > 0".format(self.file_table)
            self.connecter.commit()
        except:
            self.connecter.rollback()
            print 'Do not need to -f'

    def create_by_date(self):
        today = date.today().strftime('%Y_%m_%d')
        file_table = 'files_' + today
        invert_table = 'inverted_'+today
        if self.connected == False:
            self.connect()
        try:
            cursor = self.connecter.cursor()
            sql_order = 'SHOW TABLES'
            cursor.execute(sql_order)
            result = cursor.fetchall()
            result = map(lambda x:x[0],result)
            if file_table in result or invert_table in result:
                print 'TABLES are created'
                return False
            try:
                sql_order = """CREATE TABLE retrieval.inverted_{} (
    TERM varchar(100) NOT NULL,
    DF INT NULL,
    DATA_CHAIN LONGTEXT NULL,
    UNIQUE KEY `TERM` (`TERM`)
)
ENGINE=InnoDB
DEFAULT CHARSET=utf8
COLLATE=utf8_general_ci ;""".format(today)
                cursor.execute(sql_order)


                sql_order = """CREATE TABLE `files_{}` (
  `id` int(11) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `comment_length` int(11) DEFAULT NULL,
  `time_float` double DEFAULT NULL,
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1""".format(today)
                # print sql_order
                cursor.execute(sql_order)
            except Exception as f:
                print f.args
                self.connecter.rollback()
                print "wrong"
        except:
            print
            pass 



    def dump(self,table_name='inverted2'):
        if self.connected == False:
            self.connect()
        try:
            cursor = self.connecter.cursor()
            sql_order = 'SELECT * FROM {}'.format(table_name)
            cursor.execute(sql_order)
            result = cursor.fetchall()
            # self.close()
            return result
        except:
            print 'SQL WRONG'
            self.connecter.rollback()
            # self.close()
            return False
    def write_dict_huge(self, inverted_dict):
        num = 0
        total = len(inverted_dict)
        for term in inverted_dict:
            df = inverted_dict[term][0]
            docs = inverted_dict[term][1]
            self.insert_a_lot_doc(term, df, docs)
            num += 1
            print 'SQL Operating:{}\t{} in total {} ...'.format(term.encode('utf-8'),num,total)
    def write_dict_huge_simple(self, inverted_dict):
        num = 0
        total = len(inverted_dict)
        for term in inverted_dict:
            df = inverted_dict[term][0]
            docs = inverted_dict[term][1]
            self.insert_a_lot_doc_str(term, df, docs)
            num += 1
            print 'SQL Operating:{}\t{} in total {} ...'.format(term.encode('utf-8'),num,total)

            
    def file_reload(self):
        dumped_file = self.dump(self.file_table)
        cache = []
        cache2 = []
        for cell in dumped_file:
            cache.append(cell[1])
            cache2.append((cell[2],cell[3]))
        return cache, cache2
    def insert_invert_doc(self, count_dict, file_id_p):
        table_name = self.invert_table
        if self.connected == False:
            self.connect()
        for term in count_dict:
            tf = count_dict[term]
            try:
                # print type(term)
                term = term.encode('utf-8')
                cursor = self.connecter.cursor()
                sql_order = 'SELECT * FROM {} where term="{}"'.format(table_name,term)
                cursor.execute(sql_order)
                result = cursor.fetchall()
                # print result
                if len(result) == 0:
                    # print cell
                    good = self.insert_null(term,file_id_p,tf,0)
                    if not good:
                        print 'wrong'
                        return
                else:
                    good = self.insert_not_null(result,term,file_id_p,tf,0)
                    if not good:
                        print 'wrong'
            except:
                print 'SQL WRONG select'
                self.connecter.rollback()
                # self.close()
                return False
    def insert_a_lot_doc_str(self, term, df, docs_str):
        if not self.connected:
            self.connect()      
        try:
            connecter = self.connecter
            cursor = connecter.cursor()
            sql_order = 'SELECT * FROM {} where term="{}"'.format(self.invert_table,term.encode('utf-8'))
            # print sql_order
            cursor.execute(sql_order)
            result = cursor.fetchall()
            if len(result) == 0:
                data_chain = docs_str
                try:
                    # data_chain = '({},{},{});'.format(docId,tf,0)
                    # cursor = connecter.cursor()
                    sql_order = 'INSERT INTO {} VALUES ("{}",{},"{}")'.format(self.invert_table,term.encode('utf-8'),df,data_chain)
                    # print sql_order
                    cursor.execute(sql_order)
                    connecter.commit()
                    return True
                except:
                    print 'SQL WRONG 1'
                    connecter.rollback()
                    return False
            else:
                result = result[0]
                data_chain = result[2]

                data_chain = data_chain + docs_str
                try:
                    # data_chain = '({},{},{});'.format(docId,tf,0)
                    cursor = connecter.cursor()
                    if type(term) == type(u'1'):
                        term = term.encode('utf-8')
                    sql_order = 'UPDATE {} SET DF={}, DATA_CHAIN="{}" WHERE term="{}"'.format(self.invert_table, df,data_chain,term)
                    # print 'UPDATE ' + term 
                    cursor.execute(sql_order)
                    connecter.commit()
                    return True
                except:
                    print 'SQL WRONG 9'
                    connecter.rollback()
                    return False
            return True
        except:
            print 'SQL WRONG 11111'
            self.connecter.rollback()

    def insert_a_lot_doc(self, term, df, docs):
        if not self.connected:
            self.connect()      
        try:
            connecter = self.connecter
            cursor = connecter.cursor()
            sql_order = 'SELECT * FROM {} where term="{}"'.format(self.invert_table,term.encode('utf-8'))
            # print sql_order
            cursor.execute(sql_order)
            result = cursor.fetchall()
            if len(result) == 0:
                df_d = len(docs)
                if df != df_d:
                    print '\n\n\n\ndf count Waring \n\n\n\n'
                    df = df_d
                cell_cache = ''
                for doc in docs:
                    file_id_p = doc[0]
                    tf = doc[1]
                    tf_idf = 0
                    cell = '({},{},{});'.format(file_id_p,tf,tf_idf)
                    cell_cache += cell
                data_chain = cell_cache
                try:
                    # data_chain = '({},{},{});'.format(docId,tf,0)
                    # cursor = connecter.cursor()
                    sql_order = 'INSERT INTO {} VALUES ("{}",{},"{}")'.format(self.invert_table,term.encode('utf-8'),df,data_chain)
                    # print sql_order
                    cursor.execute(sql_order)
                    connecter.commit()
                    return True
                except:
                    print 'SQL WRONG 1'
                    connecter.rollback()
                    return False
            else:
                result = result[0]
                data_chain = result[2]

                cell_cache = ''
                for doc in docs:
                    file_id_p = doc[0]
                    # if self.check_doc_id(data_chain ,doc[0]):
                    tf = doc[1]
                    tf_idf = 0
                    cell = '({},{},{});'.format(file_id_p,tf,tf_idf)
                    cell_cache += cell
                    df += 1

                data_chain = data_chain + cell_cache
                try:
                    # data_chain = '({},{},{});'.format(docId,tf,0)
                    cursor = connecter.cursor()
                    if type(term) == type(u'1'):
                        term = term.encode('utf-8')
                    sql_order = 'UPDATE {} SET DF={}, DATA_CHAIN="{}" WHERE term="{}"'.format(self.invert_table, df,data_chain,term)
                    # print 'UPDATE ' + term 
                    cursor.execute(sql_order)
                    connecter.commit()
                    return True
                except:
                    print 'SQL WRONG 9'
                    connecter.rollback()
                    return False
            return True
        except:
            print 'SQL WRONG 11111'
            self.connecter.rollback()

    def insert_null(self, term, docId, tf, tf_idf):
        # print '111111111'
        connecter = self.connecter
        try:
            # print type(term)
            data_chain = '({},{},{});'.format(docId,tf,0)
            # print data_chain
            cursor = connecter.cursor()

            sql_order = 'INSERT INTO {} VALUES ("{}",{},"{}")'.format(self.invert_table, term,1,data_chain)
            # print sql_order
            print sql_order
            cursor.execute(sql_order)
            connecter.commit()
            return True
        except:
            print 'SQL WRONG 1'
            connecter.rollback()
            return False
    def insert_not_null(self, result, term, docId, tf, tf_idf):
        connecter = self.connecter
        result = result[0]
        df = result[1]
        doc_chain = result[2]
        try:
            data_chain = '({},{},{});'.format(docId,tf,0)
            cursor = connecter.cursor()
            sql_order = 'UPDATE {} SET DF={}, DATA_CHAIN="{}" WHERE term="{}"'.format(self.invert_table,df+1,doc_chain+data_chain,term)

            print 'UPDATE ' + term + ' ' + str(docId)
            cursor.execute(sql_order)
            connecter.commit()
            return True
        except:
            print 'SQL WRONG 2'
            connecter.rollback()
            return False
    def insert_not_null_safe(self, result, term, docId, tf, tf_idf):
        connecter = self.connecter
        result = result[0]
        df = result[1]
        doc_chain = result[2]
        if not self.check_doc_id(doc_chain,docId):
            return False
        try:
            data_chain = '({},{},{});'.format(docId,tf,0)
            cursor = connecter.cursor()
            sql_order = 'UPDATE {} SET DF={}, DATA_CHAIN="{}" WHERE term="{}"'.format(self.invert_table,df+1,doc_chain+data_chain,term)
            print 'UPDATE ' + term + ' ' + str(docId)
            cursor.execute(sql_order)
            connecter.commit()
            return True
        except:
            print 'SQL WRONG 2'
            connecter.rollback()
            return False
    def check_doc_id(self,doc_chain,docId):
        doc_chain = doc_chain.split(';')[0:-1]
        for doc in doc_chain:
            doc = doc.lstrip('(').rstrip(')')
            doc_cache = doc.split(',')
            chain_id = int(doc_cache[0])
            if chain_id == int(docId):
                return False
        return True
    def tf_idf_init(self,num):
        if self.connected == False:
            self.connect()
        connecter = self.connecter
        try:
            # data_chain = '({},{},{});'.format(docId,tf,0)
            cursor = connecter.cursor()
            sql_order = 'SELECT * FROM {}'.format(self.invert_table)
            cursor.execute(sql_order)
            result = cursor.fetchall()
            # print type(result[0][0])
            for cell in result:
                term = cell[0].encode('utf-8')
                df = cell[1]
                doc_chain = cell[2]
                doc_chain_cache = doc_chain.split(';')[0:-1]
                doc_cell_cache = ''
                for doc_cell in doc_chain_cache:
                    doc_cell = doc_cell.rstrip(')').lstrip('(')
                    doc_cache = doc_cell.split(',')
                    # print doc_cache
                    doc_cache[0] = doc_cache[0].encode('utf-8')
                    doc_cache[1] = doc_cache[1].encode('utf-8')
                    tf = float(doc_cache[1])
                    # print num
                    idf = math.log(float(num) / float(df))
                    tf_idf = str(round(tf*idf,2))
                    doc_cell_cache += '({},{},{});'.format(doc_cache[0],doc_cache[1],tf_idf)
                # print doc_cell_cache
                try:
                    cursor = connecter.cursor()
                    sql_order = 'UPDATE {} SET DATA_CHAIN="{}" WHERE term="{}"'.format(self.invert_table, doc_cell_cache,term)
                    print sql_order
                    cursor.execute(sql_order)
                    connecter.commit()
                except:
                    print 'SQL WRONG 6'
                    connecter.rollback()
        except:
            print 'SQL WRONG 4'
            connecter.rollback()
            return False
    def search(self,term):
        if self.connected == False:
            self.connect()
        connecter = self.connecter
        try:
            if type(term) != type('\x00'):
                term = term.encode('utf-8')
            # print term
            # data_chain = '({},{},{});'.format(docId,tf,0)
            cursor = connecter.cursor()
            sql_order = 'SELECT data_chain FROM {} where term = "{}"'.format(self.invert_table, term)
            print sql_order
            cursor.execute(sql_order)
            result = cursor.fetchall()
            return result[0][0]
            # print type(result[0][0])

        except:
            print 'SQL WRONG SEARCH'
            connecter.rollback()
            return False

    def search_cache(self, term_cache):
        if self.connected == False:
            self.connect()
        connecter = self.connecter
        num = 0
        sql_order = None
        for term in term_cache:
            if type(term) != type('\x00'):
                term = term.encode('utf-8')
            if num == 0:
                sql_order = 'SELECT data_chain FROM {} where term = "{}"'.format(self.invert_table, term)
            else:
                sql_order += 'UNION SELECT data_chain FROM {} where term = "{}"'.format(self.invert_table, term)
            num += 1
        try:

            # data_chain = '({},{},{});'.format(docId,tf,0)
            cursor = connecter.cursor()
            cursor.execute(sql_order)
            result = cursor.fetchall()
            return result
            # print type(result[0][0])

        except:
            print 'SQL WRONG 7'
            connecter.rollback()
            return False
    def search_term(self, term):
        if self.connected == False:
            self.connect()
        connecter = self.connecter
        sql_order = 'SELECT term FROM {} where term like "{}%"'.format(self.invert_table, term.encode('utf-8'))
        try:
            cursor = connecter.cursor()
            cursor.execute(sql_order)
            result = cursor.fetchall()
            return result
        except:
            print 'SQL WRONG 100'
            connecter.rollback()
            return False


    def print_files(self,files,files_patch):
        # print files
        if self.connected == False:
            self.connect()
        values_cache = []
        for i in range(len(files)):
            values_cache.append('({},"{}",{},{}),'.format(i+1,files[i],files_patch[i][0],files_patch[i][1]))
        values_cache[-1] = values_cache[-1].rstrip(',')

        sql_order = 'INSERT INTO {} VALUES '.format(self.file_table)
        num = 0
        len_values = len(values_cache)
        for value in values_cache:
            sql_order += value
            num += 1
            if num % 1000 == 0 or num == len_values:
                sql_order = sql_order.rstrip(',')
                try:
                    cursor = self.connecter.cursor()
                    # sql_order = 'SELECT * FROM {}'.format(self.file_table)
                    result = cursor.execute(sql_order)
                    self.connecter.commit()
                    sql_order = 'INSERT INTO {} VALUES '.format(self.file_table)
                    # self.close()
                except:
                    print 'SQL WRONG'
                    self.connecter.rollback()
                    # self.connecter.close()
                    return False
    def get_hot_list(self, order):
        if order not in [1,2]:
            print "WRONG Order"
            return
        if self.connected == False:
            self.connect()
        connecter = self.connecter
        if order == 1: # order by comments
            sql_order = 'SELECT name,comment_length,time_float FROM {} WHERE comment_length > 0 order by comment_length desc limit 10'.format(self.file_table)
            try:
                cursor = connecter.cursor()
                cursor.execute(sql_order)
                result = cursor.fetchall()
                return result
            except:
                print "hot_list SQL WRONG 1"
        elif order == 2:
            sql_order = 'SELECT name,comment_length,time_float FROM {} order by time_float desc limit 10'.format(self.file_table)
            try:
                cursor = connecter.cursor()
                cursor.execute(sql_order)
                result = cursor.fetchall()
                return result
            except:
                print "hot_list SQL WRONG 2"





if __name__ == '__main__':

    connecter = db_connecter()
    connecter.check_null()
    # connecter.create_by_date()
    # tester = connecter.search(u'奥巴马').split(';')[0:-1]
    # cache = []
    # for cell in tester:
    #     cell_dumped = cell.rstrip(')').lstrip('(')
    #     cell_cache = cell_dumped.split(',')
    #     cache.append(int(cell_cache[0]))
    # print cache
    # aaa = connecter.dump()
    # num = 0
    # length = 0
    # for cell in aaa:
    #     num += 1
    #     length += len(cell[0])
    #     length += len(str(cell[1]))
    #     length += len(cell[2])
    # print length/1024/1024

    # connecter.close()
    # print connecter.search(u'奥巴马')
    # print connecter.search(u'中国')
    # connecter.connect()
    # a = ['133','233','333']
    # # b = connecter.print_files(a)
    # print connecter.insert_invert_doc({'自然':1})
