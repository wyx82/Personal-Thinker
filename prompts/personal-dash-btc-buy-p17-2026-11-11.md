# Prompt → Personal Dash: loghează poziția BTC P17 (0,26522 BTC @ 71.670) + reconciliere USDC

*(copiat din Personal Thinker, 2026-11-12 — de trimis ca atare în sesiunea Personal Dash)*

---

## 1. Tranzacția (sursa: istoricul Binance, raportat de Dez)

| câmp | valoare |
|---|---|
| moment | `2026-11-11 11:02:23` (ora României, EET = UTC+2) |
| pereche | BTC/USDC |
| tip | Limit Buy — **Filled** |
| preț | `71.670,00` USDC |
| cantitate | `0,26522` BTC |
| total | `19.008,3174` USDC |
| fee | `0` (se plătește în BNB, nu din USDC) |
| sursă | Binance (exchange) |

**Math-check:** `71.670 × 0,26522 = 19.008,3174` — exact, fără fee dedus. Același tipar ca P15/P16: `totalCost = buyPrice × quantity`.

**Etichetă:** `P17` în conversație. În DB va fi `position_number = 18` — numerele „P" din conversație rămân cu unu în urmă față de DB (precedent: scriptul din 10.11 a creat DB #17 = P16). **Citește `MAX(position_number)` din DB și folosește valoarea reală, nu 18.**

## 2. Ce ai de făcut (2 lucruri, în ordine)

1. **Reconciliază** soldul USDC din ledger cu cel real de pe Binance (§4) — fără asta tranzacția pică pe verificarea de fonduri.
2. **Loghează poziția P17** și recalculează tot ce depinde de ea: holdings, contul de trading, prețul curent BTC, P/L ne-realizat.

## 3. Numerele așteptate la final (sanity-check, nu sursă de adevăr — DB-ul e sursa)

| metric | valoare |
|---|---|
| BTC deținut | `1,73417` BTC |
| Cost basis BTC (OPEN) | `≈ 140.864,16` USDC |
| Preț mediu de intrare | `≈ 81.228,57` USDC/BTC |
| USDC disponibil | `= soldul real de pe Binance` (vezi §4) |
| USDC nou | `19.008,3174` |

Preț BTC live la momentul redactării: **71.244,70** (24h: −3,11%; high 74.742,30 / low 71.181,32). La prețul ăsta:

| poziție | P/L ne-realizat |
|---|---|
| P14 (1,2 BTC @ 84.880) | `−16.362,36` |
| P15 (0,13234 @ 75.562,85) | `−571,46` |
| P16 (0,13661 @ 73.200) | `−267,11` |
| **P17 (0,26522 @ 71.670)** | **`−112,80`** |
| **total** | **`≈ −17.313,74` USDC (`−12,29%`)** |

## 4. Problema USDC — nu o ocoli

Ledger-ul arată `availableUSDC = 19.000,16` (snapshot holdings, reconciliat 10.11), dar tranzacția costă `19.008,3174`. Rezultatul ar fi **`availableUSDC = −8,16`** și `openPosition()` aruncă „Fonduri insuficiente".

Nu împacheta asta cu o ajustare rotundă. Diferența trebuie rezolvată **pe baza soldului real de pe Binance**, nu pe baza unei presupuneri:

- **Cere lui Dez soldul USDC curent de pe Binance** (post-tranzacție; zice că a rămas „0"). Poate și din interfață: butonul **Binance Sync** din modulul Trading afișează `Binance: X USDC` (merge pe cheia din Settings, e read-only — nu scrie nimic în DB).
- Notează dacă soldul e exact `0,00` sau ceva diferit (`0,02`, `1,47` etc.) — și dacă în ultimele 2 zile a intrat ceva pe Binance (deposit, rebate, transfer), pentru că asta se explică cei ~8,16 USDC.

**Aritmetica reconcilierii** (cu `W` = soldul real curent de pe Binance):

```
cost             = 19.008,3174
disponibil_țintă = W + cost                      ← soldul de pe Binance DUPĂ ce a scăzut tranzacția
gap              = round2(disponibil_țintă − availableUSDC_ledger)
```

- `gap ≈ +8,16` (dacă `W = 0,00`) → **corect**: ledgerul era cu 8,16 sub realitate. Inserează rândul de ajustare și loghează tranzacția.
- `|gap| < 0,01` → ledgerul e deja aliniat: **nu** insera ajustare, loghează direct tranzacția.
- `gap < 0` → **ABORTĂ** și raportează. Ledgerul ar fi mai mare decât wallet-ul, iar `holdings.usdc_amount` ar fi cel stalt (snapshot, nu realitate). Nu ajusta automat în sens invers — întreabă-mă.

## 5. Pași

**1. Citește starea reală din DB** (pe VPS, DB la `/var/data/dash-db/wealth.db`):
```bash
cd /root/Personal-Dash
sqlite3 /var/data/dash-db/wealth.db "SELECT position_number,status,buy_date,quantity,total_cost FROM trading_positions ORDER BY position_number;"
sqlite3 /var/data/dash-db/wealth.db "SELECT id,type,amount_usdc,note FROM cash_movements;"
sqlite3 /var/data/dash-db/wealth.db "SELECT * FROM holdings WHERE id=1;"
sqlite3 /var/data/dash-db/wealth.db "SELECT * FROM trading_account WHERE id=1;"
```
Asigură-te că starea e cea din §3 (1,46895 BTC / 19.000,16 USDC). **Dacă nu e, oprește-te și spune-mi** — înseamnă că au fost alte mișcări pe care nu le știu.

**2. Precedentul de urmat:** `scripts/log-btc-buy-2026-11-10.ts` (structura, guard-urile, math-check, dry-run → `--apply` → readback) și `scripts/reconcile-usdc-2026-11-10.ts` (rândul de ajustare idempotent în `cash_movements`). Le citește înainte să scrii ceva. Noul script: `scripts/log-btc-buy-2026-11-11.ts`.

**3. Scriptul — o singură tranzacție, cu ajustarea și cumpăra împreună:**

a. Citește `cash_movements`, `trading_positions`, `holdings` și calculează `availableUSDC` **exact ca `computeTradingAccount()`**: `cashSum − Σ total_cost(OPEN) + Σ profit(≠OPEN)`.

b. **Guard duplicate** — ca în precedentul: nu există deja rând `OPEN` cu același `buy_date` + `buy_price` + `quantity`.

c. **Math-check** — `71.670 × 0,26522` vs `19.008,3174`; raportul diferenței trebuie să fie `0,000%` (toleranță 0,5% ca în precedent).

d. **Ajustarea (dacă `gap ≥ 0,01`)** — `INSERT OR REPLACE INTO cash_movements (id, date, type, amount_usdc, note)` cu `type = 'adjustment'` și `id` fix, idempotent: **`cm-reconcile-usdc-2026-11-11`**. `amount_usdc = gap`, iar `note` explică: `Reconciliere ledger→wallet: availableUSDC X → Y (post-Buy P17, sold Binance confirmat de Dez)`. Dacă rândul există deja, nu-l mai insera.

e. **Loghează poziția** cu `openPosition(db, 71670, 0.26522, buyDate, notes, { totalCost: 19008.3174 })`:
   - `buyDate` = `"2026-11-11T09:02:23.000Z"` (11:02:23 EET = UTC+2; DST s-a terminat pe 25.10.2026, deci în noiembrie e tot UTC+2 — **aceeași convenție ca P15/P16**). `notes`: `Limit Buy BTC/USDC @ 71.670,00, filled 2026-11-11 11:02:23 RO time. Total cost = buyPrice × quantity (no fee deducted from BTC/USDC).`
   - `fee_rate` vine din server (`0.00075`), nu îl pasa tu.

f. **Guard fonduri** — verifică `cost <= availableUSDC + 0,01` (toleranță de 1 cent pentru erorile de virgulă mobilă). Fără toleranță, `19.008,3174` vs `19.000,16 + 8,1574` poate cădea sub limita și arunca greșit.

g. **Actualizează `holdings` (id = 1), patru coloane:**
   - `usdc_amount` = `usdc_value_usd` = **`W` (soldul real de pe Binance)** — **NU** `holdings.usdc_amount − cost`, care ar da `−8,16`. Prin construcție iese egal cu `availableUSDC` final.
   - `btc_amount` = `round8(holdings.btc_amount + 0.26522)` → `1,73417`
   - `btc_value_usd` = `round2(holdings.btc_value_usd + 19.008,3174)` → `≈ 140.864,16` (cost basis, nu valoare de piață — la fel ca la P14/P15/P16)
   - `eth_amount`, `eth_value_usd`, `stocks_*`, `eth_invested_usd` — **neatinse**.

h. **Wrap-ul totul într-un singur `db.transaction()`** — ajustarea + poziția + holdings, ca să nu rămână jumătate scris.

i. **Apoi** (tot în același script) **actualizează prețul curent BTC**: ia prețul live de pe Binance public (fără cheie) de pe VPS:
   ```bash
   curl -s "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDC"
   ```
   → `UPDATE trading_account SET current_btc_price = ? WHERE id = 1`. E câmpul de care `TradingSummary` ia prețul când prețul live nu e disponibil. (Nu atinge `total_usdc` / `available_usdc` din `trading_account` — sunt coloane vestigiale, contul se calculează din `computeTradingAccount()`.)

**4. Rulează pe VPS** (better-sqlite3 e addon Linux — local nu merge):
```bash
cd /root/Personal-Dash
npx tsx scripts/log-btc-buy-2026-11-11.ts          # dry-run
npx tsx scripts/log-btc-buy-2026-11-11.ts --apply  # commit
```

**5. Readback + verificare:**
- `SELECT * FROM trading_positions WHERE position_number = <nou>` → `status='OPEN'`, `quantity=0.26522`, `buy_price=71670`, `total_cost=19008.3174`, `buy_date='2026-11-11T09:02:23.000Z'`
- `computeTradingAccount(db)` → `btcHeld = 1.73417`, `availableUSDC = W` (tolerață 0,01), `totalUSDC = W + 140.864,16`
- `holdings` → `btc_amount = 1.73417`, `usdc_amount = W`, `eth_*` și `stocks_*` nemodificate
- **Guard final:** `|availableUSDC_final − W| < 0,01`. Dacă nu trece, **nu** forța — raportează.

**6. Nu e nevoie de build/deploy** — e un insert pur de date. Dacă se atinge codul (nu ar trebui), deploy **doar** prin `bash /root/Personal-Dash/deploy.sh` (niciun `pnpm build` / `pm2 restart` manual).

**7. Verificare în browser** (`dash.cadtechdental.ro`, modulul Trading):
- 4 poziții OPEN: P14, P15, P16, P17
- Total BTC `1,73417`, valoare la prețul live, P/L total ≈ `−17.313` (se mișcă cu prețul)
- Holdings: USDC ≈ `W`, BTC `1,73417`
- Cardul cu soldul USDC nu arată valori negative

**8. Raportează înapoi:** soldul real Binance (`W`), gap-ul de reconciliere, `availableUSDC` final, `btcHeld`, P/L total la prețul live, și ce ai mai atins.

## 6. Nu atinge

- `cash_movements` — doar rândul de ajustare `cm-reconcile-usdc-2026-11-11` (dacă e nevoie). Nu atingi rândurile existente, nu rescrii istoricul.
- `trading_account.total_usdc` / `available_usdc` / `accumulated_profit` — se calculează.
- Pozițiile P14, P15, P16 — rămân neatinse.
- `holdings` coloanele `eth_*`, `stocks_*`, `eth_invested_usd`.
- **Wallet-ul on-chain `0xe3360f51...` (88.793,98 USDC)** — e altceva, nu-l atinge. De acolo se plătește Binghatti (12th rată, 135.000 AED ≈ 37.135 USDC, 18.12.2026).
- Module care nu au legătură: `stock_positions`, `gold_positions`, `site_revenues`, `trades_income`.

## 7. De verificat cu Dez (întreabă, nu inventa)

1. **Soldul USDC real de pe Binance acum** (post-cumpărare) — valoarea exactă cu 2 zecimale. Fără ea nu se poate reconcilia corect.
2. **Ora fill-ului** — `11:02:23` e oră România (EET)? Binance arată ora browserului; confirmă că n-a fost UTC.
3. **Comisioane** — Binance a afișat `0` pentru acest fill (ca la P15/P16, plata e în BNB)? Verifică și dacă s-a mișcat ceva din soldul BNB.
4. **Intrări în ultimele 2 zile** — vreun deposit/rebate/transfer pe Binance între 10.11 și 11.11 care să explice cei ~8,16 USDC?
5. **Contextul** — a fost o cumpărare programată (DCA) sau manuală la atingerea prețului? (întreabă pentru log, nu pentru calcul)
