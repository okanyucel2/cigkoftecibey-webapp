import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { execSync } from 'child_process'

// Git bilgilerini al (Render env vars veya git komutlarından)
function getGitInfo() {
  // Render otomatik olarak RENDER_GIT_COMMIT sağlar
  const envCommit = process.env.RENDER_GIT_COMMIT || process.env.VITE_GIT_COMMIT
  const envBranch = process.env.RENDER_GIT_BRANCH || process.env.VITE_GIT_BRANCH

  if (envCommit && envCommit !== 'unknown') {
    return {
      commitHash: envCommit.substring(0, 7),
      commitDate: new Date().toISOString().split('T')[0], // Build tarihi
      branch: envBranch || 'main'
    }
  }

  // Fallback: git komutları (local development)
  try {
    const commitHash = execSync('git rev-parse --short HEAD').toString().trim()
    const commitDate = execSync('git log -1 --format=%cd --date=short').toString().trim()
    const branch = execSync('git rev-parse --abbrev-ref HEAD').toString().trim()
    return { commitHash, commitDate, branch }
  } catch {
    return { commitHash: 'unknown', commitDate: 'unknown', branch: 'unknown' }
  }
}

const gitInfo = getGitInfo()
const buildDate = new Date().toISOString().split('T')[0]

export default defineConfig({
  plugins: [vue()],
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
    __GIT_COMMIT__: JSON.stringify(gitInfo.commitHash),
    __GIT_DATE__: JSON.stringify(gitInfo.commitDate),
    __GIT_BRANCH__: JSON.stringify(gitInfo.branch),
    __BUILD_DATE__: JSON.stringify(buildDate),
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://localhost:3010',
        changeOrigin: true
      }
    }
  }
})
