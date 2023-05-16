#ifndef KERNEL_H
#define KERNEL_H
#define PY_SSIZE_T_CLEAN

#include <Python.h>

#define MAX_TASKS 20
#define TICK_RATE 1000

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
 * Dispatches the tasks
 */
void schedDispatch();

/**
 * Sets up the kernel and auxiliary modules
 */
void setup();

/**
 * Timer interruption handler
 */
void timer_handler(int signum);

#endif