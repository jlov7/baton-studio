"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type {
  AgentDetail,
  BatonStateResponse,
  CausalGraphSnapshot,
  EventEnvelope,
  MissionResponse,
  SCMetricResponse,
  WorldSnapshot,
} from "@/lib/api/types";
import { getMission } from "@/lib/api/missions";
import { getWorld } from "@/lib/api/world";
import { getBatonState } from "@/lib/api/baton";
import { listAgents } from "@/lib/api/agents";
import { getGraph } from "@/lib/api/causal";
import { getSCMetric } from "@/lib/api/metrics";
import { getEvents } from "@/lib/api/events";
import { useWebSocket } from "@/lib/ws/useWebSocket";
import { MISSION_STORAGE_KEY } from "@/config/constants";
import { ApiError } from "@/lib/api/client";

interface MissionState {
  missionId: string | null;
  mission: MissionResponse | null;
  world: WorldSnapshot | null;
  baton: BatonStateResponse | null;
  agents: AgentDetail[];
  graph: CausalGraphSnapshot | null;
  scMetric: SCMetricResponse | null;
  events: EventEnvelope[];
  wsStatus: "connecting" | "connected" | "disconnected";
  loading: boolean;
  error: string | null;
  setMissionId: (id: string | null) => void;
  refresh: () => Promise<void>;
}

const MissionContext = createContext<MissionState | null>(null);

export function MissionProvider({ children }: { children: ReactNode }) {
  const [missionId, setMissionIdState] = useState<string | null>(null);
  const [mission, setMission] = useState<MissionResponse | null>(null);
  const [world, setWorld] = useState<WorldSnapshot | null>(null);
  const [baton, setBaton] = useState<BatonStateResponse | null>(null);
  const [agents, setAgents] = useState<AgentDetail[]>([]);
  const [graph, setGraph] = useState<CausalGraphSnapshot | null>(null);
  const [scMetric, setScMetric] = useState<SCMetricResponse | null>(null);
  const [events, setEvents] = useState<EventEnvelope[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const setMissionId = useCallback((id: string | null) => {
    setMissionIdState(id);
    if (typeof window === "undefined") return;

    const url = new URL(window.location.href);
    if (id) {
      window.localStorage.setItem(MISSION_STORAGE_KEY, id);
      url.searchParams.set("mission", id);
    } else {
      window.localStorage.removeItem(MISSION_STORAGE_KEY);
      url.searchParams.delete("mission");
    }
    window.history.replaceState({}, "", `${url.pathname}${url.search}`);
  }, []);

  const refresh = useCallback(async () => {
    if (!missionId) return;
    setLoading(true);
    setError(null);
    try {
      const [m, w, b, a, g, sc, ev] = await Promise.all([
        getMission(missionId),
        getWorld(missionId),
        getBatonState(missionId),
        listAgents(missionId),
        getGraph(missionId),
        getSCMetric(missionId),
        getEvents(missionId, { limit: 200 }),
      ]);
      setMission(m);
      setWorld(w);
      setBaton(b);
      setAgents(a);
      setGraph(g);
      setScMetric(sc);
      setEvents(ev.events);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setMissionId(null);
        setError(`Mission ${missionId} was not found. The saved mission was cleared.`);
        return;
      }
      setError(err instanceof Error ? err.message : "Failed to load mission");
    } finally {
      setLoading(false);
    }
  }, [missionId, setMissionId]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const queryMission = params.get("mission");
    const storedMission = window.localStorage.getItem(MISSION_STORAGE_KEY);
    const nextMission = queryMission || storedMission;
    if (nextMission) {
      setMissionId(nextMission);
    }
  }, [setMissionId]);

  useEffect(() => {
    if (missionId) {
      refresh();
    } else {
      setMission(null);
      setWorld(null);
      setBaton(null);
      setAgents([]);
      setGraph(null);
      setScMetric(null);
      setEvents([]);
    }
  }, [missionId, refresh]);

  const handleEvent = useCallback(
    (event: EventEnvelope) => {
      setEvents((prev) => [...prev, event]);

      if (event.type.startsWith("baton.")) {
        getBatonState(event.mission_id).then(setBaton).catch(() => {});
      }
      if (event.type.startsWith("patch.")) {
        getWorld(event.mission_id).then(setWorld).catch(() => {});
        getGraph(event.mission_id).then(setGraph).catch(() => {});
        getSCMetric(event.mission_id).then(setScMetric).catch(() => {});
      }
      if (event.type === "agent.joined") {
        listAgents(event.mission_id).then(setAgents).catch(() => {});
      }
      if (event.type.startsWith("energy.")) {
        listAgents(event.mission_id).then(setAgents).catch(() => {});
      }
      if (event.type.startsWith("causal.")) {
        getGraph(event.mission_id).then(setGraph).catch(() => {});
      }
    },
    [],
  );

  const { status: wsStatus } = useWebSocket(missionId, handleEvent);

  const value = useMemo<MissionState>(
    () => ({
      missionId,
      mission,
      world,
      baton,
      agents,
      graph,
      scMetric,
      events,
      wsStatus,
      loading,
      error,
      setMissionId,
      refresh,
    }),
    [
      missionId,
      mission,
      world,
      baton,
      agents,
      graph,
      scMetric,
      events,
      wsStatus,
      loading,
      error,
      setMissionId,
      refresh,
    ],
  );

  return (
    <MissionContext.Provider value={value}>{children}</MissionContext.Provider>
  );
}

export function useMissionContext(): MissionState {
  const ctx = useContext(MissionContext);
  if (!ctx) throw new Error("useMissionContext must be used within MissionProvider");
  return ctx;
}
