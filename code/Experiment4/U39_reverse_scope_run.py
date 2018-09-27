from psychopy import core, gui
from psychopy import visual, event
from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import sound
from U39_reverse_scope import *
from os.path import expanduser


'''get participant's info'''
info = {"Participant's ID":''}#,"Code Condition":''}
infoDlg = gui.DlgFromDict(dictionary=info, title='U39', fixed=['ExpVersion1'])
if infoDlg.OK:
    print info        
else: print 'User Cancelled'

ID = info["Participant's ID"]
#code = info["Code Condition"]
code = ID[0]
condition_paramaters= get_condition(code)
condition = condition_paramaters[0]
condition_order = condition_paramaters[1]
noun_position = condition_paramaters[2]
home = expanduser("~")
path = home+"/Desktop/U39Lab/"

'''set up csv to store data'''
set_outputCSV(path,ID)

''' get meanings and signals '''
dict_signals = dict_sentences(noun_position)
dict_sentences =  dict_signals[0]
dict_words = dict_signals[1]
markerNum = sentence2text(dict_words['two'])
markerCase = sentence2text([dict_words['patient1'],dict_words['patient2']])
dict_meanings_all=dict_meanings(path,'medium', 'small', noun_position)


myWin = visual.Window((1440, 900),color='white', allowGUI=True,monitor='testMonitor', units ='pix', fullscr=True)

pre_experiment_screen(myWin,path)
experiment(myWin, path, ID, condition, condition_order, noun_position, markerNum, markerCase, dict_meanings_all, dict_sentences)
instructions_questionnaire(myWin, path)
post_experimental_questionnaire(myWin,path,ID,condition,condition_order,noun_position, markerNum, markerCase, 'Questionnaire')
post_experiment_screen(myWin,path)
