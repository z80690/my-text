cd C:\Users\Administrator\Desktop\my-text

Write-Host "=== Phase 1: Remove Git tracking ==="

if (Test-Path ".git") {
    Write-Host "Removing .git directory..."
    Remove-Item -Path ".git" -Recurse -Force
    Write-Host "Done"
}

Write-Host "`nChecking for nested .git directories..."
$nested = Get-ChildItem -Recurse -Filter ".git" -Directory -Force
if ($nested) {
    Write-Host "Found $($nested.Count) nested .git dirs"
    foreach ($dir in $nested) {
        Write-Host "Removing: $($dir.FullName)"
        Remove-Item -Path $dir.FullName -Recurse -Force
    }
} else {
    Write-Host "No nested .git directories found"
}

Write-Host "`n=== Phase 2: Reinitialize Git ==="

Write-Host "Initializing new git repo..."
git init

Write-Host "`nAdding all files..."
git add -A

Write-Host "`nCreating initial commit..."
git commit -m "Reinitialize repository - reset git tracking"

Write-Host "`nSetting up remote..."
git branch -M main
git remote add origin git@github.com:z80690/my-text.git

Write-Host "`n=== Verification ==="
Write-Host "Branch: $(git rev-parse --abbrev-ref HEAD)"
Write-Host "Remote: $(git remote get-url origin)"

Write-Host "`n=== Done ==="
Write-Host "Next: git push -u origin main"