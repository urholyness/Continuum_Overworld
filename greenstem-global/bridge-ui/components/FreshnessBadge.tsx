export default function FreshnessBadge({ ts }: { ts?: string | null }) {
  if (!ts) {
    return (
      <span className="px-3 py-1 rounded-full bg-gray-200 text-gray-600 text-sm">
        No data
      </span>
    );
  }

  const now = Date.now();
  const timestamp = new Date(ts).getTime();
  const diffMinutes = Math.floor((now - timestamp) / 60000);
  
  let bgColor = 'bg-green-100 text-green-800';
  let text = `${diffMinutes} min ago`;
  
  if (diffMinutes < 60) {
    bgColor = 'bg-green-100 text-green-800';
    text = `${diffMinutes} min ago`;
  } else if (diffMinutes < 1440) { // Less than 24 hours
    const hours = Math.floor(diffMinutes / 60);
    bgColor = 'bg-yellow-100 text-yellow-800';
    text = `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
  } else {
    const days = Math.floor(diffMinutes / 1440);
    bgColor = 'bg-red-100 text-red-800';
    text = `${days} ${days === 1 ? 'day' : 'days'} ago`;
  }

  return (
    <span className={`px-3 py-1 rounded-full text-sm ${bgColor}`}>
      Updated {text}
    </span>
  );
}