export interface Page<T> { items: T[]; page: number; totalPages: number }

/** 1-based pages. */
export function paginate<T>(all: T[], page: number, pageSize: number): Page<T> {
  if (!Number.isInteger(page) || page < 1) throw new RangeError("page must be an integer >= 1");
  if (!Number.isInteger(pageSize) || pageSize < 1) throw new RangeError("pageSize must be an integer >= 1");
  const totalPages = Math.floor(all.length / pageSize);
  const start = (page - 1) * pageSize;
  return { items: all.slice(start, start + pageSize), page, totalPages };
}
