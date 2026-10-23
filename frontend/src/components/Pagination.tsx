"use client";

interface Props {
  currentPage: number;
  totalPages: number;
  onChange: (page: number) => void;
}

export function Pagination({ currentPage, totalPages, onChange }: Props) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-center gap-2 py-4">
      <button
        onClick={() => onChange(Math.max(1, currentPage - 1))}
        disabled={currentPage === 1}
        className="px-3 py-2 rounded border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
      >
        Anterior
      </button>
      {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
        <button
          key={page}
          onClick={() => onChange(page)}
          className={`px-3 py-2 rounded border ${
            page === currentPage
              ? "bg-blue-500 text-white border-blue-500"
              : "border-gray-300 hover:bg-gray-50"
          }`}
        >
          {page}
        </button>
      ))}
      <button
        onClick={() => onChange(Math.min(totalPages, currentPage + 1))}
        disabled={currentPage === totalPages}
        className="px-3 py-2 rounded border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
      >
        Siguiente
      </button>
    </div>
  );
}
