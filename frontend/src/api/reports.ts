import { apiRequest } from "./client";
import type { TeamReport } from "./types";

export function getMyTeam() {
  return apiRequest<TeamReport>("/reports/team");
}
