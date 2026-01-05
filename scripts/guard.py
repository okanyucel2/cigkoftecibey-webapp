#!/usr/bin/env python3
"""
Session Guard - Ensures system is working before declaring "Done"

Usage:
    python guard.py verify    # Quick health + login check
    python guard.py smoke     # Full smoke test (Login + Dashboard + Create)
    python guard.py full      # verify + smoke + checkpoint
    python guard.py checkpoint # Save current state
"""

import subprocess
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CHECKPOINT_FILE = PROJECT_ROOT / ".guard_checkpoint.json"


class SessionGuard:
    def __init__(self, project: str = "cigkoftecibey-webapp"):
        self.project = project
        self.backend_url = "http://localhost:9049"
        self.frontend_url = "http://localhost:19049"
        self.results = {"checks": [], "passed": 0, "failed": 0}

    def log(self, status: str, message: str):
        icon = "✅" if status == "pass" else "❌" if status == "fail" else "⚠️"
        print(f"{icon} {message}")
        self.results["checks"].append({"status": status, "message": message})
        if status == "pass":
            self.results["passed"] += 1
        elif status == "fail":
            self.results["failed"] += 1

    # ===== VERIFY ENVIRONMENT =====
    def check_docker(self) -> bool:
        """Check if Docker daemon is running"""
        try:
            result = subprocess.run(["docker", "info"], capture_output=True, timeout=5)
            if result.returncode == 0:
                self.log("pass", "Docker daemon running")
                return True
            else:
                self.log("fail", "Docker daemon not running")
                return False
        except Exception as e:
            self.log("fail", f"Docker check failed: {e}")
            return False

    def check_database(self) -> bool:
        """Check if database container is running and healthy"""
        try:
            result = subprocess.run(
                ["docker", "exec", "cigkofte-db", "pg_isready", "-U", "postgres"],
                capture_output=True,
                timeout=10,
            )
            if result.returncode == 0:
                self.log("pass", "Database container healthy")
                return True
            else:
                self.log("fail", "Database not ready")
                return False
        except Exception as e:
            self.log("fail", f"Database check failed: {e}")
            return False

    def check_backend(self) -> bool:
        """Check backend health endpoint"""
        try:
            resp = requests.get(f"{self.backend_url}/api/health", timeout=5)
            data = resp.json()
            if data.get("status") == "healthy":
                self.log("pass", f"Backend healthy (DB: {data.get('database', 'unknown')})")
                return True
            else:
                self.log("fail", f"Backend unhealthy: {data}")
                return False
        except Exception as e:
            self.log("fail", f"Backend check failed: {e}")
            return False

    def check_frontend(self) -> bool:
        """Check if frontend is serving"""
        try:
            resp = requests.get(self.frontend_url, timeout=5)
            if "<!DOCTYPE html>" in resp.text:
                self.log("pass", "Frontend serving HTML")
                return True
            else:
                self.log("fail", "Frontend not serving HTML")
                return False
        except Exception as e:
            self.log("fail", f"Frontend check failed: {e}")
            return False

    def check_login(self) -> str | None:
        """Test login capability, return token if successful"""
        try:
            resp = requests.post(
                f"{self.backend_url}/api/auth/login-json",
                json={"email": "admin@cigkofte.com", "password": "admin123"},
                timeout=10,
            )
            data = resp.json()
            token = data.get("access_token")
            if token and len(token) > 20:
                self.log("pass", f"Login successful (token: {len(token)} chars)")
                return token
            else:
                self.log("fail", f"Login failed: {data}")
                return None
        except Exception as e:
            self.log("fail", f"Login check failed: {e}")
            return None

    # ===== SMOKE TEST (Playwright) =====
    def run_smoke_test(self) -> bool:
        """Run critical path smoke test with Playwright"""
        try:
            result = subprocess.run(
                [
                    "npx",
                    "playwright",
                    "test",
                    "tests/e2e/smoke/critical-path.spec.ts",
                    "--reporter=list",
                    "--timeout=30000",
                ],
                cwd=PROJECT_ROOT / "frontend",
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                self.log("pass", "Smoke test passed (Login + Dashboard + Create)")
                return True
            else:
                self.log("fail", f"Smoke test failed:\n{result.stdout}\n{result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.log("fail", "Smoke test timed out (>60s)")
            return False
        except Exception as e:
            self.log("fail", f"Smoke test error: {e}")
            return False

    # ===== CHECKPOINT =====
    def get_git_hash(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except Exception:
            return "unknown"

    def save_checkpoint(self):
        """Save checkpoint with current state"""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "git_hash": self.get_git_hash(),
            "services": {
                "docker": self.check_docker(),
                "database": self.check_database(),
                "backend": self.check_backend(),
                "frontend": self.check_frontend(),
            },
            "login_capable": self.check_login() is not None,
            "results": self.results,
        }

        CHECKPOINT_FILE.write_text(json.dumps(checkpoint, indent=2))
        self.log("pass", f"Checkpoint saved: {CHECKPOINT_FILE}")
        return checkpoint

    # ===== FAILURE ANALYSIS =====
    def suggest_solutions(self) -> list[str]:
        """Analyze failures and suggest solutions"""
        suggestions = []

        for check in self.results["checks"]:
            if check["status"] == "fail":
                msg = check["message"].lower()

                if "docker" in msg:
                    suggestions.append("Try: open -a Docker && sleep 10")
                elif "database" in msg:
                    suggestions.append("Try: docker start cigkofte-db && sleep 5")
                elif "backend" in msg:
                    suggestions.append(
                        "Try: cd backend && PYTHONPATH=. uvicorn app.main:app --port 9049 &"
                    )
                elif "frontend" in msg:
                    suggestions.append("Try: cd frontend && npm run dev -- --port 19049 &")
                elif "login" in msg:
                    suggestions.append("Check: Database connection, user exists, password correct")

        return suggestions[:3]  # Max 3 suggestions

    # ===== MAIN COMMANDS =====
    def verify(self) -> bool:
        """Quick verification: Docker + DB + Backend + Frontend + Login"""
        print("\n🔍 Session Guard: VERIFY")
        print("=" * 40)

        # Sequential checks with fail-fast
        checks = [
            ("Docker", self.check_docker),
            ("Database", self.check_database),
            ("Backend", self.check_backend),
            ("Frontend", self.check_frontend),
            ("Login", lambda: self.check_login() is not None),
        ]

        for name, check in checks:
            if not check():
                print(f"\n❌ Verification FAILED at: {name}")
                print("\n💡 Suggested fixes:")
                for suggestion in self.suggest_solutions():
                    print(f"   {suggestion}")
                return False

        print("\n✅ All verifications PASSED")
        return True

    def smoke(self) -> bool:
        """Full smoke test: verify + Playwright critical path"""
        print("\n🧪 Session Guard: SMOKE TEST")
        print("=" * 40)

        if not self.verify():
            return False

        print("\n🎭 Running Playwright smoke test...")
        return self.run_smoke_test()

    def full(self) -> bool:
        """Full guard: verify + smoke + checkpoint"""
        print("\n🛡️ Session Guard: FULL CHECK")
        print("=" * 40)

        if not self.smoke():
            return False

        print("\n📸 Saving checkpoint...")
        self.save_checkpoint()

        print("\n" + "=" * 40)
        print(
            f"✅ SESSION GUARD PASSED: {self.results['passed']}/{self.results['passed'] + self.results['failed']} checks"
        )
        print("=" * 40)
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python guard.py <verify|smoke|full|checkpoint>")
        sys.exit(1)

    command = sys.argv[1]
    guard = SessionGuard()

    if command == "verify":
        success = guard.verify()
    elif command == "smoke":
        success = guard.smoke()
    elif command == "full":
        success = guard.full()
    elif command == "checkpoint":
        guard.save_checkpoint()
        success = True
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
