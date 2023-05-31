#include <Python.h>
#include "kernel.h"
#include <signal.h>
#include <stdio.h>

// variable used to ignore timer interruptions while scheduling tasks. It should be set to 0 before executing tasks
int blockInterrupts = 0;

SchedTask tasks[MAX_TASKS];
int curTask = MAX_TASKS;

PyObject *tasksModule = NULL;

int schedInit()
{
    for (int i = 0; i < MAX_TASKS; i++)
        tasks[i].func = NULL;

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

    return 0;
}

int pythonInit()
{
    Py_Initialize();

    // Import the 'sys' module
    PyObject *sysModule = PyImport_ImportModule("sys");
    if (sysModule == NULL) {
        PyErr_Print();
        return 1;
    }

    // Get the 'sys.path' list
    PyObject *pSysPath = PyObject_GetAttrString(sysModule, "path");
    if (pSysPath == NULL || !PyList_Check(pSysPath)) {
        PyErr_Print();
        return 1;
    }

    // Append the directory containing the module to 'sys.path'
   PyObject * pModuleDir = PyUnicode_DecodeFSDefault("..");
    if (pModuleDir == NULL) {
        PyErr_Print();
        return 1;
    }
    int result = PyList_Append(pSysPath, pModuleDir);
    if (result == -1) {
        PyErr_Print();
        return 1;
    }

    // Import the tasks module and init functions
    tasksModule = PyImport_ImportModule("alphabot.tasks");
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

    return 0;
}

int setup()
{
    if (pythonInit() != 0) return 1;
    if (schedInit() != 0) return 1;
    // TODO add tasks

    createPythonTask("read_wii_data", 0, 100)
    createPythonTask("drive_alphabot", 0, 100)

    return 0;
}


void createPythonTask(char* name, int delay, int period)
{
    PyObject* pyFuncObj = PyObject_GetAttrString(tasksModule, name);
    if (pyFuncObj == NULL || !PyCallable_Check(pyFuncObj)) {
        if (PyErr_Occurred())
            PyErr_Print();
        return 1;
    }

    if (schedAddTask(pyFuncObj, delay, period) != 0) return 1;
    return 0;
}


int schedAddTask(PyObject *func, int delay, int period)
{
    for (int i = 0; i < MAX_TASKS; i++)
        if (!tasks[i].func)
        {
            tasks[i].period = period;
            tasks[i].delay = delay;
            tasks[i].exec = 0;
            tasks[i].func = func;
            return i;
        }
    return -1;
}

void schedSchedule()
{
    for (int i = 0; i < MAX_TASKS; i++)
    {
        if (tasks[i].func)
        {
            if (tasks[i].delay)
            {
                tasks[i].delay--;
            }
            else
            {
                /* Schedule Task */
                tasks[i].exec++;
                tasks[i].delay = tasks[i].period - 1;
            }
        }
    }
}

void schedDispatch()
{
    int prev_task = curTask;
    for (int i = 0; i < curTask; i++)
    {
        if ((tasks[i].func) && (tasks[i].exec))
        {
            tasks[i].exec = 0;
            curTask = i;
            blockInterrupts = 0;

            PyObject* args = PyTuple_New(0);
            PyObject_CallObject(tasks[i].func, args);

            blockInterrupts = 1;
            curTask = prev_task;
            /* Delete task if one-shot */
            if (!tasks[i].period)
                tasks[i].func = 0;
        }
    }
}

void timerHandler(int signum)
{
    if (blockInterrupts)
        return;

    blockInterrupts = 1;
    schedSchedule();
    schedDispatch();
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
