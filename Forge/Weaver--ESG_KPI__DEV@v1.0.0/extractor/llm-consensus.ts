// Real LLM adapters with multi-provider consensus
import fetch from "node-fetch";

export type LLM = (args: { system: string; user: string }) => Promise<string>;

// OpenAI GPT-4 adapter
export const callOpenAI: LLM = async ({ system, user }) => {
  const apiKey = process.env.AEGIS_OPENAI_API_KEY;
  if (!apiKey) throw new Error("AEGIS_OPENAI_API_KEY missing - required for real extraction");

  const response = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      response_format: { type: "json_object" },
      messages: [
        { role: "system", content: system },
        { role: "user", content: user }
      ],
      temperature: 0.1,
      max_tokens: 4000
    })
  });

  if (!response.ok) {
    throw new Error(`OpenAI API error: ${response.status} ${response.statusText}`);
  }

  const data = await response.json() as any;
  return data.choices[0].message.content ?? "{}";
};

// Claude adapter
export const callClaude: LLM = async ({ system, user }) => {
  const apiKey = process.env.AEGIS_CLAUDE_API_KEY;
  if (!apiKey) throw new Error("AEGIS_CLAUDE_API_KEY missing - required for real extraction");

  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST", 
    headers: {
      "x-api-key": apiKey,
      "Content-Type": "application/json",
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model: "claude-3-haiku-20240307",
      max_tokens: 4000,
      temperature: 0.1,
      system: system,
      messages: [{ role: "user", content: user }]
    })
  });

  if (!response.ok) {
    throw new Error(`Claude API error: ${response.status} ${response.statusText}`);
  }

  const data = await response.json() as any;
  return data.content[0].text ?? "{}";
};

// Gemini adapter  
export const callGemini: LLM = async ({ system, user }) => {
  const apiKey = process.env.AEGIS_GEMINI_API_KEY;
  if (!apiKey) throw new Error("AEGIS_GEMINI_API_KEY missing - required for real extraction");

  const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{
        parts: [{ text: `${system}\n\n${user}` }]
      }],
      generationConfig: {
        temperature: 0.1,
        maxOutputTokens: 4000,
        responseMimeType: "application/json"
      }
    })
  });

  if (!response.ok) {
    throw new Error(`Gemini API error: ${response.status} ${response.statusText}`);
  }

  const data = await response.json() as any;
  return data.candidates[0].content.parts[0].text ?? "{}";
};

// Consensus adapter - fan out to multiple models and merge results
export const callConsensus: LLM = async ({ system, user }) => {
  const providers = [];
  
  // Add available providers based on env vars
  if (process.env.AEGIS_OPENAI_API_KEY) providers.push({ name: "openai", fn: callOpenAI });
  if (process.env.AEGIS_CLAUDE_API_KEY) providers.push({ name: "claude", fn: callClaude });
  if (process.env.AEGIS_GEMINI_API_KEY) providers.push({ name: "gemini", fn: callGemini });

  if (providers.length === 0) {
    throw new Error("No LLM API keys found - need at least one of: AEGIS_OPENAI_API_KEY, AEGIS_CLAUDE_API_KEY, AEGIS_GEMINI_API_KEY");
  }

  console.log(`[consensus] Using ${providers.length} providers: ${providers.map(p => p.name).join(", ")}`);

  // Call all providers in parallel
  const results = await Promise.allSettled(
    providers.map(async (provider) => {
      try {
        const response = await provider.fn({ system, user });
        const parsed = JSON.parse(response);
        return { provider: provider.name, data: parsed, success: true };
      } catch (error) {
        console.warn(`[consensus] ${provider.name} failed:`, error);
        return { provider: provider.name, error: String(error), success: false };
      }
    })
  );

  // Extract successful results
  const successful = results
    .filter((r): r is PromiseFulfilledResult<any> => r.status === "fulfilled" && r.value.success)
    .map(r => r.value);

  if (successful.length === 0) {
    throw new Error("All LLM providers failed - no consensus possible");
  }

  // Simple consensus: merge all KPIs and contexts from successful providers
  const allKpis: any[] = [];
  const allContexts: any[] = [];

  for (const result of successful) {
    if (result.data.kpis) allKpis.push(...result.data.kpis);
    if (result.data.contexts) allContexts.push(...result.data.contexts);
  }

  // Basic deduplication by kpi_id and value
  const uniqueKpis = Array.from(
    new Map(allKpis.map(k => [`${k.kpi_id}-${k.value}-${k.unit}`, k])).values()
  );

  // Return consensus result
  const consensus = {
    kpis: uniqueKpis,
    contexts: allContexts,
    consensus_meta: {
      providers_used: successful.map(r => r.provider),
      total_providers: providers.length,
      success_rate: successful.length / providers.length
    }
  };

  return JSON.stringify(consensus);
};