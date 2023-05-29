import posixpath
import ydb

from ydb_interaction.models import PoolConfig


class YDBClient:
    def __init__(
            self,
            endpoint: str,
            database: str,
            credentials: ydb.Credentials,
            pool_config: PoolConfig = PoolConfig(),
            **kwargs
    ):
        self._endpoint = endpoint
        self._database = database
        self._driver_config = ydb.DriverConfig(
            endpoint=endpoint,
            database=database,
            credentials=credentials,
            **kwargs
        )
        self._driver = ydb.Driver(driver_config=self._driver_config)
        try:
            self._driver.wait(fail_fast=True, timeout=5)
        except TimeoutError:
            raise ydb.ConnectionError(
                f'Connect failed to YDB. Last reported errors by discovery: '
                f'{self._driver.discovery_debug_details()}'
            )
        self._pool = ydb.SessionPool(self.driver, **pool_config.to_dict())

    @property
    def driver_config(self) -> ydb.DriverConfig:
        return self._driver_config

    @property
    def driver(self) -> ydb.Driver:
        return self._driver

    def execute_query(
            self,
            query: str,
            prepare: bool = False,
            directory_path: str = '',
            parameters: dict | None = None,
            commit_tx: bool = False,
            settings: ydb.BaseRequestSettings | None = None
    ) -> ydb.convert.ResultSets:
        query = f'PRAGMA TablePathPrefix("{posixpath.join(self._database, directory_path)}"); {query}'

        def callee(session: ydb.Session):
            prepared_query = query
            if prepare:
                prepared_query = session.prepare(query)

            return session.transaction(ydb.SerializableReadWrite()).execute(
                query=prepared_query,
                parameters=parameters,
                commit_tx=commit_tx,
                settings=settings
            )

        return self._pool.retry_operation_sync(callee)

    def create_table(
            self,
            table_name: str,
            table_description: ydb.TableDescription,
            directory_path: str = '',
            settings: ydb.BaseRequestSettings | None = None
    ):
        def callee(session: ydb.Session):
            session.create_table(
                path=posixpath.join(self._database, directory_path, table_name),
                table_description=table_description,
                settings=settings
            )

        return self._pool.retry_operation_sync(callee)

    def close(self, timeout: int = 5):
        self._pool.stop(timeout=timeout)
        self._driver.stop()
