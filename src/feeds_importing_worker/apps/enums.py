from enum import Enum


class FeedStatus(str, Enum):
    NORMAL = 'normal'
    FAILED = 'failed-to-update'
    LOADING = 'is-loading'


class JobStatus(str, Enum):
    PENDING = 'pending'
    DONE = 'done'
    FAILED = 'failed'
    IN_PROGRESS = 'in-progress'

