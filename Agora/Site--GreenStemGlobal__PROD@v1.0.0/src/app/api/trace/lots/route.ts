import sample from "@/../mocks/lots_sample.json";

export async function GET() {
  return Response.json(sample);
}