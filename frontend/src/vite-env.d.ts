/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  // add more env variables here later if you need them
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}