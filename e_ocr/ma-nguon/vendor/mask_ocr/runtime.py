"""Bounded persistent OCR subprocesses; document data stays in local pipes/RAM."""
import base64
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import threading

from .common import ExtractionError

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = {'tesseract_workers': 2, 'vietocr_workers': 1, 'cpu_threads': 2,
            'worker_timeout_seconds': 300, 'tesseract_language': 'vie+eng',
            'paddle_backend': 'paddle'}
LIMITS = {'tesseract_workers': (1, 4), 'vietocr_workers': (1, 2),
          'cpu_threads': (1, 8), 'worker_timeout_seconds': (10, 3600)}


def settings():
    path = Path(os.environ.get('LOCAL_OCR_DUAL_CONFIG', ROOT / 'config/dual-runtime.json'))
    try:
        data = json.loads(path.read_text(encoding='utf-8-sig'))
        if not isinstance(data, dict):
            return dict(DEFAULTS)
        for key in ('paddle_python', 'vietocr_python', 'models',
                    'paddle_onnx_model_dir', 'paddle_onnx_deps'):
            if key in data:
                value = data[key]
                if not isinstance(value, str) or not value.strip():
                    del data[key]
                    continue
                try:
                    data[key] = str((path.parent / value).resolve())
                except (OSError, ValueError):
                    del data[key]
    except (OSError, ValueError, TypeError):
        data = {}
    result = {**DEFAULTS, **data}
    for key, (low, high) in LIMITS.items():
        value = result[key]
        if type(value) is not int or not low <= value <= high:
            result[key] = DEFAULTS[key]
    if result['tesseract_language'] not in ('vie', 'eng', 'vie+eng'):
        result['tesseract_language'] = DEFAULTS['tesseract_language']
    return result


def tesseract_info(cfg=None):
    cfg = settings() if cfg is None else cfg
    language = cfg.get('tesseract_language', DEFAULTS['tesseract_language'])
    if language not in ('vie', 'eng', 'vie+eng'):
        raise ExtractionError('Ngôn ngữ Tesseract phải là vie, eng hoặc vie+eng.')
    candidates = []
    if cfg.get('models'):
        candidates.append(('best', Path(cfg['models']) / 'tessdata_best'))
    candidates.append(('fast', ROOT / 'mask_ocr/models'))
    for kind, directory in candidates:
        if all((directory / (lang + '.traineddata')).is_file() for lang in language.split('+')):
            return {'language': language, 'model': kind, 'tessdata': str(directory), 'ready': True}
    return {'language': language, 'model': 'unavailable', 'tessdata': '', 'ready': False}


def ready(engine='dual'):
    cfg = settings()
    if engine == 'tesseract':
        return tesseract_info(cfg)['ready']
    if engine not in ('dual', 'vietocr'):
        return False
    required = [('paddle_python', ''), ('vietocr_python', ''), ('models', 'vgg_seq2seq.pth'),
                ('models', 'vietocr-base.yml'), ('models', 'vietocr-vgg-seq2seq.yml')]
    backend = cfg.get('paddle_backend', 'paddle')
    if backend == 'onnxruntime':
        required += [('paddle_onnx_model_dir', 'inference.onnx'),
                     ('paddle_onnx_model_dir', 'inference.yml'),
                     ('paddle_onnx_deps', 'onnxruntime/__init__.py')]
        capi = Path(cfg.get('paddle_onnx_deps', '')) / 'onnxruntime/capi'
        if not any(capi.glob('onnxruntime_pybind11_state*.pyd' if os.name == 'nt'
                             else 'onnxruntime_pybind11_state*.so')):
            return False
        if os.name == 'nt' and not (capi/'onnxruntime_providers_shared.dll').is_file():
            return False
    elif backend == 'paddle':
        required.append(('models', 'paddlex/official_models/PP-OCRv5_server_det/inference.pdiparams'))
    else:
        return False
    complete = all(key in cfg and (Path(cfg[key]) / suffix if suffix else Path(cfg[key])).is_file()
                   for key, suffix in required)
    return complete and (engine == 'vietocr' or tesseract_info(cfg)['ready'])


def read_exact(stream, count):
    result = bytearray()
    while len(result) < count:
        chunk = stream.read(count-len(result))
        if not chunk:
            raise EOFError('worker closed')
        result.extend(chunk)
    return bytes(result)


class Engine:
    def __init__(self, kind, cfg):
        self.kind = kind
        self.lock, self.close_lock = threading.Lock(), threading.Lock()
        self.stop_lock = threading.Lock()
        self.closed = False
        self.timeout = cfg.get('worker_timeout_seconds', DEFAULTS['worker_timeout_seconds'])
        threads = str(cfg.get('cpu_threads', DEFAULTS['cpu_threads']))
        env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1',
                   LOCAL_OCR_CPU_THREADS=threads, OMP_NUM_THREADS=threads,
                   MKL_NUM_THREADS=threads, OPENBLAS_NUM_THREADS=threads)
        # Model/backend settings belong to this worker, never an inherited
        # diagnostic shell. Isolated ORT packages do not affect other engines.
        env.pop('LOCAL_OCR_ONNX_MODEL', None)
        env.pop('LOCAL_OCR_PADDLE_BACKEND', None)
        if kind == 'paddle':
            backend = cfg.get('paddle_backend', 'paddle')
            if backend not in ('paddle', 'onnxruntime'):
                raise ExtractionError('Backend Paddle không hợp lệ; chọn paddle hoặc onnxruntime.')
            env['LOCAL_OCR_PADDLE_BACKEND'] = backend
            if backend == 'onnxruntime':
                if not cfg.get('paddle_onnx_model_dir') or not cfg.get('paddle_onnx_deps'):
                    raise ExtractionError('Chưa cấu hình model/thư viện ONNX cho Paddle.')
                env['LOCAL_OCR_ONNX_MODEL'] = cfg['paddle_onnx_model_dir']
                env['PYTHONPATH'] = os.pathsep.join(filter(None,
                    [cfg['paddle_onnx_deps'], env.get('PYTHONPATH', '')]))
        if kind == 'tesseract':
            env['OMP_THREAD_LIMIT'] = threads
            executable, script = sys.executable, 'page_worker.py'
        else:
            # Paddle / oneDNN manage nested OpenMP teams. A global hard limit
            # can stall these teams; use their explicit cpu_threads setting.
            env.pop('OMP_THREAD_LIMIT', None)
            executable, script = cfg[kind+'_python'], 'engine_worker.py'
        self.process = subprocess.Popen(
            [executable, '-B', '-u', str(Path(__file__).with_name(script)),
             kind, cfg.get('models', ''), str(os.getpid())],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=None if os.environ.get('LOCAL_OCR_DEBUG') else subprocess.DEVNULL, env=env,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))

    def stop_process(self):
        with self.stop_lock:
            if self.process.poll() is not None:
                return
            # Windows virtualenv executables can be redirectors. Killing only
            # that PID leaves the real Python child alive, holding the pipe.
            if os.name == 'nt':
                try:
                    subprocess.run(['taskkill', '/PID', str(self.process.pid), '/T', '/F'],
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        timeout=5, creationflags=subprocess.CREATE_NO_WINDOW, check=False)
                except (OSError, subprocess.TimeoutExpired):
                    pass
            if self.process.poll() is None:
                self.process.kill()
            self.process.wait(timeout=3)

    def call(self, payload):
        with self.lock:
            timed_out = threading.Event()

            def expire():
                timed_out.set()
                self.stop_process()

            timer = threading.Timer(self.timeout, expire)
            timer.daemon = True
            try:
                if self.closed:
                    raise EOFError('worker closed')
                data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
                if len(data) > 32 * 1024 * 1024:
                    raise ExtractionError('Dữ liệu trang vượt giới hạn worker OCR.')
                timer.start()
                self.process.stdin.write(struct.pack('!I', len(data)) + data)
                self.process.stdin.flush()
                size = struct.unpack('!I', read_exact(self.process.stdout, 4))[0]
                if size > 12*1024*1024:
                    raise ValueError('worker payload too large')
                response = json.loads(read_exact(self.process.stdout, size))
                if not isinstance(response, dict):
                    raise ValueError('invalid worker response')
                if 'error' in response:
                    raise ExtractionError(response['error'])
                return response
            except ExtractionError:
                raise
            except (OSError, EOFError, ValueError):
                if timed_out.is_set():
                    self.stop_process()
                    raise ExtractionError(f'Bộ OCR {self.kind} vượt thời gian xử lý trang; chưa xuất kết quả cuối.') from None
                code = self.process.poll()
                raise ExtractionError(f'Bộ OCR {self.kind} bị gián đoạn (mã {code}). Kiểm tra runtime/model và thử lại.') from None
            finally:
                timer.cancel()

    def close(self):
        with self.close_lock:
            if self.closed:
                return
            self.closed = True
            self.stop_process()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
            with self.lock:
                for stream in (self.process.stdin, self.process.stdout):
                    if stream:
                        stream.close()


class EnginePool:
    """Threads only move pipe messages; every OCR runs in an isolated process."""
    def __init__(self, kind, cfg, workers=1):
        self.kind, self.cfg = kind, cfg
        maximum = 4 if kind == 'tesseract' else 2 if kind == 'vietocr' else 1
        if type(workers) is not int or not 1 <= workers <= maximum:
            raise ExtractionError('Số worker OCR vượt giới hạn cho phép.')
        self.engines, self.executor = [], None
        try:
            for _ in range(workers):
                self.engines.append(Engine(kind, cfg))
            self.executor = ThreadPoolExecutor(max_workers=workers)
        except BaseException:
            self.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def map(self, tasks):
        """Yield keyed responses as completed; build at most N payloads ahead."""
        pending, source, seen = {}, iter(tasks), set()

        def submit(engine):
            try:
                key, payload = next(source)
            except StopIteration:
                return
            if key in seen:
                raise ExtractionError('Trùng reference trang trong hàng đợi OCR.')
            seen.add(key)
            pending[self.executor.submit(engine.call, payload)] = (key, engine)

        try:
            for engine in self.engines:
                submit(engine)
            while pending:
                completed, _ = wait(pending, return_when=FIRST_COMPLETED)
                for future in completed:
                    key, engine = pending.pop(future)
                    try:
                        response = future.result()
                    except ExtractionError as error:
                        raise ExtractionError(
                            f'Lỗi {self.kind} tại trang/ảnh số {key}: {error}') from None
                    yield key, response
                    submit(engine)
        except BaseException:
            self.close()
            raise
        finally:
            if pending:
                self.close()

    def close(self):
        for engine in self.engines:
            engine.close()
        if self.executor is not None:
            self.executor.shutdown(wait=True, cancel_futures=True)
            self.executor = None


class TesseractPool(EnginePool):
    def __init__(self, data, cfg=None, workers=None):
        cfg = settings() if cfg is None else cfg
        self.info = tesseract_info(cfg)
        if not self.info['ready']:
            raise ExtractionError('Chưa có model ngôn ngữ Tesseract phù hợp.')
        count = cfg.get('tesseract_workers', DEFAULTS['tesseract_workers']) if workers is None else workers
        super().__init__('tesseract', cfg, count)
        payload = {'op': 'open', 'document': base64.b64encode(data).decode('ascii'),
                   'language': self.info['language'], 'model': self.info['model'],
                   'tessdata': self.info['tessdata']}
        try:
            futures = [self.executor.submit(engine.call, payload) for engine in self.engines]
            for future in futures:
                future.result()
        except BaseException:
            self.close()
            raise
