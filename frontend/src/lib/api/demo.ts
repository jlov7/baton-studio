import { post } from "./client";

export function startDemo() {
  return post<{ mission_id: string; status: string }>("/demo/start");
}
