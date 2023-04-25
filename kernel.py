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
    timer = threading.Timer(0.001, Sched_Interrupt)
    timer.start()

def stop_interrupts():
    global timer
    timer.cancel()

def Sched_Init():
    print("initing scheduler")
    # TODO configure interrupts and stuff on PI
    set_interrupts()
    return

def Sched_AddTask(func, delay, period):
    print("adding task")
    global current_task
    tasks.append(Task(func, delay, period))
    current_task = len(tasks)

def Sched_Schedule():
    print("scheduling")
    for task in tasks:
        if task.func == None:
            print("no function")
            continue
        if task.delay > 0:
            print("delaying ", task.delay)
            task.delay -= 1
        else:
            print("counting")
            task.counter += 1
            task.delay = task.period - 1

def Sched_Dispatch():
    global current_task
    prev_task = current_task
    print("dispatching")
    for i in range(current_task):
        print(0)
        task = tasks[i]
        if task.func == None or task.counter == 0:
            continue
        print(1)
        task.counter = 0
        print(2)
        current_task = i
        print(3)

        # enable interrupts
        set_interrupts()
        print(4)
        task.func()
        print(5)
        # disable interrupts
        stop_interrupts()
        print(6)

        current_task = prev_task
        print(7)

        # one shot task
        if task.period == 0:
            tasks.remove(task)
        print(8)

def setup():
    print("setting up")
    # TODO initialize pins
    Sched_Init()

    # TODO add tasks
    Sched_AddTask(t1, 0, 1000)
    Sched_AddTask(t2, 0, 5000)
    Sched_AddTask(t3, 0, 10000)

def Sched_Interrupt():
    stop_interrupts()
    Sched_Schedule()
    Sched_Dispatch()
    set_interrupts()

setup()

while True:
    pass # keep it running
