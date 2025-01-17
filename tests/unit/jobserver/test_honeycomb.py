import pytest
from django.utils import timezone

from jobserver.honeycomb import (
    format_honeycomb_timestamps,
    format_trace_id,
    format_trace_link,
)

from ...factories import JobFactory


def test_format_trace_id_hexadecimal():
    decimal_trace_id = 300559129712114075302075132513478005344
    hex_trace_id = "e21d953231b76bd98bf45d5e5bc85260"
    assert format_trace_id(decimal_trace_id) == hex_trace_id


def test_format_trace_id_hexadecimal_leading_zeros():
    decimal_trace_id = 15209551489903251743569348292329094282
    hex_trace_id = "0b7140c8e6bafc8ae485e68146dc3c8a"
    assert format_trace_id(decimal_trace_id) == hex_trace_id


@pytest.mark.freeze_time("2022-06-15 13:00")
def test_format_honeycomb_timestamps():
    job = JobFactory(completed_at=timezone.now())
    honeycomb_timestamps = format_honeycomb_timestamps(job)
    assert honeycomb_timestamps["honeycomb_starttime_unix"] == 1655297940
    assert honeycomb_timestamps["honeycomb_endtime_unix"] == 1655298060


@pytest.mark.freeze_time("2022-06-15 13:00")
def test_format_trace_link():
    job = JobFactory(completed_at=timezone.now())
    url = format_trace_link(job)
    assert "trace_start_ts=1655297940&trace_end_ts=1655298060" in url
    assert "bennett-institute-for-applied-data-science" in url
