from task import Task
import threading

timer = None
tasks = []
current_task = 0

def t1():
    print("hello world 1sec")
    return

def t2():
    print("hello world 5secs")
    return

def t3():
    print("hello world 10secs")
    return

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

    # TODO this is using seconds but needs to use ms later
    Sched_AddTask(t1, 0, 10)
    Sched_AddTask(t2, 0, 50)
    Sched_AddTask(t3, 0, 100)

def Sched_Interrupt():
    stop_interrupts()
    Sched_Schedule()
    Sched_Dispatch()
    set_interrupts()

setup()

while True:
    pass # keep it running
