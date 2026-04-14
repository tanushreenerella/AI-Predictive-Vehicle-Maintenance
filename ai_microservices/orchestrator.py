"""
ai_microservices/orchestrator.py
Legacy orchestrator - redirects to new orchestrators folder
"""
import warnings
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

warnings.warn(
    "This orchestrator.py is deprecated. Use orchestrators/master_orchestrator.py instead.",
    DeprecationWarning,
    stacklevel=2
)

def redirect_to_master():
    """Redirect to the new master orchestrator"""
    print("🔄 Redirecting to Master Orchestrator...")
    try:
        from orchestrators.master_orchestrator import MasterOrchestrator
        orchestrator = MasterOrchestrator()
        orchestrator.run_interactive()
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Please run: python run_orchestrator.py")

if __name__ == "__main__":
    redirect_to_master()