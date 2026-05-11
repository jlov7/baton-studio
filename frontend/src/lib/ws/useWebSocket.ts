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
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectDelay = useRef(1000);
  const connectRef = useRef<() => void>(() => {});

  useEffect(() => {
    onEventRef.current = onEvent;
  }, [onEvent]);

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
        connectRef.current();
      }, reconnectDelay.current);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [missionId]);

  useEffect(() => {
    connectRef.current = connect;
  }, [connect]);

  useEffect(() => {
    connectRef.current();
    return () => {
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.close();
      }
      wsRef.current = null;
    };
  }, [missionId]);

  return { status };
}
