"""Test tap-to-target sync."""

import io
from pathlib import Path
from contextlib import redirect_stdout
from datetime import datetime

from tap_base.samples.sample_tap_parquet.parquet_tap import SampleTapParquet
from tap_base.samples.sample_target_parquet.parquet_target import SampleTargetParquet
from tap_base.samples.sample_target_csv.csv_target import SampleTargetCSV

SAMPLE_FILENAME = "/tmp/testfile.parquet"
SAMPLE_TAP_CONFIG = {"filepath": SAMPLE_FILENAME}
SAMPLE_TARGET_PARQUET_CONFIG = {
    "filepath": f"{SAMPLE_FILENAME.replace('.parquet', '-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.parquet')}"
}
SAMPLE_TARGET_CSV_CONFIG = {"target_folder": f"./.output"}


def sync_end_to_end(tap, target):
    buf = io.StringIO()
    with redirect_stdout(buf):
        tap.sync_all()
    buf.seek(0)
    target.process_lines(buf)


def test_parquet_to_csv():
    tap = SampleTapParquet(config=SAMPLE_TAP_CONFIG, state=None)
    target = SampleTargetCSV(config=SAMPLE_TARGET_CSV_CONFIG)
    sync_end_to_end(tap, target)


def test_parquet_to_parquet():
    tap = SampleTapParquet(config=SAMPLE_TAP_CONFIG, state=None)
    target = SampleTargetParquet(config=SAMPLE_TARGET_PARQUET_CONFIG)
    sync_end_to_end(tap, target)
    # assert Path(SAMPLE_TARGET_PARQUET_CONFIG["filepath"]).exists()
