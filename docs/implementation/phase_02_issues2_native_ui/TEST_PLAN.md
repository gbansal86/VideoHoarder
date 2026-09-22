# Test Plan

1. Compile all application Python modules.
2. Run complete unittest discovery used by the Windows build script.
3. Validate library-browser live row output includes thumbnail URL/local media path.
4. Validate library service can supply more than the old 2,000-row cap for native pagination.
5. On a PySide6-capable host, validate:
   - downloader has separate Workflow and Quality controls;
   - Audio Only disables Quality;
   - queue has Name then Type and Name starts >= 300 px;
   - Library defaults to 100/page;
   - Failure page has Action/Delete column.
6. Windows manual acceptance:
   - More → New download → Open downloader expands options;
   - download a YouTube URL and confirm filename + thumbnail + Type are visible;
   - open Library and click a downloaded video;
   - confirm thumbnail, 100/page and page-size selector;
   - compare Needs attention count with Failure/Cleanup row count;
   - delete a failure and verify both list and count decrease.
