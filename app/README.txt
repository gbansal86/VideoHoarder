VIDEO LIBRARY MANAGER - MASTER

TOP-LEVEL FILES KEPT MINIMAL
----------------------------
START.bat
app.py
config.json
urls.txt
README.txt

EXTERNAL EXECUTABLE DISCOVERY
-----------------------------
The app searches the main folder AND ALL subfolders recursively for:
- yt-dlp.exe
- ffmpeg.exe
- ffprobe.exe
- deno.exe

So your existing layout works:
VideoLibraryManager\
  START.bat
  app.py
  yt-dlp.exe
  deno.exe
  ffmpeg-master-latest-win64-gpl-shared\
    bin\
      ffmpeg.exe
      ffprobe.exe

MASTER FEATURE CHECK
--------------------
- Fast PARALLEL metadata extraction
- SQLite library database
- CSV export
- Original Title preserved exactly
- New Title updated separately
- Hindi/Hinglish/Punjabi/mixed titles -> natural English New Title through local LLM
- Unnecessary hashtags/symbols/clickbait removed from New Title
- Category / Subcategory / Main Topic / Tags
- AI Confidence / Needs Review
- Optional local Ollama model
- YouTube / Facebook / other yt-dlp-supported URLs
- Recursive yt-dlp/FFmpeg/ffprobe/Deno detection
- Optional video download
- Quality control: best / 2160 / 1440 / 1080 / 720 / 480 / 360 / audio
- Numeric quality is maximum quality, not exact-only
- English manual subtitles + English auto-subs fallback
- Subtitle conversion to SRT
- Video description
- Thumbnail
- info.json metadata
- Original transcript
- Clean transcript
- Detailed LLM transcript
- Timestamp range for every AI transcript section
- Per-video HTML report
- Local HTML5 video player
- Clickable transcript timestamps seek local video
- Searchable transcript report
- Folder name = New Title
- Video filename = New Title
- Collision protection using video ID
- Live browser progress dashboard
- Current file in progress
- Download percent
- Download speed
- ETA
- Stage status: downloading / merging / subtitles / description / metadata / AI transcript
- Recently completed files with check marks
- Cookies.txt or Firefox cookie support
- Resume-friendly SQLite/download folder behavior
- Original Title never overwritten by AI

CSV COLUMNS
-----------
Video URL
Original Title
New Title
Channel
Upload Date
Platform
Category
Subcategory
Main Topic
Tags
AI Confidence
Needs Review

IMPORTANT
---------
Original Title is always the source title.
Only New Title is translated/cleaned.

FIRST TEST
----------
1. Put yt-dlp.exe somewhere inside this folder tree.
2. Put ffmpeg.exe/ffprobe.exe anywhere inside this folder tree.
3. Optional: put deno.exe anywhere inside this folder tree.
4. Double-click START.bat.
5. Choose 1 and put one video URL in urls.txt.
6. Choose 2.
7. Check video_list.csv.
8. If Ollama is running, choose 3.
9. Enable download_video=true in config.json if you want the actual video.
10. Choose 4.

LOCAL DASHBOARD
---------------
http://127.0.0.1:8765
It opens automatically when START.bat launches.


IMPORTANT DOWNLOAD FIX
----------------------
Earlier MASTER builds defaulted to:
"download_video": false

That could create an HTML report without downloading the actual video.

Now options 4 and 5 ask at runtime:

Download actual video?
1 = Yes
2 = No, subtitles/transcript/report only

If Yes, choose:

1 = Prefer 1080p (best available <=1080p)
2 = Prefer 720p  (best available <=720p)
3 = Prefer 480p
4 = Prefer 360p
5 = Best available
6 = Audio only

"Prefer 1080p" means:
- download 1080p if available
- otherwise fall back to 720p, 480p, etc.
- do not fail just because exact 1080p is unavailable

"Prefer 720p" behaves the same way with 720p as the maximum.

OPTION 5 FLOW
-------------
1. Choose whether to download the actual video
2. Choose quality
3. Metadata scan
4. AI title/category/tag enrichment
5. Video/subtitle/description/info JSON processing
6. Original + cleaned transcript
7. Detailed LLM timestamped transcript
8. HTML report with local player and clickable seek timestamps


MASTER v3 DOWNLOAD RELIABILITY FIX
----------------------------------
The download/process step is now split into separate verified stages:

1. Actual video/audio download
2. English subtitle download
3. Description + thumbnail + info JSON
4. Original/clean/AI transcript
5. HTML report

A subtitle or description failure can no longer prevent the actual video from
being downloaded.

If a stage fails, the video's folder contains:

New Title.ERROR.txt

This shows the actual yt-dlp error instead of silently producing only report.html.

QUALITY FALLBACK
----------------
1080 preference:
best video <=1080p + best audio
then best progressive file <=1080p
then best available as final fallback

720 preference behaves the same way using 720p as the target.

FILES EXPECTED WHEN AVAILABLE
-----------------------------
New Title.mp4
New Title.en....srt
New Title.description
New Title.info.json
thumbnail
New Title.transcript_original.txt
New Title.transcript_clean.txt
New Title.transcript_detailed.json
New Title.report.html

If any file cannot be obtained, check:
New Title.ERROR.txt


MASTER v4 CRITICAL FIX
----------------------
Fixed the yt-dlp error:
"You must provide at least one URL"

The URL is now explicitly added to:
- video download command
- subtitle command
- description/thumbnail/info JSON command

DASHBOARD FILE CHECKLIST
------------------------
The dashboard now shows a table:

File                    Required   Status        Path
Video / Audio           Yes        Downloading   ...
English Subtitle        Yes        Pending       ...
Description             Yes        Complete      ...
Thumbnail               Yes        Complete      ...
Info JSON               Yes        Complete      ...
Original Transcript     Yes        Complete      ...
Clean Transcript        Yes        Complete      ...
AI Detailed Transcript  Yes        Complete      ...
HTML Report             Yes        Complete      ...

Possible statuses:
Pending
Downloading
Complete
Missing
Failed

The checklist is built from the options selected for the run, so it shows
which files are expected and whether each one was actually produced.


MASTER v5 - PORTABLE DEPENDENCY MANAGER
---------------------------------------
At startup the program checks:

Python
yt-dlp
FFmpeg
ffprobe
Deno
Ollama CLI
Ollama local server
Configured Ollama model

Missing portable tools can be downloaded into:
tools\

No Administrator installation is required for these portable downloads.

The dependency screen offers:

1 = Download all missing portable tools
2 = Download individual tool
3 = Start Ollama server
4 = Pull configured Ollama model
5 = Recheck
0 = Continue

OFFICIAL DOWNLOAD SOURCES
-------------------------
yt-dlp:
GitHub official yt-dlp latest Windows executable.

Deno:
GitHub official Deno Windows x64 ZIP.

FFmpeg:
Gyan FFmpeg Windows release essentials ZIP.

Ollama:
Official Ollama GitHub standalone Windows x64 ZIP.

OLLAMA WITHOUT ADMIN RIGHTS
---------------------------
Ollama's official Windows documentation states the normal installer does not
require Administrator rights and installs in the user profile. This program
instead supports the standalone ZIP so it can stay portable under tools\ollama.

AI MODEL
--------
The configured model is:
qwen2.5:7b

The model is NOT downloaded silently because it can require several GB.
Use dependency option 4 and confirm when prompted.

CORPORATE NETWORK NOTE
----------------------
If your corporate proxy/firewall blocks GitHub, gyan.dev, or Ollama model
downloads, automatic setup may fail. The dependency table will show what is
still missing, and you can manually copy the corresponding portable files into
any subfolder of VideoLibraryManager_MASTER_v5.


MASTER v6 - STRUCTURED CHAPTER REPORT + TRANSCRIPT-BASED ENGLISH FILENAMES
-------------------------------------------------------------------------
The local LLM now reads the actual transcript and creates the New Title from
the real video subject, instead of keeping clickbait wording from the source.

Example source title:
Sirf 1 Chammach Roz Khao — 7 Din Mein Pet Ki Charbi Kam Hone Lagegi!

A transcript-based title may become:
Cumin Carom Fennel and Fenugreek Remedies for Weight Management

The exact New Title depends on what the transcript actually discusses.

The New Title:
- is English even when source language is Hindi/Hinglish/Punjabi/etc.
- removes hashtags, emojis, decorative punctuation and unsafe filename symbols
- removes clickbait/promotional wording
- updates video_list.csv New Title
- becomes the folder name
- becomes the video filename
- renames related subtitle/transcript/report files

Original Title remains untouched.

HTML REPORT IMPROVEMENTS
------------------------
- Video is NO LONGER sticky while scrolling.
- Light blue/white background and clearer cards.
- Separate Chapters navigation.
- Structured Transcript area.
- LLM creates proper chapter headings.
- Each chapter has timestamp range.
- Chapter overview instead of dumping raw transcript.
- Topics.
- Key Points.
- Ingredients / Entities.
- Instructions mentioned.
- Claims made by the speaker.
- Content Overview near the top.
- Timestamp links still seek the local video.
- Better mobile layout.

TRANSCRIPT CLEANUP
------------------
Embedded SRT artifacts such as:
15 00:00:35,520 --> 00:00:40,079
are removed from readable transcript text.

MASTER v7
---------
- Dashboard now shows elapsed time per processing step and live running-step time.
- Embedded SRT artifacts such as '15 00:00:35,520 --> 00:00:40,079' are removed before the LLM sees transcript text.
- Chapter generation now uses timestamp-preserving groups and requires specific headings.
- If Ollama fails or returns the original title unchanged, a transcript-derived deterministic title fallback is used.
- Example fallback for this kind of transcript:
  Cumin Carom Fennel and Fenugreek Remedies for Weight Management


MASTER v8 - OLLAMA TIMEOUT RESILIENCE
-------------------------------------
If Ollama is slow, the app now:
- allows up to 600 seconds per LLM call by default
- retries failed/timed-out LLM calls twice
- uses smaller chapter chunks (120 seconds / about 3200 characters)
- shows LLM attempt number in the dashboard
- falls back to structured non-LLM output if a chapter still times out
- continues processing the rest of the video instead of failing the whole run

Config settings:
"ollama_timeout_seconds": 600
"ollama_retries": 2
"chapter_max_seconds": 120
"chapter_max_chars": 3200

If your PC is slow, you can increase timeout further.
If you want faster processing, use a smaller Ollama model.

MASTER v9 - TRANSCRIPT ENTITY FILENAMES
---------------------------------------
For list-style titles such as "5 Amazing Foods that Melt Belly Fat", the LLM
now identifies the actual foods/herbs/items from the transcript and uses them
in the English New Title/filename when practical.

Example (only when transcript supports these items):
Cumin, Fennel, Fenugreek, Cinnamon and Amla for Weight Management

The source Original Title remains unchanged. If Ollama times out, a broader
transcript entity fallback attempts the same behavior.


MASTER v10 - CMD PROGRESS + CLEAN RUN STATE + YOUTUBE 403 FALLBACK
-----------------------------------------------------------------
COMMAND PROMPT PROGRESS
The CMD window now mirrors the dashboard:
- current stage
- processed / total
- overall %
- current file
- file %
- speed
- ETA
- start/end timing for each stage

CLEAN RUN STATE
At the beginning of a new run, stale tracker/dashboard data is cleared:
- old current filename
- previous completed-file list
- previous failures
- previous file checklist
- previous stage timings
- previous percentages/speed/ETA

YOUTUBE 403 FALLBACK
A 403 on one YouTube stream no longer immediately fails the video.

The app now tries:
1. Normal best separate video/audio selection
2. YouTube web_safari client with HLS-friendly fallback
3. YouTube web_embedded fallback when applicable

If the first attempt returns HTTP 403, the app can also run yt-dlp -U once
before trying fallback strategies.

Why:
Current YouTube PO-token enforcement can make some GVS media URLs return 403.
yt-dlp documentation currently notes that web_safari exposes HLS formats that
do not require a GVS PO token at this time.

If all strategies fail, the per-video ERROR.txt records all final details.

COOKIES
If YouTube requires login/age/account access, configure browser cookies or
cookies.txt. A client fallback cannot bypass legitimate account restrictions.

MASTER v10.1 HOTFIX
-------------------
Fixed:
name 'stage_name' is not defined

The bug was in finish_stage(). It could interrupt processing after a completed
stage even though the LLM/download itself had already finished.
All v10 features remain unchanged.


MASTER v11 - TRANSCRIPT FIRST / ONE SUBTITLE REQUEST / RESUME
------------------------------------------------------------
NEW PROCESS ORDER
1. Metadata scan
2. For ALL missing videos, download exactly ONE preferred English caption track
   into tmp\transcripts\<video_id>\
3. Convert that locally into:
   <video_id>.timestamped.txt   <-- BEST LLM INPUT
   <video_id>.clean.txt
4. Use the timestamped transcript to create the final English New Title
5. Only then create the final folder and download the video/assets
6. Build structured chapters + HTML report

This means filenames are decided from actual transcript content BEFORE the
video is downloaded.

ONE ENGLISH SUBTITLE REQUEST
----------------------------
Metadata already tells the app whether manual English captions exist.
Priority:
1. Manual English subtitle
2. Auto-generated English subtitle

Only ONE source/language is requested.
The app no longer calls --write-subs and --write-auto-subs together.

The network caption is stored as VTT in tmp.
If you select "Save SRT", SRT is converted LOCALLY from that VTT.
No second YouTube subtitle request is made.

429 SAFETY
----------
For subtitle requests the app uses:
--sleep-requests 0.75
--sleep-subtitles 5
-R 3
--retry-sleep http:exp=5:60

If YouTube still returns HTTP 429, the app uses application cooldowns:
60 sec -> 180 sec -> 600 sec

Then it records the failure and continues instead of repeatedly hammering
YouTube. For a real YouTube/CAPTCHA soft block, use fresh browser cookies after
opening YouTube in the same browser/IP.

RESUME / DUPLICATE PROTECTION
-----------------------------
- tmp transcript exists -> do not download it again
- local video exists -> do not download it again
- description/thumbnail/info JSON exist -> do not request them again
- AI identity JSON exists -> do not call Ollama again
- chapter JSON exists -> do not call Ollama again
- video ID is the database primary key
- .video_id marker is used to find old downloads even when titles changed
- CSV now contains Downloaded, Downloaded Quality, Local Folder, Downloaded File

MANUAL VIDEO RENAME
-------------------
The app detects the actual media filename in the folder instead of assuming the
AI-generated filename still exists.

Menu option 9:
Refresh HTML reports / detect manually renamed video files

Use it after manually renaming a video. The HTML player source and CSV local
filename are refreshed.

UPLOAD DATE PREFIX
------------------
Options 4/5 now ask whether to prefix the FOLDER:
YYYY-MM-DD - New English Title

The video filename itself remains the meaningful New Title.

LLM INPUT
---------
Ollama now receives a clean lightweight timestamped transcript such as:

[00:00:00] Speaker introduces five remedies...
[00:00:16] First remedy uses cumin, carom seeds and fennel...
[00:01:35] Second remedy uses fenugreek and cinnamon...

Raw SRT/VTT sequence numbers and timestamp arrows are not sent to the LLM.

LLM SPEED / TIMEOUT
-------------------
Default timeout: 360 seconds
Default retries: 1
Model keep-alive: 30 minutes
Output is bounded with num_predict.

Chapter creation uses larger timestamped batches and asks the LLM to produce
multiple semantic chapters in each call, reducing the number of LLM calls per
video versus the older 2-minute-per-call design.


MASTER v12 - SINGLE AI CALL + HINDI FALLBACK + LANDSCAPE DASHBOARD
-----------------------------------------------------------------
SINGLE OLLAMA CALL PER VIDEO
After the transcript-first download, one Ollama request now returns:
- English translation/cleanup of transcript
- meaningful New Title
- title entities
- category/subcategory
- main topic
- tags
- content summary
- all structured timestamped chapters

The later download/report stage reuses those cached results and does not make
another chapter/title LLM call.

HINDI TRANSCRIPT FALLBACK
Caption priority is:
1. Manual English
2. Auto English
3. Manual Hindi
4. Auto Hindi

If Hindi is selected, the single Ollama call translates the timestamped
transcript to English while retaining [HH:MM:SS] markers. Final transcript,
filename and report are English.

EMPTY TRANSCRIPT FIX
The WebVTT parser now handles:
- HH:MM:SS.mmm
- MM:SS.mmm
- optional VTT cue settings
- cue identifiers
- rolling YouTube captions
- fallback plain-text extraction

This addresses cases where a VTT file downloaded successfully but the older
converter returned an empty transcript.

VIDEO PLAYBACK SPEED
HTML report now provides:
0.75x / 1x / 1.25x / 1.5x / 1.75x / 2x

LANDSCAPE DASHBOARD
Dashboard is now designed as a compact 3-column full-screen view:
- left: overall/current progress
- middle: stage timings/recent work
- right: required-file status
Each column scrolls internally only if necessary, avoiding one long vertical page.

MASTER v12.1 HOTFIX
-------------------
Fixed:
NameError: name 'analyze_video_once' is not defined

The single-AI-call function is now explicitly included before the naming stage.

A startup core self-check was also added. It verifies that the essential
pipeline functions exist before any long scan/download begins, so this type of
packaging error is caught immediately instead of after transcript processing.

MASTER v13 - HYBRID YOUTUBE API ARCHITECTURE
--------------------------------------------
Metadata priority: YouTube Data API v3 -> yt-dlp fallback.
Transcript priority: youtube-transcript-api -> one-caption yt-dlp fallback.

Configure the official API key from main menu option 10 or config.json. If no key is configured, metadata continues with yt-dlp.

youtube-transcript-api installs locally under tools\python_packages with pip --target, so admin rights are not required.

CSV now separates creator-supplied YouTube Tags from AI Tags and records Metadata Source and Transcript Source.


MASTER v14 - PARALLEL AI + SMART RESUME + FAST NO-LLM MODE
----------------------------------------------------------
SMART RESUME
Successful work is reused automatically:

Transcript cache exists and is non-empty
    -> REUSED; no transcript request

AI identity + chapters exist AND transcript fingerprint is unchanged
    -> REUSED; zero Ollama calls

Video already exists for the same video ID
    -> SKIPPED; no duplicate download

Description / thumbnail / info JSON already exist
    -> SKIPPED

HTML can still be regenerated locally.

AI CACHE VALIDATION
-------------------
The app stores a SHA-256 fingerprint of the timestamped transcript.
If the transcript is unchanged, cached AI analysis is reused.
If the transcript changes, AI runs again automatically.

PARALLEL OLLAMA
---------------
For missing AI work, multiple videos can be analyzed concurrently.

Selectable:
1 worker
2 workers [recommended]
3 workers
4 workers

Default is 2. More workers are not always faster when RAM/VRAM is limited.

FAST NO-LLM MODE
----------------
This performs all possible operations without Ollama:

- YouTube Data API / yt-dlp metadata
- transcript API / transcript fallback
- transcript caching
- English/Hindi transcript retrieval
- local transcript cleanup
- video download
- quality selection
- resume / duplicate checks
- optional local SRT conversion
- description
- thumbnail
- info JSON
- CSV
- HTML player/report
- playback speed
- dashboard
- file status
- step timings
- upload-date folder prefix
- manual video rename detection

Without LLM:
- filename uses deterministic source/transcript rules
- chapters use fast time-based grouping
- no semantic AI summary/category/tag enrichment
- Hindi transcript is not semantically translated by Ollama

MAIN MENU SHORTCUT
------------------
11 = FAST full pipeline without LLM

PROCESS MODES FOR OPTIONS 4/5
-----------------------------
1 = Smart Resume + LLM
2 = Smart Resume + FAST NO-LLM
3 = Retry Failed Only + LLM
4 = Refresh AI Only
5 = Force Full Reprocess

This is designed for very large libraries so completed transcript/API/AI work
is not repeated on every run.


MASTER v14.1 HOTFIX - COMPLETE NO-LLM OUTPUT
--------------------------------------------
FAST No-LLM mode now explicitly materializes:
- Video/audio
- Timestamped transcript TXT
- Clean transcript TXT
- Optional English SRT
- Description
- Thumbnail
- info JSON
- Deterministic structured chapters JSON
- HTML report
- CSV/database updates

If any expected non-AI output is missing, an ERROR.txt is written listing it.
The CMD window also prints completed and missing files after each video.


MASTER v15 FIXES
----------------
1. FAST NO-LLM filename behavior changed.

No-LLM mode now uses the CLEANED ORIGINAL YOUTUBE TITLE as the filename/folder
basis. It does NOT infer the filename from arbitrary transcript keyword hits.

Example:
Original:
How to Grow Indigo Plants & Process It into Blue Dye

FAST No-LLM New Title:
How to Grow Indigo Plants & Process It into Blue Dye

It will no longer become something unrelated such as:
Sprouts Health Guide

Transcript-based semantic renaming remains available in LLM mode.

2. Option 3 fixed.

Option 3 now:
- verifies the library contains videos
- prepares/reuses transcript cache
- performs/reuses transcript-based AI analysis
- updates New Title / Category / Tags / Chapters
- exports CSV
- prints Processed / AI done / Failed counts

The old Option 3 only selected rows with blank category/title, so it could
appear to do nothing when metadata had already populated clean_title.

3. ERROR.txt reliability fixed.

The outer download loop now catches ANY unhandled per-video exception and
always attempts to create:
New Title.ERROR.txt

The file contains:
- Video ID
- URL
- Original Title
- full Python traceback

Previously some exceptions were only written to app.log and occurred outside
the inner file-verification code, so no ERROR.txt appeared.


MASTER v15.1 HOTFIX
-------------------
- Fixed: NameError: shutil is not defined.
- FAST No-LLM now resets stale New Title values from the cleaned Original Title
  before processing, so old values such as "Sprouts Health Guide" cannot win.
- Added optional zero-byte Original Title marker file in every video folder.

Example marker:
How to Grow Indigo Plants & Process It into Blue Dye.original-title

Config:
"create_original_title_marker": true


MASTER v15.2 - WRONG-FOLDER / SHUTIL DIAGNOSTIC
-----------------------------------------------
This build explicitly imports shutil and verifies shutil.copy2 at startup.

START.bat and app.py now print:
- application version
- exact BAT folder
- exact app.py path
- Python executable
- shutil module status

You MUST see:
VideoLibraryManager MASTER v15.2

If the traceback still points to an older folder/app.py, that older copy is
being launched rather than this package.

Recommended:
1. Extract v15.2 to a NEW EMPTY folder.
2. Do not copy only START.bat.
3. Run START.bat from the newly extracted folder.
4. Confirm the CMD prints "MASTER v15.2".
5. Confirm the displayed app.py path is the new folder.


MASTER v16 - CLEAN VIDEO FOLDER LAYOUT
--------------------------------------
Top level of each video folder now contains only:

New Title.mp4
New Title.report.html
Original YouTube Title.original-title

Support files move under:

_data\
    .video_id
    New Title.transcript_timestamped.txt
    New Title.transcript_clean.txt
    New Title.en.srt
    New Title.description
    New Title.info.json
    New Title.webp
    New Title.transcript_detailed.json
    New Title.ERROR.txt

Resume/duplicate detection still works because .video_id is found recursively.


MASTER v16.1 - PLAYER SPEED + STRUCTURED TRANSCRIPT FIX
-------------------------------------------------------
PLAYBACK SPEED
The HTML player now has a real playback-rate dropdown plus shortcut buttons:
0.5x, 0.75x, 1x, 1.25x, 1.5x, 1.75x, 2x.

The script sets BOTH:
video.defaultPlaybackRate
video.playbackRate

and reapplies the selected value after metadata loads.

STRUCTURED TRANSCRIPT
The report now validates cached chapters before displaying them.

If chapters are:
- empty
- missing overview text
- only generic "Discussion 1", "Discussion 2", etc.

then the program rebuilds them from the cached timestamped transcript.

LLM mode:
attempts semantic headings from the existing one-call AI analysis.

No-LLM mode:
creates non-empty time-based sections and derives headings from meaningful
words in the corresponding transcript range instead of "Discussion 1/2/...".

Menu option 9 also performs the same chapter validation/rebuild when refreshing
existing reports.


MASTER v17
----------
Playback speed:
- direct HTML5 playbackRate dropdown
- 0.5x to 2x
- no external JS dependency

Hindi -> English without LLM:
- English transcript first
- if only Hindi exists and YouTube marks it translatable, youtube-transcript-api
  requests YouTube's English translation
- if not translatable, Hindi is kept as source

Structured Transcript:
- generic Discussion 1/2 chapters are rejected
- cached timestamped transcript is always used as fallback
- report gets time-based headings + overviews even without LLM
- option 9 rebuilds older reports


MASTER v17.1 - DESCRIPTION + DETAILED SECTION SUMMARIES
-------------------------------------------------------
Video Description:
- rendered in its own styled expandable card
- preserves paragraphs and line breaks
- URLs become clickable
- improved spacing/readability

Structured Transcript:
Every section now shows:
- Section Overview
- Detailed Summary
- Topics
- Key Points
- Ingredients / Entities
- Instructions
- Claims

If the LLM supplied a detailed summary, it is used.
If not, the report constructs a fuller detailed summary from overview, key
points, instructions, claims and entities.

No-LLM sections also populate detailed_summary so the report never relies only
on a short heading/overview.


MASTER v17.2
------------
Detailed Summary bug fixed:
the report now renders the calculated detailed summary for every section.

Without LLM, the detailed summary is built from representative transcript
sentences within that exact timestamp range, covering beginning, middle and end.

Description links are clickable for:
http://...
https://...
www....

Run option 9 to regenerate reports created by older builds.


MASTER v18 - STABILIZATION BUILD
--------------------------------
Implemented all remaining fixes identified after v17.2:

1. Description hyperlinks are now actually rendered through description_html.
2. Cached Hindi transcripts can be upgraded once to English using YouTube's
   own transcript translation, then reused forever.
3. Chapter validation is stricter and rejects generic/irrelevant headings.
4. Obsolete .report.html files are removed when New Title changes.
5. Existing old folder layouts can be reorganized into _data.
6. Every video ends with a FINAL CHECK showing PASS/FAIL for expected outputs.
7. HTML report displays the exact VideoLibraryManager version that generated it.
8. Option 9 organizes legacy files then refreshes reports.
9. New option 12 organizes the existing library without reprocessing videos.

FINAL CHECK validates:
- Video
- Original title marker
- .video_id
- Timestamped transcript
- Clean transcript
- Structured chapters
- Description
- Thumbnail
- Info JSON
- HTML report
- Optional SRT
- Playback speed control in HTML
- Detailed Summary presence in HTML
- Report generator version

If anything fails, the video's _data\ERROR.txt is updated automatically.


MASTER v19 - STRICT TIMESTAMP-BOUND MINI REPORTS
------------------------------------------------
Every Structured Transcript section now behaves like a mini knowledge article,
but ALL derived content is restricted to the transcript inside that section's
start/end timestamps.

Each section can show:
1. What This Section Is About
2. Main Idea
3. Detailed Summary
4. Important Topics / Entities
5. Step-by-Step Process / Instructions
6. Why It Matters / Who It Is Relevant For
7. Important Observations
8. Claims Made in This Section
9. Key Takeaways
10. Source Transcript for the exact timestamp range

The Source Transcript is collapsed by default.

Timestamp links continue to seek the local HTML5 video to the section start.

The program refreshes source_text from the cached timestamped transcript every
time a report is generated, preventing stale chapter boundaries from leaking
content from another time range.

Final validation now checks:
- Detailed Summary presence
- Timestamp-bound Source Transcript blocks
- seekTo timestamp links
- report version


MASTER v19.1
------------
HINDI-ONLY TRANSCRIPTS
- English SRT is no longer mandatory if English is unavailable.
- If YouTube provides only Hindi and cannot translate it, Hindi transcript/SRT
  is accepted.
- If youtube-transcript-api provides transcript text without a VTT, the app
  creates SRT locally from the cached timestamped transcript.

STRUCTURED TRANSCRIPT DESIGN
Removed:
- What This Section Is About
- Main Idea

Every section now focuses on:
Detailed Summary
- shown as bullet points
- derived only from that section's exact timestamp-bounded transcript

Optional subsections only appear when relevant:
- Step-by-Step Process / Instructions
- Why It Matters / Who It Is Relevant For
- Important Observations
- Claims Made in This Section

Source Transcript remains collapsed and displays the exact section time range.


MASTER v19.2
------------
FIXED:
NameError: timestamped_file is not defined

The final transcript paths are now created before any language-specific branch,
so Hindi-only and translation-fallback paths cannot reach validation with an
undefined variable.

STRUCTURED TRANSCRIPT SIMPLIFIED
Each section now shows only:

Detailed Summary
- meaningful paragraph-style summary
- based only on that section's exact timestamp-bounded transcript
- not one bullet per transcript line

Step-by-Step Process / Instructions
- optional
- only shown when real step/process language is detected

Source Transcript
- collapsed by default
- exact section timestamp range

Removed:
- Why It Matters / Who It Is Relevant For
- Important Observations
- Claims Made in This Section
- What This Section Is About
- Main Idea

Hindi-only subtitles remain valid when English is unavailable.


MASTER v19.3 - RESTORED VIDEO DOWNLOAD + COMPLETE ERROR CAPTURE
---------------------------------------------------------------
A structural issue was found in v19.2:
the actual video-download stage had been lost during earlier patches.
Transcript materialization was also incomplete.

v19.3 restores both.

VIDEO DOWNLOAD
- selected quality is passed to yt-dlp
- actual media file is verified after yt-dlp exits
- yt-dlp success code alone is NOT treated as success
- zero-byte/missing video is a hard failure

QUALITY:
1080 -> best available <=1080p
720  -> best available <=720p
480  -> best available <=480p
360  -> best available <=360p
best -> best available
audio -> best audio

TRANSCRIPTS
Cached timestamped/clean transcripts are copied into final _data before SRT,
report generation, and validation.

ERROR CAPTURE
Every requested artifact is checked for existence AND non-zero size.

ERROR.txt can now include:
TIMESTAMPED TRANSCRIPT MISSING
TIMESTAMPED TRANSCRIPT MATERIALIZATION FAILED
CLEAN TRANSCRIPT MISSING
CLEAN TRANSCRIPT CREATION FAILED
VIDEO DOWNLOAD FAILED
VIDEO FILE MISSING AFTER DOWNLOAD
DESCRIPTION / METADATA FAILED
HTML REPORT FAILED
MISSING EXPECTED OUTPUTS
FINAL VALIDATION

For a failed video, CMD also prints the URL and tells you where ERROR.txt is.


MASTER v20
----------
DASHBOARD:
Per-URL final-status table with PASS/FAIL checkbox, Video, Report, failure reason and URL.
Failed rows are highlighted.

OPTION 13:
Copy one best transcript for every video into all_transcripts.
English is preferred; otherwise the YouTube source language is retained.

OPTION 14:
Build compact ChatGPT JSON packages of approximately 5-15 videos depending on transcript size.
Every video is keyed by video_id.

OPTION 15:
Import structured ChatGPT result JSON from chatgpt_results.
Matching is by video_id only.
Each imported result is copied into:
_data\<title>.chatgpt_summary.json
<title>.chatgpt-summary.txt

OPTION 16:
Regenerate HTML reports using imported ChatGPT summaries.

Workflow:
14 -> upload package to ChatGPT -> save returned JSON in chatgpt_results -> 15 -> 16.


MASTER v20.1 - ENGLISH CHATGPT OUTPUT + YOUTUBE-AI STYLE GROUPED SUMMARY
-----------------------------------------------------------------------
ChatGPT package instructions now explicitly require ALL returned summary
content to be English.

If the transcript is Hindi or another language:
- ChatGPT must translate the meaning into natural English
- titles, summaries, headings, steps, tips, warnings and tags must be English
- proper nouns/product/herb names may remain as names
- video_id must never be changed

The package now requests a richer grouped result similar to YouTube AI:

Overall Summary + full-video time range

Then meaningful groups such as:
- Main Topics
- Remedies
- Methods
- Additional Recommendations & Tips
- Safety Guidelines
- Warnings
- Comparisons
- Ingredients
- Products

Only groups actually supported by the transcript should be returned.

Each grouped item includes:
- title
- start timestamp
- end timestamp
- meaningful English summary
- optional real steps/instructions

The importer supports this new grouped schema and still supports the previous
flat sections schema for backward compatibility.

HTML reports show group headings when imported ChatGPT results contain them.


MASTER v20.2
------------
FIXED option 16 crash:
NameError: group_html is not defined

write_html_report now initializes group_html on every section iteration.

Option 16 is also hardened:
- malformed/non-list section cache becomes []
- one failed video report no longer stops the whole regeneration run
- failure is written to _data\*.ERROR.txt


MASTER v20.3 - STATIC AUDIT FIXES
---------------------------------
A full static audit of v20.2 found and fixed:

1. Group headings:
   group_html could leak from a previous chapter or be missing.
   It is now reset on every section iteration.

2. Final validation:
   non-zero-size checks had been lost in the v20 branch.
   Video/transcript/report/description/thumbnail/info JSON must now be non-zero.

3. .video_id folder detection:
   with the _data layout, locate_existing_folder could incorrectly return _data
   instead of the actual video folder.
   It now returns the parent video folder.

4. Outer-error .video_id:
   fallback marker is now written under _data consistently.

5. SRT prompt:
   wording now correctly supports English OR source-language SRT.

6. ChatGPT summaries:
   timestamp source text is attached for report verification without replacing a
   valid imported ChatGPT detailed summary.

7. ChatGPT meaningful title:
   importing a summary no longer silently changes clean_title in SQLite without
   renaming the actual folder/video. This avoids title/path mismatches.

All code passes Python syntax compilation after these patches.


MASTER v20.4 - CHATGPT WORKFLOW HARDENING
-----------------------------------------
Added:

1. Processed/rejected ChatGPT result folders
   chatgpt_results\processed\
   chatgpt_results\rejected\
   Successfully imported result files are moved to processed so option 15
   does not re-import the same file every time.

2. Package validation
   package_id is checked against the exported package when available.
   Missing/extra Video IDs reject the result file.

3. Duplicate Video ID protection
   A returned JSON containing the same video_id twice is rejected.

4. English-output validation
   If ChatGPT returns substantial Devanagari/Hindi text when English is required,
   that video/result is rejected.

5. Timestamp validation
   Accepts HH:MM:SS or MM:SS, normalizes to HH:MM:SS, rejects:
   invalid minutes/seconds, end-before-start, and overlapping sections.

6. Incremental report regeneration
   Option 16 now offers:
   1 = only changed imported results
   2 = regenerate all
   Result hashes and report hashes are stored in SQLite.

7. Central transcript filename safety
   Title portion is capped to avoid Windows path-length problems.
   Older central transcript copies for the same Video ID are removed.

8. Error history
   Previous ERROR.txt is archived under _data\error_history\ before a retry.

9. Full yt-dlp failure log
   On video-download failure, _data\<title>.ytdlp.log keeps full command output.

10. ChatGPT readable summary stays in _data
    Keeps top-level video folders clean.

11. Option 16 updates dashboard status after successful/failed regeneration.


MASTER v20.5 - FINAL AUDIT FIXES
--------------------------------
1. srt_file runtime safety
   srt_file is initialized to None for every video.
   Branches that do not save SRT can no longer raise NameError.

2. Oversized transcript packages
   If one transcript exceeds chatgpt_batch_max_chars, it is isolated into its
   own one-video package instead of creating a mixed oversized package.
   Video ID matching remains unchanged.

3. ChatGPT meaningful title in report
   Imported ChatGPT meaningful_title is shown as the HTML report title when
   available.
   Physical video/folder names are NOT changed.

4. Finalized title protection
   Added title_finalized flag and safe_update_clean_title().
   Once ChatGPT results are imported, older AI/No-LLM title paths cannot silently
   overwrite clean_title.
   No-LLM normalization reports how many protected titles were skipped.

This build passes Python syntax compilation.


MASTER v20.6 - OPTION 15 FIX
----------------------------
Fixed:
NameError: hashlib is not defined

Timestamp validation changed:
- Invalid timestamps still reject the video.
- End-before-start still rejects the video.
- Legitimate overlapping sections NO LONGER reject the video.
- Overlaps are printed as warnings only.

Why:
A smaller subtopic can legitimately exist inside a larger chapter, e.g.
Turmeric section 06:29-08:06
  and
Milk absorption insight 07:35-08:06

Likewise a product/recommendation can begin while the speaker is transitioning
out of a broader remedy section.

ChatGPT package instructions now explicitly allow nested/overlapping time ranges
when they represent real subtopics/recommendations/insights.


MASTER v20.7 - HINDI/RENAMED TITLE IMPORT + VERSION-SAFE REPORT REGENERATION
----------------------------------------------------------------------------
FIXED:
Some Hindi-source videos could fail to receive/copy imported ChatGPT summaries
when ChatGPT returned a new English meaningful title.

Cause:
Summary filenames/paths could be tied too closely to the changed title.

v20.7 behavior:
- Import and report regeneration always locate the summary by Video ID.
- Physical video/folder/base filename stays stable.
- ChatGPT meaningful title is display metadata, not a lookup key.
- Canonical summary JSON is copied into the correct video's _data folder.
- Option 16 loads canonical imported summary JSON by Video ID.
- Option 16 no longer depends on an older cache/schema shape.
- Old/new grouped or flattened ChatGPT result schemas are normalized.
- Package files now include package_format_version=2.0.
- Returned results may include result_format_version=2.0.
- Report regeneration is designed to be tolerant of future package-version changes
  as long as Video ID and recognizable summary fields are present.

This is intended to remove version-related breakage in options 15 and 16.


MASTER v20.8 - CANONICAL SINGLE-FILE CHATGPT WORKFLOW
------------------------------------------------------
This build removes the remaining title-mismatch ambiguity.

ChatGPT summary lookup is ALWAYS by Video ID.

Canonical files per video:

_data\<VIDEO_ID>.chatgpt_summary.json
_data\<VIDEO_ID>.chatgpt_summary.txt

The ChatGPT-generated English title is stored INSIDE those files and displayed
in the HTML report. It is no longer used as a filename lookup key.

Legacy title-based ChatGPT summary files are automatically migrated to the
canonical Video-ID filename and stale duplicates are deleted.

REPORTS
Only one .report.html is kept in the video folder.
Older report files created under previous/new titles are deleted after successful
regeneration.

This means a Hindi-source video may have:

Physical video/folder title:
Sirf 1 Chammach Roz Khao ...

ChatGPT display title:
Five Homemade Weight Loss Remedies

But the program still finds the summary because it uses:
video_id = lYJDlH0CoE4

not either title.

Option 15:
imports/copies one canonical ChatGPT summary JSON + one readable TXT.

Option 16:
loads that canonical summary by Video ID and keeps one regenerated HTML report.


MASTER v20.9 - API KEY FILE
---------------------------
YouTube Data API key is read from:
  api_key.txt

Keep api_key.txt in the same folder as app.py / run.bat.

Accepted formats:
  AIzaSy...your-key...
or
  API_KEY=AIzaSy...your-key...
or
  YOUTUBE_API_KEY=AIzaSy...your-key...

Blank lines and lines beginning with # are ignored.
The API key is no longer intended to be stored in config.json.


MASTER v21 - OPTION 16 USES ONLY CANONICAL CHATGPT SUMMARY JSON
---------------------------------------------------------------
Option 16 now uses ONLY:

  _data\<VIDEO_ID>.chatgpt_summary.json

for all semantic/report content:

- ChatGPT English title
- Overall summary
- Category
- Subcategory
- Tags
- Chapter titles
- Chapter timestamps
- Detailed summaries
- Steps / instructions

It does NOT use the original-language transcript to rewrite/enrich those fields.

Existing local files are used only for:
- video playback
- original YouTube description
- technical metadata

This prevents a Hindi/source-language transcript from leaking back into a report
that already has an English ChatGPT summary.

If the canonical ChatGPT JSON contains no source transcript text, the report no
longer inserts a source-language transcript block during option 16 regeneration.

The canonical filename remains tied to Video ID, not title:
  _data\lYJDlH0CoE4.chatgpt_summary.json

So ChatGPT may change the English display title without affecting report lookup.


MASTER v21.1 - VERSION-AWARE CHATGPT REPORT REGENERATION
--------------------------------------------------------
Final audit found one runtime logic issue:

Option 16 incremental mode previously compared:
  chatgpt_report_hash == chatgpt_result_hash

That meant a new app/report-renderer version could skip rebuilding an older HTML
report if the ChatGPT summary itself had not changed.

v21.1 stores a report fingerprint containing:
- ChatGPT result hash
- current APP_VERSION / renderer version

Therefore after upgrading to a new package, option 16 automatically regenerates
each imported ChatGPT report once. On subsequent runs it skips unchanged reports
normally.

The audit also confirmed that option 16 does NOT call
attach_source_text_to_sections(); the reference seen during static scanning was
only inside a comment.


MASTER v21.2 - APPLY CHATGPT TITLES AND RENAME
----------------------------------------------
New menu:
17 = Apply ChatGPT Titles and Rename Files/Folders

This applies the imported ChatGPT meaningful English title to physical names.

Matching is ALWAYS by Video ID.

It renames, where present:
- video file
- HTML report
- .original-title marker filename
- video folder

It does NOT rename canonical Video-ID artifacts such as:
  _data\<VIDEO_ID>.chatgpt_summary.json
  _data\<VIDEO_ID>.chatgpt_summary.txt
  _data\.video_id

After filesystem rename succeeds, SQLite is updated:
- clean_title
- local_folder
- local_video
- report_html
- title_finalized

Finally video_list.csv is regenerated from SQLite.

Original Title is NOT changed.


MASTER v21.3 - CSV WITH CHATGPT TITLE
-------------------------------------
New menu:
18 = Create CSV with ChatGPT Title column

Creates:
  video_list_with_chatgpt_titles.csv

It retains the main library fields and adds:
  ChatGPT Title

Useful comparison columns:
  Original Title
  New Title
  ChatGPT Title

ChatGPT Title is resolved by Video ID from:
1. canonical _data\<VIDEO_ID>.chatgpt_summary.json
2. SQLite identity_json fallback

This lets you review ChatGPT names before running option 17 to physically rename
files/folders.


MASTER v21.4 - MAIN CSV CHATGPT TITLE + RENAME FROM REVIEWED CSV
---------------------------------------------------------------
video_list.csv now contains:

Original Title
New Title
ChatGPT Title

New menu:
19 = Rename Files/Folders from Reviewed CSV by Video ID

Recommended workflow:

1. Run normal CSV export or option 18.
2. Open CSV in Excel.
3. Review Original Title / New Title / ChatGPT Title.
4. Optionally add/use:
   Approved Title
5. Save CSV.
6. Run option 19.

Rename matching is ALWAYS by Video ID.

Title column priority:
1. Approved Title
2. ChatGPT Title
3. New Title

After rename, SQLite paths and clean_title are updated and video_list.csv is
refreshed automatically.


MASTER v21.5 - SCHEMA-SAFE CSV EXPORT FIX
-----------------------------------------
Fixed option 18 crash:
sqlite3.OperationalError: no such column: duration

Cause:
Older SQLite databases may not contain every column expected by newer code.

v21.5 now reads PRAGMA table_info(videos) and builds schema-safe SELECTs.
Missing optional columns are exported as blank values rather than crashing.

This applies to:
- normal video_list.csv export
- option 18 review CSV export

Option 18 now creates:
video_list_with_chatgpt_titles.csv

with:
Original Title
New Title
ChatGPT Title
Approved Title

Option 19 also skips rows where the approved title is already the current title.


MASTER v21.6 - OPTION 19 CSV PATH FIX
-------------------------------------
Fixed:
NameError: name 'CSV_FILE' is not defined

The program no longer depends on a legacy CSV_FILE global.
The canonical main CSV is resolved dynamically as:

  BASE\video_list.csv

Option 19 now explicitly passes that path into the reviewed-CSV rename routine.

Also audited the newer CSV/rename code for remaining bare CSV_FILE references.


MASTER v21.7 - OPTION 19 USES REVIEWED CHATGPT TITLE CSV
--------------------------------------------------------
Option 19 now uses:

  video_list_with_chatgpt_titles.csv

by default.

Run option 18 first, review the file in Excel, then run option 19.

Title priority for each Video ID:
1. Approved Title
2. ChatGPT Title
3. New Title

Safety improvements:
- duplicate Video IDs in reviewed CSV are flagged
- missing Video IDs are flagged
- missing title rows are skipped
- same-title rows are skipped
- existing target folder/media collisions are not overwritten
- canonical _data\<VIDEO_ID> files are not renamed
- SQLite is updated only after filesystem rename succeeds
- both video_list.csv and video_list_with_chatgpt_titles.csv are refreshed after rename


MASTER v21.8 - DASHBOARD LAUNCH CONTROL
---------------------------------------
Dashboard launch is restricted to menu options:

4
5

Other menu operations should not launch/open the dashboard, including:
- CSV exports
- ChatGPT package export/import
- ChatGPT report regeneration
- title rename operations
- library organization

This keeps lightweight maintenance operations in CMD only.


MASTER v22 - CHANNEL FOLDERS + RICH TAGGING + LOGICAL INDEXES
--------------------------------------------------------------
Default physical folder naming:
  YYYY-MM-DD - Channel Name - ChatGPT/New Title

Existing folders are not forcibly migrated during startup.
Use rename options when you want to apply the new naming.

ChatGPT schema now requests:
- Primary Category
- Primary Topic
- Topics
- Entities
- Ingredients
- Herbs
- Products
- People
- Locations
- Summary Language

These are stored in SQLite and exported to CSV when available.

Logical indexes do NOT duplicate videos.
New option:
21 = Build Topic / Entity / Channel Indexes

Creates:
  indexes\index.html

with logical views:
- By Channel
- By Category
- By Topic
- By Entity
- By Herb
- By Product

Dashboard behavior:
Dashboard no longer launches automatically during options 4/5 or startup.
New dedicated option:
20 = Open Dashboard

So processing/CSV/import/rename operations stay CMD-only unless you explicitly
choose option 20.


MASTER v22.1 - DASHBOARD + FULL FOLDER MIGRATION FIX
-----------------------------------------------------
Dashboard:
- Removed automatic dashboard launch from all processing/startup paths.
- Option 20 is the ONLY menu action that calls start_dashboard().
- Option 6 no longer launches Dashboard.

Folder rename/migration:
Option 19 now checks BOTH:
- title difference
- folder-format difference

So even if New Title already equals ChatGPT/Approved Title, the folder is still
migrated when it is missing date/channel formatting.

Target:
  YYYY-MM-DD - Channel - Title

New option:
22 = Migrate ALL Existing Folders to Date - Channel - Title

Option 22 uses current New Title, falling back to Original Title, and migrates
every known folder by Video ID. It does not require ChatGPT to have processed
every video.

This fixes the issue where only some folders were renamed.


MASTER v22.2 - BAT DASHBOARD AUTOLAUNCH FIX
--------------------------------------------
The dashboard was still opening because dashboard/browser launch logic could also
exist in the BAT launcher, outside Python menu handling.

v22.2 audits and removes dashboard/browser auto-launch commands from BAT files.

Expected behavior:
- Double-click/run BAT -> CMD menu only.
- Dashboard does NOT open automatically.
- Option 20 -> Open Dashboard.

Python menu is also audited so start_dashboard() appears only in option 20.


MASTER v22.3 - DASHBOARD HARD STOP + MIGRATION METADATA FIX
------------------------------------------------------------
Dashboard:
- Option 6 removed completely.
- All automatic dashboard/browser launch paths removed from Python and launcher scripts.
- Option 20 is the only explicit dashboard action.

Folder migration:
The previous 0 migrated / 3 skipped could occur when channel or upload_date was
missing in SQLite, causing the program to calculate an incomplete target folder
and incorrectly consider the current folder acceptable.

v22.3 resolves channel/date from:
1. SQLite
2. video_list_with_chatgpt_titles.csv / video_list.csv
3. _data\*.info.json
4. existing YYYY-MM-DD folder prefix for date

A folder is skipped only if its current name exactly matches:
  YYYY-MM-DD - Channel - Title

If channel/date cannot be resolved, the video is shown as UNRESOLVED instead of
being silently skipped.


MASTER v22.4 - RENAME ERROR LOGGING + DASHBOARD AUTOLAUNCH HARD STOP
--------------------------------------------------------------------
Option 19 now always writes:
  rename_review_results.csv

Every row shows:
- Video ID
- RENAMED / MIGRATED / SKIPPED / FAILED
- exact reason
- current title
- requested title
- current folder
- target folder

So skipped/failed rows are no longer opaque.

Option 22 writes:
  bulk_folder_migration_results.csv

Dashboard:
- option 6 removed
- launcher scripts contain no dashboard/local-browser references
- menu contains exactly one explicit start_dashboard() call under option 20
- automatic browser/dashboard launch calls outside start_dashboard() are removed


MASTER v22.5 - FINAL DASHBOARD AUTOSTART FIX
--------------------------------------------
Root cause found:
main() still contained:
  srv=start_dashboard()

That started the dashboard every time app.py/BAT launched.

v22.5 removes dashboard/server startup from main() completely.

Now:
- START.bat -> CMD menu only
- app.py -> CMD menu only
- option 20 -> starts dashboard/browser
- no server shutdown wrapper is required in main()

Executable start_dashboard() calls outside its definition: exactly one,
under menu option 20.


MASTER v23 - CHANNEL PARENT FOLDER STORAGE
------------------------------------------
New default physical layout:

Downloads\
  <Channel Name>\
    YYYY-MM-DD - <Channel Name> - <Title>\

Example:
Downloads\
  Fit Tuber\
    2026-03-20 - Fit Tuber - Cumin Ajwain Fennel and Fenugreek Remedies\

This works even when videos from the same channel are supplied one URL at a time.

The channel is taken from the video's metadata/SQLite record and the program
routes each new video into that channel's parent folder automatically.

Existing nested Video-ID lookup continues to work because folder discovery scans
recursively.

Rename/migration options now move videos into the channel parent folder as well.

Option 22 migrates existing folders into the new channel-rooted structure.

MASTER v24
----------
- Index labels use bilingual English/Hindi names for common herbs/ingredients.
- Option 17 removed.
- Physical structure is now:
  Downloads\<Channel>\YYYY-MM-DD - Title\
- Option 19 rebuilds the HTML report after rename so video playback uses the new MP4 filename.
- HTML report video source is always the current local media basename.


PHASE0-SR1 - SMART RESUME DUPLICATE FIX
---------------------------------------
Smart Resume now uses the real library as the authority.

Rules:
- Video ID already found via _data/.video_id or valid SQLite paths => SKIP download.
- TMP/cache folder => reusable cache only.
- TMP presence never triggers a redownload.

New option:
93 = Smart Resume Duplicate Audit


PHASE0-SR2 - SAFE CHATGPT TITLE RENAME + PLAYBACK REPAIR
---------------------------------------------------------
Renaming is now a single operation.

When a ChatGPT/approved title is applied, the program automatically:
1. Renames the video file.
2. Renames the HTML report filename.
3. Renames the .original-title marker filename (content stays original title).
4. Moves the video folder to:
     Downloads\<Channel>\YYYY-MM-DD - Title
5. Updates SQLite clean_title/local_folder/local_video.
6. Rebuilds the HTML report AFTER the physical rename.
7. Verifies that the HTML contains the CURRENT renamed media filename.
8. Updates report_html in SQLite.

Option 19 uses this workflow for reviewed CSV rows.

New easy option:
94 = Rename One Video Using ChatGPT Title + Repair Report

Enter only the Video ID. The program resolves the imported ChatGPT title,
renames everything and verifies local HTML playback linkage automatically.


PHASE0-SR3
----------
Smart Resume:
- skips only when a real non-zero media file already exists
- TMP/cache alone never causes a redownload decision

Option 19:
- does NOT rename the .original-title filename
- original-title marker filename/content remain untouched

New option:
95 = Download Current urls.txt Videos Only - No LLM - No Report

Option 95:
- runs metadata scan for current urls.txt
- matches only direct video URLs currently in urls.txt
- skips already completed Video IDs
- uses no LLM
- disables HTML report creation/regeneration for the run
- does not loop through unrelated old DB videos


PHASE0-SR4
----------
Option 95 is now:

95 = Complete Current urls.txt Pipeline - No LLM

It processes ONLY direct video URLs currently in urls.txt.

Existing completed videos:
- skipped entirely
- no re-download
- no report regeneration

New/incomplete videos:
- metadata
- transcript
- subtitle/SRT
- video download
- description
- thumbnail
- info JSON
- deterministic fallback title/chapters
- HTML report

No Ollama/LLM is used.


V25 PHASE 1 - LIBRARY REPAIR & INTEGRITY
-----------------------------------------
New main-menu option:
96 = Phase 1 - Library Repair & Integrity Center

Capabilities:
- full library health scan
- missing/corrupt artifact reporting
- zero-byte file detection
- SQLite path mismatch detection/repair
- missing .video_id marker repair
- broken/missing HTML report repair
- duplicate Video-ID detection
- orphan folder detection
- zero-byte quarantine (move only; no deletion)
- portable metadata backup excluding large media
- conservative DB reconstruction from folders

Outputs:
  library_health.csv
  library_health_summary.json
  _quarantine\
  _backups\
  video_library.rebuilt.db

The recovery DB is created separately. Current video_library.db is never replaced automatically.


V25 PHASE 1.1
-------------
Maintenance hierarchy:
  maintenance\
    backups\
    quarantine\
    repair_history\
    audits\
    recovery\

Use Phase 1 option 9 to migrate existing _backups, _quarantine and _repair_history.
No manual move is required.

.original-title:
- never quarantined just because it is zero-byte
- empty file is filled with original YouTube title
- missing marker can be created
- existing filename is preserved

Use Phase 1 option 10 to repair/fill all .original-title files.


V25 PHASE 2 - CHATGPT PACKAGE MANAGER
--------------------------------------
New main menu:
97 = Phase 2 - ChatGPT Package Manager

New structure:
data\
  chatgpt\
    packages\
    results\
    retry\
    archive\
    package_history.csv

Phase 2 features:
- package manifest with package ID, schema version, video count, expected Video IDs,
  transcript character count and source-language counts
- result completeness validation
- explicit missing Video-ID reporting
- unexpected/duplicate returned Video-ID detection
- partial import wrapper
- automatic retry package generation for missing/rejected videos
- manual retry package generation
- completed package archival
- package history CSV
- package dashboard
- schema normalization for older/newer result shapes

The existing canonical importer remains the deep validator/distributor.
Phase 2 adds lifecycle management around it.


V25 PHASE 2.1 - LEGACY PACKAGE / RESULT PATH FIX
-------------------------------------------------
Fixed:
1. Option 14 may still create packages in the legacy chatgpt_packages folder.
   Phase 2 now automatically syncs those packages into:
     data\chatgpt\packages\
   and creates missing manifest files.

2. Phase 2 dashboard searches both legacy and new package locations.

3. Phase 2 result validation/import no longer requires typing a full file path.
   Options 97.2 and 97.3 show a numbered list of detected JSON result files from:
     data\chatgpt\results\
     chatgpt_results\

4. PermissionError is handled with a clear message instead of a traceback.


V25 PHASE 2.2 - LEGACY COMPATIBILITY / BUG-FIX PASS
----------------------------------------------------
Phase 2 now automatically checks and supports both legacy and new ChatGPT paths.

Legacy folders supported:
  chatgpt_packages
  chatgpt_package
  packages
  chatgpt_results
  chatgpt_result
  results
  chatgpt_retry
  retry
  chatgpt_archive
  archive

New canonical folders:
  data\chatgpt\packages
  data\chatgpt\results
  data\chatgpt\retry
  data\chatgpt\archive

Compatibility behavior is COPY-ONLY by default:
old files are not deleted.

New Phase 2 options:
7 = Sync/Migrate Legacy ChatGPT Folders [Copy Only]
8 = Phase 2 Integrity Audit

Integrity audit writes:
  maintenance\audits\phase2_integrity_audit.csv

Phase 2 package manager also performs a compatibility sync automatically when opened.


V25 PHASE 2.3
-------------
Manual retry improvement:
- no Package ID typing
- choose package from numbered list
- see expected/imported/not-returned/returned-not-imported counts
- choose problem videos by number
- each problem video shows exact reason

Import improvement (97 -> 3):
- imports ONLY the selected result JSON
- does NOT call the legacy importer that scans all chatgpt_results files
- does NOT recreate work for every old result
- skips same result hash if already imported
- imports good videos independently
- creates retry package only for actual problem videos

Reasons now distinguish:
- Missing from ChatGPT returned result
- Duplicate Video ID in returned result
- Returned by ChatGPT but rejected by validation/import
- Already imported successfully

Per-package import reason report:
  maintenance\audits\<package_id>_import_status.csv


V25 PHASE 2.4 - PROJECT FOLDER RESTRUCTURE
------------------------------------------
Root now keeps only user-facing launch/input files:
  START.bat
  urls.txt
  api_key.txt

Application files:
  app\
    app.py
    config.json
    VERSION.txt
    FEATURE_AUDIT.txt
    PHASE0_CHECKLIST.txt
    README.txt

Persistent data:
  data\
    database\
      video_library.db
    exports\
      video_list.csv
      video_list_with_chatgpt_titles.csv
    chatgpt\
      ...

Maintenance:
  maintenance\
    audits\
      rename_review_results.csv
      library_health.csv
      library_health_summary.json
      phase0_core_audit.csv
    recovery\
      video_library.rebuilt.db

Logs:
  logs\
    app.log

Old root files are automatically migrated at startup.
Older menu options use canonical path helpers so they continue working.


V25 PHASE 3 - SUMMARY QUALITY & VALIDATION
------------------------------------------
New main menu:
98 = Phase 3 - Summary Quality & Validation

Checks:
- English ratio per title/summary/section
- timestamp coverage percentage
- uncovered timestamp gaps
- nested section detection
- partial-overlap warnings
- numeric/fact preservation signal
- measurement/unit preservation
- chapter confidence score
- overall quality/completeness score

Outputs:
  maintenance\audits\phase3_summary_quality.csv
  maintenance\audits\phase3\<VideoID>.quality.json

Phase 3 menu:
1 = Validate All Imported ChatGPT Summaries
2 = Show Detailed Quality for One Video
3 = Create Retry Package for Phase 3 FAIL Videos
4 = Open Phase 3 Audit Folder


V25 PHASE 4 - CONTENT INTELLIGENCE
----------------------------------
New main menu:
99 = Phase 4 - Content Intelligence

Phase 4 detects/apply structured extraction for:
- health/remedy content
- cooking/recipes
- gardening/DIY/how-to
- technology
- comparison content
- ranked lists
- Q&A/interviews
- generic instructional content

Structured outputs:
- remedy/recipe/how-to/instruction cards
- ingredients/quantities/steps/timing/frequency/duration/warnings
- comparison tables
- ranked lists
- safety notes
- products/people/locations/entities/herbs/ingredients
- named sources/organizations
- glossary
- Q&A

Outputs:
  data\intelligence\<VideoID>.intelligence.json
  data\intelligence\cards\<VideoID>.cards.json
  data\intelligence\tables\<VideoID>.tables.json
  data\intelligence\all_content_cards.csv
  maintenance\audits\phase4_content_intelligence.csv

Future ChatGPT packages created by option 14 now request these structured fields.
Existing imported summaries still work; Phase 4 extracts whatever is supported
by their current section/schema data without inventing missing facts.


V25 AUTOMATIC POST-CHATGPT PIPELINE
-----------------------------------
After Phase 2 imports a selected ChatGPT result, imported videos now automatically run:

1. Phase 3 summary quality validation
2. PASS / WARN / FAIL classification
3. Phase 4 content-intelligence extraction for PASS/WARN videos
4. HTML report regeneration
5. HTML local-video playback verification
6. CSV/DB refresh
7. Retry-package creation for hard FAIL videos only
8. Archive package only when no hard failures remain

Good videos continue even if another video fails.

Per-package orchestration audit:
  maintenance\audits\<package_id>_post_chatgpt_pipeline.csv

New Phase 2 option:
9 = Run Automatic Post-ChatGPT Pipeline for Existing Package

Use option 9 to apply the new automation to packages imported before this build.


V25 TASK-BASED MENU RESTRUCTURE
-------------------------------
Main menu is now organized by user intent:

1 = Download New Videos / Channel
2 = Resume / Retry Downloads
3 = Library & Reports
4 = Titles / Rename / Organize
5 = ChatGPT Processing
6 = Search / Topics / Intelligence
7 = Repair / Health / Maintenance
8 = Settings / Configuration
9 = Advanced Tools
20 = Open Dashboard

Old functionality has been routed into submenus instead of deleted.

ChatGPT workflow is now primarily:
  5 -> 1  Create ChatGPT Package
  5 -> 2  Import ChatGPT Result + AUTO Process

Phases 3 and 4 remain available manually for audit/rebuild, but normally run
automatically after ChatGPT import.


V25 MENU FIX1 - STABILITY AUDIT
-------------------------------
Fixed:
- Option 5 -> 1 package sync was unreachable after return.
- Option 5 -> 2 still used legacy result-folder scanning importer.
- Selected-result import now imports only that result JSON.
- Automatic Phase 3/4/report pipeline now runs after selected-result import.
- Advanced Phase 2 archive now uses package selection instead of manual ID.
- START.bat version/header updated.
- Added Advanced Tools -> 9 V25 Static Integrity Check.


V25 MENU FIX2
-------------
Additional compatibility fixes:
- migrates more legacy audit/history/log files from root
- adds Path Compatibility Audit
- V25 Static Integrity Check now reports stale root files
- no menu function references are missing
- no duplicate Phase2/autopipeline function definitions detected


V25 MENU FIX3
-------------
Fixed package-archive edge case:
- package is NOT archived merely because all returned/imported videos pass Phase 3/4
- archive requires EVERY manifest Video ID to be imported with canonical summary + report
- missing ChatGPT-returned videos keep package active
- manual archive also refuses incomplete packages
- duplicate retry packages for the same problem-video set are avoided

ChatGPT Processing adds:
13 = Check Package Completeness / Archive Eligibility


V25 MENU FIX4
-------------
Fixed:
1. Phase 1 -> Migrate Root Files now includes:
   library_health.csv
   library_health_summary.json

2. .original-title handling is now filename-independent.
   Code finds any *.original-title marker in the video folder.
   Renamed title/folder no longer requires a matching marker filename.

3. Empty/missing markers are repaired using original_title from SQLite.

4. Added Advanced Tools -> 11 Original-Title Marker Audit.


V25 MENU FIX5
-------------
Ollama:
- Normal Download now asks Yes/No/Cancel before using Ollama.
- Smart Resume Download now asks Yes/No/Cancel before using Ollama.
- No-LLM mode remains explicitly Ollama-free.
- Metadata Scan remains Ollama-free.

Smart Resume:
- audits the full managed library using SQLite + .video_id + real files
- Ollama output is NOT part of download-completeness
- classifies requested videos as:
    SKIP    = video + core support artifacts complete
    REPAIR  = video exists but support artifacts are missing
    DOWNLOAD= video missing/not found
- prints exact reason and found-by source
- Advanced Tools -> 12 runs full-library Smart Resume artifact audit


V25 MENU FIX6
-------------
Fixed fatal pre-download .original-title crash:
- ensure_original_title_marker never dereferences None
- process_download creates _data before metadata/error operations
- marker creation failure no longer aborts the video download
- ERROR.txt writer creates destination directories first

This specifically fixes:
AttributeError: 'NoneType' object has no attribute 'write_text'
and the follow-up ERROR.txt FileNotFoundError.


V25 MENU FIX7 - CENTRAL FAILED VIDEO LOG
----------------------------------------
Every download/process failure is now recorded in:
  logs\failed_videos.csv

Columns:
  Timestamp
  Video ID
  URL
  Title
  Channel
  Stage
  Error Type
  Error Message
  Folder
  Retry Status

Resume / Retry menu:
  6 = Show Failed Videos / Error Details
  7 = Clear Resolved Failure History

Advanced Tools:
  13 = Show Failed Videos / Error Details

Successful retry/process marks matching Video ID rows as RESOLVED.
Resolved history can be cleared without deleting pending failures.


V25 MENU FIX8
-------------
Transcript fallback:
- English transcript/captions first
- Hindi second
- any other available YouTube language third
- if a non-English transcript is translatable by YouTube, English translation is preferred
- video is marked transcript-failed only after no usable transcript/caption exists in any language
- failure reason explicitly states what was checked

Download menu cleanup:
- previous options 1 and 2 merged
- 1 = Download Current urls.txt Videos [Ask Ollama]
- 2 = Smart Resume Download [Ask Ollama]
- 3 = Metadata Scan [No LLM]

Failure visibility:
- app.log directory is always created before writing
- append_video_error no longer has unreachable central logging code
- logs\\failed_videos.csv is always written for failures
- current-URL pipeline prints a per-video SUCCESS/SKIPPED/FAILED table with stage + exact reason
- duplicate identical PENDING failure rows are suppressed


V25 MENU FIX9 - FIVE-PASS STABILITY AUDIT
------------------------------------------
Additional fixes found during five audit passes:
- Smart Resume transcript-first pass skips fully complete library videos instead of
  rechecking every old transcript before processing.
- generic download_stage failure path now creates _data before ERROR.txt.
- generic download_stage failures are guaranteed to enter logs\\failed_videos.csv.
- generic failure console output includes Video ID, title, URL and resolved reason.


V25 MENU FIX10
--------------
- Stops recreating root chatgpt_results/chatgpt_packages.
- Uses only data\chatgpt\results and data\chatgpt\packages.
- Smart Resume transcript-first work is limited to unresolved failed videos.
- Adds logs\failed_videos.txt with unresolved failed videos only.
- Deduplicates repeated pending failure rows by Video ID + stage.
- Adds logs\youtube_api_status.log showing API used/not-used reason.


V25 MENU FIX11
- 10-pass audit completed.
- Canonical ChatGPT writes remain under data\chatgpt\ only.
- Legacy root ChatGPT folders are read-only migration sources.
- Added ChatGPT Processing -> 14 to remove empty legacy ChatGPT folders safely.


V25 MENU FIX12 - TMP TRANSCRIPT CLASSIFICATION
----------------------------------------------
Policy:
  tmp\transcripts now keeps only Video IDs whose media file is not downloaded.

For successful video downloads, temp transcript folders are moved to:
  maintenance\transcript_archive\complete\
  maintenance\transcript_archive\subtitle_missing\
  maintenance\transcript_archive\description_missing\
  maintenance\transcript_archive\thumbnail_missing\
  maintenance\transcript_archive\info_json_missing\
  maintenance\transcript_archive\multiple_artifacts_missing\

Each archived transcript folder receives archive_status.json.

Old files:
  Resume / Retry -> 8 Clean / Classify Old tmp Transcripts
  Resume / Retry -> 9 Show tmp Transcript Problem Queue

Audit:
  maintenance\audits\temp_transcript_cleanup.csv


V25 MENU FIX13 - SHORT VIDEO TMP SEPARATION
-------------------------------------------
Temporary problem queues:
  tmp\transcripts\    = regular videos whose media is not downloaded
  tmp\short_videos\   = Shorts / short-form videos whose media is not downloaded

Short detection:
  1. /shorts/ URL
  2. duration <= 180 seconds when URL classification is unavailable

Old cleanup (Resume / Retry -> 8) now processes both temp areas.
Problem Queue (Resume / Retry -> 9) displays regular and short-video
problem queues separately.


V25 MENU FIX14
--------------
Fixes found by the second 10-pass audit:
- temp_paths now truly routes short-form videos to tmp\short_videos
- regular videos continue using tmp\transcripts
- successful regular or short video processing moves temp data out of tmp
- media-download failures remain in tmp as the problem queue
- Smart Resume completed-video cleanup uses the same generic cleanup helper


V25 MENU FIX15 - VIDEO-ONLY HARD FAILURE POLICY
-----------------------------------------------
Download success now depends only on actual video/audio media.

Missing items below are OPTIONAL and no longer make the video download fail:
- subtitles/SRT/VTT
- timestamped transcript
- clean transcript
- description
- thumbnail
- info JSON
- HTML report

A hard failure remains only when the media file itself is missing.

New transcript category:
  maintenance\transcript_archive\transcription_missing\

For old videos:
  Resume / Retry -> 10
  Reconcile Old Failures - Ignore Missing Non-Video Files

This clears old PENDING failures when the video file already exists.

Failure display now also prints:
  Missing files: ...


V25 MENU FIX16 - STRICT SMART RESUME QUEUE
------------------------------------------
Smart Resume now queues ONLY:
1. videos whose actual media file is missing
2. videos whose media exists but transcript is missing and transcript retries < 2

Transcript retries:
- maximum 2 attempts per Video ID
- attempt state stored in:
  data\database\transcript_retry_state.json
- after 2 unsuccessful transcript attempts, if video exists, Smart Resume ignores/resolves it

Queue file:
  logs\smart_resume_queue.txt

Resume / Retry:
11 = Show Smart Resume Queue
12 = Rebuild Smart Resume Queue for Existing Files

Existing files are reconciled to the new rule by option 12.


V25 MENU FIX17
--------------
- .original-title marker is now strictly best-effort metadata.
- Missing marker can never block video download.
- process_download no longer blindly dereferences marker paths.
- Existing failed rows are marked RETRYING when a retry starts.
- Added Advanced Tools -> 16 Original-Title Reference Audit.


V25 MENU FIX18 - FAILURE DIAGNOSTICS
------------------------------------
- ProcessingFailed no longer hides the real inner failure.
- failed_videos.csv stores the actual latest ERROR.txt content/reason.
- process_download guarantees a final ERROR.txt when it returns failure.
- failed-video display shows the exact ERROR.txt path when available.


V25 MENU FIX19 - _DATA DIRECTORY ROOT-CAUSE FIX
-----------------------------------------------
Root cause fixed:
- timestamped transcript copy failed because destination _data did not exist
- ERROR.txt logging failed for the same missing directory

Changes:
- support_dir() creates _data by default
- process_download creates _data before any transcript/materialization work
- timestamped transcript destination parent is created before shutil.copy2()
- transcript materialization failures are soft; video download continues
- append_video_error guarantees _data and has a fallback ERROR.txt


V25 MENU FIX20 - SMART RESUME OUTPUT CLEANUP
--------------------------------------------
Smart Resume queue/output contains ONLY:
1. VIDEO MEDIA MISSING
2. TRANSCRIPT MISSING with attempt count < 2

Completed videos are silent:
- no SMART RESUME SKIP lines
- no transcript materialization for them

Ignored completely for Smart Resume:
- missing SRT/VTT when transcript already usable
- missing description
- missing thumbnail
- missing info JSON
- missing HTML report
- any other optional artifact

Transcript retry max remains 2.


V25 MENU FIX21
--------------
Fixed error logger regression:
- append_video_error now has explicit signature:
  (folder, base, label, message, details="")
- label/message/details are always defined
- _data is created before every error write
- fallback ERROR.txt write remains best-effort
- support_dir() is hardened


V25 MENU FIX22
--------------
10-pass audit fix:
- all transcript/subtitle materialization and missing-file paths are soft
- no transcript-related branch sets overall_ok=False
- media file existence remains the only hard download requirement


V25 MENU FIX23 - WINDOWS LONG PATH FIX
--------------------------------------
Root cause for b0I3vNm480M transcript materialization:
the title-derived _data destination path exceeded classic Windows MAX_PATH.

Fix:
- long _data filenames automatically switch to VideoID-based names
- folder title remains unchanged
- timestamped transcript, clean transcript, and ERROR.txt get short fallback names
- destination parent directories are always created

Advanced Tools:
17 = Windows Long Path Audit


V25 MENU FIX24 - 50 CHARACTER FOLDER TITLE RULE
-----------------------------------------------
New folder format:
  Date - Title

Title portion maximum:
  50 characters

The code also calculates a Windows-safe full-path budget before folder creation.
If the project/channel path is already deep, the visible title is shortened below
50 characters automatically so _data files remain safely below the classic
Windows path limit.

Titles / Rename / Organize:
8 = Migrate Existing Folders to Max 50-Character Titles
9 = Audit Folder Title / Windows Path Length

Collision handling:
  shortened title + [VideoID] when needed.

The folder title may be shortened, but original title remains preserved in SQLite
and .original-title metadata.


V25 MENU FIX25
--------------
Correct central folder-path fix:
- video_folder_path() now enforces the 50-character title cap
- all new downloads pass Video ID into video_folder_path()
- existing overlong folders are normalized when process_download runs
- full path is shortened further when needed to stay below Windows safe budget


V25 MENU FIX26
--------------
- MAX_VIDEO_TITLE_CHARS=50 moved to global startup scope
- WINDOWS_SAFE_PATH_BUDGET=220 moved to global startup scope
- fixed prepare_transcript_row retry helper variable mismatch when present
- ensured path_budgeted_video_title helper exists before video_folder_path uses it
- compile/AST/critical-reference audit passed


V25 MENU FIX27
--------------
- fixed prepare_transcript_row undefined video_id reference
- function now derives vid safely from row[0]
- retained global MAX_VIDEO_TITLE_CHARS=50 and Windows path budget fix


V25 MENU FIX28
--------------
Windows-path hardening:
- video folder title remains max 50 characters
- video/media filename is capped at 50 characters
- ALL _data support artifacts use Video ID filenames
- SRT uses <VideoID>.<lang>.srt
- transcripts use <VideoID>.transcript_*.txt
- metadata assets use Video ID output stem
- all errors use short _data\ERROR.txt
- channel directory is always created before video folder creation
- .original-title fallback no longer dereferences None


V25 MENU FIX29
--------------
Central current failure files:
  logs\failed_videos.csv
  logs\failure_details.txt

Archived old/stale history:
  logs\archive\failed_videos_history.csv

Resume / Retry:
13 = Consolidate Failure Reasons + Archive Old History
14 = Clean Resolved tmp Remnants

Current URL results now use the latest captured root failure reason.


V25 MENU FIX30 - VIDEO-ID STAGING ARCHITECTURE
----------------------------------------------
All active downloads now land first in:
  downloads\_staging\<VideoID>\

Support files:
  downloads\_staging\<VideoID>\_data\

Everything is Video-ID based during download, avoiding title/path problems.

After media validation:
  staging is committed into the final channel/date-title folder.

Smart Resume:
  checks Video-ID artifact inventory, not title filenames.

Artifact registry:
  data\exports\video_artifact_registry.csv

Resume / Retry:
15 = Export Video-ID Artifact Registry
16 = Clean Empty Staging Folders


V25 MENU FIX31
--------------
Critical staging fixes:
- current URL pipeline no longer blocks media download when transcript fails
- transcript is optional, max 2 attempts
- failures use staging folder when final folder does not exist
- staging queries no longer create empty staging folders
- after staging commit, ALL SQLite artifact paths are refreshed to final paths
- Smart Resume/current URL action check aligned to COMPLETE/RETRY/DOWNLOAD
- added Resume/Retry -> 17 Staging Audit


V25 MENU FIX32
--------------
- fixed NameError: video_folder_path no longer calls nonexistent channel_folder()
- now uses defined helper: channel_root()
- added stronger bare-function-call audit against actual defined/imported/builtin symbols
- critical runtime paths checked for undefined calls


V25 MENU FIX33
--------------
- added missing folder_title_length_audit()
- full application bare-function-call audit now passes
- no undefined direct function calls remain in any top-level function
- retains channel_root() fix for video_folder_path()


V25 MENU FIX34
--------------
HTML report navigation:
- Previous Video / Next Video buttons
- Left Arrow / Right Arrow keyboard shortcuts

Delete marker workflow:
- create an empty file named .delete inside a final video folder
- run Library & Reports -> Process .delete Markers
- the Video ID is resolved from the folder
- that Video ID is purged from final library, staging, tmp, transcript archives,
  matching summary/cache paths, failed logs, retry state, and SQLite tables
- deletion audit:
  maintenance\audits\delete_marker_audit.csv


V25 MENU FIX35
--------------
Successful retry cleanup:
- when a failed video later downloads successfully, its current entries are
  removed from:
    logs\failed_videos.csv
    logs\failed_videos.txt
    logs\failure_details.txt

App log behavior:
- before each download/load run, logs\app.log is rotated to:
    logs\archive\app_YYYYMMDD_HHMMSS.log
- a fresh empty app.log is then used for the new run

Resume / Retry:
18 = Purge Resolved Failure Entries


V25 MENU FIX36
--------------
Delete marker:
- after purging a video, remove the parent channel folder if it is empty
- never remove DOWNLOADS or _staging

HTML report rebuild:
- prefer approved/final title when rebuilding reports
- preserve original-title metadata
- Library & Reports -> 9 Rebuild All HTML Reports with Approved Titles


PHASE 5 - KNOWLEDGE / GLOBAL SEARCH / CROSS-VIDEO INTELLIGENCE
--------------------------------------------------------------
Implemented:
- global search across titles, summaries, transcript text, topics/entities/herbs/products
- cross-video topic HTML pages
- related-video recommendations
- channel knowledge reports
- transparent "Worth Watching?" heuristic score
- searchable JSONL + CSV corpus

Outputs:
  data\knowledge\search\
  data\knowledge\topics\
  data\knowledge\related\
  data\knowledge\channels\
  maintenance\audits\phase5_knowledge_summary.csv

Main menu:
  6 = Search / Topics / Intelligence
    5 = Phase 5 Knowledge / Global Search / Related Videos

Phase 5 is refreshed automatically after ChatGPT result import.

PHASE5 FIX1
- added Counter/defaultdict imports
- fixed automatic Phase 5 refresh hook after ChatGPT import
- 10-pass Phase 5 audit passed

PHASE5 FIX2
- Fixed NameError: math is not defined in phase5_worth_watching.
- Added explicit import math.
- Focused 10-check Phase 5 audit passed.

PHASE5 FIX3
- fixed NameError: htmlmod not defined by adding import html as htmlmod
- audited module-qualified Phase 5 dependencies
- cleaned the .delete invalid-escape SyntaxWarning


PHASE5 DASH1
------------
Added browser-based Knowledge Center:
  data\knowledge\index.html

Dashboard:
- browser-side global search
- thumbnail cards
- approved/ChatGPT English titles preferred
- Devanagari/Hindi titles suppressed from Phase 5
- canonical topic normalization (e.g. Home Remedy/Home Remedies -> Home Remedy)
- broad categories: Health, Mobile, AI, IT, Finance, Cooking, Gardening,
  Travel, Automotive, Education, News & Current Affairs, Lifestyle, Other
- category/channel filters
- Worth Watching sort
- Open Report links

Main access:
  Search / Topics / Intelligence -> 10
or
  Phase 5 Knowledge Manager -> 9


PHASE5 DASH2
------------
Scalable dashboard for large libraries:
- front page shows category tiles only
- separate Latest 7 Days tile
- videos are rendered only after opening a category
- tags/topics shown only for the selected category
- category-local search and sorting
- Mark Delete button on each video card

Delete behavior:
- browser file:// pages cannot directly create local files
- button copies the exact <video folder>\.delete marker path
- server-side helper create_delete_marker_for_video(video_id) is included for dashboard/API integration


PHASE5 DASH3
------------
Scale/performance:
- incremental Phase 5 indexing (unchanged videos reused)
- 50-video lazy pagination per view
- category -> subcategory -> tag hierarchy

Persistent personal library state:
- Favorite (.favorite marker + DB)
- Watched/Unwatched
- Personal rating 0-5
- Archive/Unarchive (.archive marker + DB)
- Delete marker from dashboard server

Downloaded timestamp:
- videos.downloaded_at added to SQLite
- existing videos backfilled from media file modified time
- video_list.csv adds Downloaded At, Favorite, Watched, Personal Rating, Archived
- Latest 7 Days uses downloaded_at

Intelligence:
- duplicate-topic CSV
- best-video-per-topic CSV
- search snippets helper
- related videos embedded into rebuilt per-video HTML reports
- maintenance stats on dashboard

Dashboard:
- root copy: VIDEO_LIBRARY_KNOWLEDGE_CENTER.html beside START.bat
- interactive server: Phase 5 -> Open Interactive Dashboard Server


DASH3 FIX1
- fixed downloaded_at SQL placeholder
- sync .favorite/.archive markers
- category statistics
- duplicate-topic and best-video-by-topic dashboard panels
- search snippets
- timestamp Jump to Match
- report ?t= seek support
- OPEN_KNOWLEDGE_CENTER.bat beside START.bat


DASH3 FIX2
- per-video HTML reports now read ?t=seconds and seek the video player
- completes Phase 5 Jump to Match flow


PHASE5 DASH4 - MENU CLEANUP
---------------------------
Phase 5 menu is simplified to:

1 = Build / Refresh Complete Phase 5 Knowledge Layer
2 = Open Knowledge Dashboard
3 = Export / Refresh Search Index CSV
4 = Open Phase 5 Knowledge Folder
0 = Back

Option 1 automatically:
- incrementally refreshes search index
- refreshes Search Index CSV
- rebuilds cross-video topic pages
- rebuilds related-video recommendations
- rebuilds channel knowledge reports
- refreshes duplicate-topic and best-video-per-topic exports
- rebuilds Knowledge Dashboard
- refreshes root VIDEO_LIBRARY_KNOWLEDGE_CENTER.html
- writes phase5_knowledge_summary.csv

The outer Search / Topics / Intelligence menu no longer duplicates Phase 5 build/search commands.


PHASE5 DASH5
------------
Knowledge Center homepage:
- Categories shown in their own section
- Channels shown with video counts
- clicking a Channel opens only that channel's videos
- Best Video by Topic titles are clickable links to the HTML report when available


PHASE5 DASH6
------------
Thumbnail fix:
- interactive dashboard no longer uses file:/// thumbnail URLs
- local server now serves thumbnails from /thumb/<VideoID>
- standalone HTML still uses local file URI
- thumbnail images use browser lazy-loading for large libraries

PHASE5 DASH7
- tags filter inside dashboard
- Best Video and card video links open embedded report view
- Back restores previous view
- /report/<VideoID> route

PHASE5 DASH8
- media served through /media/<VideoID> with MIME and byte-range support
- embedded reports rewrite video source to server media route
- homepage global search + All Channels filter
- Top 10 videos by score in each selected category/topic/channel/search view

PHASE5 DASH9
- removed Best Video by Topic from Knowledge Center homepage

PHASE5 DASH10
- clicking thumbnail opens embedded video/report
- embedded detail view has -10 sec / +10 sec seeking buttons
- Left/Right arrow keys seek -10/+10 seconds
- regenerated standalone HTML reports get the same seek controls


PHASE5 TAGS1
------------
Added one-file ChatGPT taxonomy cleanup workflow.

Phase 5:
5 = Create ChatGPT Tag Cleanup File
6 = Import ChatGPT Cleaned Tags

Input:
  data\knowledge\chatgpt_tag_cleanup_input.jsonl

Each video includes:
- Video ID
- approved/English title
- channel
- current category
- current subcategory
- primary topic
- current canonical tags
- compact summary/intelligence context

The first JSONL record contains strict taxonomy instructions.

Expected ChatGPT output:
  data\knowledge\chatgpt_tag_cleanup_result.jsonl

Output schema:
  {"video_id":"...","category":"...","subcategory":"...","tags":["..."],"notes":"..."}

After import, Phase 5 is rebuilt automatically.

PHASE5 TAGS2
- ChatGPT taxonomy input explicitly requires output filename chatgpt_tag_cleanup_result.jsonl
- Arrow Left/Right seeking strengthened for native video fullscreen
- Fullscreen player receives keyboard focus and capture-phase key handling

PHASE5 TAGS3
- imported ChatGPT-cleaned taxonomy is now shown in every rebuilt video HTML report
- report section: Library Taxonomy -> Category / Subcategory / Tags
- importing cleaned tags automatically rebuilds only affected video HTML reports
- Phase 5 then refreshes as before


PHASE5 HARD1
------------
Final Phase 5 hardening:
- taxonomy_hash / taxonomy_updated_at tracking
- html_report_taxonomy_hash / html_report_updated_at tracking
- Option 1 recompiles only reports whose taxonomy changed
- automatic taxonomy backup before ChatGPT tag import
- taxonomy quality audit
- tag usage / rare tag report
- duplicate-tag candidate report
- taxonomy statistics report
- library orphan/integrity audit
- stronger search ranking: title > tags > category/subcategory > summary > transcript
- server-side /api/library-page pagination/filtering endpoint for 5,000+ videos
- Phase 5 menu option 7 runs taxonomy/integrity audits

Audit outputs:
  data\knowledge\audits\taxonomy_quality_audit.csv
  data\knowledge\audits\tag_usage.csv
  data\knowledge\audits\tag_duplicate_candidates.csv
  data\knowledge\audits\taxonomy_statistics.csv
  data\knowledge\audits\library_integrity_audit.csv

Taxonomy backups:
  data\knowledge\taxonomy_backups\


PHASE5 HARD2
------------
Taxonomy rebuild reliability:
- every regenerated report embeds video-library-taxonomy-hash meta
- Option 1 checks the actual HTML file hash, not only SQLite state
- old reports with no embedded hash automatically rebuild
- rebuilt report is verified after generation
- Phase 5 option 8 forces all video HTML reports to rebuild

Video controls:
- Close Video
- Picture in Picture
- existing +/-10 sec and arrow seeking retained
- standalone reports also get Picture in Picture

Dashboard media server:
- ConnectionResetError / BrokenPipeError / ConnectionAbortedError are treated as normal client disconnects
- no noisy traceback when browser closes/seeks/replaces a media range request

PHASE5 HARD3
- fixed report Video ID initialization before taxonomy hash/rendering
- fixes rebuilt=0/skipped=0/failed=6 caused by missing embedded hash
- smart rebuild now checks actual rebuild return status
- force rebuild also checks rebuild return status
- taxonomy hash reader supports either meta attribute order


PHASE 6A - RETRIEVAL FOUNDATION
-------------------------------
Added:
- incremental transcript/chapter chunk index
- timestamp-aware evidence chunks
- Search-Only mode with no LLM
- title/section/tag/category/text weighted retrieval
- direct video + timestamp results
- Knowledge Center "Ask Your Library" evidence panel
- /api/phase6-search
- Phase 6 chunk health audits
- Phase 6 outer menu entry

Files:
  data\knowledge\phase6\chunks\chunk_index.jsonl
  data\knowledge\phase6\chunks\chunk_index.csv
  data\knowledge\phase6\chunks\chunk_manifest.json
  data\knowledge\phase6\audits\phase6_chunk_health.csv
  data\knowledge\phase6\audits\phase6_missing_chunks.csv

Phase 6B will add Ollama/Qwen Fast Local + Deep Local, model routing,
keep_alive, answer cache, and evidence-only synthesis.


PHASE6A SEARCHFIX1
------------------
Retrieval fixes:
- one result per video by default
- additional matching chunks retained internally
- whole-token matching instead of arbitrary substring matching
- multi-word queries require all terms by default
- exact phrase receives strong ranking bonus
- close/proximate transcript terms receive bonus
- UI shows "N matching sections" instead of repeating the same video
- optional API debug: all_chunks=1 or loose=1


PHASE6A SEMANTIC1
-----------------
Adds local intelligent retrieval without Ollama:
- morphology/inflection handling: grey <-> greying/graying
- spelling variants: grey/gray, colour/color, fibre/fiber
- curated semantic aliases for common library domains
- multi-word queries require all CONCEPT groups rather than exact literal words
- semantic proximity bonus
- still returns one best result per video
- UI labels literal "Exact phrase" vs "Semantic match"

Example:
  query: grey hair
  can match: greying hair, graying hair, gray hair

PHASE6A HYBRID1
- hybrid semantic embedding + lexical retrieval
- sentence-transformers used automatically when available
- no-install deterministic hashing fallback otherwise
- incremental embedding cache and manifest
- semantic-only matches allowed above backend-specific threshold
- one result per video retained
- dashboard shows semantic similarity percentage


PHASE 6B - OLLAMA/QWEN AI
-------------------------
Added:
- Fast Local mode: default qwen2.5:3b + small evidence set
- Deep Local mode: default qwen2.5:7b + larger evidence set
- Search Only mode remains available with no LLM
- evidence-first prompts: answer only from library evidence
- source-number citations in AI answers
- keep_alive support to avoid repeated model reloads
- answer cache keyed by question/model/evidence
- Regenerate bypasses cache
- Ollama status/model/settings menu
- AI timing/model/cache status in dashboard
- evidence remains clickable to exact video timestamps

Settings:
  data\knowledge\phase6\ai_settings.json

Answer cache:
  data\knowledge\phase6\cache\answers\


PHASE 6C - SEARCH V2 + TOPIC COLLECTIONS + CHATGPT LIBRARY INTELLIGENCE
-----------------------------------------------------------------------
Existing videos do NOT need to be downloaded again.
1. Phase 6 -> 1 rebuilds the existing chunk/search layer incrementally.
2. Open Knowledge Center, search a topic, tick videos, save a Topic Collection.
3. Phase 6 -> 4 exports either FULL transcripts or FOCUSED relevant sections.
4. Upload the generated CHATGPT_PACKAGE.txt to ChatGPT.
5. Ask ChatGPT to follow the embedded instruction and save the JSON output as
   chatgpt_library_intelligence_result.json.
6. Put that JSON in data\\knowledge\\phase6\\chatgpt_intelligence\\ and run
   Phase 6 -> 4 -> Import ChatGPT Library Intelligence JSON.
7. Run Phase 6 -> 1 again. Imported questions/search phrases/concepts/synonyms
   become high-weight Search V2 metadata for the EXISTING videos.

A video may belong to multiple collections. Collections are persistent in:
data\\knowledge\\phase6\\collections\\collections.json
Original transcripts and YouTube metadata are never overwritten.


PHASE6C FIX1
- Ask Your Library evidence checkboxes and direct collection controls.
- Select All/Clear/Create or Add/Focused Export directly on evidence results.
- Promo/outro/intro ranking penalties and visible match reasons.
- Collection rename/remove/delete/size-estimate management.


PHASE6C FIX2
- Collection prompts accept list number, exact name, or COL-id.
- Only first 25 collections print in CLI; option 11 opens searchable Collection Home for large libraries.
- Knowledge Center has Collections and Home buttons.
- Collection Topic is separate from Source Search.
- Focused export labels DIRECT/RELATED and excludes INCIDENTAL/promo/intro/outro weak evidence.
- Put chatgpt_library_intelligence_result.json beside START.bat.
- Phase 6 -> Topic Collections -> 12 moves it to data\knowledge\phase6\chatgpt_intelligence\ and imports it.


PHASE6C FIX3
- Repairs Knowledge Center navigation/click handling.
- Video cards/titles and Ask Your Library evidence use the internal detail frame.
- Timestamp evidence opens the correct report route.
- Home navigation returns to Knowledge Center home.
- Category/channel/tag handlers are explicitly defined.
- /report/<video_id> local-server route is provided when needed.
- Removes the Python invalid-escape warning from the embedded JavaScript regex.


PHASE6C FIX4 UI REBUILD
-----------------------
Knowledge Center rebuilt from scratch, modeled on the supplied Slash Command Library UI:
dark responsive cards, sticky toolbar, category sidebar, visible Popular Tags,
global search and filters, clickable tags/categories/videos, Ask Library tab,
Collections tab, and an internal video/report viewer.
This removes the conflicting duplicate legacy JavaScript navigation functions.
Rebuild/open the dashboard after replacing the code.


PHASE6C FIX5 PREMIUM
--------------------
PREMIUM KNOWLEDGE CENTER
- Default light premium theme; optional Dark mode toggle.
- Softer background, white/slate cards, improved typography and spacing.
- Checkbox CSS fixed: checkboxes no longer inherit width:100%.
- Ask evidence rows and collection controls are aligned consistently.

CHATGPT -> PHYSICAL CATEGORY ORGANIZATION
- ChatGPT package now requires `video_updates`, one entry per VIDEO_ID.
- VIDEO_ID is copied exactly from the package and is the authoritative mapping key.
- Each video update can return approved English title, category, subcategory,
  primary topic, canonical tags, concepts, search questions, aliases and confidence.
- If a transcript is missing, ChatGPT is explicitly told to classify ONLY from
  title/channel/description/tags/metadata and mark classification_basis=metadata_only.
- Import automatically applies the per-video taxonomy and moves the physical folder to:
      downloads\<Category>\<Channel>\<Video Folder>
- Database file paths are rewritten after a move.
- Empty old channel/category folders are removed when safe.
- Phase 6 Collections menu option 13 can re-apply organization later.

CHATGPT RESULT LOCATION
- Fixed project-root bug: drop chatgpt_library_intelligence_result.json beside START.bat.
- Phase 6 -> Topic Collections -> 12 finds it, moves it to the intelligence folder and imports it.

MEDIA ONLY / ENTERTAINMENT MODE
Download New Videos -> 6
- Downloads the video/media first.
- Makes a separate best-effort English VTT request if subtitles are available.
- VTT failure does NOT fail/delete a successful video.
- No transcript processing, no Ollama, no ChatGPT, no chapters, no HTML report.
- Destination defaults to downloads\Entertainment\<Uploader>\...
- You can enter another category folder at run time.


V27 BROWSER CONTROL CENTER
- Browser is primary for Full Download, Media Only, Smart Resume, Metadata Scan,
  Knowledge Center, library indexes, Phase 5/6, embeddings, taxonomy, delete markers.
- CMD remains fallback for low-frequency advanced settings.
- Dedicated taxonomy export supports unclassified/all/new/test/channel/category.
- ChatGPT result is imported from beside START.bat and uses exact VIDEO_ID.
- Import updates taxonomy and moves physical folders to downloads\Category\Channel\Video.


V28 FULL GUI
------------
Browser additions:
- Clickable top stats.
- Download Status page with failed videos and captured reasons.
- Collections page with search, rename and delete. Deleting a collection does NOT delete videos.
- Main Menu button on every browser section.
- Knowledge Center stats are clickable and apply filters.
- ChatGPT File Exchange:
  * stage any local file into chatgpt_exchange\outgoing
  * open ChatGPT in a new tab for manual attachment
  * upload/read returned JSON/text into chatgpt_exchange\incoming
  * standard taxonomy JSON can then be imported with the existing taxonomy import workflow
- Browser exchange limit is 100 MB per file; previews are limited for large/binary files.

Direct automatic attachment into an already logged-in ChatGPT web session is intentionally not automated.
The localhost app cannot safely control the user's authenticated browser session without a separate browser-extension/automation architecture.

V29 STABILIZATION + FULL BROWSER GUI
====================================
Core runtime fixes:
- Added missing base64 and timedelta imports.
- Added LOGS directory constant; failure CSV and Open Logs now work.
- Fixed write_stage_error() to write error_text instead of undefined message.
- Failure dashboard reads failure_reason and last_error.
- Browser jobs run through one serialized queue, preventing urls.txt / CFG / RUNTIME collisions.
- Downloaded stat filtering now works in the Knowledge Center.
- Advanced Tools CLI number-to-action mapping corrected.

Browser-first GUI:
- Permanent sidebar plus Main Menu/Home access.
- Clickable Active / Downloaded / Failed / Last 7 Days / Favorites / Unwatched cards.
- Full Download and Media Only + optional VTT.
- Queue status, pause/resume, cancel queued jobs, retry failed jobs.
- Library browser and per-video detail/file-completeness view.
- Failure dashboard grouped by reason.
- Collections search / rename / delete.
- ChatGPT taxonomy exporter with all/new/unclassified/test/channel/category modes.
- ChatGPT File Exchange with result-type recognition.
- Direct import of incoming taxonomy result files.
- Taxonomy import validates VIDEO_ID/category and marks only successfully applied videos as processed.
- Folder organization is now Preview -> Apply -> Undo, with conflict rows not moved.
- System Health page and safe repair.
- Large set of Phase 0-6 / repair / audit / title / path tools available as GUI buttons.
- Key config settings editable from the GUI.
- Browser pages/API use no-cache headers.

Taxonomy transcript fallback:
If Phase 6 chunks are absent but a transcript file exists, the taxonomy package reads the transcript file directly. A video is marked MISSING only when no usable transcript text is available.

ChatGPT web-session note:
The local application can stage any file and inspect/import returned files. It does not automate attachment into an authenticated chatgpt.com tab. That requires separate browser automation/extension support or API credentials.


V29.1 TOOL SEARCH FIX
---------------------
- Fixed All GUI Tool Actions showing no results.
- Root cause: loadToolCatalog() existed but was never called when Tools / Settings opened.
- Tool catalog now loads on startup and whenever Tools / Settings is opened.
- Search matches tool label, backend action ID, and group name.
- Added result count and clear "No tools match" feedback.
- Expanded catalog to include all current non-interactive browser job actions.


V29.2 DELETE / PURGE FIX
------------------------
Dashboard "Mark Delete" no longer writes an empty .delete inside the video's folder.
That was unsafe for Media Only downloads because several videos may share one channel folder.

New flow:
1. Browser Mark Delete writes maintenance\delete_queue\<VIDEO_ID>.delete.json.
2. Process .delete Markers reads exact VIDEO_ID from that request.
3. Purge removes exact DB file paths plus files containing VIDEO_ID.
4. A whole directory is removed only when it is strongly owned by that VIDEO_ID.
5. SQLite rows are deleted from every table with current/legacy recognized video-ID columns.
6. Collection membership, Phase 5 search index, Phase 6 chunk index,
   ChatGPT intelligence and taxonomy-processed state are cleaned.
7. Failure/retry state is cleaned and video_list.csv is refreshed.
8. Successful queue requests are deleted. Failed requests stay queued for retry.

Legacy empty downloads\**\.delete files are still supported when VIDEO_ID can be
resolved from _data\.video_id, .video_id, a unique DB folder match, or [VIDEO_ID]
filename. If identity cannot be resolved, the marker is deliberately SKIPPED rather
than risking deletion of an entire shared channel folder.


V29.3 VISUAL DASHBOARD
----------------------
Merged the approved visual redesign into the actual local browser app.
The Dashboard itself now contains a one-page Menu Map & App Flow, Detailed Tool
Groups, Typical User Paths, Quick Access, and Help & Documentation.

The v29.2 delete/purge fix and its exact VIDEO_ID central delete queue are retained.


V29.4 DASHBOARD HELP
--------------------
Added inline 'What is covered here' explanations inside:
- Library Intelligence
- System Health


V29.5 LIBRARY ROOT / ZERO-STATS FIX
-----------------------------------
- Fixed Dashboard showing 0 when a new release is extracted into/next to the existing library.
- App now scores nearby candidate roots and auto-selects the root containing the real populated database/downloads.
- Supports explicit VLM_LIBRARY_ROOT / VIDEO_LIBRARY_ROOT environment override.
- Supports library_root.txt beside the release and optional config.json library_root field.
- Dashboard now displays the resolved Library Root, DB row count, media count and root source.
- If SQLite has zero rows but media exists, dashboard uses filesystem counts instead of showing an empty library and offers Build Recovery DB from Folders.
- Release ZIP no longer contains the smoke-test/blank video_library.db, preventing upgrades from overwriting a real database.
- Removed an obsolete duplicate dashboard_html definition from the source.


V29.6 JSON JOB FIX
------------------
Fixes browser request crashes after Phase 6 Health:
TypeError: Object of type WindowsPath is not JSON serializable

All browser API responses now safely serialize pathlib.Path and other common
diagnostic types. Job polling also returns compact summaries instead of sending
the complete heavy diagnostic result every two seconds.


V30 CONTROL TOWER
-----------------
- Source/official video category capture. YouTube categoryId + category title when API key is available; yt-dlp source categories fallback.
- Full Download can save comments to JSON + CSV.
- video_identity.json and video.url are saved alongside .video_id.
- Media Only now creates one VIDEO_ID-owned folder per video and can organize by source category or custom category; safe full-folder deletion works through exact VIDEO_ID delete queue.
- Library video details support local related-video cards and YouTube same-topic suggestions.
- Clip Studio merges selected local-library videos and URL clips using timestamp ranges.
- External / M3U / HLS / DASH downloader with separate external_media SQLite table.
- YouTube subscriptions collector: Selenium existing Firefox/Chrome/Edge profile when available, with yt-dlp :ytsubs browser-cookie feed fallback. Selenium view uses https://www.youtube.com/feed/channels.
- CLI prints ALL DOWNLOADS ARE DONE and returns to menu loops after download runs.


V30.1 AUDIT FIX
---------------
Post-v30 regression audit fixes:
- Full Download + Download Comments now downloads comments even when the video is already COMPLETE/Smart-Resume skipped.
- Final staging commit refreshes video_identity_file to the real final folder.
- Category/folder moves now update comments_file, video_identity_file and chatgpt_summary_file paths.
- Delete/purge path collection includes v30 comments/identity/ChatGPT path fields.
- External/M3U downloader no longer writes literal ".50s" in filenames.
- External downloader returns ok=false for empty URL input.
- video_list.csv now exports Source Category ID, Source Category, YouTube Category,
  Comments Saved, Comments File, and Video Identity File.
- Media Only CLI no longer prints the completion banner twice.
- YouTube subscription CSV/UI fills a dominant category when the same channel already
  exists in the local library and has source/library category information.


V30.2 COMMENT INTELLIGENCE
--------------------------
Comments now produce raw JSON/CSV plus:
- <VIDEO_ID>.comments_all.txt
- <VIDEO_ID>.comments_chatgpt.txt
- <VIDEO_ID>.comments_meaningful.json

The ChatGPT transcript keeps meaningful questions, experiences, corrections,
caveats, specific details and substantive discussion while filtering duplicates,
generic reactions, emoji-only comments and obvious promotion/spam.

Meaningful comments are added to HTML reports and FULL/FOCUSED ChatGPT collection
packages. Viewer comments are always labeled as audience-generated, not verified facts.

Existing raw comments can be upgraded using:
Intelligence or Tools / Settings -> Rebuild Comment Intelligence.

V30.3 SEPARATE CONTROL TOWER
----------------------------
- Normal operational dashboard restored as the main / page.
- Design 13 / Control Tower moved to /control-tower.
- Control Tower is a separate visual/navigation page and does not replace workflows.
- All v30.2 features remain available in their normal menu pages.


V30.4 KNOWLEDGE / SELENIUM / STOP
---------------------------------
Knowledge Center:
- /knowledge was never removed.
- Direct Knowledge Center navigation is restored in the main header/top navigation,
  Main Dashboard and Design 13 Control Tower.

Selenium:
- Subscriptions collector checks Selenium automatically.
- If missing, installs first to tools/python_packages (portable/no-admin).
- If portable target installation fails, tries pip --user.
- Browser UI also provides Check Selenium and Check + Install Selenium buttons.

YouTube Subscriptions progress:
- Selenium scan prints: scan X/60 + unique channel count.
- Dashboard Subscriptions page shows the running count.
- yt-dlp browser-cookie fallback streams/parses channel records and reports count.
- Selenium page load/script timeouts and a 5-minute fallback timeout reduce silent hangs.

STOP EVERYTHING:
- Always-visible red button on Main Dashboard and Design 13.
- Cancels queued jobs.
- Sets the original application STOP flag used by existing Python loops.
- Sets a browser stop event.
- Terminates tracked yt-dlp/ffmpeg/pip/etc subprocesses.
- Closes active Selenium WebDrivers.
- New explicitly started jobs clear the previous stop state.

V30.5 LAYOUT / KNOWLEDGE CENTER FIX
-----------------------------------
- Control Tower restored from v30.3 with a class-safe function boundary.
- No Handler/routes are overwritten during Control Tower restoration.
- Same Control Tower geometry; final Quick Access row opens Knowledge Center.
- Knowledge Center has Back to Video Main Dashboard and Control Tower.
- Video cards use robust /video-view/<VIDEO_ID>.
- Stale report/media paths are resolved from the current video folder.
- Missing report falls back to local media instead of a dead link.


V30.6 MAIN LAYOUT / KNOWLEDGE LINKS / SELENIUM FIX
---------------------------------------------------
MAIN LAYOUT
- / is now the Design 13 Control Tower layout from the supplied image.
- /app is the full operational dashboard.
- Control Tower appearance remains the v30.3 reference design; only click targets changed.
- Dashboard/Downloads/Library/etc navigate to /app?tab=...
- Existing Find knowledge and Knowledge Layer areas open /knowledge without adding new visual cards.

KNOWLEDGE CENTER VIDEO LINKS
- Thumbnail, title and Open Video are now real href links, not only JavaScript click handlers.
- Phase 5 saved index is reconciled with the current videos DB before rendering.
- Stale/deleted VIDEO_ID rows are excluded.
- Current report/folder/personal-state fields are refreshed from SQLite.
- /video-view/<VIDEO_ID> remains available for the in-center iframe.
- Back to Video Main Dashboard returns to /.
- App Workspace button opens /app.

SELENIUM
- Added browser executable discovery and profiles.ini/Chromium profile discovery.
- Added profile-lock detection.
- Locked Firefox/Chrome/Edge profiles are copied to a temporary app-owned profile
  with login/session data so the browser can be launched without profile-in-use errors.
- Added Selenium preflight and Run Selenium Diagnostic UI.
- Collector reports stage-by-stage CMD progress and exact Selenium errors.
- Selenium scan uses broader YouTube channel DOM selectors.
- 180-second Selenium watchdog.
- yt-dlp :ytsubs remains best-effort fallback and now tries a specific browser profile first.
- Empty collection is a FAILED job with the actual Selenium/fallback reason instead of silent success.


V30.7 RESTORE FLOW / FUNCTIONS
------------------------------
Design 13:
- HOW THE APP WORKS now has a shallow blue connector arc like the supplied reference.
- All 10 numbered workflow steps are clickable.
- Typical User Paths A/B/C are clickable.
- All Systems Operational opens Health.
- Studio project placeholder rows open Collections rather than being dead controls.
- Library / Reports / Exports opens Library.

Operational dashboard:
- Restored Rebuild Resume Queue.
- Restored ChatGPT Folder Move Preview.
- Restored File Exchange send / receive / exchange history.
- Restored Reports / Exports controls.
- Restored Phase 0 Self-Test while retaining Phase 6 Health.
- Restored full Failure / Resume Maintenance.
- Restored Titles / Paths / Delete controls.
- Restored Phase 6 / Folders controls.
- Restored Configuration Files and editable Settings.


V31.0 STABILITY RESET
---------------------
- Knowledge Center now starts from CURRENT SQLite videos. Phase 5 only enriches them.
- Stale/missing Phase 5 data cannot hide a valid library video.
- Selenium always launches from a disposable copied browser profile.
- Full App Diagnostics shows the exact library root/database/tool/Selenium state.
- Dedicated workflows are visible in All GUI Tool Actions and navigate to the correct page.
- START.bat can start the browser directly; START_WEB.bat is also included.


V31.1 STARTUP HOTFIX
--------------------
Critical fix: v31.0 accidentally lost the top-level `if __name__ == "__main__": main()` entrypoint while main() was patched. As a result, app.py compiled but exited immediately, so the browser server and CMD menu never started.

Additional startup hardening:
- configured port can fall back to the next free localhost port
- actual selected port is printed
- START.bat supports Browser / CMD / Diagnostics
- Python launcher falls back from python to py -3
- START_DIAGNOSTICS.bat added


V31.2 CMD COMPLETION STATUS
---------------------------
Every asynchronous dashboard job prints:
  DASHBOARD COMMAND QUEUED
  DASHBOARD COMMAND STARTED
  DASHBOARD COMMAND COMPLETED SUCCESSFULLY
or a FAILED / CANCELLED banner.

Each banner contains command name, job ID, duration and a compact result/error.
Portable Metadata Backup is covered by this global job lifecycle.

Direct synchronous POST commands such as Settings, taxonomy import/export/apply/undo,
collections, file exchange and delete markers also print completion/failure.

Background GET polling is intentionally silent to avoid flooding CMD.


V31.3 ONE-CLICK OLD LIBRARY RECOVERY
------------------------------------
New Diagnostics button:
  ONE-CLICK RECOVER + REBUILD EVERYTHING

Intended for:
- ChatGPT packages reporting "missing from SQLite".
- Accidentally replaced/reset/empty video_library.db.
- Existing downloaded video folders not represented in SQLite.

Recovery order:
1. Portable metadata safety backup.
2. Raw current DB snapshot.
3. Discover likely old/current library roots.
4. Find old video_library.db files and DBs inside metadata backup ZIPs.
5. Merge missing DB rows and recover physical _data/.video_id folders.
6. Repair .video_id markers.
7. Repair SQLite folder/media/report paths.
8. Repair original-title markers.
9. Repair broken HTML links.
10. Repair missing reports.
11. Rebuild comment intelligence.
12. Rebuild CSV + logical indexes.
13. Rebuild Phase 5 Knowledge Center.
14. Rebuild Phase 6 chunks/embeddings/health.
15. Reconcile Smart Resume + final library/core audits.

Safety rules:
- The current DB is backed up before changes.
- Old DB files are MERGED; they never replace the current DB.
- Existing rows are not overwritten. Blank fields may be filled.
- No video deletion, purge or quarantine is run.
- A JSON recovery report is written under maintenance/recovery.


V31.4 COMBINED EMPTY-FOLDER CLEANUP
-----------------------------------
Visible dashboard cleanup has been simplified to one button:

  Clean All Empty Folders

It combines:
1. Clean Empty Staging
2. Remove Empty Legacy ChatGPT Folders
3. Remove All Empty Library Folders

Remove All Empty Library Folders scans downloads recursively, deepest-first, and removes
only directories that are truly empty. It never removes DOWNLOADS itself, skips symlinks,
and leaves the _staging subtree to the dedicated staging cleanup.

The old individual backend actions remain available internally for compatibility, but the
dashboard/tool catalog shows the single combined action instead.


V31.5 HELP / COMMAND GUIDE
--------------------------
New page:
  http://127.0.0.1:<port>/help

The Help / Command Guide documents dashboard commands in normal app-flow order:
Setup -> Download -> Library structure -> ChatGPT -> Knowledge/AI -> Library use
-> Health/Recovery -> Failure cleanup -> Delete -> Specialist tools/queue.

Each row shows:
- Command
- What it actually does
- Whether it changes files/data
- When to use it

The page has search, impact filtering, stage navigation and Print / Save PDF.
A Help / Commands button was added to the normal App Workspace header/top navigation.
No existing command was removed.


V31.6 BUTTON HOVER HELP
-----------------------
Every App Workspace button now receives contextual help.

Desktop:
- Hover a button to see a detailed floating help card.
- Keyboard focus also displays the card.

Touch / click:
- Tap/click the small "i" badge inside a button to pin the help card.
- Click X, press Esc, or click elsewhere to close it.

The card shows:
- What the button actually does
- Changes files/data?
- Impact badge: READ ONLY / UPDATES DATA / CLEANUP / DESTRUCTIVE
- When to use it
- View full help -> links directly to that command row on /help

The /help page and dashboard hover cards share the same central metadata source.
The Help page now includes Navigation & Interface Controls and supports direct anchors
such as /help#cmd-reconcile_failures.

No dashboard function was removed and no dashboard layout was redesigned.


V31.7 WORKFLOW CONSOLIDATION
----------------------------
Normal dashboard/help/tool-catalog/CMD menu surfaces now present connected master workflows
instead of scattered constituent commands. The original backend functions remain in app.py
for compatibility and targeted troubleshooting.

New master workflows:
- Repair & Refresh Library Core
- Full Library Health & Path Audit
- Original Title Integrity Audit
- Migrate & Modernize Library Structure
- Smart Resume — Audit, Repair & Sync
- Phase 2 Package Integrity & Completeness Audit
- Create ChatGPT Packages & Tag Cleanup
- Import, Validate & Extract ChatGPT Results
- Apply ChatGPT Updates & Organization Moves
- Knowledge & AI — Build, Verify, Ask & Find
- Repair HTML Reports & Video Links
- Full System Health Check, Backup & Safe Repair
- Repair & Clean Failure History
- Clean Temporary, Resolved & Empty Files/Folders

The Video-ID Artifact Registry now refreshes automatically after Full Download, Media Only,
and download_stage/Smart Resume completion.

/help is ordered by connected application flow and documents the consolidated commands.


V31.8 UI / QUEUE / HELP NAVIGATION
-----------------------------------
- DETAILED TOOL GROUPS now also lists Collections, Intelligence, Health, Diagnostics,
  Tools, Clip Studio, Streams and Subscriptions.
- A live queue widget is at the bottom of DETAILED TOOL GROUPS.
- The right Studio queue is live too; static placeholder queue entries were removed.
- Failures tab uses a stacked full-width layout.
- Every Help command name is clickable and safely navigates to/highlights the command.


V31.9 TAB RENDER FIX
--------------------
Fixed the actual cause of the blank App Workspace tabs.

The ChatGPT section was missing its closing </section> tag. Because of that,
Collections, Intelligence, Health, Diagnostics, Tools, Clip Studio, Streams
and Subscriptions were all nested inside ChatGPT in the browser DOM.

When one of those tabs was selected, the child section became active but its
ChatGPT parent remained hidden, making the selected tab look completely empty.

V31.9 closes ChatGPT before Collections so all App Workspace sections are
top-level siblings and can be shown independently.


V31.10 ALL BUGFIXES
-------------------
- Truthful SUCCESS / WARN / FAILED dashboard job completion.
- Complete browser Collections controls: create/add, rename, delete, full/focused export.
- Collection names with apostrophes/quotes no longer break dynamic buttons.
- Favorite / Watched / Rating / Archive controls in Video Details.
- Queue Manager with Pause, Resume, Cancel Selected, Retry Selected and history.
- Better Help-to-command targeting for real UI controls.
- Browser-visible no-admin installer for missing yt-dlp, FFmpeg/ffprobe, Deno and
  youtube-transcript-api; third-party binaries remain outside the release ZIP.
- Diagnostics direct missing-core-tool warnings to that installer.
- START.bat / START_WEB.bat / START_DIAGNOSTICS.bat version labels updated.
