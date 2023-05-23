#include <Python.h>
#include "kernel.h"
#include <signal.h>
#include <stdio.h>

// variable used to ignore timer interruptions while scheduling tasks. It should be set to 0 before executing tasks
int blockInterrupts = 0;

SchedTask Tasks[MAX_TASKS];
int curTask = MAX_TASKS;

void schedInit()
{
    for (int i = 0; i < MAX_TASKS; i++)
        Tasks[i].func = NULL;

    struct sigaction sa;
    struct itimerval timer;

    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = &timerHandler;
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

int setup()
{
    Py_Initialize();

    PyObject *pSysPath, *pModuleDir;

    // Import the 'sys' module
    PyObject *pSysModule = PyImport_ImportModule("sys");
    if (pSysModule == NULL) {
        PyErr_Print();
        return 1;
    }

    // Get the 'sys.path' list
    pSysPath = PyObject_GetAttrString(pSysModule, "path");
    if (pSysPath == NULL || !PyList_Check(pSysPath)) {
        PyErr_Print();
        return 1;
    }

    // Append the directory containing the module to 'sys.path'
    pModuleDir = PyUnicode_DecodeFSDefault("..");
    if (pModuleDir == NULL) {
        PyErr_Print();
        return 1;
    }
    int result = PyList_Append(pSysPath, pModuleDir);
    if (result == -1) {
        PyErr_Print();
        return 1;
    }

    // Import the module using its name
    PyObject *tasksModule = PyImport_ImportModule("alphabot.tasks");
    if (tasksModule == NULL) {
        PyErr_Print();
        return 1;
    }

    PyObject* initCameraFunc = PyObject_GetAttrString(tasksModule, "init_camera");
    if (initCameraFunc == NULL || !PyCallable_Check(initCameraFunc)) {
        if (PyErr_Occurred())
            PyErr_Print();
        return 1;
    }

    PyObject* args = PyTuple_New(0);
    PyObject_CallObject(initCameraFunc, args);

    schedInit();
    // TODO add tasks

    return 0;
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
    // TODO port from arduino.ino, call python functions, set blockInterrupts to 0 while calling another function
}

void timerHandler(int signum)
{
    if (blockInterrupts)
        return;

    blockInterrupts = 1;
    // TODO port from arduino.ino
    blockInterrupts = 0;
}

int main()
{
    if (setup() != 0) return 1;
    while (1)
    {
        sleep(1);
    }
    return 0;
}
