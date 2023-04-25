from task import Task
import pigpio

TIMER_FREQUENCY = 1000 # 1kHz

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
    # TODO configure interrupts and stuff on PI
    pi = pigpio.pi('soft', 8888)
    timer_handle = pi.hardware_timer(0)
    timer_handle.frequency(TIMER_FREQUENCY)
    timer_handle.callback(Sched_Interrupt)
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
    Sched_AddTask(t2, 0, 5000)
    Sched_AddTask(t3, 0, 10000)

def Sched_Interrupt():
    Sched_Schedule()
    Sched_Dispatch()

setup()

while True:
    pass # keep it running
