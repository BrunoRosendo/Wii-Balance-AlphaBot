from task import Task
import threading

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

def Sched_Init():
    print("initing scheduler")
    # TODO configure interrupts and stuff on PI
    threading.Timer(1, Sched_Interrupt).start()
    return

def Sched_AddTask(func, delay, period):
    print("adding task")
    tasks.append(Task(func, delay, period))

def Sched_Schedule():
    print("scheduling")
    for task in tasks:
        if task.func == None:
            continue
        if task.delay > 0:
            task.delay -= 1
        else:
            task.counter += 1
            task.delay = task.period - 1

def Sched_Dispatch():
    print("dispatching")
    global current_task
    prev_task = current_task
    for (i, task) in enumerate(tasks):
        if task.func == None or task.counter == 0:
            continue
        task.counter = 0
        current_task = i
        # enable interrupts
        task.func()
        # disable interrupts
        current_task = prev_task
        if task.period == 0:
            tasks.remove(task)

def setup():
    print("setting up")
    # TODO initialize pins
    Sched_Init()

    # TODO add tasks
    Sched_AddTask(t1, 0, 1000)
    Sched_AddTask(t2, 0, 5000)
    Sched_AddTask(t3, 0, 10000)

def Sched_Interrupt():
    print("interrupting")
    Sched_Schedule()
    Sched_Dispatch()

setup()

while True:
    pass # keep it running

timer.deinit()
