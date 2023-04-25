from task import Task

tasks = []
current_task = 0

def t1():
    print("hello world")
    return

def Sched_Init():
    # TODO configure interrupts and stuff on PI
    return

def Sched_AddTask(func, delay, period):
    tasks.append(Task(func, delay, period))

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
    # TODO initialize pins
    Sched_Init()

    # TODO add tasks
    Sched_AddTask(t1, 0, 1000)

# TODO subscribe timer interrupts and call Sched_Schedule() and Sched_Dispatch()

setup()

while True:
    pass # keep it running
