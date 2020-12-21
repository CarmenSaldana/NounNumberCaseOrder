'''
This script runs on Python 3 and relies on having the UD treebanks (v 2.1) and libraries in CLIQS. Follow the instructions on https://github.com/Futrell/cliqs
'''

import pandas as pd
import sys
sys.path.append('/Users/carmen/UD/cliqs-master/cliqs/')#Path to folder containing corpora.py 
import corpora
import numpy as np
from scipy import stats



dict_number={'tr': ['Number=Sing','Number=Plur'], 'hu': ['Number=Sing','Number=Plur']}
dict_cases = {'tr':['Nom','Gen', 'Acc', 'Dat', 'Loc', 'Abl','Equ', 'Ins'], 'hu':['Nom','Gen', 'Acc', 'Dat', 'Loc', 'Abl','Ess', 'Ins', 'Ine', 'All', 'Ill', 'Ade', 'Ela','Sub','Sup','Del','Tra','Ter','Tem']}

def get_sentences(language):
     corpus=corpora.ud_corpora[language]
     sentences=corpus.sentences()
     return list(sentences)


def prob(system,phrase):
	p=float(system.count(phrase))/len(system)
	return p

def get_entropy_system(system):
	system1=[i for i in system if i!='NA']
	h=0
	for i in set(system1):
		p=prob(system1,i)
		h-=p*np.log2(p)
	return h


def pars_conservative(sentences,marked_value):
    form_type=[]
    for sentence in sentences:
        for n in sentence.nodes():
            if n!=0:
                pos = sentence.node[n]['pos']
                inflection = sentence.node[n]['infl']
                numUn_caseUn = (pos == 'NOUN' and all(infl in inflection for infl in ['Number=Sing', 'Nom']))
                numUn_caseM = (pos == 'NOUN' and all(infl in inflection for infl in ['Number=Sing', marked_value]))
                numM_caseU = (pos == 'NOUN' and all(infl in inflection for infl in ['Number=Plur', 'Nom']))
                list_bool_value = [numUn_caseUn, numM_caseU, numUn_caseM]
                form_type.append([sentence.node[n]['lemma'] if i else 'NA' for i in list_bool_value])
    df_lemmas_pars = pd.DataFrame(form_type, columns=['Unmarked', 'Number','Case'])
    common_number = [i for i in set(list(df_lemmas_pars['Unmarked'])) if i in set(list(df_lemmas_pars['Number'])) and i !='NA']
    common_case = [i for i in set(list(df_lemmas_pars['Unmarked'])) if i in set(list(df_lemmas_pars['Case'])) and i !='NA']
    ratio_num = [list(df_lemmas_pars['Number']).count(i)/list(df_lemmas_pars['Unmarked']).count(i) for i in common_number ]
    ratio_case = [list(df_lemmas_pars['Case']).count(i)/list(df_lemmas_pars['Unmarked']).count(i) for i in common_case ]
    return  ratio_num, ratio_case 

def test_parsability(language, dict_number, dict_cases): 
    sentences = get_sentences(language)
    list_case = dict_cases[language]
    case_pars=[]
    for case_value in list_case[1:]:
        pars=pars_conservative(sentences, case_value)
        case_pars.extend(pars[-1])
    return (np.median(pars[-2]), np.median(case_pars), stats.mannwhitneyu(pars[-2],case_pars))

def test_parsability_pl_acc(language, dict_number, dict_cases): 
    sentences = get_sentences(language)
    list_case = dict_cases[language][2:3]
    case_pars=[]
    for case_value in list_case:
        pars=pars_conservative(sentences, case_value)
        case_pars.extend(pars[-1])
    return (np.median(pars[-2]), np.median(case_pars), stats.mannwhitneyu(pars[-2],case_pars))


def freq_infl(sentences,list_infl):
    freq=[]
    freq_by=[]
    lemmas=[]
    lemmas_by=[]
    for sentence in sentences:
        for n in sentence.nodes():
            if n!=0:
                pos = sentence.node[n]['pos']
                inflection = sentence.node[n]['infl']
                bool_value = (pos == 'NOUN' and any(infl in inflection for infl in list_infl))
                list_bool_value = [pos == 'NOUN' and infl in inflection for infl in list_infl]
                freq.append(bool_value)
                freq_by.append(list_bool_value)
                if bool_value: lemmas.append(sentence.node[n]['lemma'])
                lemmas_by.append([sentence.node[n]['lemma'] if i else 'NA' for i in list_bool_value])
    df= pd.DataFrame(freq_by, columns=list_infl)
    df_lemmas = pd.DataFrame(lemmas_by, columns=list_infl)
    sums=[sum(df[infl])for infl in list_infl]
    df_sums = pd.DataFrame([[sum(sums)]+sums], columns=['total']+list_infl)
    h_lemmas=get_entropy_system(lemmas)
    h_lemmas_by = df_lemmas.apply(get_entropy_system)
    norm_h_by=[round((h_lemmas_by[i]/(get_entropy_system(list(range(df_sums[i][0]))))),3) for i in list_infl]
    norm_h = [round(h_lemmas/(get_entropy_system(list(range(df_sums['total'][0])))),3)]
    return norm_h, norm_h_by, df_sums, h_lemmas_by, h_lemmas, df_lemmas

def integration_complexity(language):
    sentences = get_sentences(language)
    list_number = dict_number[language]
    list_case = dict_cases[language]
    df_number = freq_infl(sentences, list_number)
    df_case = freq_infl(sentences, list_case)
    return list(zip(['Number','Case']+list_number+list_case,df_number[0]+df_case[0]+df_number[1]+df_case[1]))



#############################################################
#  parsability 
#############################################################

'''
Turkish
'''
print('#################################################')
print('Parsability number & case in Turkish UD corpus:')
print (test_parsability('tr', dict_number, dict_cases))
print (test_parsability_pl_acc('tr', dict_number, dict_cases))

'''
Hungarian
'''
print('Parsability number & case in Hungarian UD corpus:')
print (test_parsability('hu', dict_number, dict_cases))
print (test_parsability_pl_acc('hu', dict_number, dict_cases))
print('#################################################')


#############################################################
#  Integration complexity
#############################################################

'''
Turkish
'''
print('#################################################')
print('Integration complexity number & case Turkish UD corpus:')
print(integration_complexity('tr'))

'''
Hungarian
'''
print('Integration complexity number & case Hungarian UD corpus:')
print(integration_complexity('hu'))
print('#################################################')



