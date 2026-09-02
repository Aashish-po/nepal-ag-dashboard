declare module '*.geojson' {
  import type { FeatureCollection } from 'geojson';
  const value: FeatureCollection;
  export default value;
}

// ponytail: .json imports are natively supported by Vite + TypeScript resolveJsonModule
declare module '*.json' {
  import type { FeatureCollection } from 'geojson';
  const value: FeatureCollection;
  export default value;
}
