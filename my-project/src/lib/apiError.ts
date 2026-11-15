// FastAPI errors carry `detail` as a string, or (for 422 validation errors)
// a list of {msg, loc, ...} objects. Turn either into one readable message.
export async function apiErrorMessage(res: Response, fallback: string): Promise<string> {
  const body = await res.json().catch(() => ({}));
  const detail = body?.detail;
  if (typeof detail === 'string' && detail) return detail;
  if (Array.isArray(detail) && detail.length) {
    return detail
      .map((d: { msg?: string; loc?: unknown[] }) => {
        const field = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : undefined;
        const msg = (d.msg ?? 'Invalid input').replace(/^Value error, /, '');
        return typeof field === 'string' && field !== 'body' ? `${field}: ${msg}` : msg;
      })
      .join(' ');
  }
  return fallback;
}
