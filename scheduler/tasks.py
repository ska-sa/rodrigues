import logging
from datetime import datetime
import tempfile
import os

from celery import shared_task
from pytz import timezone
import docker
from django.conf import settings
import requests.exceptions

from scheduler.models import Job


logger = logging.getLogger(__name__)


def crashed(job, msg):
        job.log += msg
        job.state = job.CRASHED
        job.save()
        logger.error(msg)


@shared_task
def simulate(job_id):
    job = Job.objects.get(pk=job_id)
    job.log = "running...\n"
    job.state = job.RUNNING
    job.started = datetime.now(timezone(settings.TIME_ZONE))
    job.save()
    logger.info('starting job %s' % job_id)

    client = docker.Client(**settings.DOCKER_SETTINGS)

    try:
        client.version()
    except requests.exceptions.ConnectionError as e:
        msg = "Can't connect to docker daemon:\n%s\n" % str(e)
        crashed(job, msg)
        raise

    tempdir = tempfile.mkdtemp(dir=settings.MEDIA_ROOT,
                               prefix=str(job_id))

    # Nginx container runs as unprivileged
    os.chmod(tempdir, 755)

    input = os.path.join(tempdir, 'input')
    output = os.path.join(tempdir, 'output')
    os.mkdir(input)
    os.mkdir(output)

    job.results_dir = os.path.basename(tempdir)
    job.save(update_fields=["results_dir"])

    with open(os.path.join(input, 'parameters.json'), 'w') as sims:
        sims.write((job.config))

    logging.info("creating container from image %s" % job.docker_image)
    try:
        container = client.create_container(image=job.docker_image,
                                            command='/run.sh ' + tempdir,

                                            )
    except requests.exceptions.ConnectionError as e:
        msg = "cant create container: %s" % str(e)
        crashed(job, msg)
        raise

    try:
        if hasattr(settings, 'CONTAINER'):
            client.start(container,
                         volumes_from='rodrigues_storage_1')
        else:
            client.start(container,
                         binds={tempdir: {'bind': tempdir}})
    except requests.exceptions.HTTPError as e:
        msg = "can't start container: %s" % str(e)
        crashed(job, msg)
        raise

    state = client.wait(container)
    job.log += client.logs(container).decode()
    if state != 0:
        msg = "simulation crashed (state %s)" % state
        crashed(job, msg)
        raise Exception(msg)
    else:
        msg = "simulation finished"
        logger.info(msg)
        job.state = job.FINISHED
        job.log += msg
        job.finished = datetime.now(timezone(settings.TIME_ZONE))
        job.save()
