from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock


@dataclass(frozen=True)
class RequestSample:
    method: str
    path: str
    status_code: int
    duration_ms: float


class RuntimeMetrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._request_counts: dict[tuple[str, str, int], int] = defaultdict(int)
        self._request_duration_ms: dict[tuple[str, str], float] = defaultdict(float)
        self._recent: deque[RequestSample] = deque(maxlen=200)

    def record_request(
        self,
        *,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
    ) -> None:
        route = _normalize_path(path)
        with self._lock:
            self._request_counts[(method, route, status_code)] += 1
            self._request_duration_ms[(method, route)] += duration_ms
            self._recent.append(
                RequestSample(
                    method=method,
                    path=route,
                    status_code=status_code,
                    duration_ms=duration_ms,
                )
            )

    def render_prometheus(self) -> str:
        with self._lock:
            request_counts = dict(self._request_counts)
            request_durations = dict(self._request_duration_ms)
            recent = list(self._recent)

        lines = [
            "# HELP baton_http_requests_total Total HTTP requests by method, route, and status.",
            "# TYPE baton_http_requests_total counter",
        ]
        for (method, route, status_code), count in sorted(request_counts.items()):
            lines.append(
                "baton_http_requests_total"
                f'{{method="{method}",route="{route}",status="{status_code}"}} {count}'
            )

        lines.extend(
            [
                "# HELP baton_http_request_duration_ms_total Total HTTP request duration in ms.",
                "# TYPE baton_http_request_duration_ms_total counter",
            ]
        )
        for (method, route), total in sorted(request_durations.items()):
            lines.append(
                "baton_http_request_duration_ms_total"
                f'{{method="{method}",route="{route}"}} {total:.3f}'
            )

        lines.extend(
            [
                "# HELP baton_recent_requests Current number of retained recent request samples.",
                "# TYPE baton_recent_requests gauge",
                f"baton_recent_requests {len(recent)}",
            ]
        )
        return "\n".join(lines) + "\n"


def _normalize_path(path: str) -> str:
    parts = path.strip("/").split("/")
    if not parts or parts == [""]:
        return "/"
    normalized: list[str] = []
    for part in parts:
        if part.startswith(("mis_", "evt_", "prop_", "edg_")):
            normalized.append("{id}")
        elif ":" in part:
            normalized.append("{actor_id}")
        else:
            normalized.append(part)
    return "/" + "/".join(normalized)


runtime_metrics = RuntimeMetrics()
