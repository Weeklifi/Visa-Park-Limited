import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function DashboardPage() {
  const { user } = useAuth();
  const [copied, setCopied] = useState(false);

  if (!user) return null;

  const inviteLink = `${window.location.origin}/register?ref=${user.referral_code}`;

  function copyInviteLink() {
    navigator.clipboard.writeText(inviteLink).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  return (
    <div className="page">
      <h1>My Dashboard</h1>
      <div className="card">
        <h2>Profile</h2>
        <dl className="profile-grid">
          <dt>Name</dt>
          <dd>{user.full_name}</dd>
          <dt>Email</dt>
          <dd>{user.email}</dd>
          <dt>Layer</dt>
          <dd>{user.layer_level} of 4</dd>
          <dt>Node path</dt>
          <dd>
            <code>{user.node_path}</code>
          </dd>
          <dt>Direct children</dt>
          <dd>{user.child_count} / 10</dd>
          <dt>Status</dt>
          <dd>{user.is_active ? "Active" : "Inactive"}</dd>
        </dl>
      </div>

      <div className="card">
        <h2>Invite others</h2>
        <p>
          Your referral code: <code>{user.referral_code}</code>
        </p>
        {user.child_count >= 10 || user.layer_level >= 4 ? (
          <p className="hint">
            {user.layer_level >= 4
              ? "You are a Layer 4 leaf node and cannot invite further."
              : "You have used all 10 of your direct-invite slots."}
          </p>
        ) : (
          <>
            <p>
              Share this link — new users register directly under you (Layer {user.layer_level + 1}).
            </p>
            <div className="invite-link-row">
              <input readOnly value={inviteLink} />
              <button onClick={copyInviteLink}>{copied ? "Copied!" : "Copy"}</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
