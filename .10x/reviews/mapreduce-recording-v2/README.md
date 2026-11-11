# MapReduce status recording, v2

Replaces the cropped 900 × 640 dark-only clip with full-page light and dark takes.

- Source: Exios66/MapReduce-Reloaded at `def9c62`, built with `go build ./cmd/...`.
- Cluster: one coordinator (`-addr 127.0.0.1:7070 -http 127.0.0.1:18780`) and four workers
  (`-listen`/`-advertise 127.0.0.1:7171…7174`), one slot each, on one 4-core Linux VM.
- Input: `bench/gen-weblog.py 1074372493` (1,075,197,804 bytes, seed default).
- Job: `mr submit -m 32 -r 4 -wait examples/wordcount.go`; result in `job-result.txt`
  (SUCCEEDED, 32/32 map, 4/4 reduce, 67.8 s, 5 backups started, 0 won).
- Capture: `capture.cjs`, Playwright Chromium, viewport 1200 × 760 at 2×, full-page
  screenshot of the server-rendered page every 1.5 s in each colour scheme, 52 frames each,
  six held after the job ended. No frame was drawn or edited; frames were cropped to the
  page content (2400 × 1160) only.
- Encoding: 6 frames/s (about 9× real time), last frame held 3 s, scaled to 1600 px wide,
  H.264 CRF 20, `+faststart`. Light 282 KB, dark 261 KB. Posters are frame 20.
- The status page shows host `vm` (the VM's hostname) and wall-clock times; nothing private.

Screenshots: the site page at 1280, 768 and 375 px, light and dark.
