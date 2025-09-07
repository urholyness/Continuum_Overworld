export function normalizeCompany(name: string): string {
  return name.normalize("NFKC");
}