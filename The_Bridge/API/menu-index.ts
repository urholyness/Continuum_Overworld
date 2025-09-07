/**
 * Auto-Menu API - Generates navigation from THE_BRIDGE naming grammar
 * Scans repository for artifacts matching Division/Capability--Role__Qualifier@vX.Y.Z
 */

import * as fs from 'fs';
import * as path from 'path';

// Division icons (LCARS-style, can be swapped for Star Trek sprites)
const DIVISION_ICONS: Record<string, string> = {
  The_Bridge: '🌉',  // Command
  Meridian: '⏱',     // Time/Schedule
  Forge: '🔥',        // Build/Create
  Aegis: '🛡',        // Shield/Security
  Oracle: '📊',       // Data/Prediction (01∕10 alternative)
  Atlas: '🗺',        // Maps/Planning
  Agora: '✉',        // Communication
  Ledger: '₡',        // Records/Contracts
  Archive: '🗃',      // Storage
  Pantheon: '⚡'      // Agents
};

// Dark + Green theme tokens
export const THEME = {
  bg: '#0b0f0c',        // Dark background
  panel: '#0f1512',     // Panel surface
  stroke: '#124c2f',    // Border stroke
  accent: '#22c55e',    // Neo-green accent
  warn: '#f59e0b',      // Amber warning
  text: '#e6f7ee',      // Light text
  textDim: '#7fa67a'    // Dimmed text
};

export interface MenuNode {
  name: string;
  path?: string;
  icon?: string;
  theme?: typeof THEME;
  children?: Record<string, MenuNode>;
  metadata?: {
    division?: string;
    capability?: string;
    role?: string;
    qualifier?: string;
    version?: string;
    fullPath?: string;
  };
}

export interface ArtifactIndex {
  artifacts: Array<{
    path: string;
    exists: boolean;
    type: 'directory' | 'file';
  }>;
  generated: string;
  theme: typeof THEME;
}

/**
 * Scan filesystem for artifacts matching THE_BRIDGE naming grammar
 */
export async function scanArtifacts(rootPath: string = '.'): Promise<ArtifactIndex> {
  const artifacts: ArtifactIndex['artifacts'] = [];
  const worldRoot = path.join(rootPath, 'Continuum_Overworld');
  
  // Valid divisions
  const divisions = [
    'The_Bridge', 'Pantheon', 'Aegis', 'Atlas', 
    'Forge', 'Oracle', 'Meridian', 'Agora', 
    'Ledger', 'Archive'
  ];
  
  // Scan each division
  for (const division of divisions) {
    const divPath = path.join(worldRoot, division);
    
    if (!fs.existsSync(divPath)) continue;
    
    // Look for versioned artifacts (containing @v)
    const scanDir = (dir: string, depth: number = 0) => {
      if (depth > 3) return; // Limit recursion depth
      
      const items = fs.readdirSync(dir);
      
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        const relativePath = path.relative(rootPath, fullPath).replace(/\\/g, '/');
        
        // Check if item matches versioned pattern
        if (item.includes('@v') || item.includes('--')) {
          artifacts.push({
            path: relativePath,
            exists: true,
            type: stat.isDirectory() ? 'directory' : 'file'
          });
        }
        
        // Recurse into directories
        if (stat.isDirectory() && !item.startsWith('.')) {
          scanDir(fullPath, depth + 1);
        }
      }
    };
    
    scanDir(divPath);
  }
  
  return {
    artifacts,
    generated: new Date().toISOString(),
    theme: THEME
  };
}

/**
 * Parse artifact path into components
 */
export function parseArtifactPath(artifactPath: string): MenuNode['metadata'] {
  // Pattern: Continuum_Overworld/<Division>/<Capability>--<Role>__<Qualifier>@v<version>
  const parts = artifactPath.split('/');
  
  if (parts.length < 3) return {};
  
  const [world, division, ...rest] = parts;
  const artifact = rest.join('/');
  
  // Parse the artifact name
  const [nameAndVersion] = artifact.split('/');
  if (!nameAndVersion) return { division };
  
  const [capabilityRole, versionPart] = nameAndVersion.split('@');
  if (!capabilityRole) return { division };
  
  const [capability, roleQualifier] = capabilityRole.split('--');
  if (!roleQualifier) {
    return { division, capability };
  }
  
  const [role, qualifier] = roleQualifier.split('__');
  const version = versionPart ? versionPart.replace('v', '') : undefined;
  
  return {
    division,
    capability,
    role,
    qualifier,
    version,
    fullPath: artifactPath
  };
}

/**
 * Build hierarchical menu tree from artifact paths
 */
export function buildMenuTree(paths: string[]): MenuNode {
  const root: MenuNode = {
    name: 'Continuum_Overworld',
    theme: THEME,
    children: {}
  };
  
  for (const artifactPath of paths) {
    const metadata = parseArtifactPath(artifactPath);
    
    if (!metadata.division) continue;
    
    // Create or get division node
    if (!root.children![metadata.division]) {
      root.children![metadata.division] = {
        name: metadata.division,
        icon: DIVISION_ICONS[metadata.division] || '•',
        children: {},
        metadata: { division: metadata.division }
      };
    }
    const divNode = root.children![metadata.division];
    
    // Create capability node if present
    if (metadata.capability) {
      if (!divNode.children![metadata.capability]) {
        divNode.children![metadata.capability] = {
          name: metadata.capability,
          children: {},
          metadata: { ...metadata, role: undefined, qualifier: undefined, version: undefined }
        };
      }
      const capNode = divNode.children![metadata.capability];
      
      // Create role node if present
      if (metadata.role) {
        if (!capNode.children![metadata.role]) {
          capNode.children![metadata.role] = {
            name: metadata.role,
            children: {},
            metadata: { ...metadata, qualifier: undefined, version: undefined }
          };
        }
        const roleNode = capNode.children![metadata.role];
        
        // Create qualifier node if present
        if (metadata.qualifier) {
          if (!roleNode.children![metadata.qualifier]) {
            roleNode.children![metadata.qualifier] = {
              name: metadata.qualifier,
              children: {},
              metadata: { ...metadata, version: undefined }
            };
          }
          const qualNode = roleNode.children![metadata.qualifier];
          
          // Add version as leaf
          if (metadata.version) {
            qualNode.children![`v${metadata.version}`] = {
              name: `v${metadata.version}`,
              path: artifactPath,
              metadata
            };
          }
        }
      }
    }
  }
  
  return root;
}

/**
 * Express/Node API endpoint handler
 */
export async function menuApiHandler(req: any, res: any) {
  try {
    // Get root path from environment or use current directory
    const rootPath = process.env.CONTINUUM_ROOT || '.';
    
    // Check cache
    const cacheFile = path.join(rootPath, '.bridge', 'menu-cache.json');
    const cacheMaxAge = 60 * 1000; // 1 minute cache
    
    if (fs.existsSync(cacheFile)) {
      const stat = fs.statSync(cacheFile);
      const age = Date.now() - stat.mtime.getTime();
      
      if (age < cacheMaxAge) {
        const cached = JSON.parse(fs.readFileSync(cacheFile, 'utf-8'));
        return res.json(cached);
      }
    }
    
    // Scan artifacts
    const index = await scanArtifacts(rootPath);
    
    // Build menu tree
    const menu = buildMenuTree(index.artifacts.map(a => a.path));
    
    // Prepare response
    const response = {
      menu,
      index,
      generated: new Date().toISOString(),
      cache_ttl: cacheMaxAge
    };
    
    // Cache result
    fs.mkdirSync(path.dirname(cacheFile), { recursive: true });
    fs.writeFileSync(cacheFile, JSON.stringify(response, null, 2));
    
    res.json(response);
  } catch (error) {
    res.status(500).json({
      error: 'Failed to generate menu',
      message: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}

/**
 * Invalidate menu cache (call on git changes)
 */
export function invalidateCache(rootPath: string = '.') {
  const cacheFile = path.join(rootPath, '.bridge', 'menu-cache.json');
  if (fs.existsSync(cacheFile)) {
    fs.unlinkSync(cacheFile);
  }
}

/**
 * CLI testing
 */
if (require.main === module) {
  (async () => {
    console.log('Scanning Continuum_Overworld artifacts...');
    const index = await scanArtifacts();
    console.log(`Found ${index.artifacts.length} artifacts`);
    
    const menu = buildMenuTree(index.artifacts.map(a => a.path));
    console.log('\nMenu Structure:');
    console.log(JSON.stringify(menu, null, 2));
    
    // Save to file for inspection
    fs.writeFileSync(
      'menu-output.json',
      JSON.stringify({ menu, index }, null, 2)
    );
    console.log('\nOutput saved to menu-output.json');
  })();
}