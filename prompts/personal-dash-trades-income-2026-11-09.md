# Prompt → Personal Dash: modul nou "Trades Income" (platforma TAG)

*(copiat din Personal Thinker, 2026-11-09 — de trimis ca atare în sesiunea Personal Dash)*

---

Adaugă în Personal Dash un modul nou, **"Trades Income"**, în care se loghează **sumele retrase (cash out) din platformele de copy trading**. Prima platformă: **TAG**.

## Semantica de business (citește-o înainte să scrii cod)

- **"Trades Income" = banii scoși de pe platformă**, nu valoarea contului și nici profitul ne ridicat.
- Pe TAG, **toată investiția e acoperită** (capitalul rămâne acoperit pe platformă). Prin urmare **orice sumă retrasă = 100% venit**. Nu loghea capitalul depus și nu scădea niciun cost din aceste sume.
- **Data** = data la care ai scos banii (nu data la care s-a generat profitul în cont).
- **Modulul e complet independent de "Trading Crypto"** (acela urmărește poziții BTC proprii pe Binance). **NU** atinge `trading_positions`, `cash_movements`, `trading_account`, `holdings`, `stock_*` sau `gold_*`.
- Platforma este o **dimensiune**, nu o valoare fixă: TAG acum, altele în viitor. Nu crea tabel separat de platforme — câmp text în același tabel, cu TAG pre-populat într-un `datalist`.

## Schema

```sql
CREATE TABLE IF NOT EXISTS trades_income (
  id       TEXT PRIMARY KEY,
  date     TEXT NOT NULL,   -- data retragerii, format YYYY-MM-DD
  amount   REAL NOT NULL,   -- suma retrasă (= venit), în moneda de mai jos
  currency TEXT NOT NULL DEFAULT 'USD',
  platform TEXT NOT NULL DEFAULT 'TAG',
  notes    TEXT
);
```

## Ce să faci, în ordine

1. **Tabel** — `src/lib/db.ts`: adaugă blocul `CREATE TABLE IF NOT EXISTS trades_income (...)` lângă blocul `gold_positions` (precedent: `db.ts:64-83`). Auto-migrate-ul rulează la primul `getDb()`, deci tabela se creează singură la deploy.

2. **Types** — `src/lib/types.ts`:
   ```ts
   export interface TradesIncomeEntry {
     id: string;
     date: string;
     amount: number;
     currency: "USD" | "USDT" | "EUR";
     platform: string;
     notes?: string;
   }
   export interface TradesIncomeState {
     tradesIncome: TradesIncomeEntry[];
   }
   ```
   Adaugă `TradesIncomeState` în `extends` de la `WealthDashboardStore` (`types.ts:353-363`), plus actions/selectors:
   - `addTradesIncome: (entry: Omit<TradesIncomeEntry, "id">) => void`
   - `deleteTradesIncome: (id: string) => void`
   - `getTradesIncomeTotal: () => number` — total pe toată perioada
   - `getTradesIncomeByPlatform: () => Record<string, number>` — sumă pe platformă
   - `getTradesIncomeMonth: (month: string) => number` — `month` = `"YYYY-MM"`

3. **API** — `src/app/api/data/route.ts` (tot datele trec prin singura rută `catch-all`; **nu** crea rută nouă de API):
   - **GET**: în obiectul `data` (`route.ts:54-169`) adaugă:
     ```ts
     tradesIncome: all("SELECT * FROM trades_income ORDER BY date DESC").map(rowToCamel),
     ```
     (`ORDER BY date DESC` — cele mai recente primele.)
   - **PATCH**: ramură nouă în lanțul `if/else if` (după ramura `module === "gold"`, precedent `route.ts:318-354`):
     ```ts
     } else if (module === "trades-income") {
       if (action === "upsertTradesIncome") {
         getDb()
           .prepare(
             `INSERT OR REPLACE INTO trades_income (id, date, amount, currency, platform, notes) VALUES (?, ?, ?, ?, ?, ?)`,
           )
           .run(data.id, data.date, data.amount, data.currency, data.platform, data.notes ?? null);
       } else if (action === "deleteTradesIncome") {
         getDb().prepare("DELETE FROM trades_income WHERE id = ?").run(data.id);
       }
     ```

4. **Store** — `src/lib/store.ts`:
   - state inițial: `tradesIncome: []`
   - în `hydrateFromApi` (precedent `store.ts:833-894`): `tradesIncome: data.tradesIncome ?? [],`
   - actions (precedent `addRevenue`, `store.ts:541-547`):
     ```ts
     addTradesIncome: (entry) => {
       const id = crypto.randomUUID();
       set((s) => ({ tradesIncome: [...s.tradesIncome, { ...entry, id }] }));
       void apiMutate("trades-income", "upsertTradesIncome", { ...entry, id });
     },
     deleteTradesIncome: (id) => {
       set((s) => ({ tradesIncome: s.tradesIncome.filter((e) => e.id !== id) }));
       void apiMutate("trades-income", "deleteTradesIncome", { id });
     },
     ```
   - dacă interfața `ApiData` din `src/lib/api.ts` enumeră explicit câmpurile, adaugă `tradesIncome?: TradesIncomeEntry[]`.

5. **Componente** — folder nou `src/components/trades-income/`:
   - **`TradesIncomeSummary.tsx`** — 3 carduri glass: *Total (toată perioada)*, *Luna curentă*, *Breakdown pe platformă*. Stil: `glass rounded-xl p-5` (precedent `GoldSummary.tsx:41`). Numere formatate cu `Intl.NumberFormat("ro-RO", { style: "currency", currency: "USD" })`.
   - **`TradesIncomeEntryModal.tsx`** — formular Zod:
     ```ts
     const schema = z.object({
       date: z.string().min(1, "Data retragerii este obligatorie"),
       amount: z.number().positive("Suma trebuie să fie pozitivă"),
       currency: z.enum(["USD", "USDT", "EUR"]),
       platform: z.string().min(1, "Platforma este obligatorie"),
       notes: z.string().optional(),
     });
     ```
     Platforma = `<input list="platforme">` + `<datalist id="platforme"><option value="TAG" /></datalist>` — TAG pre-populat, dar câmpul rămâne liber (platforme noi fără migrare). Sub câmpul de sumă, un text de ajutor: *„Suma retrasă de pe platformă = venit (pe TAG investiția e acoperită)"*. Shell-ul modalului: `fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm` + `glass rounded-xl border border-white/10` (`CLAUDE.md:290-309`).
   - **`TradesIncomeTable.tsx`** — coloane: dată, platformă, sumă, notițe; buton delete cu confirmare (precedent `RevenueTable.tsx:192-216`) + footer cu totaluri (precedent `RevenueTable.tsx:226-245`).

6. **Pagină** — `src/app/trades-income/page.tsx`:
   - `export const dynamic = "force-dynamic";` + `hydrateFromApi()` în `useEffect` (precedent `src/app/gold/page.tsx:10-25`).
   - Layout: `TradesIncomeSummary` sus, tabel dedesubt, buton „Adaugă retragere" care deschide modalul.

7. **Navigație**:
   - `src/components/layout/Sidebar.tsx` — în `NAV_ITEMS` (`:21-34`) adaugă `{ href: "/trades-income", label: "Trades Income", icon: CircleDollarSign }` (import din `lucide-react`; verifică că iconita nu e deja folosită). Poziție: după „Trading Gold".
   - `src/components/layout/TopBar.tsx` — în `PAGE_TITLES` (`:45-52`) adaugă `"/trades-income": { title: "Trades Income", breadcrumb: "Income" }`.

8. **[OPȚIONAL — confirmă cu Dez înainte]** integrarea în Net Worth. `TopBar.tsx:92-99` adună `sitesMonthRevenue` la `netWorth`; la fel s-ar putea aduna venitul din trades pe luna curentă. **Atenție:** e un flux (income), nu un activ (stock) — mixing-ul e moștenit de la modulul Sites. Fă-l doar dacă Dez cere; altfel lasă modulul independent.

9. **Documentație** — actualizează `CLAUDE.md`: REPO MAP (ruta `trades-income` + folderul `components/trades-income/`) și MODULE QUICK REF (rând nou: *Trades Income | Retrageri din platforme de copy trading | SQLite | addTradesIncome, deleteTradesIncome*).

10. **Deploy** — build-ul merge **doar pe VPS** (better-sqlite3 e addon Linux):
    ```bash
    git commit && git push          # local
    git pull && bash /root/Personal-Dash/deploy.sh   # pe VPS
    ```
    `deploy.sh` rulează automat `scripts/test-api.js` înainte de build; dacă testul pică, deploy-ul e oprit și build-ul vechi rămâne pornit — repară cauza, **nu** sări peste test și nu rula `pnpm build` / `pm2 restart` manual.
    - **Nu** crea tabelul printr-un script de migrare separată: auto-migrate-ul din `src/lib/db.ts` îl creează la primul `getDb()` după deploy. (Doar dacă vrei totuși un `scripts/migrate-trades-income.ts` cu pattern-ul dry-run/`--apply` din `scripts/log-iren-2026-10-12.ts` — atunci îl faci, dar nu e necesar.)
    - **Verificare finală în browser:** în sidebar apare „Trades Income"; pagina se deschide goală; adaugi o intrare de test (ex. `2026-11-09`, `100`, `USD`, `TAG`) → totalul se actualizează, tabela o afișează, iar după refresh rămâne (deci s-a scris în SQLite, nu doar în store). Apoi șterge intrarea de test. **Nu** lăsa date fictive în DB — înainte de final, confirmă cu Dez dacă vrea ca prima intrare reală să fie adăugată de tine.

## Nu atinge

`trading_positions`, `cash_movements`, `trading_account`, `holdings`, `stock_positions`, `stock_account`, `gold_positions`, `gold_account`, `site_revenues`. Acest modul e nou, izolat.

## De verificat cu Dez (întreabă, nu inventa)

- Moneda retragerilor la TAG: **USD sau USDT?** (implicit USD, USDT disponibil în form).
- Confirmă regula: pe TAG capitalul rămâne integral acoperit, deci **orice retragere e 100% venit**? (dacă există și retrageri care conțin capital returnat, trebuie un câmp suplimentar — spune-mi).
- Platforma „TAG" = **TAG Markets (CopyX)** sau altă platformă cu același nume? (se afișează în listă, așa că contează).
- Sunt retrageri anterioare (dinainte de 09.11.2026) de importat retroactiv?
- Venitul din trades intră în cifra de Net Worth din bara de sus (pasul 8) sau rămâne doar în modulul propriu?
