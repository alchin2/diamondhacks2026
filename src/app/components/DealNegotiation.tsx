import { useState, useEffect } from "react";
import { useParams, Link } from "react-router";
import { ArrowLeft } from "lucide-react";

export function DealNegotiation() {
  const { id } = useParams();
  const [deal, setDeal] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    fetch(`/deals/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch deal");
        return res.json();
      })
      .then((data) => setDeal(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!deal) return <div>No deal found.</div>;

  return (
    <div className="max-w-[1100px] mx-auto px-8 py-8">
      {/* Back Button */}
      <Link
        to="/profile"
        className="inline-flex items-center gap-2 text-[#6B6B6B] hover:text-[#1A1A1A] mb-6 transition-colors"
      >
        <ArrowLeft className="w-5 h-5" />
        Back to Profile
      </Link>

      <h1 className="mb-8" style={{ fontSize: '32px', fontWeight: 600, color: '#1A1A1A' }}>
        Trade Negotiation
      </h1>

      {/* Deal Summary */}
      <div className="bg-white rounded-xl p-6">
        <div className="mb-4">
          <span className="text-sm text-[#6B6B6B]">Deal ID:</span>
          <span className="block text-[#1A1A1A] font-medium">{deal.id}</span>
        </div>

        <div className="mb-4">
          <span className="text-sm text-[#6B6B6B]">Status:</span>
          <span className="block text-[#1A1A1A] font-medium">
            {deal.status.charAt(0).toUpperCase() + deal.status.slice(1)}
          </span>
        </div>

        <div className="mb-4">
          <span className="text-sm text-[#6B6B6B]">Cash Difference:</span>
          <span className="block text-[#1A1A1A] font-medium">
            ${deal.cash_difference.toFixed(2)}
          </span>
        </div>

        <div className="mb-4">
          <span className="text-sm text-[#6B6B6B]">Payer ID:</span>
          <span className="block text-[#1A1A1A] font-medium">{deal.payer_id}</span>
        </div>

        <div>
          <span className="text-sm text-[#6B6B6B]">Created:</span>
          <span className="block text-[#1A1A1A] font-medium">
            {new Date(deal.created_at).toLocaleString()}
          </span>
        </div>
      </div>
    </div>
  );
}
