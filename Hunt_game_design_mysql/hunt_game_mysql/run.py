from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from HuntGame import app  # goes into __init__ in HuntGame to grab app
from flask_apscheduler import APScheduler


def test_auto_jobs():
    with app.app_context():
        for job_id in scheduler.get_jobs():
            print(job_id)
            print(job_id.next_run_time)


def my_listener(event):
    if event.exception:
        print('The job crashed :(')
    else:
        print('The job worked :)')


if __name__ == "__main__":
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    test_auto_jobs()
    app.run(debug=True)
