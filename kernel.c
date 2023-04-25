#include <wiringPi.h>
#include <stdlib.h>

#include <signal.h>
#include <unistd.h>

int Sched_AddT(void (*f)(void), int d, int p);

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

void t1()
{
    printf("hello world 1sec");
}

void t2()
{
    printf("hello world 5sec");
}

void t3()
{
    printf("hello world 10sec");
}

#define NT 20
Sched_Task_t Tasks[NT];
int cur_task = NT;

int Sched_Init(void)
{
    for (int x = 0; x < NT; x++)
        Tasks[x].func = 0;

    wiringPiSetupPhys();
    signal(SIGALRM, alarmWakeup);
    ualarm(0, 1);
}

int Sched_AddT(void (*f)(void), int d, int p)
{
    for (int x = 0; x < NT; x++)
        if (!Tasks[x].func)
        {
            Tasks[x].period = p;
            Tasks[x].delay = d;
            Tasks[x].exec = 0;
            Tasks[x].func = f;
            return x;
        }
    return -1;
}

void Sched_Schedule(void)
{
    for (int x = 0; x < NT; x++)
    {
        if (Tasks[x].func)
        {
            if (Tasks[x].delay)
            {
                Tasks[x].delay--;
            }
            else
            {
                /* Schedule Task */
                Tasks[x].exec++;
                Tasks[x].delay = Tasks[x].period - 1;
            }
        }
    }
}

void Sched_Dispatch(void)
{
    int prev_task = cur_task;
    for (int x = 0; x < cur_task; x++)
    {
        if ((Tasks[x].func) && (Tasks[x].exec))
        {
            Tasks[x].exec = 0;
            cur_task = x;
            // interrupts();
            Tasks[x].func();
            // noInterrupts();
            cur_task = prev_task;
            /* Delete task if one-shot */
            if (!Tasks[x].period)
                Tasks[x].func = 0;
        }
    }
}

void setup()
{
    // initialize digital pin LED_BUILTIN as an output.
    Sched_Init();

    /* add a bunch of one-shot tasks, that will temporarily take up space in the TCB array */
    /* This forces task t1 to have a lower priority, and leave empty TCB entries for the
     *  toggle task added by t0.
     */
    Sched_AddT(t1, 0 /* delay */, 1000 /* period */);
    Sched_AddT(t2, 0 /* delay */, 5000 /* period */);
    Sched_AddT(t3, 0 /* delay */, 10000 /* period */);
}

void int_handler(int sig_num)
{
    if (sig_num != SIGALRM)
        return;
    Sched_Schedule();
    Sched_Dispatch();
}

int main()
{
    setup();
    while (1)
    {
        // nothing
    }
}
