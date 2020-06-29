export function isInLark(): boolean {
  const ua = navigator.userAgent;
  return /Lark/.test(ua);
}
