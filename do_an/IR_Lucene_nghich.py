import lucene
import sys
import glob
import os
import natsort
import nltk
import numpy as np
import time
from java.nio.file import Path, Paths
from org.apache.lucene.store import RAMDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.index import IndexOptions, IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.document import Document, Field, StoredField, StringField, TextField

from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import IndexReader

from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.tartarus.snowball.ext import PorterStemmer
MAX = 29
class LuceneIndexer:
	analyzer = None
	indexer = None
	directory = None
	searcher = None
	queryparser = None
	stemming = None # moi them
	MAX = 29 # số lượng tài liệu tối đa cần lấy
	def __init__(self, path):
		self.directory = SimpleFSDirectory(Paths.get(path))
		#self.analyzer = StandardAnalyzer()
		self.analyzer = EnglishAnalyzer()
		cf = IndexWriterConfig(self.analyzer)
		cf.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
		self.indexer = IndexWriter(self.directory,cf)
		self.stemming = PorterStemmer()
	def index(self,path):
		print("Path "+path)
		for f in glob.glob(path +"\*.*"):
			r = open(f,"r",encoding="utf-8")
			#print(f[10:])
			#text = r.readline()
			text = r.read()
			doc = Document()
			content = TextField("content",text,Field.Store.YES)
			index_text = TextField("index_text",f[10:],Field.Store.YES)
			doc.add(content)
			doc.add(index_text)
			self.indexer.addDocument(doc)
		self.indexer.close()	

class LuceneSearcher:
	directory = None
	indexReader = None
	indexSearcher = None
	analyzer = None
	MAX = 1400
	#QueryParser = None
	def __init__(self,path):
		self.directory = SimpleFSDirectory(Paths.get(path))
		self.indexReader = DirectoryReader.open(self.directory)
		self.indexSearcher = IndexSearcher(self.indexReader)
		#self.analyzer = StandardAnalyzer()
		self.analyzer = EnglishAnalyzer()
	def searchContent(self,String_Querry):
		querryparser = QueryParser("content",self.analyzer)
		querry = querryparser.parse(String_Querry)
		hits = self.indexSearcher.search(querry, self.MAX)

		result = []
		for i in hits.scoreDocs:
			doc = self.indexSearcher.doc(i.doc)
			#result.append([doc.get("content").rstrip("\n")])
			result.append([doc.get("index_text").rstrip("\n")])
			#print(doc.get("title"))
			#print(doc.get("author"))
			#print(doc.ger("content"))
		return result

lucene.initVM()

os.chdir("D:\TH_TVDPT\do_an")
index = LuceneIndexer("index")
index.index("Cranfield")
search = LuceneSearcher("index")
Result_List = [] #chứa các file txt liên quan tới từng câu truy vấn
Cranfield_List = [] # Kết quả cranfield công bố
#Đường dẫn tệp chứa các câu truy vấn:

''' Truy cập file câu hỏi'''
querry_source = open("D:\\TH_TVDPT\\do_an\\TEST\\query.txt","r",encoding="utf-8")
Precision = []
Recall = []
for querry in querry_source:
	Result_List.append(search.searchContent(querry))

filePath = "D:\TH_TVDPT\do_an\TEST\RES"
Cranfield = os.listdir(filePath)
Cranfield= natsort.natsorted(Cranfield)

''' Truy cập kết quả Cranfield'''
for f in Cranfield:
	r = open(filePath+ "\\" + f,"r",encoding="utf-8")
	column_1 = []
	for row in r:
		txt = row.split()
		txt = txt[1]+".txt"
		column_1.append(txt)
	Cranfield_List.append(column_1)


for index in range(len(Result_List)):
	True_False = np.in1d(Result_List[index],Cranfield_List[index])
	Result_True = len(Cranfield_List[index])
	#if index == 21:
		#print(True_False)
	#print(True_False)
	#print(Result_List[index])
	#print(Cranfield_List[index])
	
	n = 0 # Tổng số kết quả trả về
	y = 1 # Tổng số kết quả trả về đúng
	x = 0 # 
	p = []
	r = []
	for i in True_False:
		n += 1

		if str(i) == "True":
			p.append(y/n)
			r.append(y/Result_True)
			y += 1

	Precision.append(p)
	Recall.append(r)
#print(Recall)
print("-------------")
#print(Precision)
#Lưu trữ file kết quả
'''
for index in range(len(Result_List)):
	with open(f'{index+1}.txt' , "w") as f:
		f.writelines("%s\n" %value[0] for value in Result_List[index])
'''

#print(Precision[21])
Average_Precision = []
#print(Precision)
percent = []
#print(Precision[0].index(max(Precision[0])))


for i in range(len(Precision)):
	if(len(Precision[i]) != 0):
		percent1 = 0.1 #phan tram do phu
		#percent2 = 0.1 #phan tram do phu
		stt = 0
		percent11 = []
		percent11.append(max(Precision[i]))
		while(True):
			max_p = max(Precision[i][stt:])
			if Recall[i][stt] >= percent1:
				percent11.append(max_p)
				percent1 += 0.1
			stt += 1
			if stt == len(Precision[i]):
				if len(percent11) != 11:
					percent11.append(0)
				break
		percent.append(percent11)	


for i in range(len(percent)):
	if(str(np.average(percent[i])) != "nan"):
		Average_Precision.append(np.average(percent[i]))
	else:
		Average_Precision.append(float(0))


'''
for i in range(len(Precision)):
	#Average_Precision.append(np.average(Precision[i]))
	if (str(np.average(Precision[i])) != "nan"):
		Average_Precision.append(np.average(Precision[i]))
	else:
		Average_Precision.append(float(0))

'''

print("mean Average Precision:", np.average(Average_Precision))


	
	


		
'''
#Truy vấn theo content
print("Search = Content")
result = search.searchContent("what chemical kinetic system is applicable to hypersonic aerodynamic problems")
if not result:
	print("No document found")
else:
	print(result)
'''