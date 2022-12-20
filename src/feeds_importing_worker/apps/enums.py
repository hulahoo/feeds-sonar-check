from enum import Enum


class FeedStatus(str, Enum):
    NORMAL = 'normal'
    FAILED = 'failed-to-update'
    LOADING = 'is-loading'
