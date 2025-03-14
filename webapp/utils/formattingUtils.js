export const capitalize = s => s && String(s[0]).toUpperCase() + String(s).slice(1);

export const hideEmail = email => {
  if (!email) return '';
  const [localPart, domain] = email.split('@');
  return `${localPart.substring(0, 3)}***@${domain}`;
};
