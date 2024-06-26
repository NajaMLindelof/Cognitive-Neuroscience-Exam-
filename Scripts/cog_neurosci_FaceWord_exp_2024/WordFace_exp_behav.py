# -*- coding: utf-8 -*-
""" DESCRIPTION:
This fMRI/MEEG/behavioral experiment displays 3 different types of words 
(positive, negative, neutral), followed by a break and one of two different 
emoji faces (happy and fearful). 
Participants have to judge happy or fearful faces with buttonpresses 'y' and 'b'.
The experiment lasts 5-10 minutes per session (dependent on MEEG/behavioral 
or fMRI) and each session has 60 trials.
The script awaits a trigger pulse from the scanner or keyboard with the value "t"

/Mikkel Wallentin & Roberta Rocca 2019 (with some of the code adapted from 
Jonas LindeLoev: https://github.com/lindeloev/psychopy-course/blob/master/ppc_template.py)

Structure: 
    SET VARIABLES
    GET PARTICIPANT INFO USING GUI
    SPECIFY TIMING AND MONITOR
    STIMULI
    OUTPUT
    FUNCTIONS FOR EXPERIMENTAL LOOP
    DISPLAY INTRO TEXT AND AWAIT SCANNER TRIGGER
    CALL FUNCTION RUNNING THE EXPERIMENTAL LOOP

"""

# Import the modules that we need in this script
from __future__ import division
from psychopy import core, visual, event, gui, monitors, event
from random import sample
import pandas as pd
#Import local scripts
import ppc
import numpy as np



"""
SET VARIABLES
"""
# Monitor parameters
MON_DISTANCE = 60  # Distance between subject's eyes and monitor 
MON_WIDTH = 40  # Width of your monitor in cm
MON_SIZE = [1200, 1000]  # Pixel-dimensions of your monitor
FRAME_RATE=60 # Hz
SAVE_FOLDER = 'faceWord_exp_data'  # Log is saved to this folder. The folder is created if it does not exist.


"""
GET PARTICIPANT INFO USING GUI
"""
# Intro-dialogue. Get subject-id and other variables.
# Save input variables in "V" dictionary (V for "variables")
V= {'ID':'','exp type':['fMRI','EEG','behavioral'],'session':[1,2,3,4,5,6],'Scan day': 
    ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],'gender':['female','male','other'],'age':''}
if not gui.DlgFromDict(V, order=['ID','exp type','Scan day', 'age', 'session','gender']).OK: # dialog box; order is a list of keys 
    core.quit()

"""
SPECIFY TIMING AND MONITOR
"""

# Clock and timer
clock = core.Clock()  # A clock wich will be used throughout the experiment to time events on a trial-per-trial basis (stimuli and reaction times).

# Create psychopy window
my_monitor = monitors.Monitor('testMonitor', width=MON_WIDTH, distance=MON_DISTANCE)  # Create monitor object from the variables above. This is needed to control size of stimuli in degrees.
my_monitor.setSizePix(MON_SIZE)
win = visual.Window(monitor=my_monitor, units='deg', fullscr=True, allowGUI=False, color='black')  # Initiate psychopy Window as the object "win", using the myMon object from last line. Use degree as units!

#Prepare Fixation cross
stim_fix = visual.TextStim(win, '+')#, height=FIX_HEIGHT)  # Fixation cross is just the character "+". Units are inherited from Window when not explicitly specified.
"""
STIMULI

"""
#EXPERIMENTAL DETAILS
#Load word file
wordlist=pd.read_csv('wordlist.txt', sep='\t')
words=wordlist[wordlist.session==int(V['session'])]
words = words.reset_index()
del words['index']

#iMAGE FILES
IMG_P='image_stim_p.png' #yellow positive (aka. happy)
IMG_N='image_stim_n.png' #yellow negative (aka. fearful)
faces=(IMG_P,IMG_N)
delays=(120,180)# different time intervals between stimuli mean 
# 4.1 sec x 60 hz refresh rate = 246 for fMRI, 
# in order to make less predictable and increase power.
dur=int(0.7*FRAME_RATE) # duration in seconds multiplied by 60 Hz and made into integer
condition='FaceWord_exp' #Just a variable. If the script can run several exp 
# then this can be called in GUI. Not relevant here.

# Visual dot for check of stimulus in e.g. MEG
stimDot = visual.GratingStim(win, size=.5, tex=None, pos=(7, -6),
                             color=1, mask='circle', autoLog=False)

# The word stimulus 
ypos=0
xpos=0                          
textHeight=0.7
stim_text = visual.TextStim(win=win, pos=[xpos,ypos], height=textHeight, alignHoriz='center')

# The image size and position using ImageStim, file info added in trial list sbelow.
stim_image = visual.ImageStim(win,  # you don't have to use new lines for each attribute, but sometime it's easier to read that way
     mask=None,
    pos=(0.0, 0.0),
    size=(14.0, 10.5),
    ori=1)

""" OUTPUT """

#KEYS
KEYS_QUIT = ['escape','q']  # Keys that quits the experiment
KEYS_trigger=['t'] # The MR scanner sends a "t" to notify that it is starting

   # Prepare a csv log-file using the ppc3 script
ID_sess=  str(V['ID']) + '_sess_' + str(V['session'])
writer = ppc.csv_writer(ID_sess, folder=SAVE_FOLDER)  # writer.write(trial) will write individual trials with low latency

""" FUNCTIONS FOR EXPERIMENTAL LOOP"""

def make_trial_list(condition):
# Factorial design
    trial_list = []
    for word in range(words.shape[0]): # images
        # define triggers and image stimulus based on word
        if words.label[word]=='pos':
            img= IMG_P #image file
        if words.label[word]=='neg':
            img= IMG_N #image file
        if words.label[word]=='neu':
            img= sample([IMG_P,IMG_N],1)[0] #image file
        delaysR= sample(delays,2)
        
        # Add a dictionary for every trial
        trial_list += [{
            'ID': V['ID'],
            'age': V['age'],
            'gender': V['gender'],
            'scan day':V['Scan day'],
            'condition': condition,
            'session':V['session'],
            'word':words.word[word],
            'word_label':words.label[word],
            'word_score_pc':words.score_pc[word],
            'word_score_warriner':words.score_warriner[word],
            'pause_trigger_t':'',
            'img':img,
            'onset_word':'' ,# a place to note onsets
            'offset_word': '',
            'duration_measured_word':'',
            'onset_img':'' ,# a place to note onsets
            'offset_img': '',
            'duration_measured_img':'',
            'duration_frames': dur,
            'delay_frames_before': delaysR[0],
            'delay_frames_after': delaysR[1],
            'response': '',
            'key_t':'',
            'rt': '',
            'correct_resp': ''
        }]
    
   # Randomize order

    trial_list = sample(trial_list, len(trial_list))

    # Add trial numbers and return
    for i, trial in enumerate(trial_list):
        trial['no'] = i + 1  # start at 1 instead of 0
    return trial_list
   
    

hest=make_trial_list('WordFace_exp')

    
def run_condition(condition,exp_start):
    """
    Runs a block of trials. This is the presentation of stimuli,
    collection of responses and saving the trial
    """
    # Loop over trials
    for trial in make_trial_list(condition):
        event.clearEvents(eventType='keyboard') # clear keyboard input to make sure that no responses are logged that do not belong to stimulus
        # prepare word
        stim_text.text = trial['word']
        time_flip_word=core.monotonicClock.getTime() #onset of stimulus
        for frame in range(trial['duration_frames']):
            stim_text.draw()
            stimDot.draw()
            win.flip()

        # Display fixation cross
        offset_word = core.monotonicClock.getTime()  # offset of stimulus
        for frame in range(trial['delay_frames_before']):
            stim_fix.draw()
           
        # Prepare image
        stim_image.image = trial['img']

        # Display image and monitor time
        time_flip_img=core.monotonicClock.getTime() #onset of stimulus
        for frame in range(trial['duration_frames']):
            stim_image.draw()
            stimDot.draw()
            win.flip()
        # Display fixation cross
        offset_img = core.monotonicClock.getTime()  # offset of stimulus
        for frame in range(trial['delay_frames_after']):
            stim_fix.draw()
            win.flip()
            # Get actual duration at offset
                   

        #Log values
        trial['onset_word']=time_flip_word-exp_start
        trial['offset_word'] = offset_word-exp_start
        trial['duration_measured_word']=offset_word-time_flip_word
        #Log values
        trial['onset_img']=time_flip_img-exp_start
        trial['offset_img'] = offset_img-exp_start
        trial['duration_measured_img']=offset_img-time_flip_img

        try:
            key, time_key = event.getKeys(keyList=('y','b','escape','q'), timeStamped=True)[0]  # timestamped according to core.monotonicClock.getTime() at keypress. Select the first and only answer.

        except IndexError:  #if no responses were given, the getKeys function produces an IndexError
            trial['response']=''
            trial['key_t']=''
            trial['rt']=''
            trial['correct_resp']=''
         
        else: #if responses were given, find RT and correct responses
            trial['response']=key
            trial['key_t']=time_key-exp_start
            trial['rt'] = time_key-time_flip_img
            #check if responses are correct
            if trial['response']=='y':
                trial['correct_resp'] = 1 if trial['img']==IMG_N else 0
            elif trial['response']=='b':
                trial['correct_resp'] = 1 if trial['img']==IMG_P else 0

            if key in KEYS_QUIT:  # Look at first reponse [0]. Quit everything if quit-key was pressed
                writer.flush()
                win.close()
                core.quit()

        # Save trials to csv file
        writer.write(trial) 
    
"""
DISPLAY INTRO TEXT AND AWAIT SCANNER TRIGGER
"""    
textPos= [0, 0]                            # Position of question message
textHeight=0.6 # height in degrees
introText1=[u'In this experiment you read words and look at faces', # some blanks here to create line shifts
                  
            u'Words can be used to predict facial expression',
             
            u'Press "B" with INDEX finger if face is POSITIVE',
            
            u'Press "Y" with MIDDLE finger if face is NEGATIVE',
            
            u'The experiment starts when you press "T"']

# Loop over lines in Intro Text1
ypos=4
xpos=0
for intro in introText1:
    ypos=ypos-1
    introText1 = visual.TextStim(win=win, text=intro, pos=[xpos,ypos], height=textHeight, alignHoriz='center')
    introText1.draw()
win.flip()          # Show the stimuli on next monitor update and ...

#Wait for scanner trigger "t" to continue
event.waitKeys(keyList=KEYS_trigger) 
exp_start=core.monotonicClock.getTime()

#1 sec of fixation cross before we start
for frame in range(1*FRAME_RATE):
     stim_fix.draw()
     win.flip()
""" CALL FUNCTION RUNNING THE EXPERIMENTAL LOOP"""
run_condition('faceWord_exp',exp_start)

#Use flush function to make sure that the log file has been updated
writer.flush()
#Close the experimental window
win.close()
core.quit()