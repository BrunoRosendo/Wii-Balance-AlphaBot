#include <Python.h>
#include "kernel.h"
#include <signal.h>
#include <stdio.h>

int c = 0;

SchedTask Tasks[MAX_TASKS];
int cur_task = MAX_TASKS;

void schedInit()
{
    for (int i = 0; i < MAX_TASKS; i++)
        Tasks[i].func = NULL;

    struct sigaction sa;
    struct itimerval timer;

    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = &timer_handler;
    sa.sa_flags = SA_NODEFER;
    sigaction(SIGALRM, &sa, NULL);

    // configure timer to expire after 1 mS
    getitimer(ITIMER_REAL, &timer);

    timer.it_value.tv_sec = 0;
    timer.it_value.tv_usec = TICK_RATE;

    timer.it_interval.tv_sec = 0;
    timer.it_interval.tv_usec = TICK_RATE;

    setitimer(ITIMER_REAL, &timer, NULL);
}

void setup()
{
    // TODO setup raspberry pi modules
    schedInit();
    // TODO add tasks
}

int schedAddTask(PyObject *func, int delay, int period)
{
    // TODO port from arduino.ino
    return -1;
}

void schedSchedule()
{
    // TODO port from arduino.ino
}

void schedDispatch()
{
    // TODO port from arduino.ino, call python functions
}

void timer_handler(int signum)
{
    printf("Boas mano, olha o timer %d\n", c++);
    // TODO port from arduino.ino
    sleep(1); // test if it's still interrupting
}

int main()
{
    setup();
    while (1)
    {
        sleep(1);
    }
    return 0;
}
