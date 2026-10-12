# StandBharat — Phase 14: Connect Real Command Center Metrics

## 1. Objective
Replace hardcoded Command Center KPIs with database-backed metrics dynamically derived from real-world data tracking (`TrafficMetrics` and `Integration`), and ensure these metrics render correctly in the frontend while discarding the static mock structures.

## 2. Changes Implemented

### Backend
* Updated `/api/dashboard/command-center` in `backend/app/api/endpoints/dashboard.py`.
* Integrated queries to dynamically map backend rows:
  * **Integrations Checks:** Checks if Google Analytics (`ga4`) is present on the tenant (brand). If missing, sets data as `NOT_CONFIGURED`.
  * **Data Presence Checks:** Maps the `TrafficMetrics` table aggregated sums to standard KPIs (Leads Generated, Conversions, etc.).
  * **Auth/Tenant Constraints:** Ensure all metric aggregations run through strict workspace (`X-Workspace-ID`) and brand (`X-Brand-ID`) isolation barriers via SQLAlchemy query filters instead of trusting headers independently.

### Frontend
* Audited `app/app/page.tsx` and `app/app/command-center/page.tsx`.
* Identified that the `isApi` frontend conditional rendered a hardcoded `NO_DATA` placeholder completely bypassing the response model (`DashboardResponse.kpis`).
* **Fixed:** Replaced `NO_DATA` static placeholders with dynamic mapping of `dataModel.kpis`.

```tsx
<div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
  {dataModel?.kpis?.map((kpi: any) => (
    <div key={kpi.label} className="bg-[#242222] border border-[#373333] rounded-xl p-5 hover:border-[#4A4545] transition-colors flex flex-col justify-between">
      <h3 className="text-[11px] font-bold text-[#A9A4A0] uppercase tracking-wider mb-3">{kpi.label}</h3>
      <div className="flex items-end justify-between">
        <span className={`text-[20px] font-bold ${kpi.value === 'NOT_CONFIGURED' || kpi.value === 'NO_DATA' ? 'text-[#A9A4A0] text-[14px]' : 'text-[#F5F3F1]'}`}>
           {kpi.value === 'NOT_CONFIGURED' ? 'Not Setup' : kpi.value === 'NO_DATA' ? 'No Data' : kpi.value}
        </span>
        {kpi.value !== 'NO_DATA' && kpi.value !== 'NOT_CONFIGURED' && (
          <div className={`flex items-center gap-1 text-[12px] font-bold ${kpi.trend === 'up' ? 'text-[#00A650]' : 'text-[#EF4444]'}`}>
            {kpi.change}
          </div>
        )}
      </div>
    </div>
  ))}
</div>
```

## 3. Test Automation & Validation

### Regression Tests Created
A new automated test file (`backend/tests/test_dashboard.py`) was introduced to thoroughly test data states:
1. `test_dashboard_no_integrations`: Validates empty `NOT_CONFIGURED` KPI fields.
2. `test_dashboard_with_integrations_no_data`: Validates `NO_DATA` KPI fields.
3. `test_dashboard_populated_data`: Validates accurately calculated values on `TrafficMetrics` rows.
4. `test_dashboard_cross_tenant_access`: Verifies the route rejects querying on un-owned brands (403).

### Execution commands:
```bash
python -m pytest tests/test_dashboard.py -v
```

### Result:
```
tests/test_dashboard.py::test_dashboard_no_integrations PASSED           [ 25%]
tests/test_dashboard.py::test_dashboard_with_integrations_no_data PASSED [ 50%]
tests/test_dashboard.py::test_dashboard_populated_data PASSED            [ 75%]
tests/test_dashboard.py::test_dashboard_cross_tenant_access PASSED       [100%]
======================= 4 passed, 15 warnings in 7.86s ========================
```

### Frontend Build Execution
Verified the Next.js production build succeeds with the updated frontend page constraints:
```bash
npm run build
```

### Result:
```
  Creating an optimized production build ...
✓ Compiled successfully in 4.1s
  Running TypeScript ...
  Finished TypeScript in 4.5s ...
✓ Generating static pages using 11 workers (26/26) in 731ms
```
