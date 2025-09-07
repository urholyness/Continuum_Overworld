import yaml from 'js-yaml';
import fs from 'node:fs/promises';

export async function ingestUasinGishuWeather() {
  // Read providers.yaml
  const config = yaml.load(await fs.readFile('config/providers.yaml', 'utf8')) as any;
  
  if (config.apis?.openweather === true) {
    const apiKey = process.env.AEGIS_OPENWEATHER_KEY;
    if (!apiKey) {
      throw new Error("AEGIS_OPENWEATHER_KEY missing - secret required for real data mode");
    }
    // TODO: Real OpenWeather API call when implemented
    return { mode: 'real', data: [], source: 'openweather_api', location: 'Uasin Gishu, Kenya' };
  } else {
    // Fallback to simulation data
    const simData = await fs.readFile('/Simulations/Farm-Level/uasin_gishu_weather.csv', 'utf8');
    return { mode: 'sim', data: simData.split('\n'), source: 'simulation' };
  }
}