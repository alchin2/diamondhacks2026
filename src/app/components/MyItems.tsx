import { Link } from "react-router";
import { useState, useEffect } from "react";

interface Item {
  id: string;
  name: string;
  condition: string;
  image_url: string | null;
  category: string;
}

export function MyItems() {
  // Use real user UUID
  const userId = "19497467-e10b-4124-a65b-68c3f6b26be7";
  const [myItems, setMyItems] = useState<Item[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    fetch(`/items/?user_id=${userId}`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch items");
        return res.json();
      })
      .then((data) => setMyItems(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [userId]);

  const conditionColors = {
    good: "bg-[#1D9E75] text-white",
    fair: "bg-[#EF9F27] text-white",
    poor: "bg-[#E24B4A] text-white",
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="max-w-[1100px] mx-auto px-8 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 style={{ fontSize: '32px', fontWeight: 600, color: '#1A1A1A' }}>
          My Items
        </h1>
        <Link
          to="/list"
          className="px-6 py-3 bg-[#534AB7] text-white rounded-lg hover:bg-[#453CA0] transition-colors"
        >
          List New Item
        </Link>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {myItems.map((item) => (
          <Link key={item.id} to={`/item/${item.id}`}>
            <div className="bg-white rounded-xl overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
              <div className="aspect-square overflow-hidden">
                <img
                  src={item.image_url || "https://via.placeholder.com/400"}
                  alt={item.name}
                  className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                />
              </div>
              <div className="p-4">
                <h3 className="mb-2" style={{ fontSize: '16px', fontWeight: 500, color: '#1A1A1A' }}>
                  {item.name}
                </h3>
                <span
                  className={`inline-block px-3 py-1 text-sm rounded-full ${
                    conditionColors[item.condition as keyof typeof conditionColors]
                  }`}
                  style={{ borderRadius: "20px" }}
                >
                  {item.condition}
                </span>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
