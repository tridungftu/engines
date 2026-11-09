"""AI-1: dữ liệu DEMO, HTTP mock hoàn toàn; không mở socket/server."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import io
import json
import os
from pathlib import Path
import socket
import threading
import unittest
from contextlib import contextmanager
from unittest.mock import Mock, patch

from test_modules import FeatureCase
from kho_tri_thuc.giao_dien.operations import Operations, SOURCE_DEFAULTS
from kho_tri_thuc.tri_thuc import ai_cuc_bo as ai


OPTIONS = [{"code": "DEMO_A", "name": "DEMO Alpha"}, {"code": "DEMO_B", "name": "DEMO Beta"}]
ANSWER = "MA=DEMO_B | LY_DO=Khớp tên DEMO Beta"
INVALID_MODEL_IDS = ("", " ", "DEMO\x00", "DEMO\r", "DEMO\n", "DEMO\r\n", "DEMO\x1b",
                     "DEMO\t", "DEMO\x7f", "DEMO model", "mô-hình", "DEMO?key", "x" * 201,
                     None, False, 42, [], {})
SAFE_MODEL_IDS = ("a", "NS/DEMO_model-1.2:Q4", "x" * 200)


def config(url="http://127.0.0.1:1234/v1/chat/completions", **kwargs):
    return {"enabled": True, "url": url, "model": "demo-local", "timeout_seconds": 2, **kwargs}


@contextmanager
def fake_ai(*, model_entry=None, tags=None, tags_payload=None, redirects=None, completion=None):
    calls = []
    responses = {
        "/v1/models": {"data": [model_entry or {"id": "demo-local"}]},
        "/v1/chat/completions": completion or {"choices": [{"message": {"content": ANSWER}}]},
    }
    if tags is not None:
        responses["/api/tags"] = {"models": tags}
    if tags_payload is not None:
        responses["/api/tags"] = tags_payload

    def open_request(request, *, timeout):
        parsed = ai.urlparse(request.full_url)
        if parsed.netloc != "127.0.0.1:1234":
            raise AssertionError("Chỉ dùng địa chỉ DEMO đã chuẩn hóa")
        path, raw = parsed.path, request.data
        calls.append((request.get_method(), path, json.loads(raw) if raw else None))
        if path in (redirects or {}):
            raise ai.urllib.error.HTTPError(request.full_url, 307, "DEMO", {"Location": redirects[path]}, io.BytesIO())
        if path not in responses:
            raise ai.urllib.error.HTTPError(request.full_url, 404, "DEMO", {}, io.BytesIO())
        return io.BytesIO(json.dumps(responses[path], ensure_ascii=False).encode("utf-8"))

    opener = Mock()
    opener.open.side_effect = open_request
    with patch.object(ai.urllib.request, "build_opener", return_value=opener), \
            patch.object(socket, "socket", side_effect=AssertionError("Cấm mạng thật")):
        yield config(), calls


class AddressTests(unittest.TestCase):
    def test_default_remains_disabled(self):
        self.assertFalse(ai.local_ai_settings({})["enabled"])

    def test_accepts_only_explicit_loopback_rfc1918_and_tailscale_ranges(self):
        hosts = ("127.0.0.1", "127.2.3.4", "192.168.2.3", "10.2.3.4", "172.16.0.1",
                 "172.31.255.254", "100.64.0.1", "100.127.255.254", "[::1]", "[fd7a:115c:a1e0::2]")
        with patch.object(socket, "getaddrinfo", side_effect=AssertionError("Không được tra DNS")) as dns:
            for host in hosts:
                with self.subTest(host=host):
                    result = ai.local_ai_settings({"local_ai": config(f"http://{host}:1234/v1/chat/completions")})
                    self.assertTrue(result["enabled"], result["error"])
            dns.assert_not_called()

    def test_rejects_domains_https_public_linklocal_and_malformed_urls_without_dns(self):
        urls = ("http://ai.example:1234/v1/chat/completions", "http://0.0.0.0:1234/v1/chat/completions",
                "https://127.0.0.1:1234/v1/chat/completions", "http://8.8.8.8:1234/v1/chat/completions",
                "http://100.63.255.255:1234/v1/chat/completions", "http://100.128.0.1:1234/v1/chat/completions",
                "http://172.32.0.1:1234/v1/chat/completions", "http://169.254.1.2:1234/v1/chat/completions",
                "http://[fe80::1]:1234/v1/chat/completions", "http://[2001:db8::1]:1234/v1/chat/completions",
                "http://[::ffff:8.8.8.8]:1234/v1/chat/completions", "http://[::ffff:127.0.0.1]:1234/v1/chat/completions",
                "http://2130706433:1234/v1/chat/completions",
                "http://127.0.0.1/v1/chat/completions", "http://127.0.0.1:0/v1/chat/completions",
                "http://127.0.0.1:65536/v1/chat/completions", "http://user@127.0.0.1:1234/v1/chat/completions",
                "http://127.0.0.1:1234/v1/chat/completions?proxy=1",
                "http://127.0.0.1:1234/v1/chat/completions#fragment",
                "http://[fd7a:115c:a1e0::1%25eth0]:1234/v1/chat/completions",
                "http://127.0.0.1:1234/\nv1/chat/completions", "http://[broken")
        with patch.object(socket, "getaddrinfo", side_effect=AssertionError("Không được tra DNS")) as dns:
            transport = Mock(return_value=ANSWER)
            for url in urls:
                with self.subTest(url=url):
                    result = ai.local_ai_settings({"local_ai": config(url)})
                    self.assertFalse(result["enabled"])
                    self.assertTrue(result["error"])
                    self.assertIsNone(ai.choose_counterparty(config(url), "DEMO Beta", "DEMO", OPTIONS, transport))
            dns.assert_not_called()
            transport.assert_not_called()

    def test_tailscale_route_uses_tailscale_source_for_ipv4_and_ipv6(self):
        for host, source in (("100.64.1.2", "100.100.1.1"), ("[fd7a:115c:a1e0::2]", "fd7a:115c:a1e0::1")):
            with self.subTest(host=host), patch.object(ai, "source_address", return_value=source) as route:
                transport = Mock(return_value=ANSWER)
                result = ai.choose_counterparty(config(f"http://{host}:1234/v1/chat/completions"),
                                                "DEMO Beta", "DEMO", OPTIONS, transport)
                self.assertEqual("DEMO_B", result["code"])
                route.assert_called_once_with(host.strip("[]"), 1234)
                transport.assert_called_once()

    def test_tailscale_rejects_ordinary_or_unavailable_route_before_http(self):
        settings = config("http://100.64.1.2:1234/v1/chat/completions")
        for source in ("192.168.1.2", "10.1.2.3", "127.0.0.1", "invalid", OSError("no route")):
            kwargs = {"side_effect": source} if isinstance(source, Exception) else {"return_value": source}
            with self.subTest(source=source), patch.object(ai, "source_address", **kwargs), \
                    patch.object(ai.urllib.request, "build_opener") as opener:
                with self.assertRaisesRegex(ValueError, "bật Tailscale"):
                    ai._ask(settings, "DEMO")
                opener.assert_not_called()

    def test_tailscale_socket_binds_verified_source_without_getaddrinfo(self):
        sock = Mock()
        with patch.object(socket, "socket", return_value=sock), \
                patch.object(socket, "getaddrinfo") as dns:
            connection = ai._IPConnection("100.64.1.2:1234", source="100.100.1.1", timeout=2)
            connection.connect()
            sock.bind.assert_called_once_with(("100.100.1.1", 0))
            sock.connect.assert_called_once_with(("100.64.1.2", 1234))
            dns.assert_not_called()
            connection.close()

    def test_source_address_only_queries_udp_route(self):
        with patch.object(socket, "socket") as factory:
            probe = factory.return_value.__enter__.return_value
            probe.getsockname.return_value = ("100.100.1.1", 123)
            self.assertEqual("100.100.1.1", ai.source_address("100.64.1.2", 1234))
            factory.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
            probe.connect.assert_called_once_with(("100.64.1.2", 1234))
            probe.send.assert_not_called()
            probe.sendto.assert_not_called()

    def test_cloud_names_and_remote_config_are_disabled_without_transport(self):
        for extra in ({"model": "demo-CLOUD:latest"}, {"remote_host": "DEMO"}, {"remote_model": "DEMO"}):
            with self.subTest(extra=extra):
                settings = config(**extra)
                normalized = ai.local_ai_settings({"local_ai": settings})
                self.assertFalse(normalized["enabled"])
                self.assertIn("chọn model", normalized["error"])
                transport = Mock(return_value=ANSWER)
                self.assertIsNone(ai.choose_counterparty(settings, "DEMO", "DEMO", OPTIONS, transport))
                transport.assert_not_called()


class FakeAIIntegrationTests(unittest.TestCase):
    def test_legacy_localhost_connects_to_loopback_without_dns(self):
        with fake_ai() as (settings, calls), \
                patch.object(socket, "getaddrinfo", side_effect=AssertionError("Không được tra DNS")) as dns:
            settings["url"] = settings["url"].replace("127.0.0.1", "localhost")
            normalized = ai.local_ai_settings({"local_ai": settings})
            self.assertTrue(normalized["enabled"])
            self.assertIn("127.0.0.1", normalized["url"])
            self.assertEqual("DEMO_B", ai.choose_counterparty(settings, "DEMO", "DEMO", OPTIONS)["code"])
            self.assertEqual(3, len(calls))
            self.assertEqual("/v1/chat/completions", calls[-1][1])
            dns.assert_not_called()

    def test_choose_counterparty_works_without_dns_or_environment_proxy(self):
        with fake_ai() as (settings, calls), patch.dict(os.environ, {
                "HTTP_PROXY": "http://proxy.invalid:9999", "http_proxy": "http://proxy.invalid:9999",
                "HTTPS_PROXY": "http://proxy.invalid:9999", "ALL_PROXY": "http://proxy.invalid:9999",
                "NO_PROXY": "", "no_proxy": ""}), \
                patch.object(socket, "getaddrinfo", side_effect=AssertionError("Không được tra DNS")) as dns:
            result = ai.choose_counterparty(settings, "DEMO Beta", "Chuyển tiền DEMO", OPTIONS)
            self.assertEqual({"code": "DEMO_B", "reason": "Khớp tên DEMO Beta"}, result)
            self.assertEqual([("GET", "/v1/models"), ("GET", "/api/tags"), ("POST", "/v1/chat/completions")],
                             [(method, path) for method, path, _ in calls])
            body = calls[-1][2]
            self.assertEqual("demo-local", body["model"])
            self.assertIn("DEMO Beta", body["messages"][1]["content"])
            dns.assert_not_called()

    def test_ollama_uses_openai_completion_with_local_metadata(self):
        with fake_ai(model_entry={"id": "demo-local:latest"},
                     tags=[{"name": "demo-local:latest", "model": "demo-local:latest"}]) as (settings, calls):
            self.assertEqual("DEMO_B", ai.choose_counterparty(settings, "DEMO", "DEMO", OPTIONS)["code"])
            self.assertEqual("/v1/chat/completions", calls[-1][1])

    def test_lm_studio_unknown_tags_payload_does_not_block_completion(self):
        for payload in ({}, {"error": "Unexpected endpoint"}, {"models": None}, {"models": {}}, []):
            with self.subTest(payload=payload), fake_ai(tags_payload=payload) as (settings, calls):
                self.assertEqual("DEMO_B", ai.choose_counterparty(settings, "DEMO", "DEMO", OPTIONS)["code"])
                self.assertEqual("/v1/chat/completions", calls[-1][1])

    def test_ollama_empty_or_nonmatching_models_list_still_blocks_prompt(self):
        for tags in ([], [{"name": "another-demo-model"}]):
            with self.subTest(tags=tags), fake_ai(tags=tags) as (settings, calls):
                self.assertIsNone(ai.choose_counterparty(settings, "DEMO", "DEMO", OPTIONS))
                self.assertTrue(all(method == "GET" for method, _, _ in calls))

    def test_remote_model_metadata_blocks_prompt_even_with_innocent_name(self):
        for metadata in ({"remote_host": "DEMO"}, {"remote_model": "DEMO"}, {"model": "demo-cloud"}):
            with self.subTest(metadata=metadata), fake_ai(model_entry={"id": "demo-local", **metadata}) as (settings, calls):
                with self.assertRaisesRegex(ValueError, "chọn model chạy trên máy AI"):
                    ai._ask(settings, "DEMO PRIVATE PROMPT")
                self.assertEqual([("GET", "/v1/models", None)], calls)

    def test_ollama_remote_tags_block_prompt_before_post(self):
        for metadata in ({"remote_host": "DEMO"}, {"remote_model": "DEMO"}, {"model": "demo-cloud"}):
            with self.subTest(metadata=metadata), \
                    fake_ai(tags=[{"name": "demo-local:latest", **metadata}]) as (settings, calls):
                with self.assertRaisesRegex(ValueError, "chọn model chạy trên máy AI"):
                    ai._ask(settings, "DEMO PRIVATE PROMPT")
                self.assertTrue(all(method == "GET" and body is None for method, _, body in calls))

    def test_missing_model_blocks_prompt(self):
        with fake_ai(model_entry={"id": "another-demo-model"}) as (settings, calls):
            with self.assertRaisesRegex(ValueError, "đặt đúng tên"):
                ai._ask(settings, "DEMO")
            self.assertTrue(all(method == "GET" for method, _, _ in calls))

    def test_redirects_are_never_followed_for_metadata_or_completion(self):
        for path in ("/v1/models", "/api/tags", "/v1/chat/completions"):
            with self.subTest(path=path), fake_ai(redirects={path: "/redirected"}) as (settings, calls):
                with self.assertRaisesRegex(ValueError, "(không chuyển hướng|kiểm tra dịch vụ Local AI)"):
                    ai._ask(settings, "DEMO")
                self.assertIsNone(ai.choose_counterparty(settings, "DEMO", "DEMO", OPTIONS))
                self.assertFalse(any(url == "/redirected" for _, url, _ in calls))

    def test_output_must_still_choose_an_offered_code(self):
        with fake_ai(completion={"choices": [{"message": {"content": "MA=DEMO_OTHER"}}]}) as (settings, _):
            self.assertIsNone(ai.choose_counterparty(settings, "DEMO", "DEMO", OPTIONS))


class ConnectionCooldownTests(unittest.TestCase):
    def setUp(self):
        self.cache = patch.dict(ai._CONNECTION_FAILURES, {}, clear=True)
        self.cache.start()
        self.addCleanup(self.cache.stop)

    def test_connection_failures_skip_network_for_15_seconds_then_retry(self):
        errors = (ai.urllib.error.URLError(ConnectionRefusedError("DEMO offline")),
                  TimeoutError("DEMO timeout"), ai.http.client.RemoteDisconnected("DEMO closed"))
        for error in errors:
            with self.subTest(error=type(error).__name__), \
                    patch.dict(ai._CONNECTION_FAILURES, {}, clear=True), \
                    patch.object(ai.time, "monotonic", return_value=100) as clock, \
                    patch.object(ai.urllib.request, "build_opener") as factory:
                factory.return_value.open.side_effect = error
                settings = config("http://localhost:1234/v1/chat/completions")
                self.assertIsNone(ai.choose_counterparty(settings, "DEMO PRIVATE", "DEMO PROMPT", OPTIONS))
                self.assertEqual({config()["url"]: 100}, ai._CONNECTION_FAILURES)
                clock.return_value = 114.99
                self.assertIsNone(ai.choose_counterparty(config(), "DEMO", "DEMO", OPTIONS))
                factory.assert_called_once()
                factory.return_value.open.assert_called_once()
                transport = Mock(return_value=ANSWER)
                other = config("http://127.0.0.1:1235/v1/chat/completions")
                self.assertEqual("DEMO_B", ai.choose_counterparty(other, "DEMO", "DEMO", OPTIONS, transport)["code"])
                clock.return_value = 115
                self.assertEqual("DEMO_B", ai.choose_counterparty(settings, "DEMO", "DEMO", OPTIONS, transport)["code"])
                self.assertEqual(2, transport.call_count)
                self.assertEqual({}, ai._CONNECTION_FAILURES)

    def test_completion_connection_failure_also_starts_cooldown(self):
        with fake_ai() as (settings, calls), patch.object(ai.time, "monotonic", return_value=100):
            # Mock metadata separately so the failed socket belongs to completion.
            def read(opener, url, timeout, body=None):
                if url.endswith("/v1/models"):
                    return {"data": [{"id": "demo-local"}]}
                if url.endswith("/api/tags"):
                    return {}
                raise TimeoutError("DEMO timeout")

            with patch.object(ai, "_read_json", side_effect=read) as reader:
                self.assertIsNone(ai.choose_counterparty(settings, "DEMO", "DEMO", OPTIONS))
                self.assertIsNone(ai.choose_counterparty(settings, "DEMO", "DEMO", OPTIONS))
                self.assertEqual(reader.call_count, 3)
                self.assertEqual({settings["url"]: 100}, ai._CONNECTION_FAILURES)
            self.assertEqual([], calls)

    def test_model_or_answer_error_does_not_start_connection_cooldown(self):
        transport = Mock(side_effect=[ValueError("DEMO model error"), ANSWER])
        self.assertIsNone(ai.choose_counterparty(config(), "DEMO", "DEMO", OPTIONS, transport))
        self.assertEqual("DEMO_B", ai.choose_counterparty(config(), "DEMO", "DEMO", OPTIONS, transport)["code"])
        self.assertEqual({}, ai._CONNECTION_FAILURES)


class LocalAISettingsTests(FeatureCase):
    def setUp(self):
        super().setUp()
        self.operation = object.__new__(Operations)
        self.operation.config = self.config
        self.operation.config_path = self.root / "cau_hinh-demo.toml"
        self.operation.root = self.root
        self.operation._mutation_lock = threading.RLock()
        self.operation.bootstrap_job = None
        self.operation.bootstrap_status = {}
        self.paths = {key: str(self.root / key) for key in SOURCE_DEFAULTS}

    def write_settings(self, local_ai):
        (self.root / "source-settings.json").write_text(
            json.dumps({"paths": self.paths, "settings": {"local_ai": local_ai}}, ensure_ascii=False), encoding="utf-8")

    def test_old_localhost_config_is_normalized_before_ui_reads_it(self):
        self.write_settings(config("http://localhost:1234/v1/chat/completions", timeout_seconds=99, error="Lỗi cũ"))
        with patch.object(socket, "getaddrinfo", side_effect=AssertionError("Không được tra DNS")) as dns:
            settings = self.operation.source_settings()["settings"]["local_ai"]
            self.assertTrue(settings["enabled"])
            self.assertEqual("", settings["error"])
            self.assertEqual(config()["url"], settings["url"])
            self.assertEqual(30, settings["timeout_seconds"])
            self.assertEqual(settings, self.operation.overview()["local_ai"])
            dns.assert_not_called()

    def test_invalid_config_shows_ui_error_but_saving_preserves_user_enabled(self):
        for enabled in (True, False):
            with self.subTest(enabled=enabled):
                local_ai = config("http://0.0.0.0:1234/v1/chat/completions", enabled=enabled, error="Lỗi cũ")
                result = self.operation.save_source_settings({"paths": self.paths, "settings": {"local_ai": local_ai}})
                self.assertFalse(result["settings"]["local_ai"]["enabled"])
                self.assertTrue(self.operation.overview()["local_ai"]["error"])
                # Lưu mục khác và đồng bộ lúc khởi động cũng phải giữ enabled gốc.
                self.operation._sync_runtime_settings()
                self.operation.save_learning_settings({"scoring_mode": True})
                saved = json.loads((self.root / "source-settings.json").read_text(encoding="utf-8"))["settings"]["local_ai"]
                self.assertEqual(enabled, saved["enabled"])
                self.assertNotIn("error", saved)
                runtime = json.loads(self.store.conn.execute(
                    "SELECT value FROM workspace_meta WHERE key='v9b_runtime_settings'").fetchone()[0])["local_ai"]
                self.assertEqual(enabled, runtime["enabled"])
                self.assertNotIn("error", runtime)


@contextmanager
def model_http(responses):
    """HTTP mock hoàn toàn: cấm cả socket lẫn DNS, không dựng server."""
    calls = []

    def open_request(request, *, timeout):
        calls.append((request, timeout))
        value = responses.get(ai.urlparse(request.full_url).path, 404)
        if isinstance(value, Exception):
            raise value
        if isinstance(value, int):
            raise ai.urllib.error.HTTPError(request.full_url, value, "DEMO", {}, io.BytesIO())
        body = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False).encode("utf-8")
        return io.BytesIO(body)

    opener = Mock()
    opener.open.side_effect = open_request
    with patch.object(socket, "socket", side_effect=AssertionError("Cấm mạng thật")), \
            patch.object(socket, "getaddrinfo", side_effect=AssertionError("Cấm DNS")), \
            patch.object(ai.urllib.request, "build_opener", return_value=opener) as factory:
        yield calls, factory


class ModelDiscoveryTests(unittest.TestCase):
    def test_three_softwares_and_three_original_ids_independent_of_port_or_names(self):
        ids = ["DEMO-Alpha:Q4", "DEMO-Beta", "DEMO-Gamma"]
        cases = [
            ("ollama", {"models": [{"name": i, "model": i, "size": 1024} for i in ids]}, "da_tai"),
            ("lm_studio", {"models": [{"key": i, "type": "llm", "loaded_instances": [{}],
                                        "size_bytes": 2048, "max_context_length": 8192} for i in ids]}, "san_sang"),
            ("openai_compatible", {"data": [{"id": i, "object": "model"} for i in ids]}, "chua_ro"),
        ]
        for software, payload, state in cases:
            # Cùng cổng và cùng đường dẫn trả metadata của từng phần mềm khác nhau.
            with self.subTest(software=software), model_http({"/api/tags": payload}) as (calls, _):
                result = ai.discover_local_models(config("http://192.168.1.23:7654/v1/chat/completions"))
                self.assertEqual(result["ma_loi"], "")
                self.assertEqual([m["id_model"] for m in result["model_phat_hien"]], ids)
                for model in result["model_phat_hien"]:
                    self.assertEqual(model["loai_phan_mem"], software)
                    self.assertEqual(model["trang_thai"], state)
                    self.assertIs(model["bat"], False)
                    self.assertIsNotNone(datetime.fromisoformat(model["phat_hien_luc"]).tzinfo)
                self.assertEqual(len(calls), 1)
                if software == "lm_studio":
                    self.assertEqual(result["model_phat_hien"][0]["ngu_canh_toi_da"], 8192)
                    self.assertEqual(result["model_phat_hien"][0]["kich_thuoc_byte"], 2048)

    def test_lm_studio_v1_and_v0_fallback_then_openai_use_same_ip_port_only(self):
        cases = [
            ("/api/v1/models", {"models": [{"key": "DEMO", "type": "llm", "loaded_instances": []}]}, "lm_studio", "da_tai"),
            ("/api/v0/models", {"data": [{"id": "DEMO", "type": "llm", "state": "loaded",
                                          "max_context_length": 4096}]}, "lm_studio", "san_sang"),
            ("/v1/models", {"data": [{"id": "DEMO"}]}, "openai_compatible", "chua_ro"),
        ]
        paths = ["/api/tags", "/api/v1/models", "/api/v0/models", "/v1/models"]
        for path, payload, software, state in cases:
            with self.subTest(path=path), model_http({path: payload}) as (calls, _):
                result = ai.discover_local_models({"local_ai": config()})
                self.assertEqual(result["ma_loi"], "")
                model = result["model_phat_hien"][0]
                self.assertEqual((model["loai_phan_mem"], model["trang_thai"]), (software, state))
                self.assertEqual([ai.urlparse(req.full_url).path for req, _ in calls], paths[:paths.index(path) + 1])
                for request, timeout in calls:
                    self.assertEqual(ai.urlparse(request.full_url).netloc, "127.0.0.1:1234")
                    self.assertEqual(request.get_method(), "GET")
                    self.assertIsNone(request.data)
                    self.assertLessEqual(timeout, 2)

    def test_empty_models_are_successful_and_missing_metadata_is_not_invented(self):
        for payload in ({"models": []}, {"data": []}):
            with self.subTest(payload=payload), model_http({"/api/tags": payload}):
                self.assertEqual(ai.discover_local_models(config()), {"model_phat_hien": [], "ma_loi": ""})
        with model_http({"/v1/models": {"data": [{"id": "DEMO"}]}}):
            model = ai.discover_local_models(config())["model_phat_hien"][0]
            self.assertNotIn("kich_thuoc_byte", model)
            self.assertNotIn("ngu_canh_toi_da", model)

    def test_unexpected_endpoint_payload_falls_back_but_malformed_lists_fail_closed(self):
        with model_http({"/api/tags": {"error": "DEMO"}, "/v1/models": {"data": [{"id": "DEMO"}]}}):
            self.assertEqual(ai.discover_local_models(config())["ma_loi"], "")
        for payload in ([], {"data": {}}, {"models": [None]},
                        {"models": [{"key": "DEMO"}]}, {"data": [{"id": "DEMO"}, 42]}):
            with self.subTest(payload=payload), model_http({"/api/tags": payload}):
                self.assertEqual(ai.discover_local_models(config()),
                                 {"model_phat_hien": [], "ma_loi": "LOCAL_AI_PHAN_HOI_KHONG_HOP_LE"})

    def test_forbidden_urls_are_blocked_before_http_without_leaking_address_or_key(self):
        for url in ("http://8.8.8.8:1234/v1/chat/completions", "http://ai.example:1234/v1/chat/completions",
                    "http://169.254.1.1:1234/v1/chat/completions", "http://DEMO_SECRET@127.0.0.1:1234/v1/chat/completions"):
            with self.subTest(url=url), model_http({}) as (calls, factory):
                result = ai.discover_local_models(config(url))
                self.assertEqual(result, {"model_phat_hien": [], "ma_loi": "LOCAL_AI_DIA_CHI_KHONG_HOP_LE"})
                self.assertEqual(calls, [])
                factory.assert_not_called()

    def test_transport_errors_http_redirects_and_remote_models_return_only_fixed_codes(self):
        cases = [
            (TimeoutError("http://192.168.1.23 DEMO_SECRET"), "LOCAL_AI_KET_NOI_LOI"),
            (ai.urllib.error.URLError("http://192.168.1.23 DEMO_SECRET"), "LOCAL_AI_KET_NOI_LOI"),
            (ai.http.client.RemoteDisconnected("DEMO_SECRET"), "LOCAL_AI_KET_NOI_LOI"),
            (307, "LOCAL_AI_CHUYEN_HUONG_BI_CHAN"),
            (500, "LOCAL_AI_HTTP_LOI"),
            ({"models": [{"name": "DEMO", "size": 1, "remote_host": "DEMO_SECRET"}]}, "LOCAL_AI_MODEL_KHONG_CUC_BO"),
            ({"models": [{"key": "DEMO-cloud", "type": "llm", "loaded_instances": []}]}, "LOCAL_AI_MODEL_KHONG_CUC_BO"),
        ]
        for value, code in cases:
            with self.subTest(code=code), model_http({"/api/tags": value}) as (calls, _):
                result = ai.discover_local_models(config())
                self.assertEqual(result, {"model_phat_hien": [], "ma_loi": code})
                self.assertEqual(len(calls), 1)

    def test_response_size_utf8_json_and_total_probe_budget_remain_bounded(self):
        for value in (b"x" * 2_000_001, b"\xff", b"not json"):
            with self.subTest(size=len(value)), model_http({"/api/tags": value}):
                self.assertEqual(ai.discover_local_models(config())["ma_loi"], "LOCAL_AI_PHAN_HOI_KHONG_HOP_LE")
        with model_http({}) as (calls, _), patch.object(ai.time, "monotonic", side_effect=[0, 1, 3]):
            self.assertEqual(ai.discover_local_models(config())["ma_loi"], "LOCAL_AI_HET_THOI_GIAN")
            self.assertEqual(len(calls), 1)

    def test_invalid_model_ids_are_skipped_with_fixed_code_in_all_metadata_formats(self):
        formats = (
            ("ollama", "models", lambda value: {"name": value, "model": value, "size": 1}),
            ("ollama_model_only", "models", lambda value: {"model": value, "size": 1}),
            ("ollama_name_only", "models", lambda value: {"name": value, "size": 1}),
            ("lm_studio_v1", "models", lambda value: {"key": value, "type": "llm", "loaded_instances": []}),
            ("lm_studio_v0", "data", lambda value: {"id": value, "type": "llm", "state": "loaded"}),
            ("openai_compatible", "data", lambda value: {"id": value}),
        )
        for software, key, entry in formats:
            for invalid in INVALID_MODEL_IDS:
                payload = {key: [entry(SAFE_MODEL_IDS[1]), entry(invalid), entry("DEMO-end")]}
                with self.subTest(software=software, invalid=repr(invalid)), \
                        model_http({"/api/tags": payload}) as (calls, _):
                    result = ai.discover_local_models(config())
                    self.assertEqual(result["ma_loi"], "LOCAL_AI_ID_MODEL_KHONG_HOP_LE")
                    self.assertEqual([m["id_model"] for m in result["model_phat_hien"]],
                                     [SAFE_MODEL_IDS[1], "DEMO-end"])
                    self.assertEqual(len(calls), 1)
        with model_http({"/api/tags": {"data": [{"id": "DEMO\x00"}]}}):
            self.assertEqual(ai.discover_local_models(config()),
                             {"model_phat_hien": [], "ma_loi": "LOCAL_AI_ID_MODEL_KHONG_HOP_LE"})

    def test_safe_model_ids_keep_original_value_at_length_boundaries(self):
        with model_http({"/api/tags": {"data": [{"id": value} for value in SAFE_MODEL_IDS]}}):
            result = ai.discover_local_models(config())
        self.assertEqual(result["ma_loi"], "")
        self.assertEqual([m["id_model"] for m in result["model_phat_hien"]], list(SAFE_MODEL_IDS))

    def test_valid_json_over_two_million_bytes_is_rejected_at_exact_boundary(self):
        prefix, suffix = b'{"data":[{"id":"DEMO"}],"padding":"', b'"}'
        for size, expected in ((2_000_000, ""), (2_000_001, "LOCAL_AI_PHAN_HOI_KHONG_HOP_LE")):
            raw = prefix + b"x" * (size - len(prefix) - len(suffix)) + suffix
            self.assertEqual(len(raw), size)
            self.assertEqual(json.loads(raw)["data"], [{"id": "DEMO"}])
            with self.subTest(size=size), model_http({"/api/tags": raw}):
                result = ai.discover_local_models(config())
                self.assertEqual(result["ma_loi"], expected)
                self.assertEqual(len(result["model_phat_hien"]), 0 if expected else 1)

    def test_deep_json_is_rejected_before_parse_and_string_brackets_are_ignored(self):
        for depth in (65, 3000):
            raw = b'{"data":[{"id":"DEMO"}],"extra":' + b"[" * (depth - 1) + b"0" + b"]" * (depth - 1) + b"}"
            with self.subTest(depth=depth), model_http({"/api/tags": raw}), \
                    patch.object(ai.json, "loads", side_effect=AssertionError("Không parse JSON quá sâu")):
                self.assertEqual(ai.discover_local_models(config()),
                                 {"model_phat_hien": [], "ma_loi": "LOCAL_AI_PHAN_HOI_KHONG_HOP_LE"})
        raw = b'{"data":[{"id":"DEMO"}],"extra":' + b"[" * 63 + b"0" + b"]" * 63 + b"}"
        payload = {"data": [{"id": "DEMO"}], "extra": '[{\\\"' * 3000 + '}]\\"'}
        for value in (raw, payload):
            with self.subTest(kind=type(value).__name__), model_http({"/api/tags": value}):
                self.assertEqual(ai.discover_local_models(config())["ma_loi"], "")

    def test_json_parser_value_and_recursion_errors_return_only_fixed_code(self):
        for exception in (ValueError, RecursionError):
            with self.subTest(exception=exception.__name__), model_http({"/api/tags": b'{"data":[]}'}), \
                    patch.object(ai.json, "loads", side_effect=exception("DEMO_SECRET")):
                self.assertEqual(ai.discover_local_models(config()),
                                 {"model_phat_hien": [], "ma_loi": "LOCAL_AI_PHAN_HOI_KHONG_HOP_LE"})

    def test_large_model_lists_are_cut_at_500_entries_with_fixed_code(self):
        for count in (500, 501, 10_000):
            payload = {"data": [{"id": f"DEMO-{index}"} for index in range(count)]}
            with self.subTest(count=count), model_http({"/api/tags": payload}) as (calls, _):
                result = ai.discover_local_models(config())
                self.assertEqual(result["ma_loi"], "" if count == 500 else "LOCAL_AI_QUA_NHIEU_MODEL")
                self.assertEqual([m["id_model"] for m in result["model_phat_hien"]],
                                 [f"DEMO-{index}" for index in range(500)])
                self.assertEqual(len(calls), 1)

    def test_duplicate_models_keep_first_metadata_and_same_id_across_softwares(self):
        payload = {"data": [
            {"id": "DEMO", "type": "llm", "state": "loaded", "max_context_length": 4096},
            {"id": "DEMO", "type": "llm", "state": "not-loaded", "max_context_length": 8192},
            {"id": "DEMO"}, {"id": "DEMO"}, {"id": "DEMO-end"},
        ]}
        with model_http({"/api/tags": payload}):
            result = ai.discover_local_models(config())
        self.assertEqual(result["ma_loi"], "")
        models = result["model_phat_hien"]
        self.assertEqual([(m["loai_phan_mem"], m["id_model"]) for m in models],
                         [("lm_studio", "DEMO"), ("openai_compatible", "DEMO"), ("openai_compatible", "DEMO-end")])
        self.assertEqual((models[0]["trang_thai"], models[0]["ngu_canh_toi_da"]), ("san_sang", 4096))

    def test_deadline_expiring_during_model_processing_discards_partial_results(self):
        for count in (2, 3, 10_000):
            clock = [0]
            original = ai._model_problem

            def inspect(entry):
                problem = original(entry)
                if entry.get("id") == "DEMO-1":
                    clock[0] = 2  # Hết hạn ngay giữa xử lý, sau khi đã có model đầu.
                return problem

            payload = {"data": [{"id": f"DEMO-{index}"} for index in range(count)]}
            with self.subTest(count=count), model_http({"/api/tags": payload}) as (calls, _), \
                    patch.object(ai.time, "monotonic", side_effect=lambda: clock[0]), \
                    patch.object(ai, "_model_problem", side_effect=inspect) as check:
                self.assertEqual(ai.discover_local_models(config()),
                                 {"model_phat_hien": [], "ma_loi": "LOCAL_AI_HET_THOI_GIAN"})
                self.assertLessEqual(check.call_count, 3)
                self.assertEqual(len(calls), 1)

    def test_deadline_expiring_while_stamping_results_cannot_report_success(self):
        clock = [0]
        detected_at = datetime.fromisoformat("2026-11-07T00:00:00+00:00")

        def stamp(*args):
            clock[0] = 2
            return detected_at

        with model_http({"/api/tags": {"data": [{"id": "DEMO"}]}}), \
                patch.object(ai.time, "monotonic", side_effect=lambda: clock[0]), \
                patch.object(ai, "datetime") as date:
            date.now.side_effect = stamp
            self.assertEqual(ai.discover_local_models(config()),
                             {"model_phat_hien": [], "ma_loi": "LOCAL_AI_HET_THOI_GIAN"})

    def test_no_proxy_redirect_and_tailscale_source_guards_are_reused(self):
        with model_http({"/api/tags": {"models": []}}) as (_, factory):
            self.assertEqual(ai.discover_local_models(config())["ma_loi"], "")
            proxy, redirect, handler = factory.call_args.args
            self.assertEqual(proxy.proxies, {})
            self.assertIsNone(redirect.redirect_request(None, None, 307, "", {}, "http://8.8.8.8"))
            self.assertIsInstance(handler, ai._IPHandler)
        for source, code in (("100.100.1.1", ""), ("192.168.1.2", "LOCAL_AI_DUONG_MANG_KHONG_HOP_LE")):
            with self.subTest(source=source), model_http({"/api/tags": {"models": []}}) as (_, factory), \
                    patch.object(ai, "source_address", return_value=source):
                result = ai.discover_local_models(config("http://100.64.1.2:1234/v1/chat/completions"))
                self.assertEqual(result["ma_loi"], code)
                if not code:
                    self.assertEqual(factory.call_args.args[2]._source, source)
                else:
                    factory.assert_not_called()

    def test_default_rules_use_actual_ids_case_insensitive_prefixes_and_never_enable(self):
        ids = ["openai/GPT-OSS-20B:Q4", "Qwen3-8B-Instruct", "google/gemma3:latest", "DEMO"]
        models = [{"id_model": model_id, "bat": False} for model_id in ids]
        original = deepcopy(models)
        self.assertEqual(ai.quy_tac_model_mac_dinh(models), [{
            "module": "*", "function": "*", "uu_tien": ids[0], "du_phong": ids[1:3],
            "che_do": "tu_chon", "bat": False}])
        self.assertEqual(models, original)
        empty = ai.quy_tac_model_mac_dinh([])[0]
        self.assertEqual((empty["uu_tien"], empty["du_phong"]), ("", []))


class ModelConfigurationSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from kho_tri_thuc.core import goi, ho_so_chay
        cls.ho_so = ho_so_chay
        cls.manifest = json.loads((Path(__file__).resolve().parents[1] / "engines/e_hoi_ai/engine.json").read_text(encoding="utf-8"))
        cls.schema = cls.manifest["cau_hinh_schema"]
        cls.validator = ho_so_chay._kiem_schema(cls.schema)
        Validator, checker, registry, _, schemas = goi.dung_registry_schema()
        cls.manifest_validator = Validator(schemas["urn:ktt:manifest:engine.v1"], format_checker=checker, registry=registry)

    def test_readiness_version_matches_engine_manifest(self):
        from kho_tri_thuc.core.dispatcher import KiemSchema
        from kho_tri_thuc.engines.e_hoi_ai import chay as runtime
        from kho_tri_thuc.sdk_core.bootstrap import BiMatBootstrap

        bootstrap = runtime.Bootstrap()
        bootstrap.bi_mat = BiMatBootstrap(b'{}')
        bootstrap.socket = Mock()
        bo_ghi = Mock(spec_set=('ghi', 'thong_ke', 'da_ban_giao', 'thu_lai'))
        bo_ghi.da_ban_giao.return_value = True
        model = dict(id_model='demo-local', trang_thai='san_sang', bat=True)
        settings = dict(local_ai=config(), model_phat_hien=[model],
            quy_tac_model=[dict(module='*', function='*', uu_tien='demo-local',
                du_phong=[], che_do='tu_chon', bat=True)])
        local = Mock(side_effect=AssertionError('Không gọi model lúc readiness'))
        with patch.object(runtime.Bootstrap, "nhan", return_value=bootstrap), \
                patch.object(runtime.Bootstrap, "bao_san_sang",
                    side_effect=lambda **kw: self.assertTrue(kw['kiem_san_sang']())) as ready, \
                patch.object(runtime.Bootstrap, "cho_thu_hoi"), \
                patch.object(runtime, "_VongNhan"), \
                patch.object(runtime.ai_cuc_bo, "discover_local_models", return_value=dict(
                    ma_loi='', model_phat_hien=[model])) as discovery, \
                patch.object(socket, "socket", side_effect=AssertionError("Cấm mạng thật")), \
                patch.object(socket, "getaddrinfo", side_effect=AssertionError("Cấm DNS")):
            runtime.chay(kiem_chu_ky=Mock(), nhan_viec=Mock(), settings=settings,
                bo_ghi=bo_ghi, kiem_schema=KiemSchema().kiem, local_transport=local)
        ready.assert_called_once()
        self.assertEqual(ready.call_args.kwargs['phien_ban'], self.manifest['phien_ban'])
        capability = self.manifest['capability'][0]
        self.assertEqual(ready.call_args.kwargs['contracts'],
            [capability['dau_vao'], capability['dau_ra']])
        discovery.assert_called_once()
        local.assert_not_called()

    def test_manifest_accepts_optional_closed_configuration_schema_and_legacy_manifest(self):
        self.manifest_validator.validate(self.manifest)
        legacy = deepcopy(self.manifest)
        legacy.pop("cau_hinh_schema")
        self.manifest_validator.validate(legacy)
        for schema in ({}, [], {**self.schema, "additionalProperties": True}, {**self.schema, "type": "array"}):
            with self.subTest(schema=schema):
                self.assertFalse(self.manifest_validator.is_valid({**self.manifest, "cau_hinh_schema": schema}))

    def test_discovery_and_defaults_validate_through_existing_core_schema_gate(self):
        with model_http({"/api/tags": {"models": [{"name": "gpt-oss-20b:Q4", "size": 1024}]}}):
            models = ai.discover_local_models(config())["model_phat_hien"]
        value = {"model_phat_hien": models, "quy_tac_model": ai.quy_tac_model_mac_dinh(models)}
        self.validator.validate(value)
        self.ho_so._kiem_cau_hinh(self.schema, value)
        self.assertEqual(len(self.ho_so.kiem_schema(self.schema)), 64)
        self.validator.validate({"model_phat_hien": [], "quy_tac_model": self.schema["properties"]["quy_tac_model"]["default"]})

    def test_invalid_configuration_rejects_extra_fields_wrong_types_and_invalid_rules(self):
        good = {"model_phat_hien": [], "quy_tac_model": ai.quy_tac_model_mac_dinh([])}
        rule = good["quy_tac_model"][0]
        bad_values = [{}, {**good, "url": "DEMO"}, {**good, "model_phat_hien": {}},
                      {**good, "quy_tac_model": [{**rule, "che_do": "khac"}]},
                      {**good, "quy_tac_model": [{**rule, "bat": "true"}]},
                      {**good, "quy_tac_model": [{**rule, "module": ""}]},
                      {**good, "quy_tac_model": [{**rule, "du_phong": ["DEMO", "DEMO"]}]},
                      {**good, "quy_tac_model": [{**rule, "them": 1}]}]
        model = {"loai_phan_mem": "ollama", "id_model": "DEMO", "trang_thai": "da_tai",
                 "bat": False, "phat_hien_luc": "2026-11-07T00:00:00+00:00"}
        for changes in ({"bat": 1}, {"id_model": " "}, {"kich_thuoc_byte": -1},
                        {"ngu_canh_toi_da": True}, {"them": "DEMO"}, {"phat_hien_luc": "07/11/2026"}):
            bad_values.append({**good, "model_phat_hien": [{**model, **changes}]})
        for value in bad_values:
            with self.subTest(value=value):
                self.assertFalse(self.validator.is_valid(value))

    def test_schema_model_ids_and_rule_ids_share_safe_pattern_and_length_limits(self):
        good = {"model_phat_hien": [], "quy_tac_model": ai.quy_tac_model_mac_dinh([])}
        model = {"loai_phan_mem": "ollama", "id_model": "DEMO", "trang_thai": "da_tai",
                 "bat": False, "phat_hien_luc": "2026-11-07T00:00:00+00:00"}
        rule = good["quy_tac_model"][0]
        for value in (*SAFE_MODEL_IDS, *INVALID_MODEL_IDS):
            expected = value in SAFE_MODEL_IDS
            cases = {
                "id_model": {**good, "model_phat_hien": [{**model, "id_model": value}]},
                "du_phong": {**good, "quy_tac_model": [{**rule, "du_phong": [value]}]},
                "uu_tien": {**good, "quy_tac_model": [{**rule, "uu_tien": value}]},
            }
            for field, configuration in cases.items():
                with self.subTest(field=field, value=repr(value)):
                    self.assertEqual(self.validator.is_valid(configuration), expected or (field == "uu_tien" and value == ""))
        for count, expected in ((500, True), (501, False)):
            with self.subTest(model_count=count):
                self.assertEqual(self.validator.is_valid({**good, "model_phat_hien": [model] * count}), expected)


if __name__ == "__main__":
    unittest.main()
