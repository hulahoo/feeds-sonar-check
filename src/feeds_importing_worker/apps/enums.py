from enum import Enum


class FeedStatus(str, Enum):
    NORMAL = 'normal'
    FAILED = 'failed-to-update'
    LOADING = 'is-loading'


class JobStatus(str, Enum):
    SUCCESS = 'success'
    FAILED = 'failed'
    IN_PROGRESS = 'in-progress'


class WorkerJobStatus:
    PENDING = 'pending'
    RUNNING = 'running'
    FINISHED = 'finished'
