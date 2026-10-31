#include <dryos.h>
#include <property.h>
#include <bmp.h>
#include <config.h>
#include <consts.h>
#include <lens.h>
#include <tasks.h>

extern struct task* first_task;
extern int _get_task_info_by_id(int task_id, void *task_attr) __attribute__((weak));

int get_task_info_by_id(int task_id, void *task_attr)
{
    if (&_get_task_info_by_id && first_task)
    {
        struct task *task = first_task + (task_id & 0xff);
        return _get_task_info_by_id(task->taskId, task_attr);
    }
    return 0;
}
