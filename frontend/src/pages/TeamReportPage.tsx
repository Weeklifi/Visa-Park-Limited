import { useEffect, useState } from "react";
import { getMyTeam } from "../api/reports";
import { ApiError } from "../api/client";
import ErrorBanner from "../components/ErrorBanner";
import type { TeamReport } from "../api/types";

export default function TeamReportPage() {
  const [report, setReport] = useState<TeamReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadTeamReport() {
      try {
        const data = await getMyTeam();
        setReport(data);
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Failed to load team report");
      } finally {
        setLoading(false);
      }
    }
    loadTeamReport();
  }, []);

  if (loading) return <div className="team-report"><p>Loading team data...</p></div>;

  return (
    <div className="team-report">
      <h1>My Team Report</h1>
      <ErrorBanner message={error} />

      {report && (
        <>
          <div className="report-summary">
            <p>
              <strong>Total Team Size:</strong> {report.total_team_size} people
            </p>
            <p>
              <strong>Direct Reports:</strong> {report.direct_reports.length}
            </p>
            <p>
              <strong>Extended Network:</strong> {report.network.length}
            </p>
          </div>

          <section className="direct-team-section">
            <h2>Your Direct Team (Full Details)</h2>
            {report.direct_reports.length === 0 ? (
              <p className="empty-state">No direct team members yet.</p>
            ) : (
              <table className="team-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Phone</th>
                    <th>NID</th>
                    <th>Email</th>
                    <th>Referral Code</th>
                    <th>Layer</th>
                    <th>Direct Reports</th>
                    <th>Status</th>
                    <th>Joined</th>
                  </tr>
                </thead>
                <tbody>
                  {report.direct_reports.map((member) => (
                    <tr key={member.id}>
                      <td>{member.full_name}</td>
                      <td>{member.phone_number || "—"}</td>
                      <td>{member.nid || "—"}</td>
                      <td>{member.email}</td>
                      <td>
                        <code className="referral-code">{member.referral_code}</code>
                      </td>
                      <td>Layer {member.layer_level}</td>
                      <td>{member.child_count}</td>
                      <td>{member.is_active ? "Active" : "Inactive"}</td>
                      <td>{new Date(member.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>

          <section className="network-section">
            <h2>Your Extended Network (Name & Phone Only)</h2>
            <p className="info-note">
              For team members beyond your direct reports, only name and phone number are visible for privacy.
            </p>
            {report.network.length === 0 ? (
              <p className="empty-state">No extended network members yet.</p>
            ) : (
              <table className="network-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Phone</th>
                    <th>Layer</th>
                  </tr>
                </thead>
                <tbody>
                  {report.network.map((member) => (
                    <tr key={member.id}>
                      <td>{member.full_name}</td>
                      <td>{member.phone_number || "—"}</td>
                      <td>Layer {member.layer_level}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </>
      )}
    </div>
  );
}
