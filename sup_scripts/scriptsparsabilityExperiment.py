import csv
import glob
from os.path import expanduser
import pandas
import numpy as np
import scipy.stats

###
'''
This script calculates the average parsability of each marker across noun items along with the standard deviations. 
The top function calculates these only for the training set, and the bottom function calculates it across the experiemnt.
'''
###

listFiles=glob.glob('../data/data_freq/final_data/*.csv')
nouns = ['nork', 'tumbat', 'negid', 'vaem']

'''
TRAINING
'''
def get_parsability_training(listFiles):
	global nouns
	maxStd_case = 0
	maxStd_num = 0
	for csvFile in listFiles:
		f=pandas.read_csv(csvFile)
		markerNum = f['markerNum'][0]
		markerCase = f['markerCase'][0]
		noun_occ = [i[1] for i in zip(f['Phase'],f['InputSentence']) if type(i[1])==str and 'Complex' not in i[0] and len(i[1].split())==1]
		phrases = [i[1] for i in zip(f['Phase'],f['InputSentence']) if 'SimplePhrase' in i[0]]
		phrases = [i for i in phrases if len(i.split())!=1 ]
		freq_case = []
		freq_num = []
		print csvFile
		for n in nouns:
			countCase = sum([markerCase in i and n in i.split()[-2:] for i in phrases])
			countNum = sum([markerNum in i and n in i.split()[:3] for i in phrases])
			countNoun = sum([i==n for i in noun_occ])
			print countNum, countCase, countNoun
			freq_case.append(float(countCase)/countNoun)
			freq_num.append(float(countNum)/countNoun)
		std_case = np.std(freq_case)
		std_num = np.std(freq_num)
		if std_num > maxStd_num: maxStd_num = std_num
		if std_case > maxStd_case: maxStd_case = std_case
		print np.mean(freq_case), np.std(freq_case)
		print np.mean(freq_num), np.std(freq_num)
		print '#####'
	print maxStd_case; print maxStd_num

# get_parsability_training(listFiles)

'''
ALL
'''
def get_parsability_all(listFiles):
	global nouns
	maxStd_case = 0
	maxStd_num = 0
	for csvFile in listFiles:
		f=pandas.read_csv(csvFile)
		markerNum = f['markerNum'][0]
		markerCase = f['markerCase'][0]
		noun_occ = [i for i in f['InputSentence'] if type(i)==str and len(i.split())==1]
		phrases_simple = [i[1] for i in zip(f['binaryResp'],f['InputSentence']) if type(i[1])==str and len(i[1].split())!=1 and i[0] not in [0,1]]
		phrases_complex = [i[1] for i in zip(f['binaryResp'],f['InputSentence']) if type(i[1])==str and len(i[1].split())!=1 and i[0] in [0,1]]
		freq_case = []
		freq_num = []
		print csvFile
		for n in nouns:
			countCase_simple = sum([markerCase in i and n in i.split()[-2:] for i in phrases_simple])
			countNum_simple = sum([markerNum in i and n in i.split()[:3] for i in phrases_simple])
			count_complex = sum([n in i.split()[-3:] for i in phrases_complex])
			countCase = countCase_simple #+count_complex
			countNum = countNum_simple #+count_complex
			countNoun = sum([i==n for i in noun_occ])
			print countNum, countCase, countNoun
			freq_case.append(float(countCase)/countNoun)
			freq_num.append(float(countNum)/countNoun)
		std_case = np.std(freq_case)
		std_num = np.std(freq_num)
		if std_num > maxStd_num: maxStd_num = std_num
		if std_case > maxStd_case: maxStd_case = std_case
		print np.mean(freq_case), np.std(freq_case)
		print np.mean(freq_num), np.std(freq_num)
		print '#####'
	print maxStd_case; print maxStd_num


get_parsability_all(listFiles)
