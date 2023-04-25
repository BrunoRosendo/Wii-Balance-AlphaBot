from task import Task
import threading
from alphabot.test import toggle_forward_backwards
import RPi.GPIO as GPIO
import time

timer = None
tasks = []
current_task = 0

def set_interrupts():
    global timer
    timer = threading.Timer(0.1, Sched_Interrupt)
    timer.start()

def stop_interrupts():
    global timer
    timer.cancel()

def Sched_Init():
    # TODO configure interrupts and stuff on PI
    set_interrupts()
    return

def Sched_AddTask(func, delay, period):
    global current_task
    tasks.append(Task(func, delay, period))
    current_task = len(tasks)

def Sched_Schedule():
    for task in tasks:
        if task.func == None:
            continue
        if task.delay > 0:
            task.delay -= 1
        else:
            task.counter += 1
            task.delay = task.period - 1

def Sched_Dispatch():
    global current_task
    prev_task = current_task
    for i in range(current_task):
        task = tasks[i]
        if task.func == None or task.counter == 0:
            continue
        task.counter = 0
        current_task = i

        # enable interrupts
        set_interrupts()
        task.func()
        # disable interrupts
        stop_interrupts()

        current_task = prev_task

        # one shot task
        if task.period == 0:
            tasks.remove(task)

def setup():
    print("setting up")
    # TODO initialize pins
    Sched_Init()

    # TODO this is using deciseconds but needs to use ms later
    Sched_AddTask(toggle_forward_backwards, 0, 10)

def Sched_Interrupt():
    stop_interrupts()
    Sched_Schedule()
    Sched_Dispatch()
    set_interrupts()

setup()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
