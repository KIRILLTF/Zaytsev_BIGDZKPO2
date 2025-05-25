# tests/test_services.py
"""
Набор заглушек и тестов, дающих ≈70 % покрытия всего репозитория.
Запуск: pytest -q
"""
import sys
import types
import os
import io
import asyncio
from pathlib import Path

# --------------------- Стаб-обёртки для внешних библиотек ----------------------
def _stub_fastapi() -> None:
    fastapi = types.ModuleType("fastapi")

    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str | None = None):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail or status_code)

    class UploadFile:
        def __init__(
            self,
            *,
            filename: str = "file.txt",
            content: bytes = b"data",
            content_type: str = "text/plain",
        ):
            self.filename = filename
            self._content = content
            self.content_type = content_type

        async def read(self) -> bytes:
            return self._content

    def File(*args, **kwargs):
        return None

    class FastAPI:
        def __init__(self, *args, **kwargs):
            self.routes = []
            self.state = types.SimpleNamespace()

        def _reg(self, method: str, path: str, fn):
            self.routes.append((method, path, fn))

        def post(self, path: str, **kwargs):
            return lambda fn: (self._reg("POST", path, fn), fn)[1]

        def get(self, path: str, **kwargs):
            return lambda fn: (self._reg("GET", path, fn), fn)[1]

        def on_event(self, *args, **kwargs):
            return lambda fn: fn

    responses = types.ModuleType("fastapi.responses")

    class StreamingResponse:
        def __init__(self, content, media_type=None, headers=None):
            self.content = content
            self.media_type = media_type
            self.headers = headers or {}
            self.status_code = 200

    fastapi.FastAPI = FastAPI
    fastapi.File = File
    fastapi.UploadFile = UploadFile
    fastapi.HTTPException = HTTPException
    responses.StreamingResponse = StreamingResponse

    sys.modules["fastapi"] = fastapi
    sys.modules["fastapi.responses"] = responses


def _stub_httpx() -> None:
    httpx = types.ModuleType("httpx")

    class Response:
        def __init__(self, status_code=200, content=b"", json_data=None, headers=None):
            self.status_code = status_code
            self.content = content
            self._json = json_data or {}
            self.headers = headers or {}
            self.text = (
                content.decode()
                if isinstance(content, (bytes, bytearray))
                else str(content)
            )

        def json(self):
            return self._json

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")

    class AsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, url: str, files=None):
            if url.endswith("/internal/store"):
                return Response(201, json_data={"file_id": "dummy"})
            if "/analyse/" in url:
                return Response(json_data={"analysis": "ok"})
            return Response()

        async def get(self, url: str):
            if "/download/" in url:
                return Response(content=b"abc")
            return Response(json_data={"result": "ok"})

    httpx.Response = Response
    httpx.AsyncClient = AsyncClient
    sys.modules["httpx"] = httpx


def _stub_sqlalchemy() -> None:
    sa = types.ModuleType("sqlalchemy")

    def create_engine(*args, **kwargs):
        class _EngineStub:
            def connect(self):
                return types.SimpleNamespace(close=lambda: None)

        return _EngineStub()

    orm = types.ModuleType("sqlalchemy.orm")

    def sessionmaker(*args, **kwargs):
        def _session_factory():
            return types.SimpleNamespace(
                add=lambda *a, **k: None,
                commit=lambda: None,
                rollback=lambda: None,
                close=lambda: None,
            )

        return _session_factory

    exc = types.ModuleType("sqlalchemy.exc")
    exc.OperationalError = type("OperationalError", (), {})
    exc.SQLAlchemyError = type("SQLAlchemyError", (), {})

    sa.create_engine = create_engine
    sa.orm = orm
    sa.exc = exc
    orm.sessionmaker = sessionmaker

    sys.modules["sqlalchemy"] = sa
    sys.modules["sqlalchemy.orm"] = orm
    sys.modules["sqlalchemy.exc"] = exc


def _stub_minio() -> None:
    minio = types.ModuleType("minio")

    class Minio:
        def __init__(self, *args, **kwargs):
            pass

        def bucket_exists(self, bucket_name):
            return True

        def make_bucket(self, bucket_name):
            pass

        def put_object(self, *args, **kwargs):
            pass

        def get_object(self, *args, **kwargs):
            return io.BytesIO(b"report")

    minio.Minio = Minio
    minio.S3Error = type("S3Error", (), {})
    sys.modules["minio"] = minio


def _stub_rapidfuzz() -> None:
    rapidfuzz = types.ModuleType("rapidfuzz")

    class _Fuzz:
        @staticmethod
        def ratio(a: str, b: str) -> int:
            return 100 if a == b else 0

    rapidfuzz.fuzz = _Fuzz
    sys.modules["rapidfuzz"] = rapidfuzz


# Подключаем все стаб-стаблицы
for stub in (
    _stub_fastapi,
    _stub_httpx,
    _stub_sqlalchemy,
    _stub_minio,
    _stub_rapidfuzz,
):
    stub()

# -------------------------------------------------------------------
# Настраиваем проектный путь и переменные окружения
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

os.environ.update(
    {
        "DATABASE_URL": "sqlite:///:memory:",
        "MINIO_URL": "http://minio:9000",
        "MINIO_ACCESS_KEY": "minio",
        "MINIO_SECRET_KEY": "password",
    }
)

# Затыкаем shared.models
shared_models = types.ModuleType("shared.models")


class _Base:
    class metadata:
        @staticmethod
        def create_all(*args, **kwargs):
            return None


class _Report:
    def __init__(self, id, filename):
        self.id = id
        self.filename = filename


shared_models.Base = _Base
shared_models.Report = _Report
sys.modules["shared.models"] = shared_models

# -------------------------------------------------------------------
# Импортируем ваши сервисы
import importlib

analysis_analyse = importlib.import_module("analysis_service.analyse")
analysis_main = importlib.import_module("analysis_service.main")
storing_main = importlib.import_module("storing_service.main")
gateway_main = importlib.import_module("gateway.main")

# -------------------------------------------------------------------
# Тесты
def test_basic_helpers():
    assert analysis_analyse.basic_stats("a\n\nb")[0] == 2
    assert analysis_analyse.is_duplicate("x", ["x"]) == "x"
    assert analysis_analyse.is_duplicate("y", ["x"]) is None


def test_analysis_endpoints():
    stats = asyncio.run(analysis_main.stats("fileX"))
    assert (stats.words, stats.characters) == (1, 3)

    cmp_res = asyncio.run(
        analysis_main.compare(
            analysis_main.CompareRequest(file_id1="file1", file_id2="file2")
        )
    )
    assert cmp_res.identical


def test_storing_flow():
    asyncio.run(storing_main.startup_event())

    UFile = sys.modules["fastapi"].UploadFile
    file_obj = UFile(filename="doc.txt", content=b"hello", content_type="text/plain")
    resp = asyncio.run(storing_main.upload_report(file_obj))
    assert "file_id" in resp

    stream_resp = asyncio.run(storing_main.download_report(resp["file_id"]))
    assert stream_resp.content.read() == b"report"


def test_gateway_routes():
    UFile = sys.modules["fastapi"].UploadFile
    up_file = UFile(filename="foo.txt", content=b"bar", content_type="text/plain")

    assert asyncio.run(gateway_main.upload_file(up_file))["file_id"] == "dummy"
    assert asyncio.run(gateway_main.get_file("dummy"))["result"] == "ok"
    assert asyncio.run(gateway_main.analyse_file("dummy"))["analysis"] == "ok"

    img = asyncio.run(gateway_main.get_wordcloud("loc"))
    assert img.status_code == 200
    assert img.headers["Content-Type"] == "image/png"
