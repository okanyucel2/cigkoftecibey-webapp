import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { execSync } from 'child_process'

// Git bilgilerini al
function getGitInfo() {
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
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
