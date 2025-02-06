import { resolve } from 'path';
import { mergeConfig, defineConfig, loadEnv } from 'vite';
import { crx, ManifestV3Export } from '@crxjs/vite-plugin';
import baseConfig, { baseManifest, baseBuildOptions } from './vite.config.base'

const outDir = resolve(__dirname, 'dist_chrome');

export default defineConfig(({ mode }) => {
  // Load app-level env vars to node-level env vars.
  process.env = {...process.env, ...loadEnv(mode, process.cwd())};

  return mergeConfig(
    baseConfig,
    {
      plugins: [
        crx({
          manifest: {
            ...baseManifest,
            background: {
              service_worker: 'src/pages/background/index.ts',
              type: 'module'
            },
            oauth2: {
              client_id: process.env.VITE_GOOGLE_CLIENT_ID,
              scopes: [
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/documents.readonly"
              ]
            }, 
          } as ManifestV3Export,
          browser: 'chrome',
          contentScripts: {
            injectCss: true,
          }
        })
      ],
      build: {
        ...baseBuildOptions,
        outDir
      },
    }
  );
});