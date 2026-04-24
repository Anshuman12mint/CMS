export const formatDate = (date) => {
  if (!date) return "";

  const d = new Date(date);
  return d.toLocaleDateString();
};