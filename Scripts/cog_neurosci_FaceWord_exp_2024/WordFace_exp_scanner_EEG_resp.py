# -*- coding: utf-8 -*-
""" DESCRIPTION:
This fMRI/MEG experiment displays 3 different types of words (positive, negative,neutral),
followed by a break and one of two different emoji faces (happy and fearful).
Participants have to judge happy or fearful face with buttonpresses 'y'
and 'b'.
The experiment lasts 5 minutes per session and has 60 trials.
The script awaits a trigger pulse from the scanner/experimenter with the value "t"

/Mikkel Wallentin & Roberta Rocca 2019 (with some of the code adapted from Jonas LindeLoev:
    https://github.com/lindeloev/psychopy-course/blob/master/ppc_template.py)

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
from triggers import setParallelData


"""
SET VARIABLES
"""
# Monitor parameters
MON_DISTANCE = 60  # Distance between subject's eyes and monitor
MON_WIDTH = 20  # Width of your monitor in cm
MON_SIZE = [1200, 1000]  # Pixel-dimensions of your monitor
FRAME_RATE = 60 # Hz  [120]
SAVE_FOLDER = 'faceWord_exp_data'  # Log is saved to this folder. The folder is created if it does not exist.
RUNS = 6 # Number of sessions to loop over (useful for EEG experiment)


"""
GET PARTICIPANT INFO USING GUI
"""
# Intro-dialogue. Get subject-id and other variables.
# Save input variables in "V" dictionary (V for "variables")
V= {'ID':'','exp type':['fMRI','EEG'],'session':[1,2,3,4,5,6],'Scan day': ['Tuesday','Wednesday','Thursday'],'gender':['male','female'],'age':''}
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
#EXPERIMANTAL DETAILS
# NB! moved down to experimental loop at the end
#Load word file
#wordlist=pd.read_csv('wordlist.txt', sep='\t')
#words=wordlist[wordlist.session==int(V['session'])]
#words = words.reset_index()
#del words['index']

#words=pd.DataFrame({'word':('horse','spoon','death','pain','happiness','smile'),'score':(0.1,0.1,-1.9,-0.7,1.5,1.2),'label':('0','0','n','n','p','p')})
#words.to_csv(r'wordlist.tsv',sep='\t',header=True)

#iMAGE FILES
IMG_P='image_stim_p.png' #yellow positive
IMG_N='image_stim_n.png' #yellow negative
faces=(IMG_P,IMG_N)
#delays=(180,336)# different time intervals between stimuli mean 4.1 sec x 60 hz refresh rate =246, in order to make less predictable and increase power.
delays=(120,180)# different time intervals between stimuli mean 4.1 sec x 60 hz refresh rate =246, in order to make less predictable and increase power.
dur=int(0.7*FRAME_RATE) # duration in seconds multiplied by 60 Hz and made into integer
#dur=int(0.35*FRAME_RATE) # duration in seconds multiplied by 60 Hz and made into integer
condition='FaceWord_exp' #Just a variable. If the script can run several exp. then this can be called in GUI. Not relevant here.

# Visual dot for check of stimulus in MEG
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
KEYS_target = dict(neg=['2', 'y'],
                  pos=['1', 'b'])

# NB! Now defined as part of the exp-run-loop at the end
#   # Prepare a csv log-file using the ppc3 script
#ID_sess=  str(V['ID']) + '_sess_' + str(V['session'])
#ID_sess=  str(V['ID']) + '_sess_' + str(V['session'])
#writer = ppc.csv_writer(ID_sess, folder=SAVE_FOLDER)  # writer.write(trial) will write individual trials with low latency

""" FUNCTIONS FOR EXPERIMENTAL LOOP"""

def make_trial_list(condition, run):
# Factorial design
    trial_list = []
    for word in range(words.shape[0]): # images
        # define triggers and image stimulus based on word
        if words.label[word]=='pos':
            img= IMG_P #image file
            TRIG_I=21 #trigger code
            TRIG_W=11
            TRIG_BEFORE=31
        if words.label[word]=='neg':
            img= IMG_N #image file
            TRIG_I=22
            TRIG_W=12
            TRIG_BEFORE=32
        if words.label[word]=='neu':
            img= sample([IMG_P,IMG_N],1)[0] #image file
            TRIG_W=13
            if img==IMG_P:
                TRIG_I=41
                TRIG_BEFORE=51 #Unpredictable pause before positive image
            else:
                TRIG_I=42
                TRIG_BEFORE=52
        delaysR= sample(delays,2)

        # Add a dictionary for every trial
        trial_list += [{
            'ID': V['ID'],
            'age': V['age'],
            'gender': V['gender'],
            'scan day':V['Scan day'],
            'condition': condition,
#            'session':V['session'],
            'session':str(run+1),
            'word':words.word[word],
            'word_label':words.label[word],
            'word_score_pc':words.score_pc[word],
            'word_score_warriner':words.score_warriner[word],
            'word_trigger':TRIG_W,
            'pause_trigger':TRIG_BEFORE,
            'pause_trigger_t':'',
            'img':img,
            'img_trigger':TRIG_I,
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
    # trial_list = sample(trial_list, len(trial_list)-55) # shortened version for a test run


    # Add trial numbers and return
    for i, trial in enumerate(trial_list):
        trial['no'] = i + 1  # start at 1 instead of 0
        #if i is 0:
         #   writer.writeheader(trial) # An added line to give headers to the log-file (see ppc3.py)
    return trial_list


# NB! Now defined as part of the exp-run-loop at the end
#hest=make_trial_list('WordFace_exp')


def run_condition(condition,exp_start,run):
    """
    Runs a block of trials. This is the presentation of stimuli,
    collection of responses and saving the trial
    """
    #Set MEG trigger in off state
    pullTriggerDown = False
    # Loop over trials
    for trial in make_trial_list(condition, run):
        #event.clearEvents(eventType='keyboard')# clear keyboard input to make sure that no responses are logged that do not belong to stimulus
        # prepare word
        stim_text.text = trial['word']
        time_flip_word=core.monotonicClock.getTime() #onset of stimulus
        for frame in range(trial['duration_frames']):
            stim_text.draw()
            stimDot.draw()
            if frame==1:
                win.callOnFlip(setParallelData, trial['word_trigger'])  # pull trigger up
                pullTriggerDown = True
            win.flip()
            if pullTriggerDown:
                win.callOnFlip(setParallelData, 0)
                pullTriggerDown = False
        # Display fixation cross
        offset_word = core.monotonicClock.getTime()  # offset of stimulus
        for frame in range(trial['delay_frames_before']):
            stim_fix.draw()

            # Send pause trigger 1 sec (500 ms?) after offset
            #if frame  == 60:
            if frame  == 30:

                win.callOnFlip(setParallelData, trial['pause_trigger'])  # pull trigger up
                pullTriggerDown = True
                pause_trigger_t = core.monotonicClock.getTime()  # offset of stimulus
            win.flip()

            if pullTriggerDown:
                win.callOnFlip(setParallelData, 0)
                pullTriggerDown = False

        # Prepare image
        stim_image.image = trial['img']
        no_key_yet = 0

        # Display image and monitor time
        time_flip_img=core.monotonicClock.getTime() #onset of stimulus
        event.clearEvents(eventType='keyboard')# clear keyboard input to make sure that no responses are logged that do not belong to stimulus
        for frame in range(trial['duration_frames']):
            stim_image.draw()
            stimDot.draw()
            if frame==1:
                win.callOnFlip(setParallelData, trial['img_trigger'])  # pull trigger up
                pullTriggerDown = True
            if frame>1 and no_key_yet == 0:
                try:
                    key, time_key = event.getKeys(keyList=('y', 'b', '1', '2', 'escape'), timeStamped=True)[0]  # timestamped according to core.monotonicClock.getTime() at keypress
                except IndexError:  #if no responses were given, the getKeys function produces an IndexError
                    key = 'z'
                if key in KEYS_target['neg']:
                    no_key_yet = 1
                    trial['response']=key
                    trial['key_t']=time_key-exp_start
                    trial['rt'] = time_key-time_flip_img
                    if trial['word_trigger']==13:
#                    if trial['word_label']=='neu': # neutral word before
                        if trial['img']==IMG_N:
                            trial['correct_resp'] = 1
                            setParallelData(112)  # pull trigger up; 100 = correct; XX2 neg-response
                            pullTriggerDown = True
                        elif trial['img']==IMG_P:
                            trial['correct_resp'] = 0
                            setParallelData(212)  # pull trigger up; 200 = incorrect; XX2 neg-response
                            pullTriggerDown = True
                    else: # positive or negative word before
                        if trial['img']==IMG_N:
                            trial['correct_resp'] = 1
                            setParallelData(102)  # pull trigger up; 100 = correct; XX2 neg-response
                            pullTriggerDown = True
                        elif trial['img']==IMG_P:
                            trial['correct_resp'] = 0
                            setParallelData(202)  # pull trigger up; 200 = incorrect; XX2 neg-response
                            pullTriggerDown = True
                elif key in KEYS_target['pos']:
                    no_key_yet = 1
                    trial['response']=key
                    trial['key_t']=time_key-exp_start
                    trial['rt'] = time_key-time_flip_img
                    if trial['word_trigger']==13:
#                    if trial['word_label']=='neu': # neutral word before
                        if trial['img']==IMG_P:
                            trial['correct_resp'] = 1
                            setParallelData(111)  # pull trigger up; 100 = correct; XX1 pos-response
                            pullTriggerDown = True
                        elif trial['img']==IMG_N:
                            trial['correct_resp'] = 0
                            setParallelData(211)  # pull trigger up; 200 = incorrect; XX1 pos-response
                            pullTriggerDown = True
                    else: # positive or negative word before
                        if trial['img']==IMG_P:
                            trial['correct_resp'] = 1
                            setParallelData(101)  # pull trigger up; 100 = correct; XX1 pos-response
                            pullTriggerDown = True
                        elif trial['img']==IMG_N:
                            trial['correct_resp'] = 0
                            setParallelData(201)  # pull trigger up; 200 = incorrect; XX1 pos-response
                            pullTriggerDown = True
                if key in KEYS_QUIT:  # Look at first reponse [0]. Quit everything if quit-key was pressed
    #                writer.flush()
    #                print('just flushed!')
                    win.close()
                    core.quit()
            win.flip()
            if pullTriggerDown:
                win.callOnFlip(setParallelData, 0)
                pullTriggerDown = False

        # Display fixation cross
        offset_img = core.monotonicClock.getTime()  # offset of stimulus
        for frame in range(trial['delay_frames_after']):
            stim_fix.draw()
            if no_key_yet == 0:
                try:
                    key, time_key = event.getKeys(keyList=('y', 'b', '1', '2', 'escape'), timeStamped=True)[0]  # timestamped according to core.monotonicClock.getTime() at keypress
                except IndexError:  #if no responses were given, the getKeys function produces an IndexError
                    key = 'z'
                    if frame == trial['delay_frames_after']:
                        # NB! We only log "no response" if no keys were pressed in this section - not the previous section
                        trial['response']=''
                        trial['key_t']=''
                        trial['rt']=''
                        trial['correct_resp']=''
                if key in KEYS_target['neg']:
                    no_key_yet = 1
                    trial['response']=key
                    trial['key_t']=time_key-exp_start
                    trial['rt'] = time_key-time_flip_img
                    if trial['word_trigger']==13:
#                    if trial['word_label']=='neu': # neutral word before
                        if trial['img']==IMG_N:
                            trial['correct_resp'] = 1
                            setParallelData(112)  # pull trigger up; 100 = correct; XX2 neg-response
                            pullTriggerDown = True
                        elif trial['img']==IMG_P:
                            trial['correct_resp'] = 0
                            setParallelData(212)  # pull trigger up; 200 = incorrect; XX2 neg-response
                            pullTriggerDown = True
                    else: # positive or negative word before
                        if trial['img']==IMG_N:
                            trial['correct_resp'] = 1
                            setParallelData(102)  # pull trigger up; 100 = correct; XX2 neg-response
                            pullTriggerDown = True
                        elif trial['img']==IMG_P:
                            trial['correct_resp'] = 0
                            setParallelData(202)  # pull trigger up; 200 = incorrect; XX2 neg-response
                            pullTriggerDown = True
                elif key in KEYS_target['pos']:
                    no_key_yet = 1
                    trial['response']=key
                    trial['key_t']=time_key-exp_start
                    trial['rt'] = time_key-time_flip_img
                    if trial['word_trigger']==13:
#                    if trial['word_label']=='neu': # neutral word before
                        if trial['img']==IMG_P:
                            trial['correct_resp'] = 1
                            setParallelData(111)  # pull trigger up; 100 = correct; XX2 neg-response
                            pullTriggerDown = True
                        elif trial['img']==IMG_N:
                            trial['correct_resp'] = 0
                            setParallelData(211)  # pull trigger up; 200 = incorrect; XX2 neg-response
                            pullTriggerDown = True
                    else: # positive or negative word before
                        if trial['img']==IMG_P:
                            trial['correct_resp'] = 1
                            setParallelData(101)  # pull trigger up; 100 = correct; XX1 pos-response
                            pullTriggerDown = True
                        elif trial['img']==IMG_N:
                            trial['correct_resp'] = 0
                            setParallelData(201)  # pull trigger up; 200 = incorrect; XX1 pos-response
                            pullTriggerDown = True
                if key in KEYS_QUIT:  # Look at first reponse [0]. Quit everything if quit-key was pressed
        #                writer.flush()
        #                print('just flushed!')
                    win.close()
                    core.quit()
            win.flip()
            if pullTriggerDown:
                win.callOnFlip(setParallelData, 0)
                pullTriggerDown = False
            # Get actual duration at offset


        #Log values
        trial['onset_word']=time_flip_word-exp_start
        trial['offset_word'] = offset_word-exp_start
        trial['duration_measured_word']=offset_word-time_flip_word
                #Log values
        trial['onset_img']=time_flip_img-exp_start
        trial['offset_img'] = offset_img-exp_start
        trial['duration_measured_img']=offset_img-time_flip_img
        trial['pause_trigger_t']=pause_trigger_t-exp_start

        # Save trials to csv file
        writer.write(trial)

"""
DISPLAY INTRO TEXT AND AWAIT SCANNER TRIGGER
"""
for run in range(RUNS):
    textPos= [0, 0]                            # Position of question message
    textHeight=0.6 # height in degrees
    introText1=[u'In this experiment you will read words and look at faces', # some blanks here to create line shifts

                u'Words can be used to predict facial expressions',

                u'Press "b" key with INDEX finger if face is POSITIVE',

                u'Press "y" key with MIDDLE finger if face is NEGATIVE',

                u'',

                u'Press "t" to start the experiment']

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

#""" CALL FUNCTION RUNNING THE EXPERIMENTAL LOOP"""
       # Prepare a csv log-file using the ppc3 script
    #ID_sess=  str(V['ID']) + '_sess_' + str(V['session'])
    ID_sess=  str(V['ID']) + '_sess_' + str(run+1)
    writer = ppc.csv_writer(ID_sess, folder=SAVE_FOLDER)  # writer.write(trial) will write individual trials with low latency

       # Generate a separate trial_list for each new session
    wordlist=pd.read_csv('wordlist.txt', sep='\t')
    words=wordlist[wordlist.session==run+1]
    words = words.reset_index()
    del words['index']
    hest=make_trial_list('WordFace_exp', run+1)

       # Run the actual session
    run_condition('faceWord_exp',exp_start,run)

#Use flush function to make sure that the log file has been updated
#writer.flush()
#Close the experimental window
win.close()
core.quit()
