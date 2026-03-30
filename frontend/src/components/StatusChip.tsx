export const StatusChip = ({ status }: { status: string }) => {
  const normalized = status.toLowerCase();
  return <span className={`status-chip ${normalized}`}>{status}</span>;
};
