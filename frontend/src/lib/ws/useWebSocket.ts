"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { BATON_API_KEY, WS_URL } from "@/config/constants";
import type { EventEnvelope } from "@/lib/api/types";

type WSStatus = "connecting" | "connected" | "disconnected";

export function useWebSocket(
  missionId: string | null,
  onEvent?: (event: EventEnvelope) => void,
) {
  const [status, setStatus] = useState<WSStatus>("disconnected");
  const wsRef = useRef<WebSocket | null>(null);
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  const reconnectTimer = useRef<ReturnType<typeof setTimeout>>();
  const reconnectDelay = useRef(1000);

  const connect = useCallback(() => {
    if (!missionId) return;
    setStatus("connecting");

    const token = BATON_API_KEY ? `?token=${encodeURIComponent(BATON_API_KEY)}` : "";
    const ws = new WebSocket(`${WS_URL}/ws/${missionId}${token}`);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus("connected");
      reconnectDelay.current = 1000;
    };

    ws.onmessage = (e) => {
      try {
        const event = JSON.parse(e.data) as EventEnvelope;
        onEventRef.current?.(event);
      } catch {}
    };

    ws.onclose = () => {
      setStatus("disconnected");
      wsRef.current = null;
      reconnectTimer.current = setTimeout(() => {
        reconnectDelay.current = Math.min(reconnectDelay.current * 2, 10000);
        connect();
      }, reconnectDelay.current);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [missionId]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
      wsRef.current = null;
    };
  }, [connect]);

  return { status };
}
