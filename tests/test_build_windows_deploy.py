from pathlib import Path
import unittest


class BuildWindowsDeployTests(unittest.TestCase):
    def test_build_script_deploys_and_verifies_live_exe(self):
        source_root = Path(__file__).resolve().parents[1]
        script = (source_root / "BUILD_WINDOWS.ps1").read_text(encoding="utf-8-sig")
        self.assertIn('Join-Path $InstallRoot "VideoHoarder.exe"', script)
        self.assertIn('Join-Path $InstallRoot "VideoHoarder_previous.exe"', script)
        self.assertIn('Copy-Item -LiteralPath $OutputExe -Destination $InstalledExe -Force', script)
        self.assertIn('Get-FileHash -LiteralPath $InstalledExe -Algorithm SHA256', script)
        self.assertIn('Close VideoHoarder if it is running and retry', script)

    def test_build_and_deploy_wrapper_does_not_copy_live_exe_twice(self):
        source_root = Path(__file__).resolve().parents[1]
        wrapper = (source_root / "BUILD_AND_DEPLOY.bat").read_text(encoding="utf-8-sig")
        self.assertIn('BUILD_WINDOWS.ps1', wrapper)
        self.assertNotIn('copy /Y "%BUILT_EXE%" "%FINAL_EXE%"', wrapper)
        self.assertIn('test, build, back up, deploy, and verify', wrapper)


if __name__ == "__main__":
    unittest.main()
