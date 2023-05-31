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
int schedInit();

/**
 * Initializes the python interpreter and modules
 */
int pythonInit();

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
int setup();

/**
 * Timer interruption handler
 */
void timerHandler(int signum);


/**
 * Creates a python task and adds it to the scheduler
 * 
 * @param name the name of the task
 * @param delay the delay in ticks
 * @param period the period in ticks
*/
int createPythonTask(char* name, int delay, int period);

#endif