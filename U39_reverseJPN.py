#! /usr/bin/env python
from psychopy import core, visual,event,sound
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
import time, random
from PIL import Image
import itertools
from collections import OrderedDict
import csv
import ast
import os.path
import sys
import pyo
import copy


def get_condition(code):
  list_parameters = [['regularisation','unmarked','initial'],['regularisation','marked','initial'], ['regularisation','unmarked','final'],['regularisation','marked','final'],['extrapolation','unmarked','initial'],['extrapolation','unmarked','final']]
  code=eval(code)
  code-=1
  return list_parameters[code]

########################################################################################################################
######################### SOUND & CO ###########################################################
########################################################################################################################

def setSound(signal,path):
  instr = sound.Sound(path+'U39_stims/sentences/allJPN/'+signal+'.wav')
  dur = instr.getDuration(); instr.setVolume(1.0);
  return (instr, dur)

def playSound(theSound,path):
  (instr, dur) = setSound(theSound,path)
  instr.play(); 
  core.wait(dur+1)

def draw_fixation(myWin):
  fixation = visual.TextStim(myWin, color='gray', units='norm', pos=[0,0], text='') 
  myWin.setMouseVisible(False)
  fixation.draw()
  myWin.flip()
  core.wait(0.1)
  myWin.setMouseVisible(True)


########################################################################################################################
#################### MEANINGS & SIGNALS #########################################################
########################################################################################################################

def levenshtein(seq1, seq2):
  oneago = None
  thisrow = range(1, len(seq2) + 1) + [0]
  for x in xrange(len(seq1)):
      twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
      for y in xrange(len(seq2)):
          delcost = oneago[y] + 1
          addcost = thisrow[y - 1] + 1
          subcost = oneago[y - 1] + (seq1[x] != seq2[y])
          thisrow[y] = min(delcost, addcost, subcost)
  return thisrow[len(seq2) - 1]

def get_meanings(noun_position):
  verbs = ['kick','point','punch']#,'shoot'
  #verbs = sorted(random.sample(verbs,3))
  subjects = ['burglar','chef','cowboy','waitress']
  objects = ['burglar','chef','cowboy','waitress']
  number = ['sg','pl']
  numbers = ['two','three','four']
  case = ['patient']
  elements = [verbs, subjects,number,objects, number]
  elements1 = [objects,numbers]
  elements2 = [objects]
  combi_sentences = list(itertools.product(*elements))
  combi_sentences = [meaning for meaning in combi_sentences if meaning[1]!=meaning[3] and all(x in ['pl'] for x in [meaning[2],meaning[4]])==False]
  num_phrases = list(itertools.product(*elements1))
  nouns = list(itertools.product(*elements2))
  list_meanings = combi_sentences+num_phrases+nouns
  list_meanings_constant= copy.deepcopy(list_meanings)
  if noun_position == 'initial':
    list_meanings_specific=list_meanings_constant
  elif noun_position == 'final':
    num_phrases = [list(phrase) for phrase in num_phrases]
    combi_sentences = [list(sentence) for sentence in combi_sentences]
    for s in combi_sentences:
      s[2], s[1] = s[1], s[2]
      s[4], s[3] = s[3], s[4]
    for s in num_phrases:
      s[1], s[0] = s[0], s[1]
    num_phrases = [tuple(phrase) for phrase in num_phrases]
    combi_sentences = [tuple(sentence) for sentence in combi_sentences]
    list_meanings_specific = combi_sentences+num_phrases+nouns
  return list_meanings_specific,list_meanings_constant


def get_meaning_groups(meaning_list):
  Nouns = [meaning  for meaning in meaning_list if len(meaning) == 1]
  Num = [meaning  for meaning in meaning_list if len(meaning) == 2]
  Case = [meaning for meaning in meaning_list if meaning.count('sg')==2]
  NumCase = [meaning for meaning in meaning_list if 'pl' in meaning[-2:]]
  NNumNCase = [meaning for meaning in meaning_list if 'pl' in meaning[:-2]]
  return OrderedDict(zip(['Noun','Num','Case','NumCase', 'NNumNCase'] , [Nouns,Num,Case,NumCase,NNumNCase]))


def dict_meanings(path,size, size2, noun_position):
  list_meanings=get_meanings(noun_position)
  list_meanings_constant = list_meanings[1]
  list_meanings_specific = list_meanings[0]
  list_jpg=[path+'U39_stims/images/'+size+'/'+'_'.join(meaning)+'.png' for meaning in list_meanings_constant]
  list_jpg_small=[path+'U39_stims/images/'+size2+'/'+'_'.join(meaning)+'.png' for meaning in list_meanings_constant]  
  dict_meanings=OrderedDict(zip(list_meanings_specific,list_jpg))
  dict_meanings_small=OrderedDict(zip(list_meanings_specific,list_jpg_small))
  return dict_meanings, dict_meanings_small

def dict_words():
  verbs = ['kick','point','punch']
  participants = ['burglar','chef','cowboy','waitress']
  number = ['two','three','four', 'pl']
  singular = ['sg']
  case = ['patient']
  verb_signals = ["kerura", "sasura", "nagura"]
  participant_signals = ["sogina", "dakume", "nechibi", "tasonu"]
  singular_signal = ['']
  #if we want to randomise the name of the participants: 
  participant_signals = random.sample(participant_signals,len(participant_signals))
  case_signal = random.choice(['sehi', 'gito', 'yoza'])
  number_signal = [random.choice(['sehi', 'gito', 'yoza'])]*4
  while levenshtein(case_signal,number_signal[0]) <= 0: 
    case_signal = random.choice(['sehi', 'gito', 'yoza'])
  dict_words = OrderedDict(zip(verbs+participants+singular+number+case, verb_signals+participant_signals+singular_signal+number_signal+[case_signal]))
  return dict_words

d_words = dict_words()

def dict_sentences(noun_position):
  global d_words
  list_meanings = get_meanings(noun_position)[0]
  list_meanings_phrases = [meaning for meaning in list_meanings if len(meaning)<5]
  list_phrases = ['_'.join([d_words[word] for word in meaning]) for meaning in list_meanings_phrases]
  list_meanings_sentences = [meaning for meaning in list_meanings if len(meaning)==5]
  list_meanings_sentences_unmarked = [list(meaning) for meaning in list_meanings_sentences]
  list_meanings_sentences_marked = [list(meaning) for meaning in list_meanings_sentences]
  if noun_position == 'initial':
    for meaning in list_meanings_sentences_unmarked: meaning.append('patient')
    for meaning in list_meanings_sentences_marked: meaning.insert(-1,'patient')
  elif noun_position == 'final':
    for meaning in list_meanings_sentences_unmarked: meaning.insert(-2,'patient')
    for meaning in list_meanings_sentences_marked: meaning.insert(-1,'patient')
  list_sentences_unmarked = ['_'.join([d_words[word] for word in meaning]) for meaning in list_meanings_sentences_unmarked]  
  list_sentences_marked = ['_'.join([d_words[word] for word in meaning]) for meaning in list_meanings_sentences_marked]  
  list_sentences_unmarked = [sentence.replace('__','_') for sentence in list_sentences_unmarked]
  list_sentences_marked = [sentence.replace('__','_') for sentence in list_sentences_marked]
  list_sentences = zip(list_sentences_unmarked,list_sentences_marked)
  list_sentences_all = list_phrases + list_sentences
  list_meanings_all = list_meanings_phrases + list_meanings_sentences
  dict_sentences = OrderedDict(zip(list_meanings_all,list_sentences_all)) 
  return dict_sentences, d_words


def dict_sentence2text():
  signals =["kerura", "nagura", "sasura","sogina", "dakume", "nechibi", "tasonu",'sehi', 'gito', 'yoza']
  text_signals =["kerura", "nagura", "sasura","sogina", "dakume", "nechibi", "tasonu",'sehi', 'gito', 'yoza']
  d=OrderedDict(zip(signals,text_signals))
  return d

dict_sentence_text=dict_sentence2text()

def sentence2text(sentence):
  global dict_sentence_text
  sentence_list = sentence.split('_')
  sentence_list = [word for word in sentence_list]#REDUNDANT
  sentence_text = ' '.join([dict_sentence_text[i] for i in sentence_list])
  return sentence_text


def sentence2text_gap(sentence):
  global dict_sentence_text
  sentence_list = sentence.split('_')
  sentence_list = [word for word in sentence_list]#REDUNDANT
  gaps_list = ['_'*len(dict_sentence_text[word]) for word in sentence_list]
  if len(sentence_list) > 2:
    sentence_text = dict_sentence_text[sentence_list[0]]
    gaps_text = ' '.join(gaps_list[1:])
    sentence_text = sentence_text+' '+gaps_text
  elif len(sentence_list) <= 2:
    gaps_text = ' '.join(gaps_list)
    sentence_text = gaps_text
  return sentence_text 

'''
meanings and signals for experiment
'''

def meanings_nounPhases(condition,list_meanings,dict_meanings_byGroup):
  meanings_noun = [[meaning]*3 for meaning in dict_meanings_byGroup['Noun']]
  meanings_noun = list(itertools.chain(*meanings_noun))
  return [meanings_noun*2, meanings_noun, meanings_noun]

def get_mixed_simpleSentences(list_meanings):
  dict_meanings_byGroup = get_meaning_groups(list_meanings)
  case1 = dict_meanings_byGroup['Case']
  case2 = dict_meanings_byGroup['NNumNCase']
  indexes1 = random.sample(range(36),18)
  indexes2 = [i for i in range(36) if i not in indexes1]
  case1_sample = [case1[i] for i in indexes1]
  case2_sample = [case2[i] for i in indexes2]
  case = case1_sample+case2_sample
  case_exposure = case1_sample[:12]+case2_sample[:12]
  case_comprehension = case1_sample[12:]+case2_sample[12:]
  case_typing = random.sample(case1_sample,4) + random.sample(case2_sample,4)
  case1_sample_testing = [case1[i] for i in indexes2]
  case2_sample_testing = [case2[i] for i in indexes1]
  case_all = [case1_sample, case2_sample]
  case_rest = [case1_sample_testing, case2_sample_testing]
  return case_exposure, case_comprehension, case_typing, case_all, case_rest 

def meanings_SimplePhases(condition,list_meanings,dict_meanings_byGroup,mixed_case):
  case = mixed_case
  num = dict_meanings_byGroup['Num']
  noun = dict_meanings_byGroup['Noun']
  if condition == 'regularisation':    
    exposure = case[0]+ num + noun
    comprehension = case[1] + random.sample(num,6) + noun
    typing = case[2] + random.sample(num,4) + noun
  elif condition == 'extrapolation':
    case1 = case[3][0]
    case2 = case[3][1]
    case1_comp = random.sample(case[4][0], 10)
    case2_comp = random.sample(case[4][1], 10)
    case1_type = random.sample(case1,4)
    case2_type = random.sample(case2,4)
    num_exp = random.sample(num, 6)
    num_comp = random.sample(num, 10)
    num_type = random.sample(num, 4)  
    exposure = case1 + case2 + num + num_exp + noun*2 
    comprehension = case1_comp + case2_comp+ num_comp + noun
    typing = case1_type+case2_type+num_type+noun
  return [exposure, comprehension, typing]

def meanings_ComplexPhases(condition,list_meanings,dict_meanings_byGroup,mixed_case):
  dict_meanings_byGroup = get_meaning_groups(list_meanings)
  simple_case = mixed_case[-1]
  noun = dict_meanings_byGroup['Noun']
  numcase = dict_meanings_byGroup['NumCase']
  numcase = random.sample (numcase,len(numcase))
  num = dict_meanings_byGroup['Num']
  num_exp = random.sample(num, 6)
  num_comp = random.sample(num, 4)
  numcase_typing = random.sample(numcase[:20],4)
  case1 = simple_case[0]
  case2 = simple_case[1]
  case1_exp = case1[:6]
  case2_exp = case2[:6]
  case1_comp = simple_case[0][6:10]
  case2_comp = simple_case[1][6:10]
  exposure = numcase[:16]*3 + case1_exp + case2_exp + num_exp + noun
  comprehension = numcase[16:20]*3 + case1_comp+case2_comp+num_comp
  typing = random.sample(numcase_typing,4)+random.sample(numcase_typing,4)+random.sample(numcase_typing,4)
  if condition == 'extrapolation':
    exposure = []
    comprehension = []
    typing = typing
  return [exposure, comprehension, typing], numcase[:20]

def meanings_testing(condition,list_meanings,dict_meanings_byGroup,numcase_training):
  dict_meanings_byGroup = get_meaning_groups(list_meanings)
  noun = dict_meanings_byGroup['Noun']
  case1 = dict_meanings_byGroup['Case']
  case2 = dict_meanings_byGroup['NNumNCase']
  num = dict_meanings_byGroup['Num']
  numcase = numcase_training
  numcase_sample = random.sample(numcase,12)
  num_sample = random.sample(num, 6)
  case1_sample = random.sample(case1, 6)
  case2_sample = random.sample(case2, 6)
  testing = noun + numcase_sample + case1_sample +numcase_sample+ case2_sample + numcase_sample+ num_sample
  return [testing]


def dict_meaning_trials(condition,list_meanings):
  dict_meanings_byGroup = get_meaning_groups(list_meanings)
  list_phases = ['Noun_Training', 'Noun_Selection','Noun_Testing', 'SimplePhrase_Training','SimplePhrase_Comprehension', 'SimplePhrase_Typing', 'ComplexPhrase_Training', 'ComplexPhrase_Comprehension', 'ComplexPhrase_Typing', 'ComplexPhrase_Testing']
  mixed_case = get_mixed_simpleSentences(list_meanings)
  noun_meanings = meanings_nounPhases(condition,list_meanings,dict_meanings_byGroup)
  phase1_meanings = meanings_SimplePhases(condition,list_meanings,dict_meanings_byGroup,mixed_case)
  phase2 = meanings_ComplexPhases(condition,list_meanings,dict_meanings_byGroup,mixed_case)
  numcase_training = phase2[1]
  phase2_meanings = phase2[0]
  testing = meanings_testing(condition,list_meanings,dict_meanings_byGroup,numcase_training)
  all_meaningsList = noun_meanings+phase1_meanings+phase2_meanings+testing
  d_meanings = OrderedDict(zip(list_phases,all_meaningsList))
  return d_meanings


def dict_sentences_training(condition, condition_order, dict_sentences):
  dict_number_trials = OrderedDict(zip(['Noun','Num','Case','NNumNCase','NumCase'],[40,10,10,10,3]))#[16,4,5,4,3]
  list_meanings = dict_sentences.keys()
  dict_meanings_byGroup = get_meaning_groups(list_meanings)
  for group in dict_meanings_byGroup.keys():
    for meaning in dict_meanings_byGroup[group]:
      if meaning not in dict_meanings_byGroup['NumCase']:
        if len(meaning)<=2:
          dict_sentences[meaning] = [dict_sentences[meaning]] * dict_number_trials[group]
        else:
          dict_sentences[meaning] = [dict_sentences[meaning][0]] * dict_number_trials[group]
      else:
        if condition == 'regularisation':
          if condition_order == 'unmarked':
            dict_sentences[meaning] = [dict_sentences[meaning][0]] * (dict_number_trials[group] * 2/3) + [dict_sentences[meaning][1]] * (dict_number_trials[group] * 1/3)
          elif condition_order == 'marked':
            dict_sentences[meaning] = [dict_sentences[meaning][1]] * (dict_number_trials[group] * 2/3) + [dict_sentences[meaning][0]] * (dict_number_trials[group] * 1/3)
  return dict_sentences


'''
discrimination foils
'''

def choose_foilNoun(noun):
  object_signals = ["sogina", "dakume", "nechibi", "tasonu"]
  foil_noun = random.choice(object_signals)
  while foil_noun == noun:
    foil_noun = random.choice(object_signals)
  return foil_noun

def which_group_meaning(meaning,list_meanings):
  groups = ['Noun','Num','Case','NumCase', 'NNumNCase']
  dict_meanings_byGroup = get_meaning_groups(list_meanings)
  group_meaning = [group for group in groups if meaning in dict_meanings_byGroup[group]]
  return group_meaning[0]

def choose_foilNumber(meaning,noun_position):
  numbers = ['two','three','four']
  number = random.choice(numbers)
  if noun_position == 'initial': ind = 0
  elif noun_position == 'final': ind = 1
  if len(meaning) == 2: foil = tuple([meaning[ind]])
  elif len(meaning) == 1: 
    if noun_position == 'initial': foil = meaning + tuple([number])
    elif noun_position == 'final': foil = tuple([number]) + meaning
  return foil

def choose_foilCase(meaning,noun_position):
  foil = copy.deepcopy(meaning)
  foil = list(foil)
  if noun_position == 'initial':
    foil[3],foil[1] = foil[1],foil[3]
  elif noun_position == 'final':
    foil[4],foil[2] = foil[2],foil[4]
  foil = tuple(foil)
  return foil

def choose_foilComplex(meaning):
  foil = tuple(['pl' if feature== 'sg' else feature if feature !='pl' else 'sg' for feature in meaning])
  return foil

def choose_foilMeaning(phase, noun_position, meaning,list_meanings):
  group_meaning = which_group_meaning(meaning,list_meanings)
  if group_meaning in ['Noun', 'Num']: 
    foil = choose_foilNumber(meaning,noun_position)
  else:
    foil_case = choose_foilCase(meaning,noun_position)
    foil_complex = choose_foilComplex(meaning)
    if group_meaning == 'Case' :
      foil = foil_case
    elif group_meaning == 'NNumNCase':
      if phase != 'ComplexPhrase_Comprehension':
        foil = foil_case
      else:
        foil = random.choice([foil_case,foil_complex])
    elif group_meaning == 'NumCase':
      foil = random.choice([foil_complex,foil_case])  
  return foil

########################################################################################################################
#################################################################################
########################################################################################################################
######################  TRAINING  ##################################################################################################
#################################################################################
########################################################################################################################
########################################################################################################################


########################################################################################################################
########################## EXPOSURE  #######################################################
########################################################################################################################

def training_trial(myWin, path, meaning, sentence):
  if len(sentence.split('_'))<3: wait_time = 2
  else: wait_time = 3
  stimy=visual.ImageStim(myWin, image=meaning, units='norm',pos=[0,0.1],flipHoriz=False,flipVert=False,autoLog=True)
  texty=visual.TextStim(myWin, color='black', units='norm',pos=[0,-0.75],text=sentence2text(sentence))
  draw_fixation(myWin)
  stimy.setAutoDraw(True)
  myWin.flip()
  myWin.setMouseVisible(False)
  core.wait(1)
  texty.draw()
  myWin.flip()
  playSound(sentence,path)
  myWin.setMouseVisible(True)
  core.wait(wait_time)
  stimy.setAutoDraw(False)
  if event.getKeys(['escape']): 
      myWin.close()
      core.quit()


def exposure_trials(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, dict_meanings, dict_meaning_trials, dict_sentences_training,phase):
  global count
  meaning_trials = dict_meaning_trials[phase]
  meaning_trials = random.sample(meaning_trials,len(meaning_trials))
  for meaning in meaning_trials:
    count+=1
    meaning_file = dict_meanings[meaning]
    meaning_filename = meaning_file.replace(path+'U39_stims/images/medium/','')
    meaning_filename = meaning_filename.replace('.png','')
    sentence = dict_sentences_training[meaning].pop(random.randrange(len(dict_sentences_training[meaning])))
    training_trial(myWin, path, meaning_file, sentence)
    write_outputCSV(path,ID,condition,condition_order,noun_position, markerNum, markerCase, phase, meaning_filename, sentence2text(sentence), 'NA', 'NA', 'NA', count)
    #print dict_meanings[meaning], sentence


########################################################################################################################
####################### NOUN TESTING  #######################################################
########################################################################################################################


def noun_selection_trial(myWin,path, meaning, sentence):
  noun = sentence2text(sentence)
  foil_noun = choose_foilNoun(noun)
  positions = [[[-0.3,-0.6],'v'], [[0.3,-0.6],'n']]
  positions = random.sample(positions,2)
  stimy=visual.ImageStim(myWin, image=meaning, units='norm',pos=[0,0.1],flipHoriz=False,flipVert=False,autoLog=True)
  texty_noun=visual.TextStim(myWin, color='black', units='norm',pos=positions[0][0],text=noun)
  texty_foil=visual.TextStim(myWin, color='black', units='norm',pos=positions[1][0],text=foil_noun)
  left_key=visual.ImageStim(myWin, image=path+'keys/'+'computer_key_V.png', units='norm',pos=[-0.3,-0.8],flipHoriz=False,flipVert=False,autoLog=True)# size=[0.12,0.12]
  right_key=visual.ImageStim(myWin, image=path+'keys/'+'computer_key_N.png', units='norm', pos=[0.3,-0.8],flipHoriz=False,flipVert=False,autoLog=True)
  box1= visual.Rect(myWin, units='norm', lineWidth=2.5,width=0.25, height=0.17, pos=positions[0][0], lineColor='DimGray')
  box2= visual.Rect(myWin, units='norm', lineWidth=2.5,width=0.25, height=0.17, pos=positions[1][0], lineColor='DimGray')  
  while True:
    draw_fixation(myWin)
    stimy.setAutoDraw(True)
    myWin.flip()
    for drawing in [texty_noun, texty_foil, box1, box2, right_key, left_key]:
      drawing.setAutoDraw(True)
    myWin.flip()
    if event.getKeys(positions[0][1]):
      selection = 'correct'
      for drawing in [texty_foil, box1, box2, right_key, left_key]:
        drawing.setAutoDraw(False)
      myWin.flip()
      myWin.setMouseVisible(False)      
      playSound('soundEffects/correct',path)
      #playSound(sentence,path)
      myWin.setMouseVisible(True)
      break
    else:
      if event.getKeys(['escape']): 
          myWin.close()
          core.quit()
      elif event.getKeys(positions[1][1]):
        selection = 'wrong'
        for drawing in [texty_foil, box1, box2, right_key, left_key]:
          drawing.setAutoDraw(False)
        myWin.flip()
        myWin.setMouseVisible(False)
        playSound('soundEffects/wrong',path)
        playSound(sentence,path)
        myWin.setMouseVisible(True)
        break
  event.clearEvents()
  texty_noun.setAutoDraw(False)
  stimy.setAutoDraw(False)
  return selection

def noun_selection(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, dict_meanings,dict_meaning_trials, dict_sentences_training,phase):
  global count
  meaning_trials = dict_meaning_trials[phase]
  meaning_trials = random.sample(meaning_trials,len(meaning_trials))
  for meaning in meaning_trials:
    count+=1
    meaning_file = dict_meanings[meaning]
    meaning_filename = meaning_file.replace(path+'U39_stims/images/medium/','')
    meaning_filename = meaning_filename.replace('.png','')
    sentence = dict_sentences_training[meaning].pop()
    selection = noun_selection_trial(myWin, path, meaning_file, sentence)
    write_outputCSV(path,ID,condition,condition_order,noun_position, markerNum, markerCase, phase, meaning_filename, sentence2text(sentence), selection,'NA', 'NA', count)


def noun_production_trial(myWin, meaning, sentence):
  stimy=visual.ImageStim(myWin, image=meaning, units='norm',pos=[0,0.1],flipHoriz=False,flipVert=False,autoLog=True)
  texty=visual.TextStim(myWin, color='black', units='norm',pos=[0,-0.75],text=sentence2text_gap(sentence)+'?')
  draw_fixation(myWin)
  stimy.draw()
  texty.draw()
  myWin.flip() 
  while True:
      keys = event.getKeys()
      if 'return' in keys: break; event.clearEvents()
      if 'escape' in keys: myWin.close(); core.quit()

def noun_production(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, dict_meanings,dict_meaning_trials, dict_sentences_training,phase):
  global count
  meaning_trials = dict_meaning_trials[phase]
  meaning_trials = random.sample(meaning_trials,len(meaning_trials))
  for meaning in meaning_trials:
    count+=1
    meaning_file = dict_meanings[meaning]
    meaning_filename = meaning_file.replace(path+'U39_stims/images/medium/','')
    meaning_filename = meaning_filename.replace('.png','')
    sentence = dict_sentences_training[meaning].pop()
    noun_production_trial(myWin, meaning_file, sentence)
    write_outputCSV(path,ID,condition,condition_order,noun_position, markerNum, markerCase, phase, meaning_filename, sentence2text(sentence), 'NA','NA','NA', count)
    feedback_trial(myWin,path,meaning_file,sentence,'',phase, noun_position)

########################################################################################################################
####################### TYPING  #######################################################
########################################################################################################################


def typing_trial(myWin,meaning,sentence):
  sentence2show = sentence2text_gap(sentence)
  words_sentence = sentence2show.split(' ')
  if len(words_sentence)>2:
    verb = words_sentence[0]+' '
    gaps = sentence2show.replace(verb,'')
  else: verb = ''; gaps = sentence2show
  text=""
  shifton=0 # allows caps and ?'s etc
  stimy=visual.ImageStim(myWin, image=meaning, units='norm',pos=[0,0.1],flipHoriz=False,flipVert=False,autoLog=True)
  #initial_texty=visual.TextStim(myWin, color='black', units='norm',pos=[0,-0.75],text=sentence2show+'?')
  while event.getKeys(keyList=['return'])==[] or text=="":
      letterlist=event.getKeys(keyList=['q','w','e','r','t','y','u','i','o','p','a','s','d','f',
          'g','h','j','k','l','z','x','c','v','b','n','m','lshift','rshift','period','space','apostrophe','comma','1','slash','backspace'])
      for l in letterlist:
          if shifton:
              if l == 'space':
                  text+=' '
              elif l == 'slash':
                  text+='?'
              elif l == '1':
                  text+='!'
              elif len(l) > 1:
                  pass
              elif l !='backspace':
                  text+=l.upper()
              shifton=0
          elif shifton == 0:
      #if key isn't backspace, add key pressed to the string
              if len(l) > 1:
                  if l == 'space':
                      text+=' '
                  elif l == 'period':
                      text+='.'
                  elif (l == 'lshift') | (l == 'rshift'):
                      shifton=1
                  elif l == 'comma':
                      text+=','
                  elif l == 'apostrophe':
                      text+='\''
                  elif l == 'backspace':
                      text=text[:-1]
                  elif l == 'slash':
                      text+='/'
                  else:
                      pass
              elif l == '1':
                  pass
              else: # it would have to be a letter at this point
                  text+=l
              #otherwise, take the last letter off the string
      #continually redraw text onscreen until return pressed
      typedLetters = len(text)
      response = visual.TextStim(myWin, text=verb+text+gaps[typedLetters:],color="black",units = 'norm', pos = [0,-0.75])        
      # if len(text)==0:
      #   initial_texty.draw()
      # elif len(text)!=0: 
      response.draw()
      stimy.draw()
      myWin.flip()
  return verb+text.strip()

def reverse_NumCase(sentence,noun_position):
  s = copy.deepcopy(sentence)
  s = s.split()
  if noun_position == 'initial':
    s[4],s[3] = s[3],s[4]
  elif noun_position == 'final':
    s[3],s[2] = s[2],s[3]
  s = ' '.join(s)
  return s

def feedback_trial(myWin,path,meaning,sentence,response,phase,noun_position):
  written_sentence = sentence2text(sentence)
  #alternative_sentence = reverse_NumCase(written_sentence,noun_position)
  stimy=visual.ImageStim(myWin, image=meaning, units='norm',pos=[0,0.1],flipHoriz=False,flipVert=False,autoLog=True)
  texty=visual.TextStim(myWin, color='black', units='norm',pos=[0,-0.75],text=written_sentence)
  draw_fixation(myWin)
  stimy.setAutoDraw(True)
  texty.setAutoDraw(True)
  myWin.flip()
  myWin.setMouseVisible(False)
  if response != '':
    if written_sentence == response:
      playSound('soundEffects/correct',path)
    #if phase == 'ComplexPhrase_Typing' and alternative_sentence == response:
      #playSound('soundEffects/correct',path)   
    elif written_sentence != response:
      playSound('soundEffects/wrong',path)
  playSound(sentence,path)
  myWin.setMouseVisible(True)
  stimy.setAutoDraw(False)
  texty.setAutoDraw(False)
  if event.getKeys(['escape']): 
      myWin.close()
      core.quit()
  event.clearEvents()

def sentence_typing(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, dict_meanings,dict_meaning_trials, dict_sentences_training, d_sentences, phase):
  global count
  meaning_trials = dict_meaning_trials[phase]
  if phase !='ComplexPhrase_Typing':
    meaning_trials = random.sample(meaning_trials,len(meaning_trials))
  for meaning in meaning_trials:
    count+=1
    meaning_file = dict_meanings[meaning]
    meaning_filename = meaning_file.replace(path+'U39_stims/images/medium/','')
    meaning_filename = meaning_filename.replace('.png','')
    if phase != 'ComplexPhrase_Typing': sentence = dict_sentences_training[meaning].pop()
    else: sentence = d_sentences[meaning][0]
    response = typing_trial(myWin, meaning_file, sentence)
    if phase != 'ComplexPhrase_Typing':
      feedback_trial(myWin,path,meaning_file,sentence,response,phase,noun_position)
    write_outputCSV(path,ID,condition,condition_order,noun_position, markerNum, markerCase, phase, meaning_filename, sentence2text(sentence), 'NA',response,'NA', count)

########################################################################################################################
####################### COMPREHENSION  #######################################################
########################################################################################################################

def meaning_discrimination_trial(myWin,path,noun_position,meaning_atributes,sentence,phase,dict_meanings_discrimination):
  meaning=meaning_atributes
  foil = choose_foilMeaning(phase, noun_position, meaning,dict_meanings_discrimination.keys())
  texty=visual.TextStim(myWin, color='black', units='norm',pos=[0,-0.75],text=sentence2text(sentence))
  positions=[[[-0.45,0.1],'v'],[[0.45,0.1],'n']]
  positions = random.sample(positions,2)
  right_key = positions[0][1]
  wrong_keys = [wrong_key[1] for wrong_key in positions[1:]]
  box0= visual.Rect(myWin, units='norm', lineWidth=4.5,width=0.8, height=0.8, pos=positions[0][0], lineColor='DimGray')
  box1= visual.Rect(myWin, units='norm', lineWidth=4.5,width=0.8, height=0.8, pos=positions[1][0], lineColor='DimGray')
  leftScreen_key=visual.ImageStim(myWin, image=path+'keys/'+'computer_key_V.png', units='norm', pos=[-0.45,-0.45],flipHoriz=False,flipVert=False,autoLog=True)
  rightScreen_key=visual.ImageStim(myWin, image=path+'keys/'+'computer_key_N.png', units='norm', pos=[0.45,-0.45],flipHoriz=False,flipVert=False,autoLog=True)
  image1= visual.ImageStim(myWin, dict_meanings_discrimination[meaning], units='norm', pos=positions[0][0],flipHoriz=False,flipVert=False,autoLog=True)
  image2= visual.ImageStim(myWin, dict_meanings_discrimination[foil], units='norm', pos=positions[1][0], flipHoriz=False,flipVert=False,autoLog=True)
  play_sound=0
  while True:
    play_sound+=1
    draw_fixation(myWin)
    for drawing in [image1, image2, box0, box1, rightScreen_key, leftScreen_key]:
      drawing.setAutoDraw(True)
    myWin.flip()
    core.wait(0.5)
    texty.setAutoDraw(True)
    myWin.flip()
    if play_sound==1:
      myWin.setMouseVisible(False)
      playSound(sentence,path)
      myWin.setMouseVisible(True) 
    if event.getKeys(right_key):
      selection = 'correct'
      for drawing in [image2, box0, box1, rightScreen_key, leftScreen_key]:
         drawing.setAutoDraw(False)
      myWin.flip()
      myWin.setMouseVisible(False)
      playSound('soundEffects/correct',path)
      myWin.setMouseVisible(True)
      break
    else:
      keys = event.getKeys()
      if 'escape' in keys: 
          myWin.close()
          core.quit()
      elif any(k in wrong_keys for k in keys):
        selection = 'wrong'
        if list(keys[-1]) not in wrong_keys: keys = random.choice(wrong_keys)
        for drawing in [image2, box0, box1, rightScreen_key, leftScreen_key]:
          drawing.setAutoDraw(False)
        myWin.flip()
        myWin.setMouseVisible(False)
        playSound('soundEffects/wrong',path)
        playSound(sentence,path)
        myWin.setMouseVisible(True)
        break
  event.clearEvents()
  texty.setAutoDraw(False)
  image1.setAutoDraw(False)
  return selection


def discrimination_trials(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, dict_meanings_discrimination,dict_meaning_trials, dict_sentences_training,phase):
  global count
  meaning_trials = dict_meaning_trials[phase]
  meaning_trials = random.sample(meaning_trials,len(meaning_trials))
  for meaning in meaning_trials:
    count+=1
    meaning_file = dict_meanings_discrimination[meaning]
    meaning_filename = meaning_file.replace(path+'U39_stims/images/small/','')
    meaning_filename = meaning_filename.replace('.png','')
    sentence = dict_sentences_training[meaning].pop()
    selection = meaning_discrimination_trial(myWin,path,noun_position,meaning,sentence,phase,dict_meanings_discrimination)
    write_outputCSV(path,ID,condition,condition_order,noun_position, markerNum, markerCase, phase, meaning_filename, sentence2text(sentence), selection, 'NA','NA', count)

########################################################################################################################
####################### TESTING #######################################################
########################################################################################################################

def phrase_testing_trial(myWin, meaning, sentence):
  fillIn_sentence = sentence2text_gap(sentence)
  stimy=visual.ImageStim(myWin, image=meaning, units='norm',pos=[0,0.1],flipHoriz=False,flipVert=False,autoLog=True)
  texty=visual.TextStim(myWin, color='black', units='norm',pos=[0,-0.75],text=fillIn_sentence)
  draw_fixation(myWin)
  stimy.draw()
  texty.draw()
  myWin.flip()
  core.wait(1.5)
  while True:
    keys = event.getKeys()
    if 'return' in keys: break; event.clearEvents()
    if 'escape' in keys: myWin.close(); core.quit() 
  


def phrase_testing(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, dict_meanings, dict_meaning_trials, d_sentences, phase):
  global count
  list_meanings = dict_meanings.keys()
  dict_meanings_byGroup = get_meaning_groups(list_meanings)
  meaning_trials = dict_meaning_trials[phase]
  meaning_trials = random.sample(meaning_trials,len(meaning_trials))
  for meaning in meaning_trials:
    count+=1
    meaning_file = dict_meanings[meaning]
    meaning_filename = meaning_file.replace(path+'U39_stims/images/medium/','')
    meaning_filename = meaning_filename.replace('.png','')
    if meaning not in dict_meanings_byGroup['Num']+dict_meanings_byGroup['Noun']: 
      sentence = d_sentences[meaning][0]
    else: sentence = d_sentences[meaning]
    phrase_testing_trial(myWin, meaning_file, sentence)
    write_outputCSV(path,ID,condition,condition_order,noun_position, markerNum, markerCase, phase, meaning_filename, sentence2text(sentence), 'NA','NA','NA', count)
    if meaning not in dict_meanings_byGroup['NumCase']:
      feedback_trial(myWin,path,meaning_file,sentence,'',phase,noun_position)


########################################################################################################################
####################### Experiment #######################################################
########################################################################################################################

count = 0
def experiment(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, dict_meanings_all, dict_sentences):
  global count
  d_meanings = dict_meanings_all[0]
  d_meanings_discrimination = dict_meanings_all[1]
  list_meanings = d_meanings.keys()
  d_meaning_trials = dict_meaning_trials(condition,list_meanings)
  d_sentences = copy.deepcopy(dict_sentences)
  d_sentences_training = dict_sentences_training(condition, condition_order, dict_sentences)
  potential_training_phases = [phase for phase in d_meaning_trials.keys() if 'Train' in phase]
  if condition == 'regularisation': phases = potential_training_phases
  if condition == 'extrapolation': phases = potential_training_phases[:-1]
  instructions_NounTraining(myWin,path)
  for phase in phases[:]:
    exposure_trials(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, d_meanings, d_meaning_trials, d_sentences_training,phase)
    if phase == 'Noun_Training':
      instructions_NounSelection(myWin, path)
      noun_selection(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, d_meanings, d_meaning_trials, d_sentences_training, 'Noun_Selection')
      instructions_NounTesting(myWin,path)
      noun_production(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, d_meanings, d_meaning_trials, d_sentences_training, 'Noun_Testing')
      instructions_simplePhraseTraining(myWin,path)
    if phase == 'SimplePhrase_Training':
      instructions_comprehension(myWin, path)
      discrimination_trials(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, d_meanings_discrimination, d_meaning_trials, d_sentences_training,'SimplePhrase_Comprehension')
      instructions_simplePhraseTyping(myWin, path)
      sentence_typing(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, d_meanings, d_meaning_trials, d_sentences_training, d_sentences,'SimplePhrase_Typing')        
      if condition == 'regularisation':
        instructions_complexPhraseTraining(myWin, path)
    if phase == 'ComplexPhrase_Training':
      instructions_complexPhraseComprehension(myWin, path)
      discrimination_trials(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, d_meanings_discrimination, d_meaning_trials, d_sentences_training,'ComplexPhrase_Comprehension')
  instructions_complexPhrasetyping(myWin,path,condition)
  sentence_typing(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, d_meanings, d_meaning_trials, d_sentences_training, d_sentences,'ComplexPhrase_Typing')
  instructions_PhraseTesting(myWin,path,condition)
  phrase_testing(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, d_meanings, d_meaning_trials, d_sentences, 'ComplexPhrase_Testing')

########################################################################################################################
########################## DATA HANDLING #######################################################
########################################################################################################################

def set_outputCSV(path,ID):
    file=path+'data/%s_responses.csv'%(ID)
    if os.path.isfile(file)==False:
      with open(file,'wb') as f:
          w = csv.writer(f)
          w.writerow(['ID','Condition','MajorityOrder','NounPosition','markerNum', 'markerCase', 'Phase', 'Meaning', 'NounItem', 'Noun', 'binaryResp', 'InputSentence', 'Selection', 'TypedResponse', 'SpokenResponse', 'AnswerQuest', 'Trial', 'date&time'])
      f.close()
    else:
      print 'You already ran that participant!'
      sys.exit()
    

def write_outputCSV(path,ID,condition,condition_order,noun_position, markerNum, markerCase, phase, meaning_filename, sentence, selection, typed_response, repsonse_questionnaire,trial):
    global d_words
    #get the nounItem and the noun for each target trial
    meaning_list = meaning_filename.split('_')
    if phase in ['ComplexPhrase_Typing','ComplexPhrase_Testing'] and meaning_list[-1]=='pl':
      nounItem = meaning_filename.split('_')[-2]
      noun = d_words[nounItem]
    else: nounItem = 'NA'; noun = 'NA'
    #store data
    file=path+'data/%s_responses.csv'%(ID)
    #remember to open file with a and not w
    with open(file, 'a') as f:
        w=csv.writer(f)
        w.writerow([ID,condition,condition_order,noun_position, markerNum, markerCase, phase, meaning_filename, nounItem, noun, '',sentence, selection, typed_response, '', repsonse_questionnaire, trial, time.asctime()])
    f.close()

########################################################################################################################
#####################################################INSTRUCTIONS &###########################################################
#######################################################MESSAGES#######################################################

def pre_experiment_screen(myWin,path):
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=900, color='black',text="""Press the return key to start the experiment.""")
  next_page=visual.ImageStim(myWin, image=path+'keys/return_key.png', units='norm', size=[0.2,0.3],pos=[0.7,-0.6],flipHoriz=False,flipVert=False,autoLog=True)
  #next_tag= visual.TextStim(myWin, color='black', units='norm', pos=[0.45,-0.6], text='Start')
  instrText.draw()
  next_page.draw()
  #next_tag.draw()
  myWin.flip()
  while True:
      keys = event.getKeys()
      if 'return' in keys: break
      if 'escape' in keys: core.quit()

def instructions_NounTraining(myWin,path):
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=900, color='black',text="""Konichiwa! \n\nMy name is Maki. I am here to help you learn my native language. It is called: Yurani.  \n\nIf you can learn to speak just like me, then you will have learned Yurani successfully. \n\nWe will start with something easy.""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False)
  playSound('instructions/intro1',path)
  myWin.setMouseVisible(True) 
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=900, color='black',text="""First, I will teach you the names of some characters in Yurani.  \n\nI will show you the pictures of the characters and say their name in my language. \n\nYou must REPEAT the names aloud after me. \n\nPress the return key when you're ready to get started.""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False) 
  playSound('instructions/intro2',path)
  myWin.setMouseVisible(True) 
  while True:
      keys = event.getKeys()
      if 'return' in keys: break
      if 'escape' in keys: core.quit()

def instructions_NounSelection(myWin, path):
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=900, color='black',text="""Ok. Now it is time to take a short test on what you have learned so far. \n\nI will show you pictures of characters and you will have to select their correct names in Yurani. \n\nUse the keyboard to SELECT THE CORRECT NAME. \n\nPress the return key when you're ready to start the test. """)
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False)
  playSound('instructions/nounSelection',path)
  myWin.setMouseVisible(True) 
  while True:
    keys = event.getKeys()
    if 'return' in keys: break
    if 'escape' in keys: core.quit()

def instructions_NounTesting(myWin,path):
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=900, color='black',text="""Good job!  \n\nBefore we move on to the next training phase, I want to see how well you can speak Yurani. \n\nI will now show you pictures of characters and you will have to SAY THEIR NAME IN YURANI. \n\nSpeak clearly into the microphone in front of you, and press the return key to submit your answer. \n\nPress the return key when you're ready to start speaking!""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False)
  playSound('instructions/NounProduction',path)
  myWin.setMouseVisible(True) 
  while True:
    keys = event.getKeys()
    if 'return' in keys: break
    if 'escape' in keys: core.quit()

def instructions_simplePhraseTraining(myWin,path):
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""Well done! You have made it through the first tests!  \n\nPress the return key to hear about your next task.""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False)
  playSound('instructions/simplePhraseTraining1',path)
  myWin.setMouseVisible(True)
  while True:
    keys = event.getKeys()
    if 'return' in keys: break
    if 'escape' in keys: core.quit()
  event.clearEvents()
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""In this part of your training, I will show you pictures as before, but this time, what I will say will be a bit more complex.  \n\nThe pictures you will see will look familiar, but they will illustrate some other features of Yurani.  \n\nLOOK at the pictures, LISTEN, and REPEAT aloud after me. \n\nPress the return key when you are ready to start.""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False) 
  playSound('instructions/simplePhraseTraining2',path)
  myWin.setMouseVisible(True) 
  while True:
    keys = event.getKeys()
    if 'return' in keys: break
    if 'escape' in keys: core.quit()

def instructions_comprehension(myWin, path):
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""Ok. Now it is time to further test your understanding of Yurani. \n\nI will say a sentence in Yurani and you will have to SELECT THE PICTURE it describes. \n\nUse the keyboard to select your answer. \n\nPress the return key when you're ready to start the test.""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False)
  playSound('instructions/PhraseComprehension',path)
  myWin.setMouseVisible(True) 
  while True:
    keys = event.getKeys()
    if 'return' in keys: break
    if 'escape' in keys: core.quit()


def instructions_simplePhraseTyping(myWin, path):
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""Ok. Now it is time to take another short test on what you have learned.  \n\nThis time I will show you pictures and you will have to TYPE IN their corresponding descriptions in Yurani.   \n\nTo make this task easier, you will be able to see the blanks you need to fill in to complete each description. \n\nUse the keyboard to FILL IN THE BLANKS and press the return key to submit your answer. \n\nPress the return key when you're ready to start typing!""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False)
  playSound('instructions/simplePhraseTyping',path)
  myWin.setMouseVisible(True) 
  while True:
    keys = event.getKeys()
    if 'return' in keys: break
    if 'escape' in keys: core.quit()

def instructions_complexPhraseTraining(myWin, path):
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""Good job! Now, in this last part of your training, I will show you pictures as before, but what I say will be even more complex. \n\nYou will see pictures you are already familiar with, as well as new pictures that will illustrate further features of Yurani. \n\nLOOK at the pictures, LISTEN, and REPEAT aloud after me. \n\nPress the return key when you are ready to start.""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False)
  playSound('instructions/regularisation_complexPhraseTraining',path)
  myWin.setMouseVisible(True) 
  while True:
    keys = event.getKeys()
    if 'return' in keys: break
    if 'escape' in keys: core.quit()

def instructions_complexPhraseComprehension(myWin, path):
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""Ok. Now it is time to further test your understanding of Yurani. \n\nI will say a sentence in Yurani and you will have to SELECT THE PICTURE it describes. \n\nUse the keyboard to select your answer. \n\nPress the return key when you're ready to start the test.""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False)
  playSound('instructions/regularisation_complexPhraseComprehension',path)
  myWin.setMouseVisible(True) 
  while True:
    keys = event.getKeys()
    if 'return' in keys: break
    if 'escape' in keys: core.quit()

def instructions_complexPhrasetyping(myWin,path,condition):
  if condition == 'regularisation':
    instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""Well done! Now, before you move on to the final test, I want to make sure you are ready for the challenge with one more simple task. \n\nI will show you pictures and you will have to type in their corresponding descriptions in Yurani.  \n\nAs before, use the keyboard to TYPE IN THE DESCRIPTIONS and press the return key to submit your answers. \n\nPress the return key when you're ready to start the test.""")
  elif condition == 'extrapolation':
    instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""Well done! Now, before you move on to the final test, I want to make sure you are ready for the challenge with one more simple task. \n\n I will show you pictures, and although I have not described them for you before, you will have to type in their corresponding descriptions using the Yurani I have already taught you.  \n\nAs before, use the keyboard to TYPE IN THE DESCRIPTIONS and press the return key to submit them. \n\nPress the return key when you're ready to start.""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False)
  playSound('instructions/%s_complexPhraseTyping'%(condition),path)
  myWin.setMouseVisible(True) 
  while True:
    keys = event.getKeys()
    if 'return' in keys: break
    if 'escape' in keys: core.quit()

def instructions_PhraseTesting(myWin,path,condition):
  if condition == 'regularisation':
    instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""Ok, you are now ready for your final test: it is time for you to speak again!  \n\nI will show you pictures, and you must provide their corresponding descriptions in Yurani.""")
  elif condition == 'extrapolation':
    instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""Ok, you are now ready for your final test: it is time for you to speak again!  \n\nI will show you pictures, and although you have not heard the descriptions for all of them before, you will have to describe them using the Yurani you already know.""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False)
  playSound('instructions/%s_complexPhraseTesting1'%(condition),path)
  myWin.setMouseVisible(True) 
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""As in previous tasks, I will help you by providing some words but this time you will have to COMPLETE THE DESCRIPTIONS ORALLY.  \n\nSpeak clearly into the microphone in front of you and press the return key to submit your answer. \n\nYou will be provided with feedback every now and then to help you refresh your memory. \n\nPress the return key when you are ready to start speaking!""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False) 
  playSound('instructions/complexPhrasetesting2',path)
  myWin.setMouseVisible(True) 
  while True:
      keys = event.getKeys()
      if 'return' in keys: break
      if 'escape' in keys: core.quit()


def instructions_questionnaire(myWin, path):
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""Well done! \n\nThat is all the Yurani you will learn today.  Thank you very much for your interest in my language.  \n\nBefore you leave, I would like to ask you some questions about certain features of Yurani. \n\nPress the return key to start answering the questions.""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False)
  playSound('instructions/questionnaire',path)
  myWin.setMouseVisible(True) 
  while True:
    keys = event.getKeys()
    if 'return' in keys: break
    if 'escape' in keys: core.quit()

def post_experiment_screen(myWin,path):
  instrText = visual.TextStim(myWin,pos=(0,0), units='pix', height=40, wrapWidth=950, color='black',text="""That is all! \n\nYou are now finished. \n\nArigato, yoi hi wo!!!""")
  instrText.draw(); myWin.flip()
  myWin.setMouseVisible(False)
  playSound('instructions/farewell',path)
  myWin.setMouseVisible(True) 
  while True:
      keys = event.getKeys()
      if 'return' in keys: break
      if 'escape' in keys: core.quit()


########################################################################################################################
####################### POST-TESTING #######################################################
########################################################################################################################


def meaning_marker(myWin, markerInfo):
  marker = markerInfo[0]
  question = "What does '%s' describe in Yurani?"%(marker)
  answer = getAndShow(myWin,question)
  return answer, 'Meaning'+markerInfo[1]


def order_markerNoun(myWin, markerInfo):
  marker = markerInfo[0]
  question = "In the descriptions you were trained on, did '%s' appear before or after the name of the character it referred to?"%(marker)
  answer = getAndShow(myWin,question)
  return answer, 'Order'+markerInfo[1]+'Noun'

def order_markers(myWin, markerNum, markerCase, noun_position):
  if noun_position == 'initial':
    direction = 'after'
  elif noun_position == 'final':
    direction = 'before'
  question = "And when both '%s' and '%s' appeared %s the name of the character it referred to, did '%s' appear before '%s', after '%s', or both?"%(markerNum, markerCase,direction,markerNum, markerCase, markerCase)
  answer = getAndShow(myWin,question)
  return answer, 'OrderNumCase'


def rate_freq(myWin, markerNum, markerCase, noun_position):
  if noun_position == 'initial':
    direction = 'before'
  elif noun_position == 'final':
    direction = 'after'
  question = "During your training in Yurani, when both '%s' and '%s' appeared together, what percentage of the time did '%s' appear %s '%s'?" % (markerNum,markerCase,markerNum,direction,markerCase)
  ratingScale = visual.RatingScale(
    myWin, low=0, high=100, markerStart=5, precision =1, pos = (0.0, 0.0), lineColor = 'blue', textColor='black',
    leftKeys='left', rightKeys = 'right', acceptKeys='return', scale = "0% = never ... 100% = all the time ")
  item = visual.TextStim(myWin, color='DimGray', units='norm',pos=[0,0.75],text= question, wrapWidth = 1.5)
  while ratingScale.noResponse:
      item.draw()
      ratingScale.draw()
      myWin.flip()
      if 'return' in event.getKeys():
        break
  rating = ratingScale.getRating()
  return rating, 'FrequencyNNumCase'

def languages_spoken(myWin):
  question = 'What languages do you speak fluently?'
  answer = getAndShow(myWin,question)
  return answer, 'Languages'


def post_experimental_questionnaire(myWin,path,ID,condition,condition_order,noun_position, markerNum, markerCase, phase):
  markers = random.sample([[markerNum,'Num'],[markerCase,'Case']],2)
  selection_marker1 = meaning_marker(myWin,markers[0])
  selection_marker2 = meaning_marker(myWin,markers[1])
  selection_marker1_noun = order_markerNoun(myWin,markers[0])
  selection_marker2_noun = order_markerNoun(myWin,markers[1])
  if condition == 'regularisation':
    selection_marker_marker = order_markers(myWin,markerNum,markerCase,noun_position)
    selection_frequency = rate_freq(myWin,markerNum,markerCase,noun_position)
  spoken_languages = languages_spoken(myWin)
  if condition == 'regularisation':
    selections = [selection_marker1, selection_marker2, selection_marker1_noun, selection_marker2_noun ,selection_marker_marker, selection_frequency,spoken_languages]
  elif condition == 'extrapolation':
    selections = [selection_marker1, selection_marker2, selection_marker1_noun, selection_marker2_noun,spoken_languages]
  for selection in selections:
    write_outputCSV(path,ID,condition,condition_order,noun_position, markerNum, markerCase, phase, 'NA', 'NA', 'NA','NA',selection[0], selection[1])


########################################################################################################################
############################ typing ###########################################################
############################### #######################################################

def getAndShow(wptr,instructionsToShow):
    text=""
    shifton=0 # allows caps and ?'s etc
    instructions = visual.TextStim(wptr, text=instructionsToShow,color="DimGray",units='norm',pos=[0,0.6], wrapWidth = 1.5)
    while event.getKeys(keyList=['return'])==[]:
        letterlist=event.getKeys(keyList=['q','w','e','r','t','y','u','i','o','p','a','s','d','f',
            'g','h','j','k','l','z','x','c','v','b','n','m','lshift','rshift','period','space','apostrophe','comma','1','slash','backspace'])
        for l in letterlist:
            if shifton:
                if l == 'space':
                    text+=' '
                elif l == 'slash':
                    text+='?'
                elif l == '1':
                    text+='!'
                elif len(l) > 1:
                    pass
                elif l !='backspace':
                    text+=l.upper()
                shifton=0
            elif shifton == 0:
        #if key isn't backspace, add key pressed to the string
                if len(l) > 1:
                    if l == 'space':
                        text+=' '
                    elif l == 'period':
                        text+='.'
                    elif (l == 'lshift') | (l == 'rshift'):
                        shifton=1
                    elif l == 'comma':
                        text+=','
                    elif l == 'apostrophe':
                        text+='\''
                    elif l == 'backspace':
                        text=text[:-1]
                    elif l == 'slash':
                        text+='/'
                    else:
                        pass
                elif l == '1':
                    pass
                else: # it would have to be a letter at this point
                    text+=l
                #otherwise, take the last letter off the string
        #continually redraw text onscreen until return pressed
        response = visual.TextStim(wptr, text=text+'_',color="black",units = 'norm', pos = [0,0] )
        response.draw()
        instructions.draw()
        wptr.flip()
    return text

