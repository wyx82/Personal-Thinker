# Prompt → Personal Dash: loghează poziția SPCX (HOLD)

*(copiat din Personal Thinker, 2026-11-05 — de trimis ca atare în sesiunea Personal Dash)*

---

Adaugă în dashboard o poziție nouă pe **SPCX (SpaceX)**, tip **HOLD**, în contul IBKR.

**Datele poziției** (de la Dez, raportate pe 2026-11-05):

| câmp | valoare |
|---|---|
| ticker | `SPCX` |
| ticker_full_name | `SpaceX` |
| quantity | `8.0788` acțiuni |
| buy_price (mediu) | `123.9039` |
| total_cost | `1000.99` USD |
| preț curent | `123.79` → valoare de piață `1000.07` USD, P/L necompensat `−0.92` USD (−0,09 %) |
| buy_date | `2026-11-05` ⚠️ **presupunere** (vezi „De verificat") |
| status | `OPEN` |
| fee_rate | `0.001` ⚠️ **valoarea de platformă, nu măsurată** |
| notes | `HOLD — poziție deținută pe termen lung, fără target și fără stop. Re-intrare după poziția închisă pe 07.08.2026 (8 acțiuni @ $123,70, vândute la $127,52, +4,2%).` |

**Ce să faci, în ordine:**

1. Citește `CLAUDE.md` (deploy rules) și urmărește precedentul **`scripts/log-iren-2026-10-12.ts`** — e exact același tip de operație (dry-run implicit, `--apply` pentru commit, math-check înainte de insert, readback după).
2. **Citește starea curentă** înainte să scrii ceva: `stock_positions` și `stock_account`.
   - Atenție: există deja o poziție SPCX **închisă** (din iulie–august) — **nu o modifica și nu o dubla**. Poziția nouă e un rând `OPEN` distinct, cu `position_number` = următorul liber.
3. Scrie `scripts/log-spcx-hold-2026-11-05.ts` în același tipar: citește pozițiile existente (pentru `position_number`), face math-check (`buy_price × quantity` vs `total_cost` — aici: 123.9039 × 8.0788 = 1000.9948, deci `total_cost` = 1000.99 e rotunjit, **nu include comisioane**), apoi inserează cu `id = crypto.randomUUID()`, `status = 'OPEN'`, `sell_date`/`sell_price`/`total_revenue`/`profit` = NULL.
4. **Updatează `stock_account.current_stock_price` = `123.79`.** Din acest câmp `StocksSummary` ia prețul de afișare și calculează P&L-ul pozițiilor deschise (`calcOpenPnL`) — fără el, cardul SPCX arată P/L 0.
5. **NU** atinge `holdings.stocks_amount` / `holdings.stocks_value_usd`: totalul „Stocks" din Holdings se derivă din pozițiile `OPEN` (`HoldingsSummary.tsx`), nu din coloanele alea.
6. Rulează **pe VPS** (better-sqlite3 e Linux-only, local nu merge):
   `npx tsx scripts/log-spcx-hold-2026-11-05.ts` → verifică output-ul dry-run → `--apply` → readback.
7. Nu e nevoie de build/deploy pentru un insert pur de date. Dacă se atinge codul, deploy **doar** prin `bash /root/Personal-Dash/deploy.sh` (niciun `pnpm build` / `pm2 restart` manual).
8. Verificare finală: în interfață, poziția SPCX arată valoare `1.000,07` și P/L ≈ `−0,92`; `stock_positions` are un rând `OPEN` nou, cu `position_number` corect, și poziția veche SPCX rămâne neatinsă.

**Limitare cunoscută a platformei (notează-o, nu repara acum):** modulul Stocks are un singur câmp `current_stock_price` pentru toate acțiunile, iar `StocksSummary` calculează P&L-ul tuturor pozițiilor deschise cu același preț. Cu NKE, IREN și SPCX deschise simultan, P/L-ul total e amestecat (fiecare ticker ar avea nevoie de prețul lui).

**De verificat cu Dez înainte de commit (le-am întrebat, nu au răspuns):**
- data reală a intrării — am pus 2026-11-05, ziua raportării;
- dacă cele 8,0788 acțiuni provin din mai multe fill-uri (numărul fracționar și costul marcat „~") și care e comisionul real;
- dacă `fee_rate` 0,001 e valoarea corectă pentru IBKR sau trebuie alta.
