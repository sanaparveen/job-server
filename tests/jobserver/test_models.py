from datetime import timedelta

import pytest
from django.utils import timezone

from ..factories import JobFactory


@pytest.mark.django_db
def test_job_status_completed():
    now = timezone.now()
    one_minute = timedelta(seconds=60)
    job = JobFactory(started_at=now - one_minute, completed_at=now)

    assert job.status == "Completed"


@pytest.mark.django_db
def test_job_status_dependency_failed():
    job = JobFactory(status_code=7)

    assert job.status == "Dependency Failed"


@pytest.mark.django_db
def test_job_status_failed():
    job = JobFactory(status_code=1)

    assert job.status == "Failed"


@pytest.mark.django_db
def test_job_status_in_progress():
    one_minute = timedelta(seconds=60)
    job = JobFactory(started_at=timezone.now() - one_minute)

    assert job.status == "In Progress"


@pytest.mark.django_db
def test_job_status_status_6_is_pending():
    job = JobFactory(status_code=6)

    assert job.status == "Pending"


@pytest.mark.django_db
def test_job_status_unstarted_is_pending():
    job = JobFactory()

    assert job.status == "Pending"
