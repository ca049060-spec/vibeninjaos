# Manual test recipe: expense log, GST/HST calculator, invoice

This is the manual test for pull request 4, branch `cursor/smb-bookkeeping-tools-1ba1` (commit `f13e73cc5324c2fe3153a023a857413d8010dd4b`). It covers the expense and mileage log, the GST/HST calculator, and Simple Invoice.

The three apps are single HTML files. Styles and scripts are inline. They use the system font stack. Nothing in those files calls `fetch`, `XMLHttpRequest`, or `sendBeacon`. Saved entries and the invoice draft go to `localStorage`.

`python3 scripts/build.py --check` passes on this commit. A real iPhone, a real Android phone, and Excel were not available where this recipe was written, so the phone, airplane-mode, Excel, and print-to-PDF steps below are for a person with those devices. Do not deploy this branch, and do not change Netlify settings.

## Setup

From a checkout of this branch, at the repository root:

```
python3 scripts/build.py --check
python3 -m http.server 8765 --bind 0.0.0.0
```

`--check` must exit 0 before you test. `python3` is the interpreter to use. This environment does not provide a `python` command.

On the phone, open `http://<computer-lan-address>:8765/...`. The phone and the computer have to be on the same network for that to work. Airplane mode comes later, after each app has loaded.

## 1. Real phones: iOS Safari and Android Chrome

Run this whole section twice: once in Safari on an iPhone, once in Chrome on an Android phone.

### 375px layout

Check the layout at 375 CSS pixels wide.

- An iPhone SE-class phone is 375 CSS pixels wide, so the physical phone is the viewport.
- On a wider phone, also set a 375 CSS-pixel viewport: Safari Responsive Design Mode, or Chrome device mode, at 375 by 700. The airplane-mode check still happens on the physical phone.

Open each of these and confirm the page does not scroll sideways, fields and buttons stay on screen, and text is not cut off:

- `/`
- `/tools/`
- `/tools/gst-hst/` and `/tools/gst-hst/app/`
- `/tools/invoice/` and `/tools/invoice/app/`
- `/tools/expense-log/` and `/tools/expense-log/app/`

On the home page and the catalog, open the menu and close it. On each app, change a field and confirm the result or the preview updates without the page jumping sideways.

### Airplane mode

The goal is to show that using the three apps does not make network calls.

Load these while the phone is online, and wait until each page is visible:

- `/tools/gst-hst/app/`
- `/tools/invoice/app/`
- `/tools/expense-log/app/`

Then turn airplane mode on. Leave Wi-Fi off. Do not reload yet.

While the radio is off:

1. On the calculator, leave "Price before tax" selected, type `100`, and switch between Ontario and Quebec. Ontario must show a total of $113.00. Quebec must show GST $5.00, QST $9.98, and a total of $114.98. The numbers must update with no error about being offline.
2. On the log, add an expense for today: who you paid `Test`, amount `12.00`, what it was for `Fuel`. It must appear in the list.
3. On the invoice, set the business name to `Test Co`, add a line with description `Labour`, quantity `1`, price `10.00`, and leave the rate on Ontario. The preview total must update.

Do not tap these during the offline check. They are ordinary links, and they are supposed to fail with the radio off:

- Any `canada.ca` link (the GST/HST rates link on the calculator and the invoice, and the automobile allowance rates link on the log).
- The "About" link in each app header, which goes to another page on this site.
- "Use on an invoice" on the calculator, which goes to `/tools/invoice/app/`.

Reload each app with airplane mode still on. Record the result. A reload asks the browser for the HTML file again. If that file is not in the browser cache, the reload fails. That failure is the browser fetching the page, not the tool calling a data API. Using the already-open page in the three steps above is the proof that the tool itself made no further request.

Stronger proof, when you can attach a debugger: Safari Web Inspector for the iPhone, or `chrome://inspect` for Android. Open the Network panel, then repeat the three offline actions. Expect no new requests. A reload is a request for the page URL and does not count as the tool sending data.

### What else on this branch still contacts the network

The generated pages around the apps (home, catalog, and each tool's about page) still include the Google Fonts stylesheet that `scripts/build.py` inserts: `fonts.googleapis.com` and `fonts.gstatic.com`. Loading those pages requests Google. The three app URLs do not. A separate change for `main` removes that stylesheet. This branch does not contain that change, so an offline reload of `/` or `/tools/gst-hst/` can fail for that reason even when the app page is fine.

Visiting the site at all means the computer serving it sees the request (the page URL, and the usual connection data). On a local `http.server` that computer is yours. There is no analytics snippet in these apps.

## 2. Excel round-trip of `expense-mileage-log.csv`

Open `/tools/expense-log/app/`. The download button is "Download CSV of this list". The file name is `expense-mileage-log.csv`. The file contains the entries in the current filter, not necessarily every entry ever saved. The default filter is "This month". Click **All** before you download, or the January and March rows below will be missing.

The file is UTF-8, starts with a byte-order mark, and uses CRLF line endings. Text columns are `date`, `kind`, `category`, `payee`, `description`, `from`, `to`, and `note`. If one of those values starts with `=`, `+`, `-`, `@`, a tab, or a carriage return, the file prefixes an apostrophe so a spreadsheet keeps the cell as text. `amount_cad`, `kilometres`, `rate_per_km_cad`, and `mileage_amount_cad` are written as numbers, with no apostrophe.

Enter these three entries. Leave the category on Supplies. Click **All** if the view has not already switched there, then download.

1. Expense. Date `2026-03-15`. Who you paid `=1+1`. Amount `18.40`. What it was for `+café`. Note `-déjà`.
2. Expense. Date today. Who you paid `Renée Été`. Amount `12.00`. What it was for `Café Montréal`. Note `@note`.
3. Trip. Date `2026-01-15`. From `Québec`. To `Montréal`. Kilometres `8.5`. Leave dollars per kilometre empty. What it was for `=SUM(A1)`. Note `+follow`.

Saving a date outside the current month switches the on-screen filter to All. That is expected. Still click **All** yourself before the download so the file is not dependent on that switch.

### Columns

Open the downloaded file in a text editor before Excel touches it. The header must be this, in this order:

```
date,kind,category,payee,description,from,to,amount_cad,kilometres,rate_per_km_cad,mileage_amount_cad,note
```

Rows are sorted by date, earliest date at the top. For a download made on 2026-11-20 the body is:

```
2026-01-15,trip,,,'=SUM(A1),Québec,Montréal,,8.5,,,'+follow
2026-03-15,expense,Supplies,'=1+1,'+café,,,,18.40,,,'-déjà
2026-11-20,expense,Supplies,Renée Été,Café Montréal,,,,12.00,,,'@note
```

If today's date is not 2026-11-20, the third row uses that date instead and the row moves so the dates stay in ascending order. The other cells stay as written. `18.40` and `12.00` have no leading apostrophe. `8.5` has no leading apostrophe. The rate and mileage amount on the trip are empty because the rate was left empty.

### Excel

Open `expense-mileage-log.csv` in Excel (Windows or Mac).

- Twelve columns, with the header names above.
- The payee `=1+1` displays as the characters `=1+1`, not as the number 2. The formula bar may show a leading apostrophe. It must not evaluate.
- `+café` displays as `+café`, not as a formula error.
- `-déjà` displays as `-déjà`, not as a number.
- `@note` displays as `@note`.
- The trip's "what it was for" cell displays `=SUM(A1)`, not a calculated sum.
- `Renée Été`, `Café Montréal`, `Québec`, and `Montréal` keep their accents. If Excel shows mojibake, the failure is Excel's import: the text-editor copy from the previous step must still contain those characters. The file starts with a UTF-8 byte-order mark for this reason.
- Date cells are 15 January 2026, 15 March 2026, and today. Excel may show them as dates rather than as `YYYY-MM-DD` text. The calendar day must be that day. If Excel shifts a date by one day, record that as an Excel import quirk and confirm the text-editor copy still has the exact `YYYY-MM-DD` text.
- `amount_cad` for the March row is the number 18.40. `kilometres` for the trip is the number 8.5.

Save a copy from Excel as "CSV UTF-8", close it, and open that saved file again in Excel and in a text editor.

- The cells that started as `=1+1`, `+café`, `-déjà`, `@note`, and `=SUM(A1)` must still display as those characters, not as a calculated result.
- The accented names must still be readable.
- The three dates must still be the same calendar days.
- Excel's own save may drop the leading apostrophe or add quotes. That is Excel rewriting the file. The tool's guarantee is the file it downloaded, which the text-editor check covers. The round-trip fails if Excel shows a calculated value, loses the accents, or moves a date off the calendar day you typed.

## 3. GST/HST spot checks against the in-code rates

Open `/tools/gst-hst/app/`. Leave "Price before tax" selected. Type `100` or `100.00`. Press Enter in the amount field. The page must stay on the calculator, and the address bar must not gain a query string.

For each province and territory, the result must match the `PROVINCES` table in `tools/gst-hst/app/index.html`. Rates there are parts per 100000 (`5000` is 5%, `9975` is 9.975%, `14000` is 14%). Tax cents are `Math.floor((cents * parts + 50000) / 100000)`. For a $100.00 price before tax, that is 10000 cents.

| Code | Place | What $100.00 before tax must show |
| --- | --- | --- |
| AB | Alberta | GST $5.00. Total $105.00. The line "No separate provincial sales tax." |
| BC | British Columbia | GST $5.00, PST $7.00. Total $112.00. |
| MB | Manitoba | GST $5.00, RST $7.00. Total $112.00. |
| NB | New Brunswick | HST $15.00. Federal part of the HST $5.00. Provincial part of the HST $10.00. Total $115.00. |
| NL | Newfoundland and Labrador | Same figures as New Brunswick. |
| NT | Northwest Territories | GST $5.00. Total $105.00. "No separate provincial sales tax." |
| NS | Nova Scotia | HST $14.00. Federal part $5.00. Provincial part $9.00. Total $114.00. |
| NU | Nunavut | GST $5.00. Total $105.00. "No separate provincial sales tax." |
| ON | Ontario | HST $13.00. Federal part $5.00. Provincial part $8.00. Total $113.00. |
| PE | Prince Edward Island | Same figures as New Brunswick. |
| QC | Quebec | GST $5.00, QST $9.98. Total $114.98. |
| SK | Saskatchewan | GST $5.00, PST $6.00. Total $111.00. |
| YT | Yukon | GST $5.00. Total $105.00. "No separate provincial sales tax." |

The "General rates" list on the same page must show the same percentages the code formats with `rateText`: GST 5%, HST 13%, HST 14%, HST 15%, PST 7%, RST 7%, PST 6%, QST 9.975%.

Simple Invoice copies the same `PROVINCES` array in `tools/invoice/app/index.html`. You do not need to repeat all 13 places there. Section 4 checks Ontario. If you change the invoice rate menu, each place's label must name the same taxes as this table (for example Quebec is GST 5% + QST 9.975%).

The page says it uses the general rate, and that it is not tax advice. The spot check compares the screen to the table in the source file. It does not check place-of-supply rules, exemptions, or special rates such as liquor.

## 4. Invoice print-to-PDF

Open `/tools/invoice/app/` on the phone and, separately, at a 375 CSS-pixel width.

Fill in:

- Business name: `Atelier Côté`
- Business address: one street line, so you can see it on the sheet
- Customer name: `Musée Café`
- Invoice number: `100`
- Date: leave the date the page filled in (today)
- Due date: leave it empty
- One line: description `Seal coat`, quantity `2`, price `95.00`
- Rate: `Ontario — HST 13%`
- Leave "Prices already include this tax" unchecked

The preview must show:

- `2 × $95.00` and `$190.00` on that line
- Subtotal `$190.00`
- `HST 13% (5% federal + 8% provincial)` `$24.70`
- Total `$214.70`

That is the same rounding as the calculator: 2 times 9500 cents is 19000 cents, and 13% of that rounds to 2470 cents.

Reload the page. The business name, customer, line, and Ontario rate must still be there. The draft is stored under the localStorage key `vibeninjaos.invoice.v1`.

Tap **Print or save PDF**.

- The print preview hides the form, the top bar, and the bottom bar (those elements use the class `no-print`).
- The invoice sheet remains, with `Atelier Côté`, `Musée Café`, the seal-coat line, HST $24.70, and total $214.70.
- The empty due date does not print a due line.
- Choose Save as PDF (on iOS, use the share sheet in the print dialog and pick Save to Files; on Android Chrome, pick Save as PDF in the print destination).
- Open the PDF. The same names and figures must be readable, including the accents. The form fields, the rate menu, and the Print button must not be in the PDF.

## 5. Resolving the conflict when pull request 4 is merged into main later

Do not do this against `main` itself, and do not push the result to `main`. Pull request 4 is conflicted with current `main`. The steps below are what to run on a throwaway branch when someone is ready to land it. This test branch does not perform that merge.

Checked on 20 November 2026 against `origin/main` at `1c02b510749b9e4c2e59a9d5a01fe41482397c93` and `origin/cursor/smb-bookkeeping-tools-1ba1` at `f13e73cc5324c2fe3153a023a857413d8010dd4b`.

`git merge-tree` and a detached worktree merge both reported a content conflict in `index.html` and in no other file. `tools/index.html` and `sitemap.xml` auto-merged. The three new tool folders came in as additions. Pull request 4 does not change `scripts/build.py`, so the merge keeps `main`'s build script.

Both sides rewrote `index.html` after the common ancestor. `main` has the QuickQuote landing page. The bookkeeping branch still has the older home page, plus a generated "Ready now" block that lists the three tools. Keeping the bookkeeping copy of `index.html` would drop the current landing page. Keeping `main`'s copy drops the generated cards until `scripts/build.py` writes them back.

From a clean fetch, on a new branch that starts at current `main`:

```
git fetch origin
git checkout -b resolve-bookkeeping-tools origin/main
git merge --no-ff origin/cursor/smb-bookkeeping-tools-1ba1
```

Git stops on `index.html`. Confirm there is no other unmerged path:

```
git diff --name-only --diff-filter=U
```

That must print `index.html` and nothing else. If it prints another path, stop and look at that file. Do not assume the steps below still fit.

Keep `main`'s home page. In this merge, ours is `main` because the branch started there:

```
git checkout --ours index.html
git add index.html
python3 scripts/build.py
python3 scripts/build.py --check
```

`--check` must exit 0.

What that build did in the worktree check:

- It rewrote the `site:featured` block. The home page then listed Local Market Report, GST/HST Calculator, Simple Invoice, and Expense & Mileage Log. QuickQuote stayed in the hero and was absent from that generated grid, which is what `main`'s `scripts/build.py` does.
- The hero text from `main` was still there: "Simple tools for small business, on your phone."
- It rewrote `tools/gst-hst/index.html`, `tools/invoice/index.html`, and `tools/expense-log/index.html` onto the current page template. The copies on the bookkeeping branch were generated by an older template, so those three about pages are expected to change when the build runs.
- `tools/index.html` and `sitemap.xml` already matched the build after the auto-merge, so they were not rewritten. The sitemap contained `/tools/gst-hst/`, `/tools/invoice/`, and `/tools/expense-log/`. If `--check` reports either file out of date, let the build write it. Do not hand-edit the generated blocks.

Review `git diff`, commit the merge on `resolve-bookkeeping-tools`, and open a pull request into `main`. Do not push that branch onto `main`.

The worktree used for this check was deleted without committing and without pushing.

If `main` later contains the self-hosted font change, use the same commands. Keep that newer `index.html` with `git checkout --ours`, then run `python3 scripts/build.py` so the three new about pages pick up `main`'s head, including the font files under `/fonts` and with no Google Fonts link.
