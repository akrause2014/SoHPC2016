from flask import Flask, request
app = Flask(__name__)


import json
import database as db


@app.route('/worker', methods=['POST'])
def register():
    data = request.get_json(force=True)
    if 'name' in data:
        name = data['name']
    else:
        name = ''
    worker_id = db.register_worker(name)
    # send task if there is one
    task = db.assign_task(worker_id)
    if task:
        del task['_id']
        return json.dumps({'id': worker_id, 'task': task})
    else:
        return json.dumps({'id': worker_id, 'task': None})


@app.route('/worker/<worker_id>', methods=['POST'])
def get_task(worker_id):
    task = db.assign_task(worker_id)
    if task:
        del task['_id']
        return json.dumps({'task': task})
    else:
        return json.dumps({'task': None})


@app.route('/heartbeat/<worker>', methods=['GET'])
def heartbeat(worker):
    print('received heartbeat from %s' % worker)
    db.heartbeat(worker)
    # returns command:
    # - cancel task
    # - new task
    # - shutdown
    # - continue (None)
    return json.dumps({'command': None})


@app.route('/worker/complete/<worker_id>', methods=['POST'])
def task_complete(worker_id):
    print('worker %s has completed task' % worker_id)
    # worker has completed task
    img = request.get_json(force=True)
    db.task_complete(worker_id, img)
    # computation results in body
    # now update the results on the screen!!
    # return new task if available
    return json.dumps({'task': None})


@app.route('/master', methods=['POST'])
def submit_new_master():
    job_data = request.get_json(force=True)
    print('Creating new job: %s' % job_data)
    db.clear_all_tasks()
    num_tasks = db.create_new_job(job_data)
    return json.dumps({'tasks': num_tasks}), 200


@app.route('/master', methods=['GET'])
def view_job_info():
    job_info = db.get_job_info()
    del job_info['xstart']
    del job_info['xstop']
    del job_info['ystart']
    del job_info['ystop']
    return json.dumps(job_info)


@app.route('/master/results/', defaults={'later_than': None}, methods=['GET'])
@app.route('/master/results/<later_than>', methods=['GET'])
def get_latest_data(later_than):
    worker_tasks = db.get_latest_images(later_than)
    last_id = None
    images = []
    for w in worker_tasks:
        last_id = str(w['_id'])
        del w['_id']
        try:
            del w['task']['_id']
        except:
            pass
        images.append(w)
    return json.dumps({'last_id': last_id, 'images': images})


@app.route('/master/workers', methods=['GET'])
def get_workers():
    result = []
    for w in db.get_all_workers():
        w_info = {'name': w['name'],
                  'alive': db.get_current_time() - w['heartbeat'],
                  '_id': str(w['_id'])}
        try:
            w_info['num_tasks'] = w['num_tasks']
        except:
            pass
        result.append(w_info)
    return json.dumps(result)

if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0')
