#ifndef KERNEL_H
#define KERNEL_H
#define PY_SSIZE_T_CLEAN

#include <Python.h>

#define MAX_TASKS 20

typedef struct
{
    /* period in ticks */
    int period;
    /* ticks until next activation */
    int delay;
    /* function pointer */
    PyObject *func;
    /* activation counter */
    int exec;
} SchedTask;

/**
 * Initializes the scheduler
 */
void schedInit();

/**
 * Adds a task to the scheduler
 */
int schedAddTask(PyObject *func, int delay, int period);

/**
 * Schedules the tasks
 */
void schedSchedule();

/**
 * Sets up the kernel and auxiliary modules
 */
void setup();

#endif