#include <Python.h>
#include "kernel.h"

SchedTask Tasks[MAX_TASKS];
int cur_task = MAX_TASKS;

void schedInit()
{
    for (int i = 0; i < MAX_TASKS; i++)
        Tasks[i].func = NULL;

    // TODO setup interrupts
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

// TODO create signal handler for interrupts

int main()
{
    setup();
    return 0;
}
