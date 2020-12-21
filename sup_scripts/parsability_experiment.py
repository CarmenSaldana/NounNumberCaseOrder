import csv
import glob
from os.path import expanduser
import pandas
import numpy as np
import scipy.stats

###
'''
This script calculates the average parsability of each marker across noun items along with the standard deviations. 
The top function calculates these only for the training set, and the bottom functions calculate it across the experiemnt.
'''
###

listFiles_exp1=glob.glob('../data/data_exp1_english/final_data/*.csv')
listFiles_exp3=glob.glob('../data/data_exp3_NomSg_explicit_training/final_data/*.csv')
listFiles_exp3bis=glob.glob('../data/data_exp3bis_frequency/final_data/*.csv')
nouns = ['nork', 'tumbat', 'negid', 'vaem']

'''
TRAINING
'''
def get_parsability_training(listFiles):
	global nouns
	maxStd_case = 0
	maxStd_num = 0
	means_case = []
	means_num = []
	for csvFile in listFiles:
		f=pandas.read_csv(csvFile)
		markerNum = f['markerNum'][0]
		markerCase = f['markerCase'][0]
		noun_occ = [i[1] for i in zip(f['Phase'],f['InputSentence']) if type(i[1])==str and 'Complex' not in i[0] and len(i[1].split())==1]
		phrases = [i[1] for i in zip(f['Phase'],f['InputSentence']) if 'SimplePhrase' in i[0]]
		phrases = [i for i in phrases if len(i.split())!=1 ]
		freq_case = []
		freq_num = []
		for n in nouns:
			countCase = sum([markerCase in i and n in i.split()[-2:] for i in phrases])
			countNum = sum([markerNum in i and n in i.split()[:3] for i in phrases])
			countNoun = sum([i==n for i in noun_occ])
			freq_case.append(float(countCase)/countNoun)
			freq_num.append(float(countNum)/countNoun)
		std_case = np.std(freq_case)
		std_num = np.std(freq_num)
		if std_num > maxStd_num: maxStd_num = std_num
		if std_case > maxStd_case: maxStd_case = std_case
		means_case.append(np.mean(freq_case))
		means_num.append(np.mean(freq_num))
	print ("Average mean ratio for CASE:", np.mean(means_case))
	print ("Maximum SD across stems in a participant for CASE:",maxStd_case)
	print ("Average mean ratio for NUMBER:",np.mean(means_num))
	print ("Maximum SD across stems in a participant for NUMBER:",maxStd_num)

# get_parsability_training(listFiles)

'''
ALL
'''
def get_parsability_all(listFiles):
	global nouns
	maxStd_case = 0
	maxStd_num = 0
	means_case = []
	means_num = []
	for csvFile in listFiles:
		f=pandas.read_csv(csvFile)
		markerNum = f['markerNum'][0]
		markerCase = f['markerCase'][0]
		noun_occ = [i for i in f['InputSentence'] if type(i)==str and len(i.split())==1]
		phrases_simple = [i[1] for i in zip(f['binaryResp'],f['InputSentence']) if type(i[1])==str and len(i[1].split())!=1 and i[0] not in [0,1]]
		phrases_complex = [i[1] for i in zip(f['binaryResp'],f['InputSentence']) if type(i[1])==str and len(i[1].split())!=1 and i[0] in [0,1]]
		freq_case = []
		freq_num = []
		for n in nouns:
			countCase_simple = sum([markerCase in i and n in i.split()[-2:] for i in phrases_simple])
			countNum_simple = sum([markerNum in i and n in i.split()[:3] for i in phrases_simple])
			count_complex = sum([n in i.split()[-3:] for i in phrases_complex])
			countCase = countCase_simple #+count_complex
			countNum = countNum_simple #+count_complex
			countNoun = sum([i==n for i in noun_occ])
			freq_case.append(float(countCase)/countNoun)
			freq_num.append(float(countNum)/countNoun)
		std_case = np.std(freq_case)
		std_num = np.std(freq_num)
		if std_num > maxStd_num: maxStd_num = std_num
		if std_case > maxStd_case: maxStd_case = std_case
		means_case.append(np.mean(freq_case))
		means_num.append(np.mean(freq_num))
	print ("Average mean ratio for CASE:", np.mean(means_case))
	print ("Maximum SD across stems in a participant for CASE:",maxStd_case)
	print ("Average mean ratio for NUMBER:",np.mean(means_num))
	print ("Maximum SD across stems in a participant for NUMBER:",maxStd_num)

def get_parsability_all_nom(listFiles):
	global nouns
	maxStd_case = 0
	maxStd_num = 0
	means_case = []
	means_num = []
	for csvFile in listFiles:
		f=pandas.read_csv(csvFile)
		markerNum = f['markerNum'][0]
		markerCase = f['markerCase'][0]
		noun_occ = [i for i in f['InputSentence'] if type(i)==str and len(i.split())==1]
		phrases_simple = [i[1] for i in zip(f['BinaryResp'],f['InputSentence']) if type(i[1])==str and len(i[1].split())!=1 and i[0] not in [0,1]]
		phrases_complex = [i[1] for i in zip(f['BinaryResp'],f['InputSentence']) if type(i[1])==str and len(i[1].split())!=1 and i[0] in [0,1]]
		freq_case = []
		freq_num = []
		for n in nouns:
			countCase_simple = sum([markerCase in i.split()[1] and n in i.split()[1] for i in phrases_simple])
			countNum_simple_agent = sum([markerNum in i.split()[1] and n in i.split()[1]  for i in phrases_simple])
			countNum_simple_patient = sum([markerNum in i.split()[2] and n in i.split()[2]  for i in phrases_simple])
			countNum_simple = countNum_simple_agent+countNum_simple_patient
			count_complex = sum([n in i.split()[1] for i in phrases_complex])
			countCase = countCase_simple #+count_complex
			countNum = countNum_simple #+count_complex
			countNoun = sum([i==n for i in noun_occ])
			freq_case.append(float(countCase)/countNoun)
			freq_num.append(float(countNum)/countNoun)
		std_case = np.std(freq_case)
		std_num = np.std(freq_num)
		if std_num > maxStd_num: maxStd_num = std_num
		if std_case > maxStd_case: maxStd_case = std_case
		means_case.append(np.mean(freq_case))
		means_num.append(np.mean(freq_num))
	print ("Average mean ratio for CASE:", np.mean(means_case))
	print ("Maximum SD across stems in a participant for CASE:",maxStd_case)
	print ("Average mean ratio for NUMBER:",np.mean(means_num))
	print ("Maximum SD across stems in a participant for NUMBER:",maxStd_num)

print("#####################################")
print("# Input parsability in Experiment 1 #")
print("#####################################")
print("Training:")
get_parsability_training(listFiles_exp1)
print("Testing:")
get_parsability_all(listFiles_exp1)

print("#####################################")
print("# Input parsability in Experiment 3 #")
print("#####################################")
get_parsability_all_nom(listFiles_exp3)

print("######################################")
print("# Input parsability in Experiment 3' #")
print("######################################")
get_parsability_all(listFiles_exp3bis)

