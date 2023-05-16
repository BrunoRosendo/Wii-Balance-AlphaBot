#ifndef KERNEL_H
#define KERNEL_H

#include <Python.h>

typedef struct
{
    /* period in ticks */
    int period;
    /* ticks until next activation */
    int delay;
    /* function pointer */
    void (*func)(void);
    /* activation counter */
    int exec;
} Sched_Task_t;

#endif