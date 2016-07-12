from pymongo import MongoClient
from bson.objectid import ObjectId
import time
import random


client = MongoClient()
workers = client.cluster.workers
tasks = client.cluster.tasks
images = client.cluster.images


def register_worker(name=''):
    doc = {'heartbeat': get_current_time(), 'name': name, 'num_tasks': 0}
    return str(workers.insert_one(doc).inserted_id)


def heartbeat(worker_id):
    workers.find_one_and_update(
        {'_id': ObjectId(worker_id)},
        {'$set': {'heartbeat': get_current_time()}})


def task_complete(worker_id, imagesection):
    # remove task
    old_worker = workers.find_one_and_update(
        {'_id': ObjectId(worker_id)},
        {'$set': {'heartbeat': get_current_time()},
         '$inc': {'num_tasks': 1},
         '$unset': {'task': 1}})
    del old_worker['_id']
    # store imagesection
    old_worker['image'] = imagesection
    images.insert_one(old_worker)
    return old_worker


def get_latest_images(later_than):
    if not later_than:
        return list(images.find({}, sort=[('_id', 1)]))
    else:
        return list(images.find(filter={'_id': {'$gt': ObjectId(later_than)}},
                                sort=[('_id', 1)]))


def get_all_workers():
    return workers.find({}, sort=[('_id', 1)])


def remove_worker(worker_id):
    workers.delete_one({'_id': ObjectId(worker_id)})


def find_abandoned(delay):
    # check for all the workers whose heartbeat is older than the delay
    timestamp = get_current_time() - delay
    abandoned_tasks = set()
    abandoned_workers = set()
    cursor = workers.find({'heartbeat': {'$lt': timestamp}})
    for worker in cursor:
        abandoned_workers.add(str(worker['_id']))
        if 'task' in worker:
            task = worker['task']
            abandoned_tasks.add(task)
    return abandoned_workers, abandoned_tasks


def add_task(task):
    tasks.insert_one(task)


def assign_task(worker_id):
    # select a random task
    # task = tasks.find_one_and_delete({})
    task = tasks.find_one_and_delete({}, limit=1, sort=[('random_id', 1)])
    # assign it to the worker
    workers.find_one_and_update(
        {'_id': ObjectId(worker_id)},
        {'$set': {'task': task}})
    return task


def delete_abandoned_workers(delay):
    timestamp = get_current_time() - delay
    workers.delete_many({'heartbeat': {'$lt': timestamp}})


def clear_all_tasks():
    # delete all unassigned tasks
    tasks.delete_many({})
    images.delete_many({})
    # delete all tasks that are assigned
    workers.update_many({}, {'$unset': {'task': 1}})


def create_new_job(job_description):
    # compute_function = point_in_julia_set;
    # xmin = -2.0;
    # xmax = 1.0;
    # ymin = -1.5;
    # ymax = 1.5;
    # cim = 0.01;
    # cre = 0.285;
    # grid_size_x = 768;
    # grid_size_y = Math.floor(grid_size_x * (ymax - ymin)/(xmax - xmin));
    # max_iter = 5000;
    # pixels_in_task = 96
    grid_size_x = int(job_description['grid_size_x'])
    task_size = int(job_description['task_size'])
    xmin = float(job_description['xmin'])
    xmax = float(job_description['xmax'])
    ymin = float(job_description['ymin'])
    ymax = float(job_description['ymax'])
    grid_size_y = int(grid_size_x * (ymax - ymin) / (xmax - xmin))
    job_description['grid_size_y'] = grid_size_y
    num_tasks = 0
    total_num_tasks = grid_size_y / task_size * grid_size_x / task_size
    task_ids = random.sample(range(0, total_num_tasks), total_num_tasks)
    for xstart in range(0, grid_size_x, task_size):
        xstop = min(grid_size_x, xstart + task_size)
        for ystart in range(0, grid_size_y, task_size):
            ystop = min(grid_size_y, ystart + task_size)
            # print('creating task: (%s, %s) (%s, %s)' %
            #                       (xstart, xstop, ystart, ystop))
            task = create_task(xstart, xstop, ystart, ystop,
                               job_description, task_ids.pop())
            num_tasks += 1
            # print(task)
            add_task(task)
    print('created %s tasks' % num_tasks)
    return num_tasks


def create_task(xstart, xstop, ystart, ystop, job_description, task_id):
    task = {
        'random_id': task_id,
        'xstart': xstart,
        'xstop': xstop,
        'ystart': ystart,
        'ystop': ystop,
        'grid_size_x': int(job_description['grid_size_x']),
        'grid_size_y': int(job_description['grid_size_y']),
        'max_iter': int(job_description['max_iter']),
        'xmin': float(job_description['xmin']),
        'xmax': float(job_description['xmax']),
        'ymin': float(job_description['ymin']),
        'ymax': float(job_description['ymax']),
        'task_size': int(job_description['task_size']),
        'cim': float(job_description['cim']),
        'cre': float(job_description['cre']),
        'compute_function': job_description['compute_function']
    }
    return task


def get_job_info():
    return tasks.find_one({}, {'_id': 0})


def get_current_time():
    return int(time.time())
