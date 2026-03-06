import { post } from "./client";
import type {
  CommitPatchRequest,
  CommitPatchResponse,
  ProposePatchRequest,
  ProposePatchResponse,
} from "./types";

export function proposePatch(missionId: string, req: ProposePatchRequest) {
  return post<ProposePatchResponse>(
    `/missions/${missionId}/patches/propose`,
    req,
  );
}

export function commitPatch(missionId: string, req: CommitPatchRequest) {
  return post<CommitPatchResponse>(
    `/missions/${missionId}/patches/commit`,
    req,
  );
}
