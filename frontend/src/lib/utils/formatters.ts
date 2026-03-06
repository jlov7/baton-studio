export function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

export function formatEnergy(amount: number, total: number): string {
  return `${amount}/${total}`;
}

export function shortId(id: string): string {
  if (id.length <= 12) return id;
  return id.slice(0, 12) + "…";
}

export function agentName(actorId: string): string {
  const parts = actorId.split(":");
  return parts.length > 1 ? parts[1] : actorId;
}

export function eventLabel(type: string): string {
  return type.replace(/\./g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
