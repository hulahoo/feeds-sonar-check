from src.models.base import SyncPostgresDriver
from src.models.models import Feed, Source, Indicator


class FeedProvider:
    def create(self, *, data_to_create: dict) -> Feed:
        with SyncPostgresDriver().session() as db:
            feed = Feed(**data_to_create)

            db.add(feed)
            db.flush()
            db.commit()
            db.refresh(feed)
            return feed

    def delete(self, feed_name: str):
        with SyncPostgresDriver().session() as db:
            db.query(Feed).filter(Feed.name == feed_name).delete()
            db.commit()


class SourceProvider:
    # def create(self, *, data_to_create: dict) -> Feed:
    #     with SyncPostgresDriver().session() as db:
    #         feed = Feed(**data_to_create)

    #         db.add(feed)
    #         db.flush()
    #         db.commit()
    #         db.refresh(feed)
    #         return feed

    def read(self) -> list:
        with SyncPostgresDriver().session() as db:
            sources = db.query(Source).all()
            return sources


class IndicatorProvider:
    def create(self, *, data_to_create: dict) -> Indicator:
        with SyncPostgresDriver().session() as db:
            indicator = Indicator(**data_to_create)

            db.add(indicator)
            db.flush()
            db.commit()
            db.refresh(indicator)
            return indicator

    def read_by_value(self, **kwargs):
        with SyncPostgresDriver().session() as db:
            sources = db.query(Indicator)filter_by(**kwargs).first()
            return sources
