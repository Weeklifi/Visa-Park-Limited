import { useState, type FormEvent } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { register } from "../api/auth";
import { ApiError } from "../api/client";
import ErrorBanner from "../components/ErrorBanner";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [nid, setNid] = useState("");
  const [referralCode, setReferralCode] = useState(searchParams.get("ref") ?? "");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setSubmitting(true);
    try {
      const isRootUser = !referralCode.trim();
      if (!isRootUser && (!phoneNumber.trim() || !nid.trim())) {
        setError("Phone number and NID are required when registering with a sponsor code");
        setSubmitting(false);
        return;
      }

      const result = await register({
        full_name: fullName,
        email,
        password,
        phone_number: phoneNumber.trim() || undefined,
        nid: nid.trim() || undefined,
        parent_referral_code: referralCode.trim() || undefined,
      });
      setSuccess(
        `Account created at Layer ${result.layer_level}. Your referral code is ${result.referral_code} — share it to invite others.`
      );
      setTimeout(() => navigate("/login"), 2500);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="auth-page">
      <h1>Register</h1>
      <p className="hint">
        The platform is invite-only. Enter the referral code from the person who invited you, or leave
        it blank if you are the very first (root) user.
      </p>
      <ErrorBanner message={error} />
      {success && <div className="success-banner">{success}</div>}
      <form onSubmit={handleSubmit} className="form">
        <label>
          Full name
          <input value={fullName} onChange={(e) => setFullName(e.target.value)} required minLength={2} />
        </label>
        <label>
          Email
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={8}
          />
        </label>
        <label>
          Phone Number
          <input
            type="tel"
            value={phoneNumber}
            onChange={(e) => setPhoneNumber(e.target.value)}
            placeholder="e.g., +1 (555) 123-4567"
          />
        </label>
        <label>
          NID (National ID)
          <input
            type="text"
            value={nid}
            onChange={(e) => setNid(e.target.value)}
            placeholder="e.g., 123456789"
          />
        </label>
        <label>
          Sponsor (Referral code - optional for root)
          <input value={referralCode} onChange={(e) => setReferralCode(e.target.value)} />
        </label>
        <button type="submit" disabled={submitting}>
          {submitting ? "Registering…" : "Register"}
        </button>
      </form>
      <p>
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </div>
  );
}
