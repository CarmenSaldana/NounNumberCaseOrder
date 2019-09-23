# Cognitive constraints on number and case morpheme orders: experimental code and data sets

This repository contains all the materials needed to run the experiments and analyses reported in in Saldana, Yohei & Culbertson (submitted) ''Cross-linguistic patterns of morpheme order reflect cognitive biases: An experimental study of case and number morphology''.

##Experimental code

This repository contains all the materials needed to run the reported experiment using the ``PsychoPy2`` standalone (python 2.7). The versions of the code provided are set to to run on a 13” screen as well as on a 27”. [Caveat: If you are running the code on the terminal instead, make sure you have PsychoPy installed as well as all the other required packages specified in the header of the two .py files contained in this folder.]

## Running the experiments

### Prior to running the experiment:

1. Create a ``U39Lab`` folder on your desktop and add the two ``.py`` scripts contained on the code folder of the experiment you wish to run (e.g., in ``code/code_exp1_english`` if you wish to run Experiment 1).  

2. Add the ``keys`` folder and the ``U39_stims`` folder to it, unzip all folders within. 

3. When you unzip ``U39_stims/sentences/all/phrases`` and ``U39_stims/sentences/allJPN/phrases``you will need to run the ``combinePhrases.py`` file to generate all the sentences used as stimuli. Then move all the geenrated sentences on folder up to ``U39_stims/sentences/all`` or ``U39_stims/sentences/allJPN`` accordingly; the ``instructions`` and ``soundeffects`` folders should also be there (as folders). 

4. Create a ``data`` folder within ``U39Lab`` where the data will be stored.

### When all of this is set up:

Run the ``_run.py`` script that now you have in the ``U39Lab`` folder to run the experiment (e.g., ``U39_reverse_run.py`` if you wish to run Experiment 1). Alternatively, change the necessary paths (the other .py file contains the experiment and it is imported in the file to run it).










